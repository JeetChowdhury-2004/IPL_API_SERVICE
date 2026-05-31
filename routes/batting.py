from flask import Blueprint
from flask import request

from database.database import get_connection


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

    # ====================================
    # QUERY PARAM
    # ====================================

    player = request.args.get("player")

    # ====================================
    # PLAYER SPECIFIC
    # ====================================

    if player:

        query = """

            SELECT
                batter,
                SUM(batsman_run) AS total_runs

            FROM deliveries

            WHERE batter = %s

            GROUP BY batter

        """

        rows = execute_query(

            query,

            (player,)
        )

        if not rows:

            return {
                "message": "Player not found"
            }, 404

        row = rows[0]

        return {

            "player": row[0],

            "runs": row[1]
        }

    # ====================================
    # LEADERBOARD
    # ====================================

    query = """

        SELECT
            batter,
            SUM(batsman_run) AS total_runs

        FROM deliveries

        GROUP BY batter

        ORDER BY total_runs DESC

        LIMIT 10

    """

    rows = execute_query(query)

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

# =========================================
# HIGHEST INDIVIDUAL SCORES
# =========================================

@batting_bp.route("/batting/highest-score")
def highest_score():

    # ====================================
    # QUERY PARAM
    # ====================================

    player = request.args.get("player")

    # ====================================
    # PLAYER SPECIFIC
    # ====================================

    if player:

        query = """

            SELECT
                batter,
                match_id,
                SUM(batsman_run) AS runs

            FROM deliveries

            WHERE batter = %s

            GROUP BY batter, match_id

            ORDER BY runs DESC

            LIMIT 1

        """

        rows = execute_query(

            query,

            (player,)
        )

        if not rows:

            return {
                "message": "Player not found"
            }, 404

        row = rows[0]

        return {

            "player": row[0],

            "match_id": row[1],

            "highest_score": row[2]
        }

    # ====================================
    # LEADERBOARD
    # ====================================

    query = """

        SELECT
            batter,
            match_id,
            SUM(batsman_run) AS runs

        FROM deliveries

        GROUP BY batter, match_id

        ORDER BY runs DESC

        LIMIT 10

    """

    rows = execute_query(query)

    innings_list = []

    for row in rows:

        innings_list.append({

            "player": row[0],

            "match_id": row[1],

            "runs": row[2]
        })

    return {

        "count": len(innings_list),

        "highest_scores": innings_list
    }

# =========================================
# BEST STRIKE RATES
# =========================================

# =========================================
# STRIKE RATE
# =========================================

