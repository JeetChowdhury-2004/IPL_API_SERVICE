from .database import get_connection
from psycopg2.extras import execute_values


def insert_wickets(wickets):

    """
    Batch insert wickets into PostgreSQL.
    """

    # =====================================
    # EMPTY CHECK
    # =====================================

    if not wickets:
        return

    conn = get_connection()

    cursor = conn.cursor()

    # =====================================
    # INSERT QUERY
    # =====================================

    query = """

        INSERT INTO wickets (

            delivery_key,
            player_out,
            dismissal_kind,
            fielders_involved

        )

        VALUES %s

    """

    # =====================================
    # BUILD VALUES
    # =====================================

    values = [

        (

            w["delivery_key"],

            w["player_out"],

            w["dismissal_kind"],

            w["fielders_involved"]

        )

        for w in wickets
    ]

    # =====================================
    # INSERT
    # =====================================

    try:

        execute_values(

            cursor,
            query,
            values,

            page_size=1000
        )

        conn.commit()

        print(

            f"Inserted "
            f"{len(values)} wickets"
        )

    except Exception as e:

        conn.rollback()

        print(

            f"Wicket batch insert failed:\n{e}"
        )

    finally:

        cursor.close()

        conn.close()