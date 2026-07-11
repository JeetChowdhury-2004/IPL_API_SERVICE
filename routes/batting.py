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

    'retired hurt',
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

            AND d.batter ILIKE %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    limit, offset = get_pagination()

    query += """

        GROUP BY d.batter

        ORDER BY total_runs DESC

    """

    query += """

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

            "Player not found",

            404
        )

    if player:

        row = rows[0]

        response = {

            "player": row[0],

            "runs": int(row[1])
        }

        if season:

            response["season"] = season

        return success_response(response)

    players = []

    for row in rows:

        players.append({

            "player": row[0],

            "runs": int(row[1])
        })

    return success_response({

        "count": len(players),

        "players": players
    })

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

            AND d.batter ILIKE %s

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
            d.batter,
            d.match_id,
            m.season

        ORDER BY runs DESC

    """

    if not player:

        query += """

            LIMIT %s
            OFFSET %s

        """

        values.extend([limit, offset])

    else:

        query += """

            LIMIT 1

        """

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return error_response(

            "Player not found",

            404
        )

    if player:

        row = rows[0]

        return success_response({

            "player": row[0],

            "match_id": row[1],

            "season": row[2],

            "highest_score": int(row[3])
        })

    innings_list = []

    for row in rows:

        innings_list.append({

            "player": row[0],

            "match_id": row[1],

            "season": row[2],

            "runs": int(row[3])
        })

    return success_response({

        "count": len(innings_list),

        "highest_scores": innings_list
    })

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

            AND d.batter ILIKE %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    limit, offset = get_pagination()

    query += """

        GROUP BY d.batter

    """

    if not player:

        if not season:

            query += """

                HAVING COUNT(*) >= 500

            """

        else:

            query += """

                HAVING COUNT(*) >= 100

            """

    query += """

        ORDER BY strike_rate DESC

    """

    if not player:

        query += """

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

            "Player not found",

            404
        )

    if player:

        row = rows[0]

        response = {

            "player": row[0],

            "runs": int(row[1]),

            "balls": int(row[2]),

            "strike_rate": float(row[3])
        }

        if season:

            response["season"] = season

        return success_response(response)

    players = []

    for row in rows:

        players.append({

            "player": row[0],

            "runs": int(row[1]),

            "balls": int(row[2]),

            "strike_rate": float(row[3])
        })

    return success_response({

        "count": len(players),

        "players": players
    })

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

            AND d.batter ILIKE %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    limit, offset = get_pagination()

    query += """

        GROUP BY d.batter

    """

    if not player:

        if not season:

            query += """

                HAVING COUNT(*) >= 500

            """

        else:

            query += """

                HAVING COUNT(*) >= 100

            """

    query += """

        ORDER BY batting_average DESC

    """

    if not player:

        query += """

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

            "Player not found",

            404
        )

    if player:

        row = rows[0]

        response = {

            "player": row[0],

            "runs": int(row[1]),

            "dismissals": int(row[2]),

            "batting_average": (

                float(row[3])

                if row[3] is not None

                else None
            )
        }

        if season:

            response["season"] = season

        return success_response(response)

    players = []

    for row in rows:

        players.append({

            "player": row[0],

            "runs": int(row[1]),

            "dismissals": int(row[2]),

            "batting_average": (

                float(row[3])

                if row[3] is not None

                else None
            )
        })

    return success_response({

        "count": len(players),

        "players": players
    })

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

            AND d.batter ILIKE %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    limit, offset = get_pagination()

    query += """

        GROUP BY d.batter

        ORDER BY sixes DESC

    """

    if not player:

        query += """

            LIMIT %s
            OFFSET %s

        """

        values.extend([limit, offset])

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return error_response("No data found")

    players = []

    for row in rows:

        players.append({

            "player": row[0],

            "sixes": int(row[1])
        })

    return success_response({

        "count": len(players),

        "players": players
    })

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

            AND d.batter ILIKE %s

        """

        values.append(player)

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    limit, offset = get_pagination()

    query += """

        GROUP BY d.batter

        ORDER BY fours DESC

    """

    if not player:

        query += """

            LIMIT %s
            OFFSET %s

        """

        values.extend([limit, offset])

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return error_response("No data found")

    players = []

    for row in rows:

        players.append({

            "player": row[0],

            "fours": int(row[1])
        })

    return success_response({

        "count": len(players),

        "players": players
    })

# =========================================
# ORANGE CAP BY SEASON# =========================================
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

        LIMIT %s
        OFFSET %s

    """

    limit, offset = get_pagination()

    rows = execute_query(query, (limit, offset))

    results = []

    for row in rows:

        results.append({

            "season": row[0],

            "player": row[1],

            "runs": int(row[2])
        })

    return success_response({

        "count": len(results),

        "orange_caps": results
    })



# =========================================
# MOST 50s
# =========================================

@batting_bp.route("/batting/most-50s")
def most_fifties():

    player = request.args.get("player")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        WITH player_scores AS (

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

            AND d.batter ILIKE %s

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
                d.batter,
                d.match_id,
                m.season
        )

        SELECT
            batter,

            COUNT(*) AS fifties

        FROM player_scores

        WHERE runs >= 50
        AND runs < 100

        GROUP BY batter

        ORDER BY fifties DESC

    """

    if not player:

        query += """

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

            "Player not found",

            404
        )

    if player:

        row = rows[0]

        response = {

            "player": row[0],

            "fifties": int(row[1])
        }

        if season:

            response["season"] = season

        return success_response(response)

    players = []

    for row in rows:

        players.append({

            "player": row[0],

            "fifties": int(row[1])
        })

    return success_response({

        "count": len(players),

        "players": players
    })


# =========================================
# MOST 100s
# =========================================

@batting_bp.route("/batting/most-100s")
def most_hundreds():

    player = request.args.get("player")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        WITH player_scores AS (

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

            AND d.batter ILIKE %s

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
                d.batter,
                d.match_id,
                m.season
        )

        SELECT
            batter,

            COUNT(*) AS hundreds

        FROM player_scores

        WHERE runs >= 100

        GROUP BY batter

        ORDER BY hundreds DESC

    """

    if not player:

        query += """

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

            "Player not found",

            404
        )

    if player:

        row = rows[0]

        response = {

            "player": row[0],

            "hundreds": int(row[1])
        }

        if season:

            response["season"] = season

        return success_response(response)

    players = []

    for row in rows:

        players.append({

            "player": row[0],

            "hundreds": int(row[1])
        })

    return success_response({

        "count": len(players),

        "players": players
    })