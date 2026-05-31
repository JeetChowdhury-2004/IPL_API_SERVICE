from flask import Blueprint
from flask import request

from database.database import get_connection


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

    cursor.execute(

        query,

        values if values else ()
    )

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    return rows


# =========================================
# BATTER VS BOWLER
# =========================================

@matchups_bp.route("/matchups/batter-vs-bowler")
def batter_vs_bowler():

    # ====================================
    # QUERY PARAMS
    # ====================================

    batter = request.args.get("batter")

    bowler = request.args.get("bowler")

    season = request.args.get(

        "season",

        type=int
    )

    # ====================================
    # VALIDATION
    # ====================================

    if not batter or not bowler:

        return {

            "error": "batter and bowler are required"
        }, 400

    # ====================================
    # BASE QUERY
    # ====================================

    query = """

        SELECT

            d.batter,

            d.bowler,

            COUNT(*) AS balls,

            SUM(d.batsman_run) AS runs,

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

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE

            d.batter = %s

            AND d.bowler = %s

    """

    values = [

        batter,

        bowler
    ]

    # ====================================
    # OPTIONAL SEASON FILTER
    # ====================================

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    # ====================================
    # GROUPING
    # ====================================

    query += """

        GROUP BY

            d.batter,
            d.bowler

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

            "message": "No matchup data found"
        }

    row = rows[0]

    # ====================================
    # RESPONSE
    # ====================================

    response = {

        "batter": row[0],

        "bowler": row[1],

        "balls": row[2],

        "runs": row[3],

        "dismissals": row[4],

        "strike_rate": float(row[5]),

        "fours": row[6],

        "sixes": row[7]
    }

    if season:

        response["season"] = season

    return response

# =========================================
# BATTER VS TEAM
# =========================================

@matchups_bp.route("/matchups/batter-vs-team")
def batter_vs_team():

    # ====================================
    # QUERY PARAMS
    # ====================================

    batter = request.args.get("batter")

    team = request.args.get("team")

    season = request.args.get(

        "season",

        type=int
    )

    # ====================================
    # VALIDATION
    # ====================================

    if not batter or not team:

        return {

            "error": "batter and team are required"
        }, 400

    # ====================================
    # BASE QUERY
    # ====================================

    query = """

        SELECT

            d.batter,

            d.bowling_team,

            COUNT(*) AS balls,

            SUM(d.batsman_run) AS runs,

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

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE

            d.batter = %s

            AND d.bowling_team = %s

    """

    values = [

        batter,

        team
    ]

    # ====================================
    # OPTIONAL SEASON FILTER
    # ====================================

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    # ====================================
    # GROUPING
    # ====================================

    query += """

        GROUP BY

            d.batter,
            d.bowling_team

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

            "message": "No matchup data found"
        }

    row = rows[0]

    # ====================================
    # RESPONSE
    # ====================================

    response = {

        "batter": row[0],

        "against_team": row[1],

        "balls": row[2],

        "runs": row[3],

        "dismissals": row[4],

        "strike_rate": float(row[5]),

        "batting_average": (

            float(row[6])

            if row[6] is not None

            else None
        ),

        "fours": row[7],

        "sixes": row[8]
    }

    if season:

        response["season"] = season

    return response

# =========================================
# BOWLER VS TEAM
# =========================================

