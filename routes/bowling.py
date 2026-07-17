from flask import Blueprint
from flask import request

from database.database import get_connection

from utils.api_response import (
    success_response,
    error_response
)

from utils.pagination import get_pagination

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

bowling_bp = Blueprint(

    "bowling",

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
# MOST WICKETS
# =========================================

@bowling_bp.route("/bowling/most-wickets")
def most_wickets():

    player = request.args.get("player")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT
            d.bowler,

            COUNT(w.player_out) AS wickets

        FROM wickets w

        JOIN deliveries d

        ON w.delivery_key = d.delivery_key

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE w.dismissal_kind NOT IN %s

    """

    values = [INVALID_DISMISSALS]

    if player:

        query += """

            AND d.bowler ILIKE %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    limit, offset = get_pagination()

    query += """

        GROUP BY d.bowler

        ORDER BY wickets DESC

        LIMIT %s
        OFFSET %s

    """

    values.extend([limit, offset])

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return error_response(

            "No data found",

            404
        )

    bowlers = []

    for row in rows:

        bowlers.append({

            "player": row[0],

            "wickets": int(row[1])
        })

    return success_response({

        "count": len(bowlers),

        "players": bowlers
    })

# =========================================
# BOWLING ECONOMY
# =========================================

@bowling_bp.route("/bowling/economy")
def economy():

    player = request.args.get("player")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT
            d.bowler,

            SUM(

                CASE

                    WHEN d.extra_type LIKE '%%byes%%'
                        OR d.extra_type LIKE '%%legbyes%%'
                        OR d.extra_type LIKE '%%penalty%%'
                    THEN d.batsman_run

                    ELSE d.total_run

                END

            ) AS runs_conceded,

            COUNT(

                CASE

                    WHEN d.extra_type IS NULL
                        OR (
                            d.extra_type NOT LIKE '%%wides%%'
                            AND d.extra_type NOT LIKE '%%noballs%%'
                        )
                    THEN 1

                END

            ) AS balls_bowled,

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
                ) / NULLIF(
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

            ) AS economy

        FROM deliveries d

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE 1=1

    """

    values = []

    if player:

        query += """

            AND d.bowler ILIKE %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    limit, offset = get_pagination()

    query += """

        GROUP BY d.bowler

    """

    if not player and not season:

        query += """

            HAVING
                COUNT(
                    CASE
                        WHEN d.extra_type IS NULL
                            OR (
                                d.extra_type NOT LIKE '%%wides%%'
                                AND d.extra_type NOT LIKE '%%noballs%%'
                            )
                        THEN 1
                    END
                ) >= 300

        """

    elif season:

        query += """

            HAVING
                COUNT(
                    CASE
                        WHEN d.extra_type IS NULL
                            OR (
                                d.extra_type NOT LIKE '%%wides%%'
                                AND d.extra_type NOT LIKE '%%noballs%%'
                            )
                        THEN 1
                    END
                ) >= 60

        """

    query += """

        ORDER BY economy ASC

        LIMIT %s
        OFFSET %s

    """

    values.extend([limit, offset])

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return error_response(

            "No data found",

            404
        )

    bowlers = []

    for row in rows:

        bowlers.append({

            "player": row[0],

            "runs_conceded": int(row[1]),

            "balls_bowled": int(row[2]),

            "economy": float(row[3])
        })

    return success_response({

        "count": len(bowlers),

        "players": bowlers
    })

# =========================================
# BOWLING STRIKE RATE
# =========================================

@bowling_bp.route("/bowling/strike-rate")
def bowling_strike_rate():

    player = request.args.get("player")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT
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

            ) AS balls_bowled,

            COUNT(w.player_out) AS wickets,

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

            ) AS strike_rate

        FROM deliveries d

        LEFT JOIN wickets w

        ON d.delivery_key = w.delivery_key

        AND w.dismissal_kind NOT IN %s

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE 1=1

    """

    values = [INVALID_DISMISSALS]

    if player:

        query += """

            AND d.bowler ILIKE %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    limit, offset = get_pagination()

    query += """

        GROUP BY d.bowler

    """

    if not player and not season:

        query += """

            HAVING
                COUNT(
                    CASE
                        WHEN d.extra_type IS NULL
                            OR (
                                d.extra_type NOT LIKE '%%wides%%'
                                AND d.extra_type NOT LIKE '%%noballs%%'
                            )
                        THEN 1
                    END
                ) >= 300
                AND COUNT(w.player_out) > 0

        """

    elif season:

        query += """

            HAVING
                COUNT(
                    CASE
                        WHEN d.extra_type IS NULL
                            OR (
                                d.extra_type NOT LIKE '%%wides%%'
                                AND d.extra_type NOT LIKE '%%noballs%%'
                            )
                        THEN 1
                    END
                ) >= 60
                AND COUNT(w.player_out) > 0

        """

    query += """

        ORDER BY strike_rate ASC

        LIMIT %s
        OFFSET %s

    """

    values.extend([limit, offset])

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return error_response(

            "No data found",

            404
        )

    bowlers = []

    for row in rows:

        bowlers.append({

            "player": row[0],

            "balls_bowled": int(row[1]),

            "wickets": int(row[2]),

            "strike_rate": float(row[3])
        })

    return success_response({

        "count": len(bowlers),

        "players": bowlers
    })

# =========================================
# BOWLING AVERAGE
# =========================================

