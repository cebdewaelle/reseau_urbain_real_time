from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from google.transit import gtfs_realtime_pb2
import requests
import pandas as pd
from datetime import datetime, date, time, timedelta, timezone
import pendulum
import os
import pytz
from commun.fonctions import retourne_jour, init_gtfs


BASEDIR_IN = "/opt/airflow/data/in/"
BASEDIR_OUT = "/opt/airflow/data/out/"
BASEDIR_ARC = "/opt/airflow/data/archives/"
URL_STABLE_VEHICULES = (
    "https://www.data.gouv.fr/api/1/datasets/r/5f571595-aef1-480f-acde-b9315d9f5f3b"
)
URL_STABLE_TRIPS = (
    "https://www.data.gouv.fr/api/1/datasets/r/af3f0734-ef07-468e-b8c9-aed97e4c8a32"
)


rep_jour = os.path.join(BASEDIR_IN, retourne_jour())
rep_gtfs = os.path.join(rep_jour, "gtfs")

gtfs_tz = pytz.timezone("Europe/Paris")


def parse_gtfs_time_to_datetime(time_str, service_date, timezone_obj):
    """
    Convertit un temps GTFS (pouvant dépasser 24h) en datetime timezone-aware

    Args:
        time_str: temps GTFS format "HH:MM:SS" (peut être >24h comme "25:30:00")
        service_date: date du service (datetime.date)
        timezone_obj: timezone pytz

    Returns:
        datetime timezone-aware
    """
    hours, minutes, seconds = map(int, time_str.split(":"))

    # Gérer les heures qui dépassent 24h
    extra_days = 0
    if hours >= 24:
        extra_days = hours // 24
        hours = hours % 24

    base_datetime = datetime.combine(service_date, time(hours, minutes, seconds))

    if extra_days > 0:
        base_datetime += timedelta(days=extra_days)

    return timezone_obj.localize(base_datetime)


def fetch_gtfs_rt(**context):
    try:
        response_trips = requests.get(URL_STABLE_TRIPS)
        feed_trips = gtfs_realtime_pb2.FeedMessage()
        feed_trips.ParseFromString(response_trips.content)

        records = []
        for entity in feed_trips.entity:
            # print(f"entity: {entity}")
            if entity.HasField("trip_update"):
                trip_id = entity.trip_update.trip.trip_id
                route_id = entity.trip_update.trip.route_id

                for stu in entity.trip_update.stop_time_update:
                    stop_id = stu.stop_id

                    if stu.HasField("arrival") and stu.arrival.HasField("time"):
                        realtime_arrival = datetime.fromtimestamp(stu.arrival.time)
                        realtime_arrival = realtime_arrival.astimezone(gtfs_tz)
                        # now_local = datetime.now(gtfs_tz)
                        records.append(
                            {
                                "trip_id": trip_id,
                                "route_id": route_id,
                                "stop_id": stop_id,
                                "realtime_arrival": realtime_arrival,
                                # "record_time": now_local,
                            }
                        )

        print(f"TOTAL RECORDS FETCHED: {len(records)}")

        if records:
            realtime_df = pd.DataFrame(records)

            hook = PostgresHook(postgres_conn_id="postgres_reseau")
            engine = hook.get_sqlalchemy_engine()

            realtime_df.to_sql("rt_temp", engine, if_exists="replace", index=False)
            print(f"Données RT stockées en base: {len(records)} records")

            return len(records)
        else:
            print("Aucune donnée RT trouvée")
            return 0

    except requests.exceptions.RequestException as ex:
        print(f"Erreur lors de la récupération du flux GTFS-RT: {ex}")
        # Retourner 0 si une erreur survient
        return 0
    except Exception as e:
        print(f"Une erreur inattendue est survenue: {e}")
        return 0


def enrich_with_static(**context):
    hook = PostgresHook(postgres_conn_id="postgres_reseau")
    engine = hook.get_sqlalchemy_engine()

    with engine.connect() as conn:
        realtime_df = pd.read_sql("SELECT * FROM rt_temp", conn)

        stop_times = pd.read_sql(
            "SELECT trip_id, stop_id, arrival_time, stop_sequence FROM stop_times", conn
        )
        # stop.name route.route_long_name

        routes = pd.read_sql("SELECT route_id, route_long_name FROM routes", conn)

        stops = pd.read_sql(
            "SELECT stop_id, stop_name, stop_lat, stop_lon FROM stops", conn
        )

    # Convertir realtime_arrival en datetime si ce n'est pas déjà fait
    realtime_df["realtime_arrival"] = pd.to_datetime(realtime_df["realtime_arrival"])
    # realtime_df["record_time"] = pd.to_datetime(realtime_df["record_time"])

    # Convertir en string pour être sûr de la compatibilité
    realtime_df["trip_id"] = realtime_df["trip_id"].astype(str)
    realtime_df["stop_id"] = realtime_df["stop_id"].astype(str)
    stop_times["trip_id"] = stop_times["trip_id"].astype(str)
    stop_times["stop_id"] = stop_times["stop_id"].astype(str)

    # Date du service (aujourd'hui en local)
    service_date = datetime.now(gtfs_tz).date()

    # Conversion des temps GTFS en datetime timezone
    def convert_gtfs_time(time_str):
        return parse_gtfs_time_to_datetime(time_str, service_date, gtfs_tz)

    stop_times["planned_arrival"] = stop_times["arrival_time"].apply(convert_gtfs_time)

    merged = pd.merge(
        realtime_df,
        stop_times[["trip_id", "stop_id", "planned_arrival", "stop_sequence"]],
        on=["trip_id", "stop_id"],
        how="left",
    )
    merged2 = pd.merge(
        merged,
        routes[["route_id", "route_long_name"]],
        on=["route_id"],
        how="left",
    )
    merged3 = pd.merge(
        merged2,
        stops[["stop_id", "stop_name", "stop_lat", "stop_lon"]],
        on=["stop_id"],
        how="left",
    )

    merged = merged3.dropna(subset=["route_long_name"])
    merged = merged[merged["route_long_name"].str.strip() != ""]

    # Calcul du retard en secondes
    merged["delay"] = (
        (merged["realtime_arrival"] - merged["planned_arrival"])
        .dt.total_seconds()
        .astype("Int64")
    )

    merged = merged.dropna(subset=["planned_arrival"])

    print(f"Nombre de correspondances trouvées: {len(merged)}")
    if len(merged) > 0:

        try:
            df_to_insert = merged.copy()
            df_to_insert.to_sql("anomalies", engine, if_exists="replace", index=False)
            print(f"{len(df_to_insert)} anomalies insérées avec succès")
            return f"{len(df_to_insert)} anomalies insérées avec succès"
        except Exception as e:
            print(f"Erreur lors de l'insertion dans la base de données : {e}")
            return "Échec de l'insertion"
    else:
        print("Aucune donnée enrichie à insérer.")
        return "Aucune anomalie à insérer"


