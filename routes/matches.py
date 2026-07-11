import os
import sys

from flask import Blueprint
from flask import request

from utils.pagination import get_pagination
from utils.api_response import (
    success_response,
    error_response
)

# =========================================
# PROJECT ROOT
# =========================================

ROOT_DIR = os.path.abspath(

    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if ROOT_DIR not in sys.path:

    sys.path.insert(0, ROOT_DIR)

# =========================================
# IMPORTS
# =========================================

from database.database import (
    get_connection
)

from team_name_normalization import (
    normalize_team_name
)


# =========================================
# BLUEPRINT
# =========================================

matches_bp = Blueprint(

    "matches",

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
# ALL MATCHES
# =========================================

@matches_bp.route("/matches")
def all_matches():

    limit, offset = get_pagination()

    # =====================================
    # QUERY
    # =====================================

    query = """

        SELECT
            match_id,
            season,
            city,
            venue,
            team1,
            team2,
            toss_winner,
            toss_decision,
            winner,
            result_type,
            result_margin,
            player_of_match,
            match_stage,
            match_date

        FROM matches

        ORDER BY match_date ASC

        LIMIT %s
        OFFSET %s

    """

    rows = execute_query(

        query,

        (limit, offset)
    )

    matches_list = []

    for row in rows:

        matches_list.append({

            "match_id": row[0],

            "season": row[1],

            "city": row[2],

            "venue": row[3],

            "teams": [

                normalize_team_name(row[4]),

                normalize_team_name(row[5])
            ],

            "toss": {

                "winner": normalize_team_name(
                    row[6]
                ),

                "decision": row[7]
            },

            "winner": normalize_team_name(
                row[8]
            ) if row[8] else None,

            "result": {

                "type": row[9],

                "margin": row[10]
            },

            "player_of_match": row[11],

            "match_stage": row[12],

            "match_date": str(row[13])
        })

    return success_response({

        "count": len(matches_list),

        "matches": matches_list
    })


# =========================================
# MATCHES BY SEASON
# =========================================

@matches_bp.route("/matches/season/<int:season>")
def get_match_by_season(season):

    limit, offset = get_pagination()

    query = """

        SELECT
            match_id,
            season,
            city,
            venue,
            team1,
            team2,
            toss_winner,
            toss_decision,
            winner,
            result_type,
            result_margin,
            player_of_match,
            match_stage,
            match_date

        FROM matches

        WHERE season = %s

        ORDER BY match_date ASC

        LIMIT %s
        OFFSET %s

    """

    rows = execute_query(

        query,

        (season, limit, offset)
    )

    matches_list = []

    for row in rows:

        matches_list.append({

            "match_id": row[0],

            "season": row[1],

            "city": row[2],

            "venue": row[3],

            "teams": [

                normalize_team_name(row[4]),

                normalize_team_name(row[5])
            ],

            "toss": {

                "winner": normalize_team_name(
                    row[6]
                ),

                "decision": row[7]
            },

            "winner": normalize_team_name(
                row[8]
            ) if row[8] else None,

            "result": {

                "type": row[9],

                "margin": row[10]
            },

            "player_of_match": row[11],

            "match_stage": row[12],

            "match_date": str(row[13])
        })

    return success_response({

        "season": season,

        "count": len(matches_list),

        "matches": matches_list
    })


# =========================================
# FILTER MATCHES
# =========================================

@matches_bp.route("/matches/filter")
def filter_matches():

    team = request.args.get("team")

    city = request.args.get("city")

    winner = request.args.get("winner")

    season = request.args.get(

        "season",

        type=int
    )

    query = """

        SELECT
            match_id,
            season,
            city,
            venue,
            team1,
            team2,
            winner

        FROM matches

        WHERE 1=1

    """

    values = []

    if team:

        query += """

            AND (
                team1 = %s
                OR team2 = %s
            )

        """

        values.extend([team, team])

    if city:

        query += """

            AND city = %s

        """

        values.append(city)

    if winner:

        query += """

            AND winner = %s

        """

        values.append(winner)

    if season:

        query += """

            AND season = %s

        """

        values.append(season)

    query += """

        ORDER BY match_date ASC

        LIMIT 50

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    matches = []

    for row in rows:

        matches.append({

            "match_id": row[0],

            "season": row[1],

            "city": row[2],

            "venue": row[3],

            "team1": normalize_team_name(
                row[4]
            ),

            "team2": normalize_team_name(
                row[5]
            ),

            "winner": normalize_team_name(
                row[6]
            ) if row[6] else None
        })

    return success_response({

        "count": len(matches),

        "matches": matches
    })


# =========================================
# HEAD TO HEAD
# =========================================

@matches_bp.route("/matches/head-to-head")
def head_to_head():

    team1 = request.args.get("team1")

    team2 = request.args.get("team2")

    if not team1 or not team2:

        return error_response(

            "team1 and team2 are required",

            400
        )

    if team1 == team2:

        return error_response(

            "Both teams cannot be same",

            400
        )

    query = """

        SELECT
            match_id,
            season,
            city,
            venue,
            team1,
            team2,
            winner,
            match_date

        FROM matches

        WHERE (

            (team1 = %s AND team2 = %s)

            OR

            (team1 = %s AND team2 = %s)

        )

        ORDER BY match_date ASC

    """

    rows = execute_query(

        query,

        (
            team1,
            team2,

            team2,
            team1
        )
    )

    total_matches = len(rows)

    team1_wins = 0

    team2_wins = 0

    no_result = 0

    matches = []

    for row in rows:

        winner = row[6]

        if winner == team1:

            team1_wins += 1

        elif winner == team2:

            team2_wins += 1

        else:

            no_result += 1

        matches.append({

            "match_id": row[0],

            "season": row[1],

            "city": row[2],

            "venue": row[3],

            "teams": [

                normalize_team_name(row[4]),

                normalize_team_name(row[5])
            ],

            "winner": normalize_team_name(
                row[6]
            ) if row[6] else None,

            "match_date": str(row[7])
        })

    return success_response({

        "summary": {

            "team1": normalize_team_name(
                team1
            ),

            "team2": normalize_team_name(
                team2
            ),

            "total_matches": total_matches,

            "team1_wins": team1_wins,

            "team2_wins": team2_wins,

            "no_result": no_result
        },

        "matches": matches
    })


# =========================================
# ALL TITLE WINNERS
# =========================================

@matches_bp.route("/matches/title-winners")
def get_all_title_winners():

    query = """

        SELECT DISTINCT winner

        FROM matches

        WHERE LOWER(
            TRIM(match_stage)
        ) = 'final'

        AND winner IS NOT NULL

        ORDER BY winner ASC

    """

    rows = execute_query(query)

    teams = sorted(

        list(

            set(

                normalize_team_name(row[0])

                for row in rows
            )
        )
    )

    return success_response({

        "count": len(teams),

        "teams": teams
    })


# =========================================
# TITLE COUNTS
# =========================================

@matches_bp.route("/matches/title-counts")
def title_counts():

    query = """

        SELECT
            winner,
            COUNT(*) AS titles

        FROM matches

        WHERE LOWER(
            TRIM(match_stage)
        ) = 'final'

        AND winner IS NOT NULL

        GROUP BY winner

        ORDER BY titles DESC,
                 winner ASC

    """

    rows = execute_query(query)

    teams = []

    for row in rows:

        teams.append({

            "team": normalize_team_name(
                row[0]
            ),

            "titles": int(row[1])
        })

    return success_response({

        "count": len(teams),

        "title_counts": teams
    })


# =========================================
# MOST SUCCESSFUL TEAM
# =========================================

@matches_bp.route("/matches/most-successful-team")
def most_successful_team():

    query = """

        SELECT
            winner,
            COUNT(*) AS wins

        FROM matches

        WHERE winner IS NOT NULL

        GROUP BY winner

        ORDER BY wins DESC

    """

    rows = execute_query(query)

    if not rows:

        return error_response(

            "No data found",

            404
        )

    top_team = rows[0][0]

    total_wins = rows[0][1]

    matches_query = """

        SELECT COUNT(*)

        FROM matches

        WHERE team1 = %s
           OR team2 = %s

    """

    match_rows = execute_query(

        matches_query,

        (
            top_team,
            top_team
        )
    )

    total_matches = match_rows[0][0]

    losses = total_matches - total_wins

    win_percentage = (

        total_wins / total_matches

    ) * 100

    return success_response({

        "team": normalize_team_name(
            top_team
        ),

        "total_matches": int(total_matches),

        "wins": int(total_wins),

        "losses": int(losses),

        "win_percentage": round(

            win_percentage,

            2
        )
    })


# =========================================
# ALL UNIQUE IPL TEAMS
# =========================================

@matches_bp.route("/teams")
def get_all_teams():

    query = """

        SELECT DISTINCT team_name

        FROM (

            SELECT team1 AS team_name

            FROM matches

            UNION

            SELECT team2 AS team_name

            FROM matches

        ) AS teams

        ORDER BY team_name ASC

    """

    rows = execute_query(query)

    teams = sorted(

        list(

            set(

                normalize_team_name(row[0])

                for row in rows

                if row[0] is not None
            )
        )
    )

    return success_response({

        "count": len(teams),

        "teams": teams
    })

# =========================================
# HIGHEST RUN CHASES
# =========================================

@matches_bp.route("/matches/highest-run-chases")
def highest_run_chases():

    # ====================================
    # QUERY PARAMS
    # ====================================

    season = request.args.get(

        "season",

        type=int
    )

    team = request.args.get("team")

    if team:

        team = normalize_team_name(team)

    # ====================================
    # BASE QUERY
    # ====================================

    query = """

        SELECT

            season,

            team2 AS chasing_team,

            team1 AS defending_team,

            venue,

            city,

            target_runs,

            winner,

            result_margin,

            match_date

        FROM matches

        WHERE

            result_type = 'wickets'

            AND winner = team2

            AND target_runs IS NOT NULL

    """

    values = []

    # ====================================
    # OPTIONAL FILTERS
    # ====================================

    if season:

        query += """

            AND season = %s

        """

        values.append(season)

    if team:

        query += """

            AND team2 = %s

        """

        values.append(team)

    limit, offset = get_pagination()

    # ====================================
    # ORDERING
    # ====================================

    query += """

        ORDER BY

            target_runs DESC,

            result_margin DESC

        LIMIT %s
        OFFSET %s

    """

    rows = execute_query(

        query,

        tuple(values + [limit, offset])
    )

    # ====================================
    # NO DATA
    # ====================================

    if not rows:

        return error_response(

            "No data found",

            404
        )

    # ====================================
    # RESPONSE
    # ====================================

    chases = []

    for row in rows:

        chases.append({

            "season": row[0],

            "chasing_team": normalize_team_name(
                row[1]
            ),

            "defending_team": normalize_team_name(
                row[2]
            ),

            "venue": row[3],

            "city": row[4],

            "target": int(row[5]),

            "winner": normalize_team_name(
                row[6]
            ),

            "wickets_remaining": int(row[7]),

            "match_date": str(row[8])
        })

    return success_response({

        "count": len(chases),

        "highest_run_chases": chases
    })

# =========================================
# HIGHEST TEAM TOTALS
# =========================================

@matches_bp.route("/matches/highest-team-totals")
def highest_team_totals():

    # ====================================
    # QUERY PARAMS
    # ====================================

    season = request.args.get(

        "season",

        type=int
    )

    team = request.args.get("team")

    if team:

        team = normalize_team_name(team)

    # ====================================
    # BASE QUERY
    # ====================================

    query = """

        SELECT

            d.match_id,

            m.season,

            d.batting_team,

            m.venue,

            m.city,

            d.innings,

            SUM(d.total_run) AS total_runs

        FROM deliveries d

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE 1=1

    """

    values = []

    # ====================================
    # TEAM FILTER
    # ====================================

    if team:

        query += """

            AND d.batting_team = %s

        """

        values.append(team)

    # ====================================
    # SEASON FILTER
    # ====================================

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    limit, offset = get_pagination()

    # ====================================
    # GROUPING
    # ====================================

    query += """

        GROUP BY

            d.match_id,
            m.season,
            d.batting_team,
            m.venue,
            m.city,
            d.innings

    """

    # ====================================
    # ORDERING
    # ====================================

    query += """

        ORDER BY

            total_runs DESC

        LIMIT %s
        OFFSET %s

    """

    rows = execute_query(

        query,

        tuple(values + [limit, offset])
    )

    # ====================================
    # NO DATA
    # ====================================

    if not rows:

        return error_response(

            "No data found",

            404
        )

    # ====================================
    # RESPONSE
    # ====================================

    totals = []

    for row in rows:

        totals.append({

            "match_id": row[0],

            "season": row[1],

            "team": normalize_team_name(
                row[2]
            ),

            "venue": row[3],

            "city": row[4],

            "innings": int(row[5]),

            "total_runs": int(row[6])
        })

    return success_response({

        "count": len(totals),

        "highest_team_totals": totals
    })

# =========================================
# LOWEST DEFENDED SCORES
# =========================================

@matches_bp.route("/matches/lowest-defended-scores")
def lowest_defended_scores():

    # ====================================
    # QUERY PARAMS
    # ====================================

    season = request.args.get(

        "season",

        type=int
    )

    team = request.args.get("team")

    if team:

        team = normalize_team_name(team)

    # ====================================
    # BASE QUERY
    # ====================================

    query = """

        SELECT

            d.match_id,

            m.season,

            d.batting_team AS defending_team,

            CASE

                WHEN d.batting_team = m.team1
                THEN m.team2

                ELSE m.team1

            END AS chasing_team,

            m.venue,

            m.city,

            SUM(d.total_run) AS defended_score,

            m.winner,

            m.result_margin

        FROM deliveries d

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE

            d.innings = 1

            AND m.result_type = 'runs'

            AND m.winner = d.batting_team

    """

    values = []

    # ====================================
    # TEAM FILTER
    # ====================================

    if team:

        query += """

            AND d.batting_team = %s

        """

        values.append(team)

    # ====================================
    # SEASON FILTER
    # ====================================

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    limit, offset = get_pagination()

    # ====================================
    # GROUPING
    # ====================================

    query += """

        GROUP BY

            d.match_id,
            m.season,
            d.batting_team,
            m.team1,
            m.team2,
            m.venue,
            m.city,
            m.winner,
            m.result_margin

    """

    # ====================================
    # ORDERING
    # ====================================

    query += """

        ORDER BY

            defended_score ASC,

            result_margin ASC

        LIMIT %s
        OFFSET %s

    """

    rows = execute_query(

        query,

        tuple(values + [limit, offset])
    )

    # ====================================
    # NO DATA
    # ====================================

    if not rows:

        return error_response(

            "No data found",

            404
        )

    # ====================================
    # RESPONSE
    # ====================================

    scores = []

    for row in rows:

        scores.append({

            "match_id": row[0],

            "season": row[1],

            "defending_team": normalize_team_name(
                row[2]
            ),

            "chasing_team": normalize_team_name(
                row[3]
            ),

            "venue": row[4],

            "city": row[5],

            "defended_score": int(row[6]),

            "winner": normalize_team_name(
                row[7]
            ),

            "win_margin_runs": int(row[8])
        })

    return success_response({

        "count": len(scores),

        "lowest_defended_scores": scores
    })

# =========================================
# LOWEST TEAM TOTALS
# =========================================

@matches_bp.route("/matches/lowest-team-totals")
def lowest_team_totals():

    # ====================================
    # QUERY PARAMS
    # ====================================

    season = request.args.get(

        "season",

        type=int
    )

    team = request.args.get("team")

    if team:

        team = normalize_team_name(team)

    # ====================================
    # BASE QUERY
    # ====================================

    query = """

        SELECT

            d.match_id,

            m.season,

            d.batting_team,

            m.venue,

            m.city,

            d.innings,

            SUM(d.total_run) AS total_runs,

            m.winner

        FROM deliveries d

        JOIN matches m

        ON d.match_id = m.match_id

        WHERE d.innings IN (1, 2)

    """

    values = []

    # ====================================
    # TEAM FILTER
    # ====================================

    if team:

        query += """

            AND d.batting_team = %s

        """

        values.append(team)

    # ====================================
    # SEASON FILTER
    # ====================================

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    limit, offset = get_pagination()

    # ====================================
    # GROUPING
    # ====================================

    query += """

        GROUP BY

            d.match_id,
            m.season,
            d.batting_team,
            m.venue,
            m.city,
            d.innings,
            m.winner

    """

    # ====================================
    # ORDERING
    # ====================================

    query += """

        ORDER BY

            total_runs ASC

        LIMIT %s
        OFFSET %s

    """

    rows = execute_query(

        query,

        tuple(values + [limit, offset])
    )

    # ====================================
    # NO DATA
    # ====================================

    if not rows:

        return error_response(

            "No data found",

            404
        )

    # ====================================
    # RESPONSE
    # ====================================

    totals = []

    for row in rows:

        totals.append({

            "match_id": row[0],

            "season": row[1],

            "team": normalize_team_name(
                row[2]
            ),

            "venue": row[3],

            "city": row[4],

            "innings": int(row[5]),

            "total_runs": int(row[6]),

            "winner": normalize_team_name(
                row[7]
            )
        })

    return success_response({

        "count": len(totals),

        "lowest_team_totals": totals
    })

# =========================================
# CLOSEST FINISHES
# =========================================

@matches_bp.route("/matches/closest-finishes")
def closest_finishes():

    # ====================================
    # QUERY PARAMS
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

            match_id,

            season,

            team1,

            team2,

            winner,

            venue,

            city,

            result_type,

            result_margin,

            super_over,

            match_date

        FROM matches

        WHERE

            (

                (result_type = 'runs'

                 AND result_margin <= 5)

                OR

                (result_type = 'wickets'

                 AND result_margin <= 2)

                OR

                super_over = TRUE

            )

    """

    values = []

    # ====================================
    # SEASON FILTER
    # ====================================

    if season:

        query += """

            AND season = %s

        """

        values.append(season)

    # ====================================
    # ORDERING
    # ====================================

    query += """

        ORDER BY

            result_margin ASC,

            match_date DESC

        LIMIT 20

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    # ====================================
    # NO DATA
    # ====================================

    if not rows:

        return error_response(

            "No data found",

            404
        )

    # ====================================
    # RESPONSE
    # ====================================

    matches = []

    for row in rows:

        matches.append({

            "match_id": row[0],

            "season": row[1],

            "team1": normalize_team_name(
                row[2]
            ),

            "team2": normalize_team_name(
                row[3]
            ),

            "winner": normalize_team_name(
                row[4]
            ),

            "venue": row[5],

            "city": row[6],

            "result_type": row[7],

            "result_margin": row[8],

            "super_over": row[9],

            "match_date": str(row[10])
        })

    return success_response({

        "count": len(matches),

        "closest_finishes": matches
    })

# =========================================
# SUPER OVER MATCHES
# =========================================

@matches_bp.route("/matches/super-over-matches")
def super_over_matches():

    # ====================================
    # QUERY PARAMS
    # ====================================

    season = request.args.get(

        "season",

        type=int
    )

    team = request.args.get("team")

    if team:

        team = normalize_team_name(team)

    # ====================================
    # BASE QUERY
    # ====================================

    query = """

        SELECT

            match_id,

            season,

            team1,

            team2,

            winner,

            venue,

            city,

            result_type,

            result_margin,

            match_date

        FROM matches

        WHERE super_over = TRUE

    """

    values = []

    # ====================================
    # TEAM FILTER
    # ====================================

    if team:

        query += """

            AND (

                team1 = %s

                OR

                team2 = %s

            )

        """

        values.extend([

            team,
            team
        ])

    # ====================================
    # SEASON FILTER
    # ====================================

    if season:

        query += """

            AND season = %s

        """

        values.append(season)

    # ====================================
    # ORDERING
    # ====================================

    query += """

        ORDER BY

            match_date DESC

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    # ====================================
    # NO DATA
    # ====================================

    if not rows:

        return error_response(

            "No data found",

            404
        )

    # ====================================
    # RESPONSE
    # ====================================

    matches = []

    for row in rows:

        matches.append({

            "match_id": row[0],

            "season": row[1],

            "team1": normalize_team_name(
                row[2]
            ),

            "team2": normalize_team_name(
                row[3]
            ),

            "winner": normalize_team_name(
                row[4]
            ),

            "venue": row[5],

            "city": row[6],

            "result_type": row[7],

            "result_margin": row[8],

            "match_date": str(row[9])
        })

    return success_response({

        "count": len(matches),

        "super_over_matches": matches
    })

# =========================================
# HIGHEST SUCCESSFUL CHASES
# =========================================

@matches_bp.route("/matches/highest-successful-chases")
def highest_successful_chases():

    season = request.args.get(

        "season",

        type=int
    )

    team = request.args.get("team")

    query = """

        WITH innings_totals AS (

            SELECT

                d.match_id,

                d.innings,

                d.batting_team,

                SUM(d.total_run) AS total_runs,

                COUNT(

                    DISTINCT CASE

                        WHEN w.player_out IS NOT NULL
                        THEN w.player_out

                    END

                ) AS wickets_lost

            FROM deliveries d

            LEFT JOIN wickets w

            ON d.delivery_key = w.delivery_key

            WHERE d.innings IN (1, 2)

            GROUP BY

                d.match_id,
                d.innings,
                d.batting_team

        )

        SELECT

            m.match_id,

            m.season,

            i2.batting_team,

            i1.total_runs + 1 AS target,

            i2.total_runs AS chased_score,

            10 - i2.wickets_lost AS wickets_left,

            m.venue,

            m.city,

            m.match_date,

            m.winner

        FROM innings_totals i1

        JOIN innings_totals i2

        ON i1.match_id = i2.match_id

        JOIN matches m

        ON m.match_id = i1.match_id

        WHERE

            i1.innings = 1

            AND i2.innings = 2

            AND i2.total_runs >= i1.total_runs + 1

            AND m.winner = i2.batting_team

    """

    values = []

    # =====================================
    # OPTIONAL FILTERS
    # =====================================

    if season:

        query += """

            AND m.season = %s

        """

        values.append(season)

    if team:

        query += """

            AND i2.batting_team = %s

        """

        values.append(team)

    limit, offset = get_pagination()

    # =====================================
    # ORDERING
    # =====================================

    query += """

        ORDER BY

            chased_score DESC,

            wickets_left DESC

        LIMIT %s
        OFFSET %s

    """

    rows = execute_query(

        query,

        tuple(values + [limit, offset])
    )

    # =====================================
    # NO DATA
    # =====================================

    if not rows:

        return error_response(

            "No data found",

            404
        )

    # =====================================
    # RESPONSE
    # =====================================

    chases = []

    for row in rows:

        chases.append({

            "match_id": row[0],

            "season": row[1],

            "team": row[2],

            "target": int(row[3]),

            "chased_score": int(row[4]),

            "wickets_left": int(row[5]),

            "venue": row[6],

            "city": row[7],

            "match_date": str(row[8]),

            "winner": row[9]
        })

    return success_response({

        "count": len(chases),

        "highest_successful_chases": chases
    })
