import os
import sys

from flask import Blueprint
from flask import request

# Ensure the project root is on sys.path when this module is executed directly.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database.database import get_connection


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

    # =====================================
    # QUERY PARAMS
    # =====================================

    limit = request.args.get(
        "limit",
        default=10,
        type=int
    )

    # Safety
    if limit <= 0:
        limit = 10

    if limit > 100:
        limit = 100

    # =====================================
    # SQL QUERY
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

    """

    rows = execute_query(
        query,
        (limit,)
    )

    # =====================================
    # BUILD RESPONSE
    # =====================================

    matches_list = []

    for row in rows:

        match = {

            "match_id": row[0],

            "season": row[1],

            "city": row[2],

            "venue": row[3],

            "teams": [
                row[4],
                row[5]
            ],

            "toss": {

                "winner": row[6],
                "decision": row[7]
            },

            "winner": row[8],

            "result": {

                "type": row[9],
                "margin": row[10]
            },

            "player_of_match": row[11],

            "match_stage": row[12],

            "match_date": str(row[13])
        }

        matches_list.append(match)

    # =====================================
    # RESPONSE
    # =====================================

    return {

        "count": len(matches_list),

        "matches": matches_list
    }


# =========================================
# MATCHES BY SEASON
# =========================================

@matches_bp.route("/matches/season/<int:season>")
def get_match_by_season(season):

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

    """

    rows = execute_query(
        query,
        (season,)
    )

    matches_list = []

    for row in rows:

        match = {

            "match_id": row[0],

            "season": row[1],

            "city": row[2],

            "venue": row[3],

            "teams": [
                row[4],
                row[5]
            ],

            "toss": {

                "winner": row[6],
                "decision": row[7]
            },

            "winner": row[8],

            "result": {

                "type": row[9],
                "margin": row[10]
            },

            "player_of_match": row[11],

            "match_stage": row[12],

            "match_date": str(row[13])
        }

        matches_list.append(match)

    return {

        "season": season,

        "count": len(matches_list),

        "matches": matches_list
    }


# =========================================
# FILTER MATCHES
# =========================================