def export_csv_data(**context):

    hook = PostgresHook(postgres_conn_id="postgres_reseau")
    engine = hook.get_sqlalchemy_engine()

    with engine.connect() as conn:
        anomalies_df = pd.read_sql("SELECT * FROM anomalies", conn)

    now_local = datetime.now(gtfs_tz)
    now_str = now_local.strftime("%Y%m%d_%H%M%S")

    nomfic_export = os.path.join(BASEDIR_OUT, "current_data.csv")
    nomfic_archive = os.path.join(BASEDIR_ARC, f"ano_{now_str}.csv")

    if os.path.exists(nomfic_export):
        os.rename(nomfic_export, nomfic_archive)

    anomalies_df.to_csv(nomfic_export, ";", index=False)
    return f"Fichier archivé: {nomfic_archive}"


def export_csv_mean_delays(**context):
    nomfic_import = os.path.join(BASEDIR_OUT, "current_data.csv")

    now_local = datetime.now(gtfs_tz)
    today_str = now_local.strftime("%Y%m%d")
    time_str = now_local.strftime("%H:%M:%S")

    df = pd.read_csv(nomfic_import, sep=";")

    mean_delay = df["delay"].mean()

    print(f"delai global moyen: {mean_delay}")

    dict_now_stats = {"execution_date": time_str, "delai_moyen": mean_delay}
    df_now_stats = pd.DataFrame.from_records([dict_now_stats])

    nomfic_export = os.path.join(BASEDIR_OUT, f"global_delays_{today_str}.csv")
    if not os.path.exists(nomfic_export):
        df_stats = df_now_stats
    else:
        df_stats = pd.read_csv(nomfic_export, sep=";")
        df_stats = pd.concat([df_stats, df_now_stats], ignore_index=True)

    print(f"stats: {df_stats}")
    df_stats.to_csv(nomfic_export, ";", index=False)
    return f"Fichier mis à jour: {nomfic_export}"


def export_csv_mean_route_delays(**context):
    nomfic_import = os.path.join(BASEDIR_OUT, "current_data.csv")

    now_local = datetime.now(gtfs_tz)
    today_str = now_local.strftime("%Y%m%d")
    time_str = now_local.strftime("%H:%M:%S")

    df = pd.read_csv(nomfic_import, sep=";")

    df_by_route = df.groupby("route_id")["delay"].mean().reset_index()
    df_by_route["execution_date"] = time_str
    df_by_route = df_by_route[["execution_date", "route_id", "delay"]]
    df_by_route.rename(columns={"delay": "delai_moyen"}, inplace=True)

    nomfic_export = os.path.join(BASEDIR_OUT, f"delays_routes_{today_str}.csv")
    if not os.path.exists(nomfic_export):
        df_stats = df_by_route
    else:
        df_stats = pd.read_csv(nomfic_export, sep=";")
        df_stats = pd.concat([df_stats, df_by_route], ignore_index=True)

    df_stats.to_csv(nomfic_export, ";", index=False)
    return f"Fichier mis à jour: {nomfic_export}"


with DAG(
    "gtfs_realtime",
    schedule_interval="*/5 * * * *",
    start_date=pendulum.datetime(2025, 9, 6, tz="UTC"),
    catchup=False,
    tags=["gtfs", "realtime"],
) as dag:

    fetch = PythonOperator(
        task_id="fetch_gtfs_rt",
        python_callable=fetch_gtfs_rt,
        provide_context=True,
    )

    enrich = PythonOperator(
        task_id="enrich_with_static",
        python_callable=enrich_with_static,
        provide_context=True,
    )

    export = PythonOperator(
        task_id="export_csv_data",
        python_callable=export_csv_data,
        provide_context=True,
    )

    stats = PythonOperator(
        task_id="export_csv_mean_delays",
        python_callable=export_csv_mean_delays,
        provide_context=True,
    )

    stats_delais = PythonOperator(
        task_id="export_csv_mean_route_delays",
        python_callable=export_csv_mean_route_delays,
        provide_context=True,
    )

    fetch >> enrich >> export >> stats >> stats_delais
