# Assistant SQL en Langage Naturel

Une interface développée avec **Streamlit** et **LangChain** qui traduit des questions en langage naturel vers des requêtes SQL exécutables. L'application interroge une base de données PostgreSQL locale à l'aide d'un modèle d'IA local (**Ollama**).

## Fonctionnalités
- Interface : UI propulsée par Streamlit avec conservation de l'historique de la session.
- Modèle Local : Utilisation de `qwen2.5-coder:7b` via Ollama pour garantir la confidentialité des données et des performances optimales en génération de code.
- Connexion PostgreSQL : Exécution directe et sécurisée des requêtes sur la base de données.
- Affichage dynamique : Les résultats SQL sont automatiquement formatés en tableaux interactifs grâce à Pandas.

## 🛠 Prérequis
- Python 3.8+
- [Ollama](https://ollama.com/) installé localement.
- Une base de données PostgreSQL.