@matches_bp.route("/matches/filter")
def filter_matches():

    # ====================================
    # QUERY PARAMETERS
    # ====================================

    team = request.args.get("team")

    city = request.args.get("city")

    winner = request.args.get("winner")

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
            city,
            venue,
            team1,
            team2,
            winner

        FROM matches

        WHERE 1=1

    """

    values = []

    # ====================================
    # FILTERS
    # ====================================

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

    # ====================================
    # RESPONSE
    # ====================================

    matches = []

    for row in rows:

        matches.append({

            "match_id": row[0],

            "season": row[1],

            "city": row[2],

            "venue": row[3],

            "team1": row[4],

            "team2": row[5],

            "winner": row[6]
        })

    return {

        "count": len(matches),

        "matches": matches
    }


# =========================================
# HEAD TO HEAD
# =========================================

@matches_bp.route("/matches/head-to-head")
def head_to_head():

    # ====================================
    # QUERY PARAMETERS
    # ====================================

    team1 = request.args.get("team1")

    team2 = request.args.get("team2")

    # ====================================
    # VALIDATION
    # ====================================

    if not team1 or not team2:

        return {
            "error": "team1 and team2 are required"
        }, 400

    if team1 == team2:

        return {
            "error": "Both teams cannot be same"
        }, 400

    # ====================================
    # SQL QUERY
    # ====================================

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

    # ====================================
    # SUMMARY
    # ====================================

    total_matches = len(rows)

    team1_wins = 0

    team2_wins = 0

    no_result = 0

    matches = []

    # ====================================
    # PROCESS ROWS
    # ====================================

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
                row[4],
                row[5]
            ],

            "winner": row[6],

            "match_date": str(row[7])
        })

    return {

        "summary": {

            "team1": team1,

            "team2": team2,

            "total_matches": total_matches,

            "team1_wins": team1_wins,

            "team2_wins": team2_wins,

            "no_result": no_result
        },

        "matches": matches
    }


# =========================================
# TOSS IMPACT
# =========================================

@matches_bp.route("/matches/toss-impact")
def toss_impact():

    # ====================================
    # QUERY PARAMETERS
    # ====================================

    season = request.args.get(
        "season",
        type=int
    )

    team = request.args.get("team")

    city = request.args.get("city")

    venue = request.args.get("venue")

    toss_decision = request.args.get(
        "toss_decision"
    )

    # ====================================
    # BASE QUERY
    # ====================================

    query = """

        SELECT
            toss_winner,
            winner

        FROM matches

        WHERE 1=1

    """

    values = []

    # ====================================
    # FILTERS
    # ====================================

    if season:

        query += " AND season = %s "
        values.append(season)

    if team:

        query += """

            AND (
                team1 = %s
                OR team2 = %s
            )

        """

        values.extend([team, team])

    if city:

        query += " AND city = %s "
        values.append(city)

    if venue:

        query += " AND venue = %s "
        values.append(venue)

    if toss_decision:

        query += " AND toss_decision = %s "
        values.append(toss_decision)

    rows = execute_query(
        query,
        tuple(values)
    )

    # ====================================
    # ANALYTICS
    # ====================================

    total_matches = len(rows)

    if total_matches == 0:

        return {

            "message": "No matches found",

            "total_matches": 0
        }

    toss_winner_wins = 0

    toss_winner_losses = 0

    # ====================================
    # CALCULATE
    # ====================================

    for row in rows:

        toss_winner = row[0]

        winner = row[1]

        if toss_winner == winner:

            toss_winner_wins += 1

        else:

            toss_winner_losses += 1

    # ====================================
    # WIN PERCENTAGE
    # ====================================

    win_percentage = (

        toss_winner_wins / total_matches

    ) * 100

    return {

        "filters": {

            "season": season,

            "team": team,

            "city": city,

            "venue": venue,

            "toss_decision": toss_decision
        },

        "total_matches": total_matches,

        "toss_winner_wins": toss_winner_wins,

        "toss_winner_losses": toss_winner_losses,

        "win_percentage": round(
            win_percentage,
            2
        )
    }


# =========================================
# ALL TITLE WINNERS
# =========================================

@matches_bp.route("/matches/title-winners")
def get_all_title_winners():

    query = """

        SELECT DISTINCT winner

        FROM matches

        WHERE match_stage = 'Final'

        AND winner IS NOT NULL

        ORDER BY winner ASC

    """

    rows = execute_query(query)

    teams = [

        row[0]

        for row in rows
    ]

    return {

        "count": len(teams),

        "teams": teams
    }

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

        WHERE match_stage = 'Final'

        AND winner IS NOT NULL

        GROUP BY winner

        ORDER BY titles DESC,
                 winner ASC

    """

    rows = execute_query(query)

    teams = []

    for row in rows:

        teams.append({

            "team": row[0],

            "titles": row[1]
        })

    return {

        "count": len(teams),

        "title_counts": teams
    }

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

    # ====================================
    # NO DATA CHECK
    # ====================================

    if not rows:

        return {
            "message": "No data found"
        }

    # ====================================
    # TOP TEAM
    # ====================================

    top_team = rows[0][0]

    total_wins = rows[0][1]

    # ====================================
    # TOTAL MATCHES PLAYED
    # ====================================

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

    # ====================================
    # WIN PERCENTAGE
    # ====================================

    win_percentage = (

        total_wins / total_matches

    ) * 100

    # ====================================
    # RESPONSE
    # ====================================

    return {

        "team": top_team,

        "total_matches": total_matches,

        "wins": total_wins,

        "losses": losses,

        "win_percentage": round(
            win_percentage,
            2
        )
    }

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

    teams = [

        row[0]

        for row in rows

        if row[0] is not None
    ]

    return {

        "count": len(teams),

        "teams": teams
    }