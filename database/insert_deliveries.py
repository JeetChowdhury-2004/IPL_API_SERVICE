from database.database import get_connection
from psycopg2.extras import execute_values


def insert_deliveries(deliveries):

    """
    Batch insert deliveries into PostgreSQL.

    Parameters:
        deliveries (list): List of delivery dictionaries
    """

    # Skip empty list
    if not deliveries:
        return

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO deliveries (

            delivery_key,
            match_id,
            innings,
            over_no,
            ball_no,
            batter,
            bowler,
            non_striker,
            batting_team,
            bowling_team,
            batsman_run,
            extras_run,
            total_run,
            extra_type,
            phase,
            is_boundary,
            is_dot_ball,
            non_boundary,
            is_super_over

        )

        VALUES %s

        ON CONFLICT (delivery_key)
        DO NOTHING
    """

    values = [

        (

            d["delivery_key"],
            d["match_id"],
            d["innings"],
            d["over_no"],
            d["ball_no"],
            d["batter"],
            d["bowler"],
            d["non_striker"],
            d["batting_team"],
            d["bowling_team"],
            d["batsman_run"],
            d["extras_run"],
            d["total_run"],
            d["extra_type"],
            d["phase"],
            d["is_boundary"],
            d["is_dot_ball"],
            d["non_boundary"],
            d["is_super_over"]

        )

        for d in deliveries
    ]

    try:

        execute_values(

            cursor,
            query,
            values,

            # rows per SQL statement
            page_size=10000
        )

        conn.commit()

        print(
            f"Inserted {len(values)} deliveries"
        )

    except Exception as e:

        conn.rollback()

        print(
            f"Delivery batch insert failed:\n{e}"
        )

    finally:

        cursor.close()
        conn.close()