# from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow import DAG
from datetime import datetime, date
import duckdb
import zipfile
import requests
import os


BASEDIR_IN = "/opt/airflow/data/in/"
BASEDIR_ARC = "/opt/airflow/data/archives/"
URL_STABLE = (
    "https://www.data.gouv.fr/api/1/datasets/r/f5678ab2-c863-4b48-ba1f-9021c7d97634"
)


def retourne_jour() -> str:
    return date.today().strftime("%Y%m%d")


def download_dtfs():
    jour = retourne_jour()
    rep_destination = os.path.join(BASEDIR_IN, jour)
    os.makedirs(rep_destination, exist_ok=True)

    nomfic = "gtfs.zip"
    chemin_fic = os.path.join(rep_destination, nomfic)

    try:
        with requests.get(URL_STABLE, stream=True) as req:
            req.raise_for_status()
            with open(chemin_fic, "wb") as fic:
                for chunk in req.iter_content(chunk_size=8192):
                    fic.write(chunk)
        print(f"Fichier téléchargé avec succès: {chemin_fic}")
    except requests.exceptions.RequestException as ex:
        raise Exception(f"Erreur lors du téléchargement du fichier: {ex}")


def unzip_dtfs():
    jour = retourne_jour()
    rep_zip = os.path.join(BASEDIR_IN, jour)

    rep_unzip = os.path.join(rep_zip, "gtfs")
    fic_zip = "gtfs.zip"

    if not fic_zip:
        raise FileNotFoundError("Aucun fichier .zip dans le répertoire.")

    chemin_zip = os.path.join(rep_zip, fic_zip)

    try:
        with zipfile.ZipFile(chemin_zip, "r") as zip_ref:
            zip_ref.extractall(rep_unzip)
        print(f"Fichier décompressé avec succès dans : {rep_unzip}")
    except zipfile.BadZipFile as ex:
        raise Exception(f"Erreur lors de la décompression du fichier : {ex}")


def archive_dtfs():
    jour = retourne_jour()
    rep_zip = os.path.join(BASEDIR_IN, jour)

    old_fic_zip = os.path.join(rep_zip, "gtfs.zip")
    new_fic_zip = os.path.join(BASEDIR_ARC, f"gtfs{jour}.zip")

    try:
        os.rename(old_fic_zip, new_fic_zip)
        print(f"Fichier {new_fic_zip} archivé.")
    except PermissionError:
        print("Problèmes de droits lors du renommage.")


default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 9, 1),
    # "retries": 1,
}


with DAG(
    "dag_download_unzip_archive_gtfs_statiques",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["statiques", "Extract", "download", "unzip", "archive"],
) as dag_download_unzip_gtfs_statiques:
    t0 = PythonOperator(
        task_id="download_gtfs",
        python_callable=download_dtfs,
    )
    t1 = PythonOperator(
        task_id="unzip_gtfs",
        python_callable=unzip_dtfs,
    )
    t2 = PythonOperator(
        task_id="archive_gtfs",
        python_callable=archive_dtfs,
    )
    t0 >> t1 >> t2


# def lecture_gtfs_date(date_lecture: str = ""):
#     rep_jour = date.today().strftime("%Y%m%d")

#     if date_lecture:
#         rep = f"./data/in/{date_lecture}"
#     else:
#         # date_lecture = date.today()
#         date_lecture = date.today().strftime("%Y%m%d")
#         print(date_lecture)
#         rep = f"./data/in/{rep_jour}"


# def connect_duckdb():
#     # Le chemin vers le fichier DuckDB dans le conteneur Airflow
#     db_path = "/opt/airflow/duckdb/reseau_urbain.duckdb"

#     # Connexion
#     con = duckdb.connect(db_path)
#     return con

# def select_test():
#     con = connect_duckdb()

#     result = con.execute("SELECT * FROM test").fetchall()
#     for row in result:
#         print(f"nom du test: {row[1]}")
