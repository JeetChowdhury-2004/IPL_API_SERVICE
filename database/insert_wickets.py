from psycopg2.extras import execute_values

from .database import get_connection

# =========================================
# INSERT WICKETS
# =========================================

def insert_wickets(wickets):

    """
    Batch insert wickets into PostgreSQL.
    """

    # =====================================
    # EMPTY CHECK
    # =====================================

    if not wickets:

        return 0

    # =====================================
    # REMOVE DUPLICATES
    # =====================================

    unique_wickets = {}

    for w in wickets:

        delivery_key = w.get("delivery_key")

        player_out = w.get("player_out")

        dismissal_kind = w.get(
            "dismissal_kind"
        )

        unique_key = (

            f"{delivery_key}_"
            f"{player_out}_"
            f"{dismissal_kind}"
        )

        unique_wickets[unique_key] = w

    wickets = list(

        unique_wickets.values()
    )

    # =====================================
    # VALIDATE ROWS
    # =====================================

    cleaned_wickets = []

    for w in wickets:

        if not w.get("delivery_key"):

            continue

        if not w.get("player_out"):

            continue

        cleaned_wickets.append(w)

    # =====================================
    # NO VALID DATA
    # =====================================

    if not cleaned_wickets:

        return 0

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

        for w in cleaned_wickets
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
        # INSERT QUERY
        # =================================

        query = """

            INSERT INTO wickets (

                delivery_key,
                player_out,
                dismissal_kind,
                fielders_involved

            )

            VALUES %s

            ON CONFLICT (

                delivery_key,
                player_out,
                dismissal_kind

            )

            DO NOTHING

        """

        # =================================
        # INSERT
        # =================================

        execute_values(

            cursor,
            query,
            values,

            page_size=2000
        )

        conn.commit()

        print(

            f"Inserted "
            f"{len(values)} wickets"
        )

        return len(values)

    except Exception as e:

        # =================================
        # ROLLBACK
        # =====================================

        if conn:

            conn.rollback()

        print("\n=================================")

        print("WICKET INSERT ERROR")

        print("=================================\n")

        print(e)

        print("\n=================================\n")

        raise e

    finally:

        # =================================
        # CLEANUP
        # =====================================

        if cursor:

            cursor.close()

        if conn:

            conn.close()