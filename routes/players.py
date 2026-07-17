from flask import Blueprint
from flask import request

from database.database import get_connection

from utils.api_response import (
    success_response,
    error_response
)

from utils.pagination import get_pagination
from utils.available_data import load_available_data


# =========================================
# PLAYER NAME NORMALIZATION
# =========================================

def normalize_player(name):
    if not name:
        return name

    available_data = load_available_data()
    players = available_data["batters"] + available_data["bowlers"]

    lname = name.lower()
    # exact match
    for cand in players:
        if cand.lower() == lname:
            return cand
    # substring match
    for cand in players:
        if lname in cand.lower() or cand.lower() in lname:
            return cand
    # last-name match
    last = lname.split()[-1]
    matches = [c for c in players if c.lower().endswith(last)]
    if matches:
        return matches[0]
    return name

# =========================================
# INVALID DISMISSALS
# =========================================

INVALID_DISMISSALS = (

    'run out',
    'retired hurt',
    'retired out',
    'obstructing the field'
)

BATTING_NOT_OUT_DISMISSALS = (

    'retired hurt',
)

DEFAULT_PLAYER_SEARCH_LIMIT = 10

MAX_PLAYER_SEARCH_LIMIT = 50

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
# PLAYER SEARCH
# =========================================

@players_bp.route("/players/search")
def search_players():

    player_name = request.args.get(

        "player_name",

        ""
    ).strip()

    role = request.args.get(

        "role",

        "all"
    ).strip().lower()

    limit = request.args.get(

        "limit",

        default=DEFAULT_PLAYER_SEARCH_LIMIT,

        type=int
    )

    if not player_name:

        return error_response(

            "player_name is required",

            400
        )

    if role not in ("all", "batter", "bowler"):

        return error_response(

            "role must be one of: all, batter, bowler",

            400
        )

    if limit is None or limit <= 0:

        limit = DEFAULT_PLAYER_SEARCH_LIMIT

    if limit > MAX_PLAYER_SEARCH_LIMIT:

        limit = MAX_PLAYER_SEARCH_LIMIT

    search_pattern = f"%{player_name}%"

    prefix_pattern = f"{player_name}%"

    sql = """

        WITH player_roles AS (

            SELECT
                batter AS player,
                'batter' AS role,
                match_id
            FROM deliveries
            WHERE batter IS NOT NULL

            UNION ALL

            SELECT
                bowler AS player,
                'bowler' AS role,
                match_id
            FROM deliveries
            WHERE bowler IS NOT NULL
        ),

        grouped_players AS (

            SELECT
                player,
                BOOL_OR(role = 'batter') AS is_batter,
                BOOL_OR(role = 'bowler') AS is_bowler,
                COUNT(DISTINCT match_id) AS matches
            FROM player_roles
            WHERE player ILIKE %s
            GROUP BY player
        )

        SELECT
            player,
            is_batter,
            is_bowler,
            matches
        FROM grouped_players
        WHERE (
            %s = 'all'
            OR (%s = 'batter' AND is_batter = TRUE)
            OR (%s = 'bowler' AND is_bowler = TRUE)
        )
        ORDER BY
            CASE
                WHEN LOWER(player) = LOWER(%s) THEN 0
                WHEN player ILIKE %s THEN 1
                ELSE 2
            END,
            player ASC
        LIMIT %s

    """

    rows = execute_query(

        sql,

        (
            search_pattern,
            role,
            role,
            role,
            player_name,
            prefix_pattern,
            limit
        )
    )

    players = []

    for row in rows:

        available_as = []

        if row[1]:

            available_as.append("batter")

        if row[2]:

            available_as.append("bowler")

        players.append({

            "player": row[0],

            "available_as": available_as,

            "matches": int(row[3])
        })

    return success_response({

        "player_name": player_name,

        "role": role,

        "count": len(players),

        "players": players
    })

# =========================================
# PLAYER SUMMARY
# =========================================

