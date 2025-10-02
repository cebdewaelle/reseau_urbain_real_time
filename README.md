# reseau_urbain_real_time
Traitement des données en temps réel d'un réseau de transport urbain




# exemple de fichier .env (nommé .env.dev)
# Postgres
POSTGRES_USER_AIRFLOW=airflow_user
POSTGRES_PASSWORD=motdepasse
POSTGRES_DB_AIRFLOW=airflow_db
POSTGRES_USER_RESEAU=reseau_user
POSTGRES_DB_RESEAU=reseau_db

# pgAdmin
PGADMIN_DEFAULT_EMAIL=mon_email@example.com
PGADMIN_DEFAULT_PASSWORD=motdepasse

# Airflow
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://${POSTGRES_USER_AIRFLOW}:${POSTGRES_PASSWORD}@psql_dev:5432/${POSTGRES_DB_AIRFLOW}
AIRFLOW__CORE__FERNET_KEY=AAAAA11111AAAAA11111AAAAA11111AAAAA11111AAA=
AIRFLOW__WEBSERVER__SECRET_KEY=11111AAAAA11111AAAAA11111AAAAA11



Commandes d'initialisation d'airflow

docker compose -f docker-compose.yaml --env-file .env.dev build
docker compose -f docker-compose.yaml --env-file .env.dev up -d

# Initialisation de l'enironnement airflow
docker compose -f docker-compose.yaml --env-file .env.dev run airflow-webserver airflow db init

# création de l'utilisateur admin d'airflow
docker compose -f docker-compose.yaml --env-file .env.dev run airflow-webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
    

docker compose -f docker-compose.yaml --env-file .env.dev up -d


## Remplacer les ${} par les valeurs du .env
# création de l'utilisateur POSTGRES_USER_RESEAU
CREATE USER ${POSTGRES_USER_RESEAU} WITH PASSWORD '${POSTGRES_PASSWORD}';

# création de la base POSTGRES_DB_RESEAU
CREATE DATABASE ${POSTGRES_DB_RESEAU} OWNER ${POSTGRES_USER_RESEAU};

# affectation des droits
GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB_RESEAU} TO ${POSTGRES_USER_RESEAU};


# créer une base de données qui contiendra les données métier


