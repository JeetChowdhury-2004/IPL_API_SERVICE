import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from database.database import get_connection


def load_available_data():
    conn = None

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

        matches_df = pd.read_sql(
            """
            SELECT
                season,
                city,
                venue,
                team1,
                team2
            FROM matches
            """,
            conn
        )

        deliveries_df = pd.read_sql(
            """
            SELECT
                batter,
                bowler
            FROM deliveries
            """,
            conn
        )

        teams = sorted(
            set(matches_df["team1"].dropna().unique()).union(
                set(matches_df["team2"].dropna().unique())
            )
        )

        return {
            "database_available": True,
            "error_message": None,
            "teams": teams,
            "seasons": sorted(
                matches_df["season"].dropna().astype(int).unique().tolist()
            ),
            "cities": sorted(matches_df["city"].dropna().unique().tolist()),
            "venues": sorted(matches_df["venue"].dropna().unique().tolist()),
            "batters": sorted(
                deliveries_df["batter"].dropna().unique().tolist()
            ),
            "bowlers": sorted(
                deliveries_df["bowler"].dropna().unique().tolist()
            )
        }

    except Exception as exc:
        print("Available data could not be loaded:", exc)
        return empty_data

    finally:
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
