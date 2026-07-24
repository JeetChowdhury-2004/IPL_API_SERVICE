from flask import Blueprint

from database.database import get_connection

from team_name_normalization import normalize_team_name

from utils.api_response import success_response, error_response


seasons_bp = Blueprint(

    "seasons",

    __name__
)


INVALID_DISMISSALS = (

    "run out",
    "retired hurt",
    "retired out",
    "obstructing the field",
    "hit the ball twice",
    "handled the ball",
    "timed out"
)


def execute_query(query, values=None):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute(

            query,

            values if values else ()
        )

        rows = cursor.fetchall()

        return rows

    finally:

        cursor.close()

        conn.close()


def serialize_date(value):

    if value is None:

        return None

    return value.isoformat() if hasattr(value, "isoformat") else str(value)


def team_payload(team):

    if team is None:

        return None

    return {

        "team": team,

        "normalized_team": normalize_team_name(team)
    }


@seasons_bp.route("/seasons/<int:season>/summary")
def season_summary(season):

    overview_rows = execute_query(

        """

        WITH season_teams AS (

            SELECT team1 AS team
            FROM matches
            WHERE season = %s
              AND team1 IS NOT NULL

            UNION

            SELECT team2 AS team
            FROM matches
            WHERE season = %s
              AND team2 IS NOT NULL
        )

        SELECT
            COUNT(DISTINCT m.match_id) AS matches,
            COUNT(DISTINCT st.team) AS teams,
            MIN(m.match_date) AS start_date,
            MAX(m.match_date) AS end_date,
            COUNT(DISTINCT m.city) AS cities,
            COUNT(DISTINCT m.venue) AS venues
        FROM matches m
        CROSS JOIN season_teams st
        WHERE m.season = %s

        """,

        (
            season,
            season,
            season
        )
    )

    overview = overview_rows[0] if overview_rows else None

    if not overview or int(overview[0] or 0) == 0:

        return error_response(

            "Season not found",

            404
        )

    final_rows = execute_query(

        """

        SELECT
            match_id,
            match_date,
            city,
            venue,
            team1,
            team2,
            winner,
            player_of_match
        FROM matches
        WHERE season = %s
          AND LOWER(match_stage) = 'final'
        ORDER BY match_date DESC, match_id DESC
        LIMIT 1

        """,

        (season,)
    )

    top_batter_rows = execute_query(

        """

        SELECT
            d.batter,
            SUM(d.batsman_run) AS runs
        FROM deliveries d
        JOIN matches m
          ON d.match_id = m.match_id
        WHERE m.season = %s
          AND d.batter IS NOT NULL
        GROUP BY d.batter
        ORDER BY runs DESC, d.batter ASC
        LIMIT 1

        """,

        (season,)
    )

    top_bowler_rows = execute_query(

        """

        SELECT
            d.bowler,
            COUNT(w.player_out) AS wickets
        FROM wickets w
        JOIN deliveries d
          ON w.delivery_key = d.delivery_key
        JOIN matches m
          ON d.match_id = m.match_id
        WHERE m.season = %s
          AND d.bowler IS NOT NULL
          AND w.dismissal_kind NOT IN %s
        GROUP BY d.bowler
        ORDER BY wickets DESC, d.bowler ASC
        LIMIT 1

        """,

        (
            season,
            INVALID_DISMISSALS
        )
    )

    highest_total_rows = execute_query(

        """

        SELECT
            d.match_id,
            d.innings,
            d.batting_team,
            d.bowling_team,
            SUM(d.total_run) AS runs
        FROM deliveries d
        JOIN matches m
          ON d.match_id = m.match_id
        WHERE m.season = %s
          AND d.innings IN (1, 2)
        GROUP BY
            d.match_id,
            d.innings,
            d.batting_team,
            d.bowling_team
        ORDER BY runs DESC, d.match_id ASC
        LIMIT 1

        """,

        (season,)
    )

    final = None

    champion = None

    runner_up = None

    if final_rows:

        final_row = final_rows[0]

        champion = final_row[6]

        if final_row[4] == champion:

            runner_up = final_row[5]

        elif final_row[5] == champion:

            runner_up = final_row[4]

        final = {

            "match_id": int(final_row[0]),

            "date": serialize_date(final_row[1]),

            "city": final_row[2],

            "venue": final_row[3],

            "team1": team_payload(final_row[4]),

            "team2": team_payload(final_row[5]),

            "winner": team_payload(champion),

            "runner_up": team_payload(runner_up),

            "player_of_match": final_row[7]
        }

    top_batter = None

    if top_batter_rows:

        top_batter = {

            "player": top_batter_rows[0][0],

            "runs": int(top_batter_rows[0][1])
        }

    top_bowler = None

    if top_bowler_rows:

        top_bowler = {

            "player": top_bowler_rows[0][0],

            "wickets": int(top_bowler_rows[0][1])
        }

    highest_team_total = None

    if highest_total_rows:

        highest_total = highest_total_rows[0]

        highest_team_total = {

            "match_id": int(highest_total[0]),

            "innings": int(highest_total[1]),

            "team": team_payload(highest_total[2]),

            "opponent": team_payload(highest_total[3]),

            "runs": int(highest_total[4])
        }

    return success_response({

        "season": season,

        "matches": int(overview[0]),

        "teams": int(overview[1]),

        "date_range": {

            "start": serialize_date(overview[2]),

            "end": serialize_date(overview[3])
        },

        "cities": int(overview[4]),

        "venues": int(overview[5]),

        "champion": team_payload(champion),

        "runner_up": team_payload(runner_up),

        "final": final,

        "top_batter": top_batter,

        "top_bowler": top_bowler,

        "highest_team_total": highest_team_total
    })
