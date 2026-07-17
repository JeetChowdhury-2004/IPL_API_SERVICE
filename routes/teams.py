from flask import Blueprint
from flask import request

from team_name_normalization import (
    normalize_team_name
)

from database.database import (
    get_connection
)

from utils.api_response import (
    success_response,
    error_response
)

from utils.pagination import get_pagination


DEFAULT_TEAM_SEARCH_LIMIT = 10

MAX_TEAM_SEARCH_LIMIT = 50

TEAM_NAME_CASE_SQL = """
    CASE
        WHEN {column} IN ('Delhi Daredevils', 'Delhi Capitals')
        THEN 'Delhi Capitals'
        WHEN {column} IN ('Kings XI Punjab', 'Punjab Kings')
        THEN 'Punjab Kings'
        WHEN {column} IN ('Rising Pune Supergiant', 'Rising Pune Supergiants')
        THEN 'Rising Pune Supergiants'
        ELSE {column}
    END
"""


def normalized_team_sql(column):

    return TEAM_NAME_CASE_SQL.format(column=column)


# =========================================
# BLUEPRINT
# =========================================

teams_bp = Blueprint(

    "teams",

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
# TEAM SEARCH
# =========================================

@teams_bp.route("/teams/search")
def search_teams():

    team_name = request.args.get(

        "team_name",

        ""
    ).strip()

    limit = request.args.get(

        "limit",

        default=DEFAULT_TEAM_SEARCH_LIMIT,

        type=int
    )

    if not team_name:

        return error_response(

            "team_name is required",

            400
        )

    if limit is None or limit <= 0:

        limit = DEFAULT_TEAM_SEARCH_LIMIT

    if limit > MAX_TEAM_SEARCH_LIMIT:

        limit = MAX_TEAM_SEARCH_LIMIT

    search_pattern = f"%{team_name}%"

    prefix_pattern = f"{team_name}%"

    sql = """

        WITH team_rows AS (

            SELECT
                team1 AS team,
                match_id
            FROM matches
            WHERE team1 IS NOT NULL

            UNION ALL

            SELECT
                team2 AS team,
                match_id
            FROM matches
            WHERE team2 IS NOT NULL
        )

        SELECT
            team,
            COUNT(DISTINCT match_id) AS matches
        FROM team_rows
        WHERE team ILIKE %s
        GROUP BY team
        ORDER BY
            CASE
                WHEN LOWER(team) = LOWER(%s) THEN 0
                WHEN team ILIKE %s THEN 1
                ELSE 2
            END,
            team ASC
        LIMIT %s

    """

    rows = execute_query(

        sql,

        (
            search_pattern,
            team_name,
            prefix_pattern,
            limit
        )
    )

    teams = []

    for row in rows:

        team = row[0]

        teams.append({

            "team": team,

            "normalized_team": normalize_team_name(team),

            "matches": int(row[1])
        })

    return success_response({

        "team_name": team_name,

        "count": len(teams),

        "teams": teams
    })


# =========================================
# MOST WINS
# =========================================

@teams_bp.route("/teams/most-wins")
def most_wins():

    season = request.args.get(

        "season",

        type=int
    )

    winner_team = normalized_team_sql("winner")

    query = f"""

        SELECT

            {winner_team} AS team,

            COUNT(*) AS wins

        FROM matches

        WHERE winner IS NOT NULL

    """

    values = []

    if season:

        query += """

            AND season = %s

        """

        values.append(season)

    limit, offset = get_pagination()

    query += """

        GROUP BY team

        ORDER BY wins DESC

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

    teams = []

    for row in rows:

        teams.append({

            "team": normalize_team_name(
                row[0]
            ),

            "wins": int(row[1])
        })

    return success_response({

        "count": len(teams),

        "teams": teams
    })


# =========================================
# WIN PERCENTAGE
# =========================================

@teams_bp.route("/teams/win-percentage")
def win_percentage():

    season = request.args.get(

        "season",

        type=int
    )

    team = request.args.get("team")

    if team:

        team = normalize_team_name(team)

    team1_name = normalized_team_sql("team1")

    team2_name = normalized_team_sql("team2")

    winner_name = normalized_team_sql("winner")

    query = f"""

        SELECT

            team_name,

            SUM(matches_played) AS matches,

            SUM(matches_won) AS wins,

            ROUND(

                (
                    SUM(matches_won) * 100.0
                )

                /

                NULLIF(
                    SUM(matches_played),
                    0
                ),

                2

            ) AS win_percentage

        FROM (

            SELECT

                {team1_name} AS team_name,

                COUNT(*) AS matches_played,

                SUM(

                    CASE

                        WHEN {winner_name} = {team1_name}
                        THEN 1

                        ELSE 0

                    END

                ) AS matches_won

            FROM matches

            WHERE winner IS NOT NULL

    """

    values = []

    if season:

        query += """

            AND season = %s

        """

        values.append(season)

    query += """

            GROUP BY team1

            UNION ALL

            SELECT

                {team2_name} AS team_name,

                COUNT(*) AS matches_played,

                SUM(

                    CASE

                        WHEN {winner_name} = {team2_name}
                        THEN 1

                        ELSE 0

                    END

                ) AS matches_won

            FROM matches

            WHERE winner IS NOT NULL

    """

    if season:

        query += """

            AND season = %s

        """

        values.append(season)

    query += """

            GROUP BY team2

        ) AS combined

        WHERE 1=1

    """

    if team:

        query += """

            AND team_name = %s

        """

        values.append(team)

    limit, offset = get_pagination()

    query += """

        GROUP BY team_name

    """

    if not team and not season:

        query += """

            HAVING SUM(matches_played) >= 20

        """

    elif season:

        query += """

            HAVING SUM(matches_played) >= 10

        """

    query += """

        ORDER BY win_percentage DESC

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

    teams = []

    for row in rows:

        teams.append({

            "team": normalize_team_name(
                row[0]
            ),

            "matches": int(row[1]),

            "wins": int(row[2]),

            "win_percentage": float(row[3])
        })

    return success_response({

        "count": len(teams),

        "teams": teams
    })


# =========================================
# PLAYOFF RECORD
# =========================================

@teams_bp.route("/teams/playoff-record")
def playoff_record():

    season = request.args.get(

        "season",

        type=int
    )

    team = request.args.get("team")

    if team:

        team = normalize_team_name(team)

    team1_name = normalized_team_sql("team1")

    team2_name = normalized_team_sql("team2")

    winner_name = normalized_team_sql("winner")

    query = f"""

        SELECT

            team_name,

            COUNT(*) AS matches,

            SUM(

                CASE

                    WHEN normalized_winner = team_name
                    THEN 1

                    ELSE 0

                END

            ) AS wins,

            ROUND(

                (
                    SUM(

                        CASE

                            WHEN normalized_winner = team_name
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

            ) AS win_percentage

        FROM (

            SELECT

                {team1_name} AS team_name,

                season,

                {winner_name} AS normalized_winner

            FROM matches

            WHERE is_playoff = TRUE

            UNION ALL

            SELECT

                {team2_name} AS team_name,

                season,

                {winner_name} AS normalized_winner

            FROM matches

            WHERE is_playoff = TRUE

        ) AS playoff_matches

        WHERE 1=1

    """

    values = []

    if season:

        query += """

            AND season = %s

        """

        values.append(season)

    if team:

        query += """

            AND team_name = %s

        """

        values.append(team)

    limit, offset = get_pagination()

    query += """

        GROUP BY team_name

    """

    if not team and not season:

        query += """

            HAVING COUNT(*) >= 5

        """

    query += """

        ORDER BY

            win_percentage DESC,

            wins DESC

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

    teams = []

    for row in rows:

        teams.append({

            "team": normalize_team_name(
                row[0]
            ),

            "matches": int(row[1]),

            "wins": int(row[2]),

            "win_percentage": float(row[3])
        })

    return success_response({

        "count": len(teams),

        "teams": teams
    })


# =========================================
# FINALS RECORD
# =========================================

@teams_bp.route("/teams/finals-record")
def finals_record():

    season = request.args.get(

        "season",

        type=int
    )

    team = request.args.get("team")

    if team:

        team = normalize_team_name(team)

    team1_name = normalized_team_sql("team1")

    team2_name = normalized_team_sql("team2")

    winner_name = normalized_team_sql("winner")

    query = f"""

        SELECT

            team_name,

            COUNT(*) AS finals_played,

            SUM(

                CASE

                    WHEN normalized_winner = team_name
                    THEN 1

                    ELSE 0

                END

            ) AS finals_won,

            ROUND(

                (
                    SUM(

                        CASE

                            WHEN normalized_winner = team_name
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

            ) AS finals_win_percentage

        FROM (

            SELECT

                season,

                {team1_name} AS team_name,

                {winner_name} AS normalized_winner

            FROM matches

            WHERE LOWER(
                TRIM(match_stage)
            ) = 'final'

            UNION ALL

            SELECT

                season,

                {team2_name} AS team_name,

                {winner_name} AS normalized_winner

            FROM matches

            WHERE LOWER(
                TRIM(match_stage)
            ) = 'final'

        ) AS finals

        WHERE 1=1

    """

    values = []

    if season:

        query += """

            AND season = %s

        """

        values.append(season)

    if team:

        query += """

            AND team_name = %s

        """

        values.append(team)

    query += """

        GROUP BY team_name

        ORDER BY

            finals_won DESC,

            finals_played DESC,

            finals_win_percentage DESC

    """

    rows = execute_query(

        query,

        tuple(values)
    )

    if not rows:

        return error_response(

            "No data found",

            404
        )

    teams = []

    for row in rows:

        teams.append({

            "team": row[0],

            "finals_played": int(row[1]),

            "finals_won": int(row[2]),

            "finals_win_percentage": float(row[3])
        })

    return success_response({

        "count": len(teams),

        "teams": teams
    })
# =========================================
# CHASING RECORD
# =========================================

@teams_bp.route("/teams/chasing-record")
def chasing_record():

    # ====================================
    # QUERY PARAMS
    # ====================================

    team = request.args.get("team")

    season = request.args.get(

        "season",

        type=int
    )

    if team:

        team = normalize_team_name(team)

    # ====================================
    # BASE QUERY
    # ====================================

    batting_team = normalized_team_sql("batting_team")

    winner_name = normalized_team_sql("winner")

    query = f"""

        WITH innings_teams AS (

            SELECT DISTINCT
                d.match_id,
                d.innings,
                {batting_team} AS batting_team

            FROM deliveries d

            WHERE d.innings IN (1, 2)
        )

        SELECT

            chasing_team,

            COUNT(*) AS matches_chased,

            SUM(

                CASE

                    WHEN normalized_winner = chasing_team
                    THEN 1

                    ELSE 0

                END

            ) AS successful_chases,

            SUM(

                CASE

                    WHEN normalized_winner IS NOT NULL
                    AND normalized_winner != chasing_team
                    THEN 1

                    ELSE 0

                END

            ) AS failed_chases,

            ROUND(

                (
                    SUM(

                        CASE

                            WHEN normalized_winner = chasing_team
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

            ) AS chasing_win_percentage

        FROM (

            SELECT

                i2.batting_team AS chasing_team,

                {winner_name} AS normalized_winner,

                m.season

            FROM matches m

            JOIN innings_teams i2

            ON m.match_id = i2.match_id

            WHERE m.target_runs IS NOT NULL

            AND i2.innings = 2

        ) AS chasing_matches

        WHERE 1=1

    """

    values = []

    # ====================================
    # TEAM FILTER
    # ====================================

    if team:

        query += """

            AND chasing_team = %s

        """

        values.append(team)

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

        GROUP BY chasing_team

    """

    # ====================================
    # SMART HAVING
    # ====================================

    if not team and not season:

        query += """

            HAVING COUNT(*) >= 20

        """

    elif season:

        query += """

            HAVING COUNT(*) >= 5

        """

    limit, offset = get_pagination()

    # ====================================
    # ORDERING
    # ====================================

    query += """

        ORDER BY

            chasing_win_percentage DESC,

            successful_chases DESC

        LIMIT %s
        OFFSET %s

    """

    values.extend([limit, offset])

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

    teams = []

    for row in rows:

        teams.append({

            "team": normalize_team_name(
                row[0]
            ),

            "matches_chased": int(row[1]),

            "successful_chases": int(row[2]),

            "failed_chases": int(row[3]),

            "chasing_win_percentage": float(row[4])
        })

    return success_response({

        "count": len(teams),

        "teams": teams
    })

# =========================================
# DEFENDING RECORD
# =========================================

@teams_bp.route("/teams/defending-record")
def defending_record():

    # ====================================
    # QUERY PARAMS
    # ====================================

    team = request.args.get("team")

    season = request.args.get(

        "season",

        type=int
    )

    if team:

        team = normalize_team_name(team)

    # ====================================
    # BASE QUERY
    # ====================================

    batting_team = normalized_team_sql("batting_team")

    winner_name = normalized_team_sql("winner")

    query = f"""

        WITH innings_teams AS (

            SELECT DISTINCT
                d.match_id,
                d.innings,
                {batting_team} AS batting_team

            FROM deliveries d

            WHERE d.innings IN (1, 2)
        )

        SELECT

            defending_team,

            COUNT(*) AS matches_defended,

            SUM(

                CASE

                    WHEN normalized_winner = defending_team
                    THEN 1

                    ELSE 0

                END

            ) AS successful_defends,

            SUM(

                CASE

                    WHEN normalized_winner IS NOT NULL
                    AND normalized_winner != defending_team
                    THEN 1

                    ELSE 0

                END

            ) AS failed_defends,

            ROUND(

                (
                    SUM(

                        CASE

                            WHEN normalized_winner = defending_team
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

            ) AS defending_win_percentage

        FROM (

            SELECT

                i1.batting_team AS defending_team,

                {winner_name} AS normalized_winner,

                m.season

            FROM matches m

            JOIN innings_teams i1

            ON m.match_id = i1.match_id

            WHERE m.target_runs IS NOT NULL

            AND i1.innings = 1

        ) AS defending_matches

        WHERE 1=1

    """

    values = []

    # ====================================
    # TEAM FILTER
    # ====================================

    if team:

        query += """

            AND defending_team = %s

        """

        values.append(team)

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

        GROUP BY defending_team

    """

    # ====================================
    # SMART HAVING
    # ====================================

    if not team and not season:

        query += """

            HAVING COUNT(*) >= 20

        """

    elif season:

        query += """

            HAVING COUNT(*) >= 5

        """

    limit, offset = get_pagination()

    # ====================================
    # ORDERING
    # ====================================

    query += """

        ORDER BY

            defending_win_percentage DESC,

            successful_defends DESC

        LIMIT %s
        OFFSET %s

    """

    values.extend([limit, offset])

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

    teams = []

    for row in rows:

        teams.append({

            "team": normalize_team_name(
                row[0]
            ),

            "matches_defended": int(row[1]),

            "successful_defends": int(row[2]),

            "failed_defends": int(row[3]),

            "defending_win_percentage": float(row[4])
        })

    return success_response({

        "count": len(teams),

        "teams": teams
    })