@matchups_bp.route("/matchups/bowler-vs-team")
def bowler_vs_team():

    # ====================================
    # QUERY PARAMS
    # ====================================

    bowler = request.args.get("bowler")

    team = request.args.get("team")

    season = request.args.get(

        "season",

        type=int
    )

    # ====================================
    # VALIDATION
    # ====================================

    if not bowler or not team:

        return {

            "error": "bowler and team are required"
        }, 400

    # ====================================
    # BASE QUERY
    # ====================================

    query = """

        SELECT

            d.bowler,

            d.batting_team,

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

            ) AS strike_rate,

            ROUND(

                (
                    SUM(d.total_run) * 1.0
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

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE

            d.bowler = %s

            AND d.batting_team = %s

    """

    values = [

        bowler,

        team
    ]

    # ====================================
    # OPTIONAL SEASON FILTER
    # ====================================

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    # ====================================
    # GROUPING
    # ====================================

    query += """

        GROUP BY

            d.bowler,
            d.batting_team

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

            "message": "No matchup data found"
        }

    row = rows[0]

    # ====================================
    # RESPONSE
    # ====================================

    response = {

        "bowler": row[0],

        "against_team": row[1],

        "balls": row[2],

        "runs_conceded": row[3],

        "wickets": row[4],

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

    return response

# =========================================
# DEATH OVER SPECIALISTS
# =========================================

@matchups_bp.route("/matchups/death-over-specialists")
def death_over_specialists():

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

            d.bowler,

            COUNT(*) AS balls,

            SUM(d.total_run) AS runs_conceded,

            COUNT(w.player_out) AS wickets,

            SUM(

                CASE

                    WHEN d.is_dot_ball = TRUE
                    THEN 1

                    ELSE 0

                END

            ) AS dot_balls,

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

                (
                    SUM(

                        CASE

                            WHEN d.is_dot_ball = TRUE
                            THEN 1

                            ELSE 0

                        END

                    ) * 100.0
                )

                /

                NULLIF(
                    COUNT(*),
                    0
                ),

                2

            ) AS dot_ball_percentage

        FROM deliveries d

        LEFT JOIN wickets w

        ON d.delivery_key = w.delivery_key

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE d.phase = 'death'

    """

    values = []

    # ====================================
    # OPTIONAL FILTERS
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

    # ====================================
    # GROUPING
    # ====================================

    query += """

        GROUP BY d.bowler

    """

    # ====================================
    # SMART HAVING
    # ====================================

    if not player and not season:

        query += """

            HAVING COUNT(*) >= 200

        """

    elif season:

        query += """

            HAVING COUNT(*) >= 60

        """

    # ====================================
    # ORDERING
    # ====================================

    query += """

        ORDER BY

            economy ASC,

            wickets DESC

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

    bowlers = []

    for row in rows:

        bowlers.append({

            "player": row[0],

            "balls": row[1],

            "runs_conceded": row[2],

            "wickets": row[3],

            "dot_balls": row[4],

            "economy": float(row[5]),

            "dot_ball_percentage": float(row[6])
        })

    return {

        "count": len(bowlers),

        "specialists": bowlers
    }

# =========================================
# POWERPLAY HITTERS
# =========================================

@matchups_bp.route("/matchups/powerplay-hitters")
def powerplay_hitters():

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

            d.batter,

            COUNT(*) AS balls,

            SUM(d.batsman_run) AS runs,

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

            ) AS sixes,

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
                    SUM(

                        CASE

                            WHEN d.batsman_run IN (4, 6)
                            THEN 1

                            ELSE 0

                        END

                    ) * 100.0
                )

                /

                NULLIF(
                    COUNT(*),
                    0
                ),

                2

            ) AS boundary_percentage

        FROM deliveries d

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE d.phase = 'powerplay'

    """

    values = []

    # ====================================
    # OPTIONAL FILTERS
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

    # ====================================
    # GROUPING
    # ====================================

    query += """

        GROUP BY d.batter

    """

    # ====================================
    # SMART HAVING
    # ====================================

    if not player and not season:

        query += """

            HAVING COUNT(*) >= 300

        """

    elif season:

        query += """

            HAVING COUNT(*) >= 60

        """

    # ====================================
    # ORDERING
    # ====================================

    query += """

        ORDER BY

            strike_rate DESC,

            runs DESC

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

    batters = []

    for row in rows:

        batters.append({

            "player": row[0],

            "balls": row[1],

            "runs": row[2],

            "fours": row[3],

            "sixes": row[4],

            "strike_rate": float(row[5]),

            "boundary_percentage": float(row[6])
        })

    return {

        "count": len(batters),

        "powerplay_hitters": batters
    }

# =========================================
# BEST FINISHERS
# =========================================

@matchups_bp.route("/matchups/best-finishers")
def best_finishers():

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

            d.batter,

            COUNT(*) AS balls,

            SUM(d.batsman_run) AS runs,

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

            ) AS sixes,

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
                    SUM(

                        CASE

                            WHEN d.batsman_run IN (4, 6)
                            THEN 1

                            ELSE 0

                        END

                    ) * 100.0
                )

                /

                NULLIF(
                    COUNT(*),
                    0
                ),

                2

            ) AS boundary_percentage

        FROM deliveries d

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE d.phase = 'death'

    """

    values = []

    # ====================================
    # OPTIONAL FILTERS
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

    # ====================================
    # GROUPING
    # ====================================

    query += """

        GROUP BY d.batter

    """

    # ====================================
    # SMART HAVING
    # ====================================

    if not player and not season:

        query += """

            HAVING COUNT(*) >= 200

        """

    elif season:

        query += """

            HAVING COUNT(*) >= 40

        """

    # ====================================
    # ORDERING
    # ====================================

    query += """

        ORDER BY

            strike_rate DESC,

            sixes DESC,

            runs DESC

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

    batters = []

    for row in rows:

        batters.append({

            "player": row[0],

            "balls": row[1],

            "runs": row[2],

            "fours": row[3],

            "sixes": row[4],

            "strike_rate": float(row[5]),

            "boundary_percentage": float(row[6])
        })

    return {

        "count": len(batters),

        "best_finishers": batters
    }

# =========================================
# DOT BALL SPECIALISTS
# =========================================

@matchups_bp.route("/matchups/dot-ball-specialists")
def dot_ball_specialists():

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

            d.bowler,

            COUNT(*) AS balls,

            SUM(

                CASE

                    WHEN d.is_dot_ball = TRUE
                    THEN 1

                    ELSE 0

                END

            ) AS dot_balls,

            ROUND(

                (
                    SUM(

                        CASE

                            WHEN d.is_dot_ball = TRUE
                            THEN 1

                            ELSE 0

                        END

                    ) * 100.0
                )

                /

                NULLIF(
                    COUNT(*),
                    0
                ),

                2

            ) AS dot_ball_percentage,

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

    values = []

    # ====================================
    # OPTIONAL FILTERS
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

    # ====================================
    # GROUPING
    # ====================================

    query += """

        GROUP BY d.bowler

    """

    # ====================================
    # SMART HAVING
    # ====================================

    if not player and not season:

        query += """

            HAVING COUNT(*) >= 300

        """

    elif season:

        query += """

            HAVING COUNT(*) >= 60

        """

    # ====================================
    # ORDERING
    # ====================================

    query += """

        ORDER BY

            dot_ball_percentage DESC,

            wickets DESC

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

    bowlers = []

    for row in rows:

        bowlers.append({

            "player": row[0],

            "balls": row[1],

            "dot_balls": row[2],

            "dot_ball_percentage": float(row[3]),

            "wickets": row[4],

            "economy": float(row[5])
        })

    return {

        "count": len(bowlers),

        "specialists": bowlers
    }

