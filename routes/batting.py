from flask import Blueprint
from flask import request

from database.database import get_connection


# =========================================
# INVALID DISMISSALS
# =========================================

INVALID_DISMISSALS = (

    'retired hurt'
)


# =========================================
# BLUEPRINT
# =========================================

batting_bp = Blueprint(

    "batting",

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
# MOST RUNS
# =========================================

@batting_bp.route("/batting/most-runs")
def most_runs():

    player = request.args.get("player")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT
            d.batter,

            SUM(d.batsman_run) AS total_runs

        FROM deliveries d

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE 1=1

    """

    values = []

    if player:

        query += """

            AND d.batter = %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

        GROUP BY d.batter

        ORDER BY total_runs DESC

    """

    if not player:

        query += """

            LIMIT 10

        """

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return {

            "message": "Player not found"
        }, 404

    if player:

        row = rows[0]

        response = {

            "player": row[0],

            "runs": row[1]
        }

        if season:

            response["season"] = season

        return response

    players = []

    for row in rows:

        players.append({

            "player": row[0],

            "runs": row[1]
        })

    return {

        "count": len(players),

        "players": players
    }


# =========================================
# HIGHEST INDIVIDUAL SCORES
# =========================================

@batting_bp.route("/batting/highest-score")
def highest_score():

    player = request.args.get("player")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT
            d.batter,

            d.match_id,

            m.season,

            SUM(d.batsman_run) AS runs

        FROM deliveries d

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE 1=1

    """

    values = []

    if player:

        query += """

            AND d.batter = %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

        GROUP BY
            d.batter,
            d.match_id,
            m.season

        ORDER BY runs DESC

    """

    if not player:

        query += """

            LIMIT 10

        """

    else:

        query += """

            LIMIT 1

        """

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return {

            "message": "Player not found"
        }, 404

    if player:

        row = rows[0]

        return {

            "player": row[0],

            "match_id": row[1],

            "season": row[2],

            "highest_score": row[3]
        }

    innings_list = []

    for row in rows:

        innings_list.append({

            "player": row[0],

            "match_id": row[1],

            "season": row[2],

            "runs": row[3]
        })

    return {

        "count": len(innings_list),

        "highest_scores": innings_list
    }


# =========================================
# STRIKE RATE
# =========================================

@batting_bp.route("/batting/strike-rate")
def strike_rate():

    player = request.args.get("player")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT
            d.batter,

            SUM(d.batsman_run) AS runs,

            COUNT(*) AS balls,

            ROUND(

                (
                    SUM(d.batsman_run) * 100.0
                ) / NULLIF(
                    COUNT(*),
                    0
                ),

                2

            ) AS strike_rate

        FROM deliveries d

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE 1=1

    """

    values = []

    if player:

        query += """

            AND d.batter = %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

        GROUP BY d.batter

    """

    if not player and not season:

        query += """

            HAVING COUNT(*) >= 500

        """

    elif season:

        query += """

            HAVING COUNT(*) >= 100

        """

    query += """

        ORDER BY strike_rate DESC

    """

    if not player:

        query += """

            LIMIT 10

        """

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return {

            "message": "Player not found"
        }, 404

    if player:

        row = rows[0]

        response = {

            "player": row[0],

            "runs": row[1],

            "balls": row[2],

            "strike_rate": float(row[3])
        }

        if season:

            response["season"] = season

        return response

    players = []

    for row in rows:

        players.append({

            "player": row[0],

            "runs": row[1],

            "balls": row[2],

            "strike_rate": float(row[3])
        })

    return {

        "count": len(players),

        "players": players
    }


# =========================================
# BATTING AVERAGE
# =========================================

@batting_bp.route("/batting/batting-average")
def batting_average():

    player = request.args.get("player")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT
            d.batter,

            SUM(d.batsman_run) AS runs,

            COUNT(w.player_out) AS dismissals,

            ROUND(

                (
                    SUM(d.batsman_run) * 1.0
                ) / NULLIF(
                    COUNT(w.player_out),
                    0
                ),

                2

            ) AS batting_average

        FROM deliveries d

        LEFT JOIN wickets w

        ON d.delivery_key = w.delivery_key

        AND d.batter = w.player_out

        AND w.dismissal_kind NOT IN %s

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE 1=1

    """

    values = [INVALID_DISMISSALS]

    if player:

        query += """

            AND d.batter = %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

        GROUP BY d.batter

    """

    if not player and not season:

        query += """

            HAVING COUNT(*) >= 500

        """

    elif season:

        query += """

            HAVING COUNT(*) >= 100

        """

    query += """

        ORDER BY batting_average DESC

    """

    if not player:

        query += """

            LIMIT 10

        """

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return {

            "message": "Player not found"
        }, 404

    if player:

        row = rows[0]

        response = {

            "player": row[0],

            "runs": row[1],

            "dismissals": row[2],

            "batting_average": (

                float(row[3])

                if row[3] is not None

                else None
            )
        }

        if season:

            response["season"] = season

        return response

    players = []

    for row in rows:

        players.append({

            "player": row[0],

            "runs": row[1],

            "dismissals": row[2],

            "batting_average": (

                float(row[3])

                if row[3] is not None

                else None
            )
        })

    return {

        "count": len(players),

        "players": players
    }


# =========================================
# MOST SIXES
# =========================================

@batting_bp.route("/batting/most-sixes")
def most_sixes():

    player = request.args.get("player")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT
            d.batter,

            COUNT(*) AS sixes

        FROM deliveries d

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE d.batsman_run = 6

    """

    values = []

    if player:

        query += """

            AND d.batter = %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

        GROUP BY d.batter

        ORDER BY sixes DESC

    """

    if not player:

        query += """

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

    players = []

    for row in rows:

        players.append({

            "player": row[0],

            "sixes": row[1]
        })

    return {

        "count": len(players),

        "players": players
    }


# =========================================
# MOST FOURS
# =========================================

@batting_bp.route("/batting/most-fours")
def most_fours():

    player = request.args.get("player")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT
            d.batter,

            COUNT(*) AS fours

        FROM deliveries d

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE d.batsman_run = 4

    """

    values = []

    if player:

        query += """

            AND d.batter = %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

        GROUP BY d.batter

        ORDER BY fours DESC

    """

    if not player:

        query += """

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

    players = []

    for row in rows:

        players.append({

            "player": row[0],

            "fours": row[1]
        })

    return {

        "count": len(players),

        "players": players
    }


# =========================================
# MOST FIFTIES
# =========================================

@batting_bp.route("/batting/50s")
def fifties():

    player = request.args.get("player")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT
            batter,

            COUNT(*) AS fifties

        FROM (

            SELECT
                d.batter,
                d.match_id,

                SUM(d.batsman_run) AS runs

            FROM deliveries d

            JOIN matches m

            ON d.match_id = m.match_id

            WHERE 1=1

    """

    values = []

    if player:

        query += """

            AND d.batter = %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

            GROUP BY
                d.batter,
                d.match_id

            HAVING
                SUM(d.batsman_run) >= 50
                AND SUM(d.batsman_run) < 100

        ) AS innings_scores

        GROUP BY batter

        ORDER BY fifties DESC

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

    players = []

    for row in rows:

        players.append({

            "player": row[0],

            "fifties": row[1]
        })

    return {

        "count": len(players),

        "players": players
    }


# =========================================
# MOST HUNDREDS
# =========================================

@batting_bp.route("/batting/100s")
def hundreds():

    player = request.args.get("player")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT
            batter,

            COUNT(*) AS hundreds

        FROM (

            SELECT
                d.batter,
                d.match_id,

                SUM(d.batsman_run) AS runs

            FROM deliveries d

            JOIN matches m

            ON d.match_id = m.match_id

            WHERE 1=1

    """

    values = []

    if player:

        query += """

            AND d.batter = %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

            GROUP BY
                d.batter,
                d.match_id

            HAVING
                SUM(d.batsman_run) >= 100

        ) AS innings_scores

        GROUP BY batter

        ORDER BY hundreds DESC

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

    players = []

    for row in rows:

        players.append({

            "player": row[0],

            "hundreds": row[1]
        })

    return {

        "count": len(players),

        "players": players
    }


# =========================================
# ORANGE CAP
# =========================================

@batting_bp.route("/batting/orange-cap")
def orange_cap():

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT
            d.batter,

            SUM(d.batsman_run) AS runs

        FROM deliveries d

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE 1=1

    """

    values = []

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    query += """

        GROUP BY d.batter

        ORDER BY runs DESC

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

        "runs": row[1]
    }

    if season:

        response["season"] = season

    return response


# =========================================
# ORANGE CAP BY SEASON
# =========================================

@batting_bp.route("/batting/orange-cap-by-season")
def orange_cap_by_season():

    query = """

        WITH season_runs AS (

            SELECT
                m.season,

                d.batter,

                SUM(d.batsman_run) AS runs

            FROM deliveries d

            JOIN matches m

            ON d.match_id = m.match_id

            GROUP BY
                m.season,
                d.batter

        ),

        ranked_players AS (

            SELECT
                season,
                batter,
                runs,

                RANK() OVER (

                    PARTITION BY season

                    ORDER BY runs DESC

                ) AS rank

            FROM season_runs

        )

        SELECT
            season,
            batter,
            runs

        FROM ranked_players

        WHERE rank = 1

        ORDER BY season ASC

    """

    rows = execute_query(query)

    results = []

    for row in rows:

        results.append({

            "season": row[0],

            "player": row[1],

            "runs": row[2]
        })

    return {

        "count": len(results),

        "orange_caps": results
    }