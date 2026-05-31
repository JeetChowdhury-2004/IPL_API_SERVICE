import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "ipl_db",
    "user": "postgres",
    "password": "jeet2004"
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)