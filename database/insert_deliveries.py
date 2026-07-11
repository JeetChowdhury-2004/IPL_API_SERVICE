from psycopg2.extras import execute_values

from .database import get_connection

# =========================================
# INSERT DELIVERIES
# =========================================

def insert_deliveries(deliveries):

    """
    Batch insert deliveries into PostgreSQL.
    """

    # =====================================
    # EMPTY CHECK
    # =====================================

    if not deliveries:

        return 0

    # =====================================
    # REMOVE DUPLICATES IN MEMORY
    # =====================================

    unique_deliveries = {}

    for d in deliveries:

        delivery_key = d.get("delivery_key")

        if delivery_key:

            unique_deliveries[delivery_key] = d

    deliveries = list(

        unique_deliveries.values()
    )

    # =====================================
    # VALIDATE ROWS
    # =====================================

    cleaned_deliveries = []

    for d in deliveries:

        # REQUIRED FIELDS

        if not d.get("delivery_key"):

            continue

        if not d.get("match_id"):

            continue

        if d.get("innings") is None:

            continue

        if d.get("over_no") is None:

            continue

        if d.get("ball_no") is None:

            continue

        cleaned_deliveries.append(d)

    # =====================================
    # NO VALID DATA
    # =====================================

    if not cleaned_deliveries:

        return 0

    # =====================================
    # PREPARE VALUES
    # =====================================

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

        for d in cleaned_deliveries
    ]

    # =====================================
    # CONNECTION
    # =====================================

    conn = None

    cursor = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        # =================================
        # QUERY
        # =================================

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

        # =================================
        # BATCH INSERT
        # =================================

        execute_values(

            cursor,
            query,
            values,

            page_size=5000
        )

        conn.commit()

        print(

            f"Inserted "
            f"{len(values)} deliveries"
        )

        return len(values)

    except Exception as e:

        # =================================
        # ROLLBACK
        # =================================

        if conn:

            conn.rollback()

        print("\n=================================")

        print("DELIVERY INSERT ERROR")

        print("=================================\n")

        print(e)

        print("\n=================================\n")

        raise e

    finally:

        # =================================
        # CLEANUP
        # =================================

        if cursor:

            cursor.close()

        if conn:

            conn.close()