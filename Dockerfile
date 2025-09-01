FROM apache/airflow:2.10.2-python3.9

RUN pip install psycopg2-binary
