import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from database.database import get_connection


def fetch_column(cursor, query):
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall() if row[0] is not None]


def load_available_data():
    conn = None
    cursor = None

    empty_data = {
        "database_available": False,
        "error_message": "Database unavailable. Check PostgreSQL and .env credentials.",
        "teams": [],
        "seasons": [],
        "cities": [],
        "venues": [],
        "batters": [],
        "bowlers": []
    }

    try:
        conn = get_connection()
        cursor = conn.cursor()

        teams = fetch_column(
            cursor,
            """
            SELECT DISTINCT team
            FROM (
                SELECT team1 AS team
                FROM matches
                WHERE team1 IS NOT NULL

                UNION

                SELECT team2 AS team
                FROM matches
                WHERE team2 IS NOT NULL
            ) teams
            ORDER BY team
            """
        )

        seasons = fetch_column(
            cursor,
            """
            SELECT DISTINCT season
            FROM matches
            WHERE season IS NOT NULL
            ORDER BY season
            """
        )

        cities = fetch_column(
            cursor,
            """
            SELECT DISTINCT city
            FROM matches
            WHERE city IS NOT NULL
            ORDER BY city
            """
        )

        venues = fetch_column(
            cursor,
            """
            SELECT DISTINCT venue
            FROM matches
            WHERE venue IS NOT NULL
            ORDER BY venue
            """
        )

        batters = fetch_column(
            cursor,
            """
            SELECT DISTINCT batter
            FROM deliveries
            WHERE batter IS NOT NULL
            ORDER BY batter
            """
        )

        bowlers = fetch_column(
            cursor,
            """
            SELECT DISTINCT bowler
            FROM deliveries
            WHERE bowler IS NOT NULL
            ORDER BY bowler
            """
        )

        return {
            "database_available": True,
            "error_message": None,
            "teams": teams,
            "seasons": [int(season) for season in seasons],
            "cities": cities,
            "venues": venues,
            "batters": batters,
            "bowlers": bowlers
        }

    except Exception as exc:
        print("Available data could not be loaded:", exc)
        return empty_data

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


TEAMS = []
SEASONS = []
CITIES = []
VENUES = []
BATTERS = []
BOWLERS = []
ALL_AVAILABLE_DATA = {
    "teams": TEAMS,
    "seasons": SEASONS,
    "cities": CITIES,
    "venues": VENUES,
    "batters": BATTERS,
    "bowlers": BOWLERS
}


if __name__ == "__main__":
    ALL_AVAILABLE_DATA = load_available_data()
    TEAMS = ALL_AVAILABLE_DATA["teams"]
    SEASONS = ALL_AVAILABLE_DATA["seasons"]
    CITIES = ALL_AVAILABLE_DATA["cities"]
    VENUES = ALL_AVAILABLE_DATA["venues"]
    BATTERS = ALL_AVAILABLE_DATA["batters"]
    BOWLERS = ALL_AVAILABLE_DATA["bowlers"]

    print("\n================================")
    print("AVAILABLE IPL DATA")
    print("================================\n")
    print(f"Teams   : {len(TEAMS)}")
    print(f"Seasons : {len(SEASONS)}")
    print(f"Cities  : {len(CITIES)}")
    print(f"Venues  : {len(VENUES)}")
    print(f"Batters : {len(BATTERS)}")
    print(f"Bowlers : {len(BOWLERS)}")
    print("\n================================\n")
