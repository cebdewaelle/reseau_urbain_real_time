# reseau_urbain_real_time
Traitement des données en temps réel d'un réseau de transport urbain

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


# accéder au conteneur duckdb
docker compose -f docker-compose.yaml --env-file .env.dev exec duckdb duckdb /data/reseau_urbain.duckdb

# création d'une table test dans le conteneur duckdb (qui va créer le fichier ma_database.duckdb)
CREATE TABLE reseau_urbain.main.test (
	id integer NOT NULL,
	name_t varchar(100) NOT NULL,
	CONSTRAINT test_pk PRIMARY KEY (id)
);

# insertion de quelques lignes dans la table test
INSERT INTO test (id, name_t) VALUES (1, '1test1');
INSERT INTO test (id, name_t) VALUES (2, '2test');
INSERT INTO test (id, name_t) VALUES (3, 'test');

# QUITTER LE CONTENEUR DUCKDB POUR "LIBERER" le fichier ma_database.duckdb avec un double ctrl-c
