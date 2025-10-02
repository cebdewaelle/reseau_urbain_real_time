# from airflow import DAG
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import pandas as pd
import requests
import zipfile
from commun.fonctions import retourne_jour, init_gtfs


BASEDIR_IN = "/opt/airflow/data/in/"
BASEDIR_ARC = "/opt/airflow/data/archives/"
URL_STABLE = (
    "https://www.data.gouv.fr/api/1/datasets/r/f5678ab2-c863-4b48-ba1f-9021c7d97634"
)


rep_jour = os.path.join(BASEDIR_IN, retourne_jour())
rep_gtfs = os.path.join(rep_jour, "gtfs")


def download_gtfs():
    nomfic = "gtfs.zip"
    chemin_fic = os.path.join(rep_jour, nomfic)

    try:
        with requests.get(URL_STABLE, stream=True) as req:
            req.raise_for_status()
            with open(chemin_fic, "wb") as fic:
                for chunk in req.iter_content(chunk_size=8192):
                    fic.write(chunk)
        print(f"Fichier téléchargé avec succès: {chemin_fic}")
    except requests.exceptions.RequestException as ex:
        raise Exception(f"Erreur lors du téléchargement du fichier: {ex}")


def unzip_gtfs():
    fic_zip = "gtfs.zip"

    if not fic_zip:
        raise FileNotFoundError("Aucun fichier .zip dans le répertoire.")

    chemin_zip = os.path.join(rep_jour, fic_zip)

    try:
        with zipfile.ZipFile(chemin_zip, "r") as zip_ref:
            zip_ref.extractall(rep_gtfs)
        print(f"Fichier décompressé avec succès dans : {rep_gtfs}")
    except zipfile.BadZipFile as ex:
        raise Exception(f"Erreur lors de la décompression du fichier : {ex}")


def archive_gtfs():
    jour = retourne_jour()

    old_fic_zip = os.path.join(rep_jour, "gtfs.zip")
    new_fic_zip = os.path.join(BASEDIR_ARC, f"gtfs{jour}.zip")

    try:
        os.rename(old_fic_zip, new_fic_zip)
        print(f"Fichier {new_fic_zip} archivé.")
    except PermissionError:
        print("Problèmes de droits lors du renommage.")


def persist_et_supprime(rep_gtfs: str):
    liste_fic_txt = get_liste_fichiers_txt()
    for nomfic in liste_fic_txt:
        chemin_fic = os.path.join(rep_gtfs, nomfic)
        df = pd.read_csv(chemin_fic, sep=",", header=0)

        nom_table = os.path.splitext(nomfic)[0]

        hook = PostgresHook(postgres_conn_id="postgres_reseau")
        engine = hook.get_sqlalchemy_engine()

        nb_lig = df.to_sql(nom_table, engine, if_exists="replace", index=False)
        print(f"Fichier {nomfic}, {nb_lig} lignes insérées en bdd ({nom_table}).")

        try:
            os.remove(chemin_fic)
            print(f"Fichier {chemin_fic} supprimé.")
        except PermissionError:
            print(f"Problèmes de droits lors de la suppression de {chemin_fic}.")


def get_liste_fichiers_txt():
    liste_fic_txt = [
        fic_txt for fic_txt in os.listdir(rep_gtfs) if fic_txt.endswith(".txt")
    ]
    return liste_fic_txt


default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 9, 1),
    # "retries": 1,
}


with DAG(
    "dag_gtfs_statiques",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["statiques", "gtfs"],
) as dag_gtfs_statiques:

    t_init = PythonOperator(
        task_id="init_gtfs",
        python_callable=init_gtfs,
        op_args=[rep_jour, rep_gtfs],
    )
    t_download = PythonOperator(
        task_id="download_gtfs",
        python_callable=download_gtfs,
    )
    t_unzip = PythonOperator(
        task_id="unzip_gtfs",
        python_callable=unzip_gtfs,
    )
    t_archive = PythonOperator(
        task_id="archive_gtfs",
        python_callable=archive_gtfs,
    )
    t_persist_supprime = PythonOperator(
        task_id="persist_et_supprime",
        python_callable=persist_et_supprime,
        op_args=[rep_gtfs],
    )
    t_init >> t_download >> t_unzip >> [t_archive, t_persist_supprime]
