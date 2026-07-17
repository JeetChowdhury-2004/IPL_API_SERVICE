from flask import Blueprint
from flask import request

from database.database import get_connection

from team_name_normalization import (
    normalize_team_name
)

from utils.api_response import (
    success_response,
    error_response
)

# =========================================
# INVALID DISMISSALS
# =========================================

INVALID_DISMISSALS = (

    'run out',
    'retired hurt',
    'retired out',
    'obstructing the field'
)

# =========================================
# BLUEPRINT
# =========================================

matchups_bp = Blueprint(

    "matchups",

    __name__
)

# =========================================
# DATABASE HELPER
# =========================================

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

# =========================================
# BATTER VS BOWLER
# =========================================

@matchups_bp.route("/matchups/batter-vs-bowler")
def batter_vs_bowler():

    batter = request.args.get("batter")

    bowler = request.args.get("bowler")

    season = request.args.get(

        "season",

        type=int
    )

    if not batter or not bowler:

        return error_response(

            "batter and bowler are required",

            400
        )

    query = """

        SELECT

            d.batter,

            d.bowler,

            COUNT(

                CASE

                    WHEN d.extra_type IS NULL
                        OR (
                            d.extra_type NOT LIKE '%%wides%%'
                            AND d.extra_type NOT LIKE '%%noballs%%'
                        )
                    THEN 1

                END

            ) AS balls,

            SUM(d.batsman_run) AS runs,

            COUNT(w.player_out) AS dismissals,

            ROUND(

                (
                    SUM(d.batsman_run) * 100.0
                )

                /

                NULLIF(
                    COUNT(

                        CASE

                            WHEN d.extra_type IS NULL
                                OR (
                                    d.extra_type NOT LIKE '%%wides%%'
                                    AND d.extra_type NOT LIKE '%%noballs%%'
                                )
                            THEN 1

                        END

                    ),
                    0
                ),

                2

            ) AS strike_rate,

            SUM(

                CASE

                    WHEN d.batsman_run = 4
                    THEN 1

                    ELSE 0

                END

            ) AS fours,

            SUM(

                CASE

                    WHEN d.batsman_run = 6
                    THEN 1

                    ELSE 0

                END

            ) AS sixes

        FROM deliveries d

        LEFT JOIN wickets w

        ON d.delivery_key = w.delivery_key

        AND w.dismissal_kind NOT IN %s

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE

            d.batter ILIKE %s

            AND d.bowler ILIKE %s

    """

    values = [

        INVALID_DISMISSALS,

        batter,

        bowler
    ]

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

        GROUP BY

            d.batter,
            d.bowler

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return error_response(

            "No matchup data found",

            404
        )

    row = rows[0]

    response = {

        "batter": row[0],

        "bowler": row[1],

        "balls": int(row[2]),

        "runs": int(row[3]),

        "dismissals": int(row[4]),

        "strike_rate": float(row[5]),

        "fours": int(row[6]),

        "sixes": int(row[7])
    }

    if season:

        response["season"] = season

    return success_response(response)

# =========================================
# BATTER VS TEAM
# =========================================

@matchups_bp.route("/matchups/batter-vs-team")
def batter_vs_team():

    batter = request.args.get("batter")

    team = request.args.get("team")

    if team:

        team = normalize_team_name(team)

    season = request.args.get(

        "season",

        type=int
    )

    if not batter or not team:

        return error_response(

            "batter and team are required",

            400
        )

    query = """

        SELECT

            d.batter,

            d.bowling_team,

            COUNT(

                CASE

                    WHEN d.extra_type IS NULL
                        OR (
                            d.extra_type NOT LIKE '%%wides%%'
                            AND d.extra_type NOT LIKE '%%noballs%%'
                        )
                    THEN 1

                END

            ) AS balls,

            SUM(d.batsman_run) AS runs,

            COUNT(w.player_out) AS dismissals,

            ROUND(

                (
                    SUM(d.batsman_run) * 100.0
                )

                /

                NULLIF(
                    COUNT(

                        CASE

                            WHEN d.extra_type IS NULL
                                OR (
                                    d.extra_type NOT LIKE '%%wides%%'
                                    AND d.extra_type NOT LIKE '%%noballs%%'
                                )
                            THEN 1

                        END

                    ),
                    0
                ),

                2

            ) AS strike_rate,

            ROUND(

                (
                    SUM(d.batsman_run) * 1.0
                )

                /

                NULLIF(
                    COUNT(w.player_out),
                    0
                ),

                2

            ) AS batting_average,

            SUM(

                CASE

                    WHEN d.batsman_run = 4
                    THEN 1

                    ELSE 0

                END

            ) AS fours,

            SUM(

                CASE

                    WHEN d.batsman_run = 6
                    THEN 1

                    ELSE 0

                END

            ) AS sixes

        FROM deliveries d

        LEFT JOIN wickets w

        ON d.delivery_key = w.delivery_key

        AND w.dismissal_kind NOT IN %s

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE

            d.batter ILIKE %s

            AND d.bowling_team = %s

    """

    values = [

        INVALID_DISMISSALS,

        batter,

        team
    ]

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

        GROUP BY

            d.batter,
            d.bowling_team

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return error_response(

            "No matchup data found",

            404
        )

    row = rows[0]

    response = {

        "batter": row[0],

        "against_team": row[1],

        "balls": int(row[2]),

        "runs": int(row[3]),

        "dismissals": int(row[4]),

        "strike_rate": float(row[5]),

        "batting_average": (

            float(row[6])

            if row[6] is not None

            else None
        ),

        "fours": int(row[7]),

        "sixes": int(row[8])
    }

    if season:

        response["season"] = season

    return success_response(response)

