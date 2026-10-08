import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate

load_dotenv()

st.set_page_config(page_title="Assistant SQL", page_icon="🥇")
st.title("Discute avec la Base de Données Olympics")
st.markdown("Pose tes questions en langage naturel, l'IA générera et exécutera le SQL pour toi.")

@st.cache_resource
def init_system():
    model = ChatOllama(model="qwen2.5-coder:7b", temperature=0)

    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "") 
    DB_HOST = os.getenv("DB_HOST", "localhost") 
    DB_PORT = os.getenv("DB_PORT", "5432") 
    DB_NAME = os.getenv("DB_NAME", "postgres") 
    
    db_uri = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    db = SQLDatabase.from_uri(db_uri)
    return model, db

try:
    model, db = init_system()
except Exception as e:
    st.error(f"Erreur d'initialisation : {e}")
    st.stop()

try:
    schema_bd = db.get_table_info() 
except Exception as e:
    st.error(f"Erreur lors de la lecture du schéma de la base de données : {e}")
    st.stop()

template = """Tu es un expert PostgreSQL.
Voici le schéma de ma base de données :
{schema}

Écris la requête SQL exacte pour répondre à cette question : {question}
Ne renvoie RIEN D'AUTRE que le code SQL (pas de texte, pas d'explications).
"""

prompt_template = PromptTemplate.from_template(template)
chain = prompt_template | model

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question := st.chat_input("Ex: Affiche les 3 premiers pays de la table region"):
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})
    
    with st.chat_message("assistant"):
        with st.spinner("Génération et exécution de la requête en cours..."):
            try:
                reponse = chain.invoke({"schema": schema_bd, "question": question})
                
                sql_req = reponse.content.strip()
                if sql_req.startswith("```sql"):
                    sql_req = sql_req[6:]
                if sql_req.startswith("```"):
                    sql_req = sql_req[3:]
                if sql_req.endswith("```"):
                    sql_req = sql_req[:-3]
                sql_req = sql_req.strip()
                
                resultat = db.run(sql_req)
                
                reponse_visuelle = f"**Requête générée :**\n```sql\n{sql_req}\n```\n\n"

                if isinstance(resultat, str):
                    reponse_visuelle += f"**Résultat :**\n{resultat}"
                else:
                    try:
                        import pandas as pd
                        df = pd.DataFrame(resultat)
                        reponse_visuelle += "**Résultat :**"
                        st.dataframe(df, use_container_width=True)
                    except Exception:
                        reponse_visuelle += f"**Résultat brut :**\n{resultat}"

                st.markdown(reponse_visuelle)

            except Exception as e:
                erreur = f"Erreur lors du traitement : {e}"
                st.error(erreur)
                reponse_visuelle = erreur

    st.session_state.messages.append({"role": "assistant", "content": reponse_visuelle})