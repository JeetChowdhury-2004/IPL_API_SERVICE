from flask import Blueprint
from flask import request

from database.database import get_connection


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

    cursor.execute(

        query,

        values if values else ()
    )

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    return rows


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

            AND d.bowler = %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

        GROUP BY d.bowler

        ORDER BY wickets DESC

        LIMIT 10

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return {

            "message": "No data found"
        }

    bowlers = []

    for row in rows:

        bowlers.append({

            "player": row[0],

            "wickets": row[1]
        })

    return {

        "count": len(bowlers),

        "players": bowlers
    }


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

            SUM(d.total_run) AS runs_conceded,

            COUNT(*) AS balls_bowled,

            ROUND(

                (
                    SUM(d.total_run) * 6.0
                ) / NULLIF(
                    COUNT(*),
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

            AND d.bowler = %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

        GROUP BY d.bowler

    """

    if not player and not season:

        query += """

            HAVING COUNT(*) >= 300

        """

    elif season:

        query += """

            HAVING COUNT(*) >= 60

        """

    query += """

        ORDER BY economy ASC

        LIMIT 10

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return {

            "message": "No data found"
        }

    bowlers = []

    for row in rows:

        bowlers.append({

            "player": row[0],

            "runs_conceded": row[1],

            "balls_bowled": row[2],

            "economy": float(row[3])
        })

    return {

        "count": len(bowlers),

        "players": bowlers
    }


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

            COUNT(*) AS balls_bowled,

            COUNT(w.player_out) AS wickets,

            ROUND(

                COUNT(*) * 1.0

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

            AND d.bowler = %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

        GROUP BY d.bowler

    """

    if not player and not season:

        query += """

            HAVING
                COUNT(*) >= 300
                AND COUNT(w.player_out) > 0

        """

    elif season:

        query += """

            HAVING
                COUNT(*) >= 60
                AND COUNT(w.player_out) > 0

        """

    query += """

        ORDER BY strike_rate ASC

        LIMIT 10

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return {

            "message": "No data found"
        }

    bowlers = []

    for row in rows:

        bowlers.append({

            "player": row[0],

            "balls_bowled": row[1],

            "wickets": row[2],

            "strike_rate": float(row[3])
        })

    return {

        "count": len(bowlers),

        "players": bowlers
    }


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

            SUM(d.total_run) AS runs_conceded,

            COUNT(w.player_out) AS wickets,

            ROUND(

                SUM(d.total_run) * 1.0

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

            AND d.bowler = %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

        GROUP BY d.bowler

    """

    if not player and not season:

        query += """

            HAVING
                COUNT(*) >= 300
                AND COUNT(w.player_out) > 0

        """

    elif season:

        query += """

            HAVING
                COUNT(*) >= 60
                AND COUNT(w.player_out) > 0

        """

    query += """

        ORDER BY bowling_average ASC

        LIMIT 10

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return {

            "message": "No data found"
        }

    bowlers = []

    for row in rows:

        bowlers.append({

            "player": row[0],

            "runs_conceded": row[1],

            "wickets": row[2],

            "bowling_average": float(row[3])
        })

    return {

        "count": len(bowlers),

        "players": bowlers
    }


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

            SUM(d.total_run) AS runs_conceded,

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

            AND d.bowler = %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

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

        LIMIT 10

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return {

            "message": "No data found"
        }

    figures = []

    for row in rows:

        figures.append({

            "player": row[0],

            "match_id": row[1],

            "season": row[2],

            "runs_conceded": row[3],

            "wickets": row[4],

            "figure": f"{row[4]}/{row[3]}"
        })

    return {

        "count": len(figures),

        "best_figures": figures
    }


# =========================================
# PURPLE CAP
# =========================================

@bowling_bp.route("/bowling/purple-cap")
def purple_cap():

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT
            d.bowler,

            COUNT(w.player_out) AS wickets

        FROM deliveries d

        JOIN wickets w

        ON d.delivery_key = w.delivery_key

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE w.dismissal_kind NOT IN %s

    """

    values = [INVALID_DISMISSALS]

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

        GROUP BY d.bowler

        ORDER BY wickets DESC

        LIMIT 1

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return {

            "message": "No data found"
        }

    row = rows[0]

    response = {

        "player": row[0],

        "wickets": row[1]
    }

    if season:

        response["season"] = season

    return response


# =========================================
# PURPLE CAP BY SEASON
# =========================================

@bowling_bp.route("/bowling/purple-cap-by-season")
def purple_cap_by_season():

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

        ORDER BY season ASC

    """

    rows = execute_query(query)

    if not rows:

        return {

            "message": "No data found"
        }

    results = []

    for row in rows:

        results.append({

            "season": row[0],

            "player": row[1],

            "wickets": row[2]
        })

    return {

        "count": len(results),

        "purple_caps": results
    }