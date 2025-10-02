from datetime import date
import os


def retourne_jour() -> str:
    return date.today().strftime("%Y%m%d")


def init_gtfs(rep_jour: str, rep_gtfs: str):
    os.makedirs(rep_jour, exist_ok=True)
    os.makedirs(rep_gtfs, exist_ok=True)
