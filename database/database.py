import os

import psycopg2

from psycopg2.extras import RealDictCursor

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

# =========================================
# DATABASE CONFIG
# =========================================

DB_CONFIG = {

    "host": os.getenv(

        "DB_HOST",

        "localhost"
    ),

    "database": os.getenv(

        "DB_NAME",

        "ipl_db"
    ),

    "user": os.getenv(

        "DB_USER",

        "postgres"
    ),

    "password": os.getenv(

        "DB_PASSWORD",

        ""
    ),

    "port": os.getenv(

        "DB_PORT",

        "5432"
    )
}

# =========================================
# GET CONNECTION
# =========================================

def get_connection():

    """
    Create PostgreSQL connection.
    """

    try:

        conn = psycopg2.connect(

            host=DB_CONFIG["host"],

            database=DB_CONFIG["database"],

            user=DB_CONFIG["user"],

            password=DB_CONFIG["password"],

            port=DB_CONFIG["port"],

            # =============================
            # SAFETY
            # =============================

            connect_timeout=10,

            application_name="ipl_api"
        )

        # =================================
        # UTF-8 SUPPORT
        # =================================

        conn.set_client_encoding(

            "UTF8"
        )

        return conn

    except Exception as e:

        print("\n=================================")

        print("DATABASE CONNECTION ERROR")

        print("=================================\n")

        print(e)

        print("\n=================================\n")

        raise e

# =========================================
# TEST CONNECTION
# =========================================

def test_connection():

    """
    Test database connectivity.
    """

    conn = None

    cursor = None

    try:

        conn = get_connection()

        cursor = conn.cursor(

            cursor_factory=RealDictCursor
        )

        cursor.execute(

            "SELECT version();"
        )

        version = cursor.fetchone()

        print("\n=================================")

        print("DATABASE CONNECTED")

        print("=================================\n")

        print(version)

        print("\n=================================\n")

    except Exception as e:

        print("\n=================================")

        print("DATABASE TEST FAILED")

        print("=================================\n")

        print(e)

        print("\n=================================\n")

    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()

# =========================================
# MAIN
# =========================================

if __name__ == "__main__":

    test_connection()