@players_bp.route("/players/player-summary")
def player_summary():

    player = request.args.get("player")

    if not player:

        return error_response(

            "player is required",

            400
        )

    # ====================================
    # MATCHES PLAYED
    # ====================================

    # Normalize player using available data
    player = normalize_player(player)

    matches_query = """

        SELECT

            COUNT(DISTINCT match_id)

        FROM deliveries

        WHERE batter ILIKE %s
           OR bowler ILIKE %s

    """

    # player already normalized above

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

            ) AS batting_average

        FROM deliveries d

        LEFT JOIN wickets w

        ON d.delivery_key = w.delivery_key

        AND d.batter = w.player_out

        AND w.dismissal_kind NOT IN %s

        WHERE d.batter ILIKE %s

    """

    batting_row = execute_query(

        batting_query,

        (
            BATTING_NOT_OUT_DISMISSALS,
            player
        )
    )[0]

    # ====================================
    # BOWLING STATS
    # ====================================

    bowling_query = """

        SELECT

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

            COUNT(

                CASE

                    WHEN w.dismissal_kind NOT IN %s

                    THEN w.player_out

                END

            ) AS wickets,

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
                    COUNT(

                        CASE

                            WHEN w.dismissal_kind NOT IN %s

                            THEN w.player_out

                        END

                    ),
                    0
                ),

                2

            ) AS bowling_strike_rate

        FROM deliveries d

        LEFT JOIN wickets w

        ON d.delivery_key = w.delivery_key

        WHERE d.bowler ILIKE %s

    """

    bowling_row = execute_query(

        bowling_query,

        (
            INVALID_DISMISSALS,
            INVALID_DISMISSALS,
            player
        )
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

        return error_response(

            "Player not found",

            404
        )

    # ====================================
    # RESPONSE
    # ====================================

    return success_response({

        "player": player,

        "role": role,

        "matches_played": int(matches_played),

        "batting": {

            "runs": int(total_runs),

            "balls": int(batting_row[1] or 0),

            "dismissals": int(batting_row[2] or 0),

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

            "balls": int(bowling_row[0] or 0),

            "runs_conceded": int(bowling_row[1] or 0),

            "wickets": int(total_wickets),

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
    })

# =========================================
# PLAYER OF THE MATCH
# =========================================

@players_bp.route("/players/player-of-the-match")
def player_of_the_match():

    player = request.args.get("player")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT

            player_of_match,

            COUNT(*) AS awards

        FROM matches

        WHERE player_of_match IS NOT NULL

    """

    values = []

    if player:

        query += """

            AND player_of_match ILIKE %s

        """

        values.append(player)

    if season:

        query += """

            AND season = %s

        """

        values.append(season)

    limit, offset = get_pagination()

    query += """

        GROUP BY player_of_match

        ORDER BY awards DESC

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

    players = []

    for row in rows:

        players.append({

            "player": row[0],

            "awards": int(row[1])
        })

    return success_response({

        "count": len(players),

        "players": players
    })

# =========================================
# PLAYER CAREER SPAN
# =========================================

@players_bp.route("/players/player-career-span")
def player_career_span():

    player = request.args.get("player")

    if not player:

        return error_response(

            "player is required",

            400
        )

    # Normalize player using available data
    player = normalize_player(player)

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

            d.batter ILIKE %s

            OR

            d.bowler ILIKE %s

    """

    rows = execute_query(

        query,

        (
            player,
            player
        )
    )

    row = rows[0]

    if row[0] is None:

        return error_response(

            "Player not found",

            404
        )

    return success_response({

        "player": player,

        "debut_season": int(row[0]),

        "last_season": int(row[1]),

        "seasons_played": int(row[2]),

        "matches_played": int(row[3])
    })

# =========================================
# BEST ALL-ROUNDERS
# =========================================

@players_bp.route("/players/best-all-rounders")
def best_all_rounders():

    season = request.args.get(

        "season",

        type=int
    )

    player = request.args.get("player")

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

                ) AS batting_strike_rate

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

    if player:

        query += """

            AND d.batter ILIKE %s

        """

        values.append(player)

    query += """

            GROUP BY d.batter

        ) AS batting

        JOIN (

            SELECT

                d.bowler AS player,

                COUNT(

                    CASE

                        WHEN w.dismissal_kind NOT IN %s

                        THEN w.player_out

                    END

                ) AS wickets,

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

                ) AS economy

            FROM deliveries d

            LEFT JOIN wickets w

            ON d.delivery_key = w.delivery_key

            JOIN matches m

            ON d.match_id = m.match_id

            WHERE 1=1

    """

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    if player:

        query += """

            AND d.bowler ILIKE %s

        """

        values.append(player)

    limit, offset = get_pagination()

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

        LIMIT %s
        OFFSET %s

    """

    values.extend([limit, offset])

    # Insert INVALID_DISMISSALS at the position corresponding to the
    # bowling NOT IN %s placeholder. Batting placeholders (season, player)
    # appear first in `values` (in that order if present). Compute how many
    # batting placeholders were added to place INVALID_DISMISSALS correctly.
    batting_count = 0
    if request.args.get('season', type=int) is not None:
        batting_count += 1
    if request.args.get('player'):
        batting_count += 1

    final_values = values[:batting_count] + [INVALID_DISMISSALS] + values[batting_count:]

    rows = execute_query(

        query,

        tuple(final_values)
    )

    if not rows:

        return error_response(

            "No data found",

            404
        )

    players = []

    for row in rows:

        players.append({

            "player": row[0],

            "runs": int(row[1]),

            "batting_strike_rate": float(row[2]),

            "wickets": int(row[3]),

            "economy": float(row[4]),

            "all_rounder_index": float(row[5])
        })

    return success_response({

        "count": len(players),

        "all_rounders": players
    })