# =========================================
# MIDDLE OVER ANCHORS
# =========================================

@matchups_bp.route("/matchups/middle-over-anchors")
def middle_over_anchors():

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

            d.batter,

            COUNT(*) AS balls,

            SUM(d.batsman_run) AS runs,

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

            ) AS batting_average,

            SUM(

                CASE

                    WHEN d.batsman_run IN (4, 6)
                    THEN 1

                    ELSE 0

                END

            ) AS boundaries,

            ROUND(

                (
                    SUM(

                        CASE

                            WHEN d.batsman_run IN (4, 6)
                            THEN 1

                            ELSE 0

                        END

                    ) * 100.0
                )

                /

                NULLIF(
                    COUNT(*),
                    0
                ),

                2

            ) AS boundary_percentage

        FROM deliveries d

        LEFT JOIN wickets w

        ON d.delivery_key = w.delivery_key

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE d.phase = 'middle'

    """

    values = []

    # ====================================
    # OPTIONAL FILTERS
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

    # ====================================
    # GROUPING
    # ====================================

    query += """

        GROUP BY d.batter

    """

    # ====================================
    # SMART HAVING
    # ====================================

    if not player and not season:

        query += """

            HAVING COUNT(*) >= 300

        """

    elif season:

        query += """

            HAVING COUNT(*) >= 80

        """

    # ====================================
    # ORDERING
    # ====================================

    query += """

        ORDER BY

            batting_average DESC,

            strike_rate DESC

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

    batters = []

    for row in rows:

        batters.append({

            "player": row[0],

            "balls": row[1],

            "runs": row[2],

            "dismissals": row[3],

            "strike_rate": float(row[4]),

            "batting_average": (

                float(row[5])

                if row[5] is not None

                else None
            ),

            "boundaries": row[6],

            "boundary_percentage": float(row[7])
        })

    return {

        "count": len(batters),

        "anchors": batters
    }

