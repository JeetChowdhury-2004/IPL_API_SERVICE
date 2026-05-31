from pathlib import Path
import sys
import os
import json
import pandas as pd

# =========================================
# PROJECT ROOT
# =========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(0, str(PROJECT_ROOT))

from database.database import get_connection
from database.insert_matches import insert_match


# =========================================
# IPL PLAYOFF STAGE MAP
# =========================================

IPL_STAGE_MAP = {

    '2007/08': [
        "Semi Final 1",
        "Semi Final 2",
        "Final"
    ],

    '2009': [
        "Semi Final 1",
        "Semi Final 2",
        "Final"
    ],

    '2009/10': [
        "Semi Final 1",
        "Semi Final 2",
        "3rd Place",
        "Final"
    ],

    '2011': [
        "Qualifier 1",
        "Eliminator",
        "Qualifier 2",
        "Final"
    ],

    '2012': [
        "Qualifier 1",
        "Eliminator",
        "Qualifier 2",
        "Final"
    ],

    '2013': [
        "Qualifier 1",
        "Eliminator",
        "Qualifier 2",
        "Final"
    ],

    '2014': [
        "Qualifier 1",
        "Eliminator",
        "Qualifier 2",
        "Final"
    ],

    '2015': [
        "Qualifier 1",
        "Eliminator",
        "Qualifier 2",
        "Final"
    ],

    '2016': [
        "Qualifier 1",
        "Eliminator",
        "Qualifier 2",
        "Final"
    ],

    '2017': [
        "Qualifier 1",
        "Eliminator",
        "Qualifier 2",
        "Final"
    ],

    '2018': [
        "Qualifier 1",
        "Eliminator",
        "Qualifier 2",
        "Final"
    ],

    '2019': [
        "Qualifier 1",
        "Eliminator",
        "Qualifier 2",
        "Final"
    ],

    '2020/21': [
        "Qualifier 1",
        "Eliminator",
        "Qualifier 2",
        "Final"
    ],

    '2021': [
        "Qualifier 1",
        "Eliminator",
        "Qualifier 2",
        "Final"
    ],

    '2022': [
        "Qualifier 1",
        "Eliminator",
        "Qualifier 2",
        "Final"
    ],

    '2023': [
        "Qualifier 1",
        "Eliminator",
        "Qualifier 2",
        "Final"
    ],

    '2024': [
        "Qualifier 1",
        "Eliminator",
        "Qualifier 2",
        "Final"
    ]
}


# =========================================
# CLEAN SEASON
# =========================================

def clean_season(season):

    season = str(season)

    if "/" in season:

        first_year = int(season.split("/")[0])

        if first_year == 2020:
            return 2020

        second_part = season.split("/")[1]

        if len(second_part) == 2:

            century = str(first_year)[:2]

            return int(century + second_part)

        return int(second_part)

    return int(season)


# =========================================
# CLEAN PLAYOFF MAP
# =========================================

CLEAN_STAGE_MAP = {

    clean_season(season): stages

    for season, stages in IPL_STAGE_MAP.items()
}


# =========================================
# LOAD ALL MATCHES
# =========================================

folder = PROJECT_ROOT / "raw_data" / "json_matches"

all_matches = []

files = [

    f for f in os.listdir(folder)

    if f.endswith(".json")
]

print(f"Total files: {len(files)}")


# =========================================
# PARSE JSON FILES
# =========================================

for file in files:

    path = os.path.join(folder, file)

    with open(path, "r", encoding="utf-8") as f:

        data = json.load(f)

    info = data.get("info", {})

    teams = info.get("teams", [])

    team1 = teams[0] if len(teams) > 0 else None
    team2 = teams[1] if len(teams) > 1 else None

    season = clean_season(
        info.get("season")
    )

    outcome = info.get("outcome", {})

    winner = outcome.get("winner")

    result_type = None
    result_margin = None

    if "by" in outcome:

        if "runs" in outcome["by"]:

            result_type = "runs"

            result_margin = outcome["by"]["runs"]

        elif "wickets" in outcome["by"]:

            result_type = "wickets"

            result_margin = outcome["by"]["wickets"]

    toss = info.get("toss", {})

    toss_winner = toss.get("winner")

    toss_decision = toss.get("decision")

    umpires = info.get("officials", {}).get("umpires", [])

    umpire1 = umpires[0] if len(umpires) > 0 else None
    umpire2 = umpires[1] if len(umpires) > 1 else None

    dates = info.get("dates", [])

    innings = data.get("innings", [])

    target_runs = None
    target_overs = None

    if len(innings) > 1:

        target_info = innings[1].get("target", {})

        target_runs = target_info.get("runs")

        target_overs = target_info.get("overs")

    match_row = {

        "match_id": int(
            file.replace(".json", "")
        ),

        "season": season,

        "match_date": dates[0] if dates else None,

        "city": info.get("city"),

        "venue": info.get("venue"),

        "team1": team1,

        "team2": team2,

        "toss_winner": toss_winner,

        "toss_decision": toss_decision,

        "winner": winner,

        "player_of_match": (
            info.get(
                "player_of_match",
                [None]
            )[0]
        ),

        "result_type": result_type,

        "result_margin": result_margin,

        "target_runs": target_runs,

        "target_overs": target_overs,

        "super_over": len(innings) > 2,

        # DEFAULT VALUES
        "match_stage": "League",

        "is_playoff": False,

        "umpire1": umpire1,

        "umpire2": umpire2
    }

    all_matches.append(match_row)


# =========================================
# CREATE DATAFRAME
# =========================================

df = pd.DataFrame(all_matches)


# =========================================
# FIX DATE COLUMN
# =========================================

df["match_date"] = pd.to_datetime(
    df["match_date"]
)


# =========================================
# SORT MATCHES
# =========================================

df = df.sort_values(

    by="match_date",

    ascending=True

).reset_index(drop=True)


# =========================================
# ASSIGN PLAYOFF STAGES
# =========================================

for season, stage_names in CLEAN_STAGE_MAP.items():

    season_df = df[
        df["season"] == season
    ]

    if season_df.empty:
        continue

    playoff_count = len(stage_names)

    playoff_matches = season_df.tail(
        playoff_count
    )

    for idx, stage in zip(

        playoff_matches.index,

        stage_names
    ):

        df.loc[idx, "match_stage"] = stage

        df.loc[idx, "is_playoff"] = True


# =========================================
# DATABASE INSERT
# =========================================

conn = get_connection()

success_count = 0

error_count = 0


for _, row in df.iterrows():

    # ====================================
    # CONVERT NaN -> None
    # ====================================

    row = row.where(
        pd.notnull(row),
        None
    )

    try:

        insert_match(

            row.to_dict(),

            conn=conn
        )

        success_count += 1

    except Exception as e:

        error_count += 1

        print("\n=================================")
        print("ERROR INSERTING MATCH")
        print("=================================\n")

        print(row)

        print("\nERROR:\n")

        print(e)

        print("\n=================================\n")


# =========================================
# COMMIT & CLOSE
# =========================================

conn.commit()

conn.close()


# =========================================
# FINAL STATUS
# =========================================

print("\n=================================")
print("MATCH LOADING COMPLETED")
print("=================================")

print(f"Successful Inserts : {success_count}")

print(f"Failed Inserts     : {error_count}")

print("=================================\n")