from .database import get_connection


def insert_match(match_data, conn=None):

    own_connection = False

    if conn is None:

        conn = get_connection()

        own_connection = True

    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO matches (

            match_id,
            season,
            match_date,
            city,
            venue,
            team1,
            team2,
            toss_winner,
            toss_decision,
            winner,
            player_of_match,
            result_type,
            result_margin,
            target_runs,
            target_overs,
            super_over,
            match_stage,
            is_playoff,
            umpire1,
            umpire2

        )

        VALUES (

            %(match_id)s,
            %(season)s,
            %(match_date)s,
            %(city)s,
            %(venue)s,
            %(team1)s,
            %(team2)s,
            %(toss_winner)s,
            %(toss_decision)s,
            %(winner)s,
            %(player_of_match)s,
            %(result_type)s,
            %(result_margin)s,
            %(target_runs)s,
            %(target_overs)s,
            %(super_over)s,
            %(match_stage)s,
            %(is_playoff)s,
            %(umpire1)s,
            %(umpire2)s

        )

        ON CONFLICT (match_id)

        DO UPDATE SET

            match_stage = EXCLUDED.match_stage,
            is_playoff = EXCLUDED.is_playoff

    """, match_data)

    if own_connection:

        conn.commit()

        cursor.close()

        conn.close()