# =========================================
# CHASING SPECIALISTS
# =========================================

@matchups_bp.route("/matchups/chasing-specialists")
def chasing_specialists():

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

            d.batter,

            COUNT(*) AS balls,

            SUM(d.batsman_run) AS runs,

            COUNT(w.player_out) AS dismissals,

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

            ) AS sixes,

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

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE d.innings = 2

    """

    values = []

    # ====================================
    # OPTIONAL FILTERS
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

    # ====================================
    # GROUPING
    # ====================================

    query += """

        GROUP BY d.batter

    """

    # ====================================
    # SMART HAVING
    # ====================================

    if not player and not season:

        query += """

            HAVING COUNT(*) >= 300

        """

    elif season:

        query += """

            HAVING COUNT(*) >= 60

        """

    # ====================================
    # ORDERING
    # ====================================

    query += """

        ORDER BY

            batting_average DESC,

            strike_rate DESC,

            runs DESC

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

    batters = []

    for row in rows:

        batters.append({

            "player": row[0],

            "balls": row[1],

            "runs": row[2],

            "dismissals": row[3],

            "fours": row[4],

            "sixes": row[5],

            "strike_rate": float(row[6]),

            "batting_average": (

                float(row[7])

                if row[7] is not None

                else None
            )
        })

    return {

        "count": len(batters),

        "chasing_specialists": batters
    }

# =========================================
# CLUTCH PERFORMERS
# =========================================

@matchups_bp.route("/matchups/clutch-performers")
def clutch_performers():

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

            d.batter,

            COUNT(*) AS balls,

            SUM(d.batsman_run) AS runs,

            COUNT(w.player_out) AS dismissals,

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

            ) AS sixes,

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

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE m.is_playoff = TRUE

    """

    values = []

    # ====================================
    # OPTIONAL FILTERS
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

    # ====================================
    # GROUPING
    # ====================================

    query += """

        GROUP BY d.batter

    """

    # ====================================
    # SMART HAVING
    # ====================================

    if not player and not season:

        query += """

            HAVING COUNT(*) >= 100

        """

    elif season:

        query += """

            HAVING COUNT(*) >= 20

        """

    # ====================================
    # ORDERING
    # ====================================

    query += """

        ORDER BY

            batting_average DESC,

            strike_rate DESC,

            runs DESC

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

    batters = []

    for row in rows:

        batters.append({

            "player": row[0],

            "balls": row[1],

            "runs": row[2],

            "dismissals": row[3],

            "fours": row[4],

            "sixes": row[5],

            "strike_rate": float(row[6]),

            "batting_average": (

                float(row[7])

                if row[7] is not None

                else None
            )
        })

    return {

        "count": len(batters),

        "clutch_performers": batters
    }