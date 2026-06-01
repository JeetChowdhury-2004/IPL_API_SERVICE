from flask import Blueprint
from flask import request

from database.database import get_connection


# =========================================
# BLUEPRINT
# =========================================

players_bp = Blueprint(
    "players",
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


from flask import Blueprint
from flask import request

from database.database import get_connection


# =========================================
# BLUEPRINT
# =========================================

players_bp = Blueprint(

    "players",

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
# PLAYER SUMMARY
# =========================================

@players_bp.route("/players/player-summary")
def player_summary():

    # ====================================
    # QUERY PARAM
    # ====================================

    player = request.args.get("player")

    # ====================================
    # VALIDATION
    # ====================================

    if not player:

        return {

            "error": "player is required"
        }, 400

    # ====================================
    # MATCHES PLAYED
    # ====================================

    matches_query = """

        SELECT

            COUNT(DISTINCT match_id)

        FROM deliveries

        WHERE batter = %s
           OR bowler = %s

    """

    matches_row = execute_query(

        matches_query,

        (
            player,
            player
        )
    )

    matches_played = matches_row[0][0]

    # ====================================
    # BATTING STATS
    # ====================================

    batting_query = """

        SELECT

            SUM(d.batsman_run) AS runs,

            COUNT(*) AS balls,

            COUNT(w.player_out) AS dismissals,

            ROUND(

                (
                    SUM(d.batsman_run) * 100.0
                )

                /

                NULLIF(
                    COUNT(*),
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

            ) AS batting_average

        FROM deliveries d

        LEFT JOIN wickets w

        ON d.delivery_key = w.delivery_key

        AND d.batter = w.player_out

        WHERE d.batter = %s

    """

    batting_row = execute_query(

        batting_query,

        (player,)
    )[0]

    # ====================================
    # BOWLING STATS
    # ====================================

    bowling_query = """

        SELECT

            COUNT(*) AS balls,

            SUM(d.total_run) AS runs_conceded,

            COUNT(w.player_out) AS wickets,

            ROUND(

                (
                    SUM(d.total_run) * 6.0
                )

                /

                NULLIF(
                    COUNT(*),
                    0
                ),

                2

            ) AS economy,

            ROUND(

                COUNT(*) * 1.0

                /

                NULLIF(
                    COUNT(w.player_out),
                    0
                ),

                2

            ) AS bowling_strike_rate

        FROM deliveries d

        LEFT JOIN wickets w

        ON d.delivery_key = w.delivery_key

        WHERE d.bowler = %s

    """

    bowling_row = execute_query(

        bowling_query,

        (player,)
    )[0]

    # ====================================
    # ROLE DETECTION
    # ====================================

    total_runs = batting_row[0] or 0

    total_wickets = bowling_row[2] or 0

    role = "Unknown"

    if total_runs >= 1000 and total_wickets >= 25:

        role = "All-Rounder"

    elif total_runs >= 1000:

        role = "Batter"

    elif total_wickets >= 25:

        role = "Bowler"

    # ====================================
    # NO DATA
    # ====================================

    if (

        total_runs == 0

        and total_wickets == 0

        and matches_played == 0

    ):

        return {

            "message": "Player not found"
        }

    # ====================================
    # RESPONSE
    # ====================================

    return {

        "player": player,

        "role": role,

        "matches_played": matches_played,

        "batting": {

            "runs": total_runs,

            "balls": batting_row[1] or 0,

            "dismissals": batting_row[2] or 0,

            "strike_rate": (

                float(batting_row[3])

                if batting_row[3] is not None

                else None
            ),

            "batting_average": (

                float(batting_row[4])

                if batting_row[4] is not None

                else None
            )
        },

        "bowling": {

            "balls": bowling_row[0] or 0,

            "runs_conceded": bowling_row[1] or 0,

            "wickets": total_wickets,

            "economy": (

                float(bowling_row[3])

                if bowling_row[3] is not None

                else None
            ),

            "bowling_strike_rate": (

                float(bowling_row[4])

                if bowling_row[4] is not None

                else None
            )
        }
    }

# =========================================
# PLAYER OF THE MATCH
# =========================================

@players_bp.route("/players/player-of-the-match")
def player_of_the_match():

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

            player_of_match,

            COUNT(*) AS awards

        FROM matches

        WHERE player_of_match IS NOT NULL

    """

    values = []

    # ====================================
    # PLAYER FILTER
    # ====================================

    if player:

        query += """

            AND player_of_match = %s

        """

        values.append(player)

    # ====================================
    # SEASON FILTER
    # ====================================

    if season:

        query += """

            AND season = %s

        """

        values.append(season)

    # ====================================
    # GROUPING
    # ====================================

    query += """

        GROUP BY player_of_match

    """

    # ====================================
    # ORDERING
    # ====================================

    query += """

        ORDER BY awards DESC

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

            "awards": row[1]
        })

    return {

        "count": len(players),

        "players": players
    }

# =========================================
# PLAYER CAREER SPAN
# =========================================

@players_bp.route("/players/player-career-span")
def player_career_span():

    # ====================================
    # QUERY PARAM
    # ====================================

    player = request.args.get("player")

    # ====================================
    # VALIDATION
    # ====================================

    if not player:

        return {

            "error": "player is required"
        }, 400

    # ====================================
    # SQL QUERY
    # ====================================

    query = """

        SELECT

            MIN(m.season) AS debut_season,

            MAX(m.season) AS last_season,

            COUNT(DISTINCT m.season) AS seasons_played,

            COUNT(DISTINCT d.match_id) AS matches_played

        FROM deliveries d

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE

            d.batter = %s

            OR

            d.bowler = %s

    """

    rows = execute_query(

        query,

        (
            player,
            player
        )
    )

    row = rows[0]

    # ====================================
    # NO DATA
    # ====================================

    if row[0] is None:

        return {

            "message": "Player not found"
        }

    # ====================================
    # RESPONSE
    # ====================================

    return {

        "player": player,

        "debut_season": row[0],

        "last_season": row[1],

        "seasons_played": row[2],

        "matches_played": row[3]
    }

# =========================================
# BEST ALL-ROUNDERS
# =========================================

@players_bp.route("/players/best-all-rounders")
def best_all_rounders():

    # ====================================
    # QUERY PARAMS
    # ====================================

    season = request.args.get(

        "season",

        type=int
    )

    player = request.args.get("player")

    # ====================================
    # BASE QUERY
    # ====================================

    query = """

        SELECT

            batting.player,

            batting.runs,

            batting.batting_strike_rate,

            bowling.wickets,

            bowling.economy,

            ROUND(

                (
                    batting.runs * 1.0
                )

                /

                NULLIF(
                    bowling.wickets,
                    0
                ),

                2

            ) AS all_rounder_index

        FROM (

            SELECT

                d.batter AS player,

                SUM(d.batsman_run) AS runs,

                ROUND(

                    (
                        SUM(d.batsman_run) * 100.0
                    )

                    /

                    NULLIF(
                        COUNT(*),
                        0
                    ),

                    2

                ) AS batting_strike_rate

            FROM deliveries d

            JOIN matches m

            ON d.match_id = m.match_id

            WHERE 1=1

    """

    values = []

    # ====================================
    # OPTIONAL FILTERS FOR BATTING
    # ====================================

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    if player:

        query += """

            AND d.batter = %s

        """

        values.append(player)

    query += """

            GROUP BY d.batter

        ) AS batting

        JOIN (

            SELECT

                d.bowler AS player,

                COUNT(w.player_out) AS wickets,

                ROUND(

                    (
                        SUM(d.total_run) * 6.0
                    )

                    /

                    NULLIF(
                        COUNT(*),
                        0
                    ),

                    2

                ) AS economy

            FROM deliveries d

            LEFT JOIN wickets w

            ON d.delivery_key = w.delivery_key

            JOIN matches m

            ON d.match_id = m.match_id

            WHERE 1=1

    """

    # ====================================
    # OPTIONAL FILTERS FOR BOWLING
    # ====================================

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    if player:

        query += """

            AND d.bowler = %s

        """

        values.append(player)

    query += """

            GROUP BY d.bowler

        ) AS bowling

        ON batting.player = bowling.player

        WHERE

            batting.runs >= 500

            AND bowling.wickets >= 20

        ORDER BY

            all_rounder_index DESC,

            batting.runs DESC,

            bowling.wickets DESC

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

            "runs": row[1],

            "batting_strike_rate": float(row[2]),

            "wickets": row[3],

            "economy": float(row[4]),

            "all_rounder_index": float(row[5])
        })

    return {

        "count": len(players),

        "all_rounders": players
    }

