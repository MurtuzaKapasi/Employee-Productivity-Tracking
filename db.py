import psycopg2
from psycopg2 import sql

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="employee_tracking",
        user="postgres",
        password="Emp123"
    )
    return conn
