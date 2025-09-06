# from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow import DAG
from datetime import datetime, date
from google.transit import gtfs_realtime_pb2
import os
import pandas as pd
import requests


BASEDIR_IN = "/opt/airflow/data/in/"
BASEDIR_ARC = "/opt/airflow/data/archives/"
URL_STABLE_VEHICULES = (
    "https://www.data.gouv.fr/api/1/datasets/r/5f571595-aef1-480f-acde-b9315d9f5f3b"
)
URL_STABLE_TRIPS = (
    "https://www.data.gouv.fr/api/1/datasets/r/af3f0734-ef07-468e-b8c9-aed97e4c8a32"
)


def retourne_jour() -> str:
    return date.today().strftime("%Y%m%d")


rep_jour = os.path.join(BASEDIR_IN, retourne_jour())


def download_rt_gtfs(url: str, nomfic: str):
    os.makedirs(rep_jour, exist_ok=True)
    chemin_fic = os.path.join(rep_jour, nomfic)

    try:
        with requests.get(url, stream=True, timeout=30) as req:
            req.raise_for_status()
            with open(chemin_fic, "wb") as fic:
                for chunk in req.iter_content(chunk_size=8192):
                    fic.write(chunk)
        print(f"Fichier téléchargé avec succès: {chemin_fic}")
    except requests.exceptions.RequestException as ex:
        raise Exception(f"Erreur lors du téléchargement du fichier {nomfic}: {ex}")


def parse_and_persist_trip_updates():
    # chemin_fic = os.path.join(rep_jour, nomfic)
    feed = gtfs_realtime_pb2.FeedMessage()

    response = requests.get(URL_STABLE_TRIPS)
    feed.ParseFromString(response.content)
    for entity in feed.entity:
        if entity.HasField("trip_update"):
            print(entity.trip_update)

    # with open(chemin_fic, "rb") as fic:
    #     feed.ParseFromString(fic.read())

    # rows = []
    # for entity in feed.entity:
    #     if entity.HasField("trip_update"):
    #         tp = entity.trip_update
    #         rows.append(
    #             {
    #                 "trip_id": tp.trip.trip_id,
    #                 "start_time": tp.trip.start_time,
    #                 "start_date": tp.trip.start_date,
    #                 "timestamp": (
    #                     datetime.fromtimestamp(tp.timestamp) if tp.timestamp else None
    #                 ),
    #             }
    #         )

    # df = pd.DataFrame(rows)

    # if not df.empty:
    #     hook = PostgresHook(postgres_conn_id="postgres_reseau")
    #     engine = hook.get_sqlalchemy_engine()
    #     df.to_sql("trip_updates", engine, if_exists="append", index=False)
    #     print(f"{len(df)} enregistrements insérés dans trip_updates")

    # os.remove(chemin_fic)
    # print(f"Fichier {chemin_fic} supprimé.")


def parse_persist_position_vehicules(nomfic: str):
    chemin_fic = os.path.join(rep_jour, nomfic)
    feed = gtfs_realtime_pb2.FeedMessage()

    with open(chemin_fic, "rb") as fic:
        feed.ParseFromString(fic.read())

    rows = []
    for entity in feed.entity:
        if entity.HasField("vehicle"):
            veh = entity.vehicle
            rows.append(
                {
                    "vehicle_id": veh.vehicle.id,
                    "trip_id": veh.trip.trip_id,
                    "latitude": veh.position.latitude,
                    "longitude": veh.position.longitude,
                    "timestamp": (
                        datetime.fromtimestamp(veh.timestamp) if veh.timestamp else None
                    ),
                }
            )

    df = pd.DataFrame(rows)

    if not df.empty:
        hook = PostgresHook(postgres_conn_id="postgres_reseau")
        engine = hook.get_sqlalchemy_engine()
        df.to_sql("vehicle_positions", engine, if_exists="append", index=False)
        print(f"{len(df)} enregistrements insérés dans vehicle_positions")

    os.remove(chemin_fic)
    print(f"Fichier {chemin_fic} supprimé.")


default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 9, 1),
    # "retries": 1,
}

with DAG(
    "dag_gtfs_realtime",
    default_args=default_args,
    schedule_interval="*/30 * * * *",
    catchup=False,
    tags=["real-time", "Extract", "download", "archive"],
) as dag_download_gtfs_realtime:
    # t_dowload_vehicles_maj = PythonOperator(
    #     task_id="download_vehicules_maj",
    #     python_callable=download_rt_gtfs,
    #     op_args=[URL_STABLE_VEHICULES, "vehicle-positions"],
    # )
    # t_dowload_trips_maj = PythonOperator(
    #     task_id="download_trips_maj",
    #     python_callable=download_rt_gtfs,
    #     op_args=[URL_STABLE_TRIPS, "trips"],
    # )
    t_parse_and_persist_trip_updates = PythonOperator(
        task_id="rt_trips_updates",
        python_callable=parse_and_persist_trip_updates,
    )

    # t_dowload_vehicles_maj >>
    # t_dowload_trips_maj >>