@batting_bp.route("/batting/strike-rate")
def strike_rate():

    # ====================================
    # QUERY PARAM
    # ====================================

    player = request.args.get("player")

    # ====================================
    # PLAYER SPECIFIC
    # ====================================

    if player:

        query = """

            SELECT
                batter,

                SUM(batsman_run) AS runs,

                COUNT(*) AS balls,

                ROUND(

                    (
                        SUM(batsman_run) * 100.0
                    ) / COUNT(*),

                    2

                ) AS strike_rate

            FROM deliveries

            WHERE batter = %s

            GROUP BY batter

        """

        rows = execute_query(

            query,

            (player,)
        )

        if not rows:

            return {
                "message": "Player not found"
            }, 404

        row = rows[0]

        return {

            "player": row[0],

            "runs": row[1],

            "balls": row[2],

            "strike_rate": float(row[3])
        }

    # ====================================
    # LEADERBOARD
    # ====================================

    query = """

        SELECT
            batter,

            SUM(batsman_run) AS runs,

            COUNT(*) AS balls,

            ROUND(

                (
                    SUM(batsman_run) * 100.0
                ) / COUNT(*),

                2

            ) AS strike_rate

        FROM deliveries

        GROUP BY batter

        HAVING COUNT(*) >= 500

        ORDER BY strike_rate DESC

        LIMIT 10

    """

    rows = execute_query(query)

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

    # ====================================
    # QUERY PARAM
    # ====================================

    player = request.args.get("player")

    # ====================================
    # PLAYER SPECIFIC
    # ====================================

    if player:

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

            WHERE d.batter = %s

            GROUP BY d.batter

        """

        rows = execute_query(

            query,

            (player,)
        )

        if not rows:

            return {
                "message": "Player not found"
            }, 404

        row = rows[0]

        return {

            "player": row[0],

            "runs": row[1],

            "dismissals": row[2],

            "batting_average": (

                float(row[3])

                if row[3] is not None

                else None
            )
        }

    # ====================================
    # LEADERBOARD
    # ====================================

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

        GROUP BY d.batter

        HAVING COUNT(*) >= 500

        ORDER BY batting_average DESC

        LIMIT 10

    """

    rows = execute_query(query)

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

    # ====================================
    # QUERY PARAMS
    # ====================================

    player = request.args.get("player")

    season = request.args.get(
        "season",
        type=int
    )

    # ====================================
    # BASE QUERY
    # ====================================

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

    # ====================================
    # FILTERS
    # ====================================

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

    # ====================================
    # FINAL QUERY
    # ====================================

    query += """

        GROUP BY d.batter

        ORDER BY sixes DESC

        LIMIT 10

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    # ====================================
    # NO DATA
    # ====================================

    if not rows:

        return {

            "message": "No data found"
        }

    # ====================================
    # RESPONSE
    # ====================================

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

    # ====================================
    # QUERY PARAMS
    # ====================================

    player = request.args.get("player")

    season = request.args.get(
        "season",
        type=int
    )

    # ====================================
    # BASE QUERY
    # ====================================

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

    # ====================================
    # FILTERS
    # ====================================

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

    # ====================================
    # FINAL QUERY
    # ====================================

    query += """

        GROUP BY d.batter

        ORDER BY fours DESC

        LIMIT 10

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    # ====================================
    # NO DATA
    # ====================================

    if not rows:

        return {

            "message": "No data found"
        }

    # ====================================
    # RESPONSE
    # ====================================

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

    # ====================================
    # QUERY PARAMS
    # ====================================

    player = request.args.get("player")

    season = request.args.get(
        "season",
        type=int
    )

    # ====================================
    # BASE QUERY
    # ====================================

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

    # ====================================
    # FILTERS
    # ====================================

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

    # ====================================
    # INNINGS FILTER
    # ====================================

    query += """

            GROUP BY d.batter, d.match_id

            HAVING SUM(d.batsman_run) >= 50

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

    # ====================================
    # NO DATA
    # ====================================

    if not rows:

        return {

            "message": "No data found"
        }

    # ====================================
    # RESPONSE
    # ====================================

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

    # ====================================
    # QUERY PARAMS
    # ====================================

    player = request.args.get("player")

    season = request.args.get(
        "season",
        type=int
    )

    # ====================================
    # BASE QUERY
    # ====================================

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

    # ====================================
    # FILTERS
    # ====================================

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

    # ====================================
    # INNINGS FILTER
    # ====================================

    query += """

            GROUP BY d.batter, d.match_id

            HAVING SUM(d.batsman_run) >= 100

        ) AS innings_scores

        GROUP BY batter

        ORDER BY hundreds DESC

        LIMIT 10

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    # ====================================
    # NO DATA
    # ====================================

    if not rows:

        return {

            "message": "No data found"
        }

    # ====================================
    # RESPONSE
    # ====================================

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

    # ====================================
    # QUERY PARAM
    # ====================================

    season = request.args.get(
        "season",
        type=int
    )

    # ====================================
    # BASE QUERY
    # ====================================

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

    # ====================================
    # SEASON FILTER
    # ====================================

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    # ====================================
    # FINAL QUERY
    # ====================================

    query += """

        GROUP BY d.batter

        ORDER BY runs DESC

        LIMIT 1

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    # ====================================
    # NO DATA
    # ====================================

    if not rows:

        return {

            "message": "No data found"
        }

    row = rows[0]

    # ====================================
    # RESPONSE
    # ====================================

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

            GROUP BY m.season, d.batter

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