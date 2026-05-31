from .database import get_connection
from psycopg2.extras import execute_values


def insert_wickets(wickets):

    """
    Batch insert wickets into PostgreSQL.
    """

    # Skip empty list
    if not wickets:
        return

    conn = get_connection()

    cursor = conn.cursor()

    query = """
        INSERT INTO wickets (

            delivery_key,
            player_out,
            dismissal_kind,
            fielders_involved

        )

        VALUES %s
    """

    values = [

        (

            w["delivery_key"],
            w["player_out"],
            w["dismissal_kind"],
            w["fielders_involved"]

        )

        for w in wickets
    ]

    try:

        execute_values(

            cursor,
            query,
            values,

            # rows per SQL statement
            page_size=1000
        )

        conn.commit()

        print(
            f"Inserted {len(values)} wickets"
        )

    except Exception as e:

        conn.rollback()

        print(
            f"Wicket batch insert failed:\n{e}"
        )

    finally:

        cursor.close()
        conn.close()