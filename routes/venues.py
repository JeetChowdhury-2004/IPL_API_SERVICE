from flask import Blueprint
from flask import request

from database.database import get_connection

from team_name_normalization import normalize_team_name

from utils.api_response import success_response, error_response


venues_bp = Blueprint(

    "venues",

    __name__
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


def team_payload(team):

    if team is None:

        return None

    return {

        "team": team,

        "normalized_team": normalize_team_name(team)
    }


@venues_bp.route("/venues/stats")
def venue_stats():

    venue_name = request.args.get(

        "venue_name",

        ""
    ).strip()

    if not venue_name:

        return error_response(

            "venue_name is required",

            400
        )

    venue_pattern = f"%{venue_name}%"

    overview_rows = execute_query(

        """

        SELECT
            COUNT(DISTINCT match_id) AS matches,
            MIN(season) AS first_season,
            MAX(season) AS last_season,
            ARRAY_AGG(DISTINCT city) FILTER (WHERE city IS NOT NULL) AS cities,
            ARRAY_AGG(DISTINCT venue) AS venues
        FROM matches
        WHERE venue ILIKE %s

        """,

        (venue_pattern,)
    )

    overview = overview_rows[0] if overview_rows else None

    if not overview or int(overview[0] or 0) == 0:

        return error_response(

            "Venue not found",

            404
        )

    first_innings_rows = execute_query(

        """

        WITH first_innings_totals AS (

            SELECT
                d.match_id,
                SUM(d.total_run) AS runs
            FROM deliveries d
            JOIN matches m
              ON d.match_id = m.match_id
            WHERE m.venue ILIKE %s
              AND d.innings = 1
            GROUP BY d.match_id
        )

        SELECT
            ROUND(AVG(runs), 2) AS average_first_innings_score
        FROM first_innings_totals

        """,

        (venue_pattern,)
    )

    result_rows = execute_query(

        """

        WITH innings_teams AS (

            SELECT
                d.match_id,
                MAX(CASE WHEN d.innings = 1 THEN d.batting_team END) AS defending_team,
                MAX(CASE WHEN d.innings = 2 THEN d.batting_team END) AS chasing_team
            FROM deliveries d
            JOIN matches m
              ON d.match_id = m.match_id
            WHERE m.venue ILIKE %s
              AND d.innings IN (1, 2)
            GROUP BY d.match_id
        )

        SELECT
            COUNT(*) FILTER (
                WHERE m.winner IS NOT NULL
                  AND m.winner = i.chasing_team
            ) AS chasing_wins,
            COUNT(*) FILTER (
                WHERE m.winner IS NOT NULL
                  AND m.winner = i.defending_team
            ) AS defending_wins,
            COUNT(*) FILTER (
                WHERE m.winner IS NULL
            ) AS no_results
        FROM innings_teams i
        JOIN matches m
          ON i.match_id = m.match_id

        """,

        (venue_pattern,)
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
        WHERE m.venue ILIKE %s
          AND d.innings IN (1, 2)
        GROUP BY
            d.match_id,
            d.innings,
            d.batting_team,
            d.bowling_team
        ORDER BY runs DESC, d.match_id ASC
        LIMIT 1

        """,

        (venue_pattern,)
    )

    top_team_rows = execute_query(

        """

        WITH team_rows AS (

            SELECT
                team1 AS team,
                match_id
            FROM matches
            WHERE venue ILIKE %s
              AND team1 IS NOT NULL

            UNION ALL

            SELECT
                team2 AS team,
                match_id
            FROM matches
            WHERE venue ILIKE %s
              AND team2 IS NOT NULL
        )

        SELECT
            team,
            COUNT(DISTINCT match_id) AS matches
        FROM team_rows
        GROUP BY team
        ORDER BY matches DESC, team ASC
        LIMIT 5

        """,

        (
            venue_pattern,
            venue_pattern
        )
    )

    average_first_innings_score = None

    if first_innings_rows and first_innings_rows[0][0] is not None:

        average_first_innings_score = float(first_innings_rows[0][0])

    result_row = result_rows[0] if result_rows else (0, 0, 0)

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

    top_teams_by_matches = []

    for row in top_team_rows:

        top_teams_by_matches.append({

            "team": team_payload(row[0]),

            "matches": int(row[1])
        })

    return success_response({

        "venue_name": venue_name,

        "matched_venues": sorted(overview[4] or []),

        "matches": int(overview[0]),

        "seasons": {

            "first": int(overview[1]),

            "last": int(overview[2])
        },

        "cities": sorted(overview[3] or []),

        "average_first_innings_score": average_first_innings_score,

        "chasing_wins": int(result_row[0] or 0),

        "defending_wins": int(result_row[1] or 0),

        "no_results": int(result_row[2] or 0),

        "highest_team_total": highest_team_total,

        "top_teams_by_matches": top_teams_by_matches
    })