@bowling_bp.route("/bowling/average")
def bowling_average():

    player = request.args.get("player")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT
            d.bowler,

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

                SUM(

                    CASE

                        WHEN d.extra_type LIKE '%%byes%%'
                            OR d.extra_type LIKE '%%legbyes%%'
                            OR d.extra_type LIKE '%%penalty%%'
                        THEN d.batsman_run

                        ELSE d.total_run

                    END

                ) * 1.0

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

        WHERE 1=1

    """

    values = [INVALID_DISMISSALS]

    if player:

        query += """

            AND d.bowler ILIKE %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    limit, offset = get_pagination()

    query += """

        GROUP BY d.bowler

    """

    if not player and not season:

        query += """

            HAVING
                COUNT(
                    CASE
                        WHEN d.extra_type IS NULL
                            OR (
                                d.extra_type NOT LIKE '%%wides%%'
                                AND d.extra_type NOT LIKE '%%noballs%%'
                            )
                        THEN 1
                    END
                ) >= 300
                AND COUNT(w.player_out) > 0

        """

    elif season:

        query += """

            HAVING
                COUNT(
                    CASE
                        WHEN d.extra_type IS NULL
                            OR (
                                d.extra_type NOT LIKE '%%wides%%'
                                AND d.extra_type NOT LIKE '%%noballs%%'
                            )
                        THEN 1
                    END
                ) >= 60
                AND COUNT(w.player_out) > 0

        """

    query += """

        ORDER BY bowling_average ASC

        LIMIT %s
        OFFSET %s

    """

    values.extend([limit, offset])

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return error_response(

            "No data found",

            404
        )

    bowlers = []

    for row in rows:

        bowlers.append({

            "player": row[0],

            "runs_conceded": int(row[1]),

            "wickets": int(row[2]),

            "bowling_average": float(row[3])
        })

    return success_response({

        "count": len(bowlers),

        "players": bowlers
    })

# =========================================
# BEST BOWLING FIGURES
# =========================================

@bowling_bp.route("/bowling/best-figures")
def best_figures():

    player = request.args.get("player")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT
            d.bowler,

            d.match_id,

            m.season,

            SUM(

                CASE

                    WHEN d.extra_type LIKE '%%byes%%'
                        OR d.extra_type LIKE '%%legbyes%%'
                        OR d.extra_type LIKE '%%penalty%%'
                    THEN d.batsman_run

                    ELSE d.total_run

                END

            ) AS runs_conceded,

            COUNT(w.player_out) AS wickets

        FROM deliveries d

        LEFT JOIN wickets w

        ON d.delivery_key = w.delivery_key

        AND w.dismissal_kind NOT IN %s

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE 1=1

    """

    values = [INVALID_DISMISSALS]

    if player:

        query += """

            AND d.bowler ILIKE %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    limit, offset = get_pagination()

    query += """

        GROUP BY
            d.bowler,
            d.match_id,
            m.season

        HAVING COUNT(w.player_out) > 0

        ORDER BY
            wickets DESC,
            runs_conceded ASC,
            d.match_id ASC

        LIMIT %s
        OFFSET %s

    """

    values.extend([limit, offset])

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return error_response(

            "No data found",

            404
        )

    figures = []

    for row in rows:

        figures.append({

            "player": row[0],

            "match_id": row[1],

            "season": row[2],

            "runs_conceded": int(row[3]),

            "wickets": int(row[4]),

            "figure": f"{row[4]}/{row[3]}"
        })

    return success_response({

        "count": len(figures),

        "best_figures": figures
    })

# =========================================
# PURPLE CAP BY SEASON
# =========================================

@bowling_bp.route("/bowling/purple-cap-by-season")
def purple_cap_by_season():

    season_count_query = """

        SELECT COUNT(DISTINCT season)

        FROM matches

    """

    season_count_rows = execute_query(season_count_query)

    season_count = int(season_count_rows[0][0]) if season_count_rows else 10

    limit, offset = get_pagination(

        default_limit=season_count,

        max_limit=season_count
    )

    query = """

        WITH season_wickets AS (

            SELECT
                m.season,

                d.bowler,

                COUNT(

                    CASE

                        WHEN w.dismissal_kind NOT IN (

                            'run out',
                            'retired hurt',
                            'retired out',
                            'obstructing the field'

                        )

                        THEN w.player_out

                    END

                ) AS wickets

            FROM deliveries d

            JOIN wickets w

            ON d.delivery_key = w.delivery_key

            JOIN matches m

            ON d.match_id = m.match_id

            GROUP BY
                m.season,
                d.bowler
        ),

        ranked_bowlers AS (

            SELECT
                season,

                bowler,

                wickets,

                RANK() OVER (

                    PARTITION BY season

                    ORDER BY wickets DESC

                ) AS rank

            FROM season_wickets
        )

        SELECT
            season,

            bowler,

            wickets

        FROM ranked_bowlers

        WHERE rank = 1

        ORDER BY season DESC

        LIMIT %s
        OFFSET %s

    """

    rows = execute_query(query, (limit, offset))

    if not rows:

        return error_response(

            "No data found",

            404
        )

    results = []

    for row in rows:

        results.append({

            "season": row[0],

            "player": row[1],

            "wickets": int(row[2])
        })

    return success_response({

        "count": len(results),

        "purple_caps": results
    })
