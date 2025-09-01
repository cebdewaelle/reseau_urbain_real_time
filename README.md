# reseau_urbain_real_time
Traitement des données en temps réel d'un réseau de transport urbain


Commandes d'initialisation d'airflow

docker compose -f docker-compose.yaml --env-file .env.dev build
docker compose -f docker-compose.yaml --env-file .env.dev up -d
docker compose -f docker-compose.yaml --env-file .env.dev run airflow-webserver airflow db init
docker compose -f docker-compose.yaml --env-file .env.dev run airflow-webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin


docker compose -f docker-compose.yaml --env-file .env.dev up -d