# =========================================
# BOWLER VS TEAM
# =========================================

@matchups_bp.route("/matchups/bowler-vs-team")
def bowler_vs_team():

    bowler = request.args.get("bowler")

    team = request.args.get("team")

    if team:

        team = normalize_team_name(team)

    season = request.args.get(

        "season",

        type=int
    )

    if not bowler or not team:

        return error_response(

            "bowler and team are required",

            400
        )

    query = """

        SELECT

            d.bowler,

            d.batting_team,

            COUNT(

                CASE

                    WHEN d.extra_type IS NULL
                        OR (
                            d.extra_type NOT LIKE '%%wides%%'
                            AND d.extra_type NOT LIKE '%%noballs%%'
                        )
                    THEN 1

                END

            ) AS balls,

            SUM(

                CASE

                    WHEN d.extra_type LIKE '%%byes%%'
                        OR d.extra_type LIKE '%%legbyes%%'
                        OR d.extra_type LIKE '%%penalty%%'
                    THEN d.batsman_run

                    ELSE d.total_run

                END

            ) AS runs_conceded,

            COUNT(w.player_out) AS wickets,

            ROUND(

                (
                    SUM(

                        CASE

                            WHEN d.extra_type LIKE '%%byes%%'
                                OR d.extra_type LIKE '%%legbyes%%'
                                OR d.extra_type LIKE '%%penalty%%'
                            THEN d.batsman_run

                            ELSE d.total_run

                        END

                    ) * 6.0
                )

                /

                NULLIF(
                    COUNT(

                        CASE

                            WHEN d.extra_type IS NULL
                                OR (
                                    d.extra_type NOT LIKE '%%wides%%'
                                    AND d.extra_type NOT LIKE '%%noballs%%'
                                )
                            THEN 1

                        END

                    ),
                    0
                ),

                2

            ) AS economy,

            ROUND(

                COUNT(

                    CASE

                        WHEN d.extra_type IS NULL
                            OR (
                                d.extra_type NOT LIKE '%%wides%%'
                                AND d.extra_type NOT LIKE '%%noballs%%'
                            )
                        THEN 1

                    END

                ) * 1.0

                /

                NULLIF(
                    COUNT(w.player_out),
                    0
                ),

                2

            ) AS strike_rate,

            ROUND(

                (
                    SUM(

                        CASE

                            WHEN d.extra_type LIKE '%%byes%%'
                                OR d.extra_type LIKE '%%legbyes%%'
                                OR d.extra_type LIKE '%%penalty%%'
                            THEN d.batsman_run

                            ELSE d.total_run

                        END

                    ) * 1.0
                )

                /

                NULLIF(
                    COUNT(w.player_out),
                    0
                ),

                2

            ) AS bowling_average

        FROM deliveries d

        LEFT JOIN wickets w

        ON d.delivery_key = w.delivery_key

        AND w.dismissal_kind NOT IN %s

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE

            d.bowler ILIKE %s

            AND d.batting_team = %s

    """

    values = [

        INVALID_DISMISSALS,

        bowler,

        team
    ]

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

        GROUP BY

            d.bowler,
            d.batting_team

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return error_response(

            "No matchup data found",

            404
        )

    row = rows[0]

    response = {

        "bowler": row[0],

        "against_team": row[1],

        "balls": int(row[2]),

        "runs_conceded": int(row[3]),

        "wickets": int(row[4]),

        "economy": float(row[5]),

        "strike_rate": (

            float(row[6])

            if row[6] is not None

            else None
        ),

        "bowling_average": (

            float(row[7])

            if row[7] is not None

            else None
        )
    }

    if season:

        response["season"] = season

    return success_response(response)
