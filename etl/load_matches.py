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

# =========================================
# IMPORTS
# =========================================

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
    ],

    '2025': [
        "Qualifier 1",
        "Eliminator",
        "Qualifier 2",
        "Final"
    ]
}

# =========================================
# AUTO FUTURE IPL SEASONS
# =========================================

CURRENT_YEAR = 2100

for year in range(2026, CURRENT_YEAR + 1):

    IPL_STAGE_MAP[str(year)] = [

        "Qualifier 1",

        "Eliminator",

        "Qualifier 2",

        "Final"
    ]

# =========================================
# CLEAN SEASON
# =========================================

def clean_season(season):

    season = str(season)

    if season == "2007/08":

        return 2008

    if season == "2009/10":

        return 2010

    if season == "2020/21":

        return 2020

    return int(season)

# =========================================
# CLEAN PLAYOFF MAP
# =========================================

CLEAN_STAGE_MAP = {

    clean_season(season): stages

    for season, stages in IPL_STAGE_MAP.items()
}

# =========================================
# JSON FILE HELPER
# =========================================

def get_json_files(folder):

    return [

        f for f in os.listdir(folder)

        if f.endswith(".json")
    ]

# =========================================
# LOAD MATCHES
# =========================================

def load_matches(files_to_process=None):

    # =====================================
    # FOLDER
    # =====================================

    folder = (

        PROJECT_ROOT
        / "raw_data"
        / "json_matches"
    )

    # =====================================
    # FILES
    # =====================================

    if files_to_process:

        files = files_to_process

    else:

        files = get_json_files(folder)

    print(

        f"Total files found: "
        f"{len(files)}"
    )

    # =====================================
    # STORE MATCHES
    # =====================================

    all_matches = []

    # =====================================
    # PARSE JSON FILES
    # =====================================

    for file in files:

        # =================================
        # SAFE FILENAME CHECK
        # =================================

        filename = file.replace(

            ".json",
            ""
        )

        if not filename.isdigit():

            print(

                f"Skipping invalid file: "
                f"{file}"
            )

            continue

        path = os.path.join(

            folder,
            file
        )

        with open(

            path,
            "r",
            encoding="utf-8"

        ) as f:

            data = json.load(f)

        info = data.get(
            "info",
            {}
        )

        teams = info.get(
            "teams",
            []
        )

        team1 = (

            teams[0]

            if len(teams) > 0

            else None
        )

        team2 = (

            teams[1]

            if len(teams) > 1

            else None
        )

        season = clean_season(

            info.get("season")
        )

        # =================================
        # OUTCOME
        # =================================

        outcome = info.get(
            "outcome",
            {}
        )

        innings = data.get(
            "innings",
            []
        )

        # =================================
        # DEBUG SUPER OVER
        # =================================

        if len(innings) > 2:

            print("\n================================")

            print("SUPER OVER MATCH")

            print("FILE:", file)

            print("OUTCOME:")

            print(

                json.dumps(
                    outcome,
                    indent=4
                )
            )

            print("================================\n")

        # =================================
        # WINNER
        # =================================

        winner = outcome.get(
            "winner"
        )

        if winner is None:

            winner = outcome.get(
                "eliminator"
            )

        # =================================
        # RESULT INFO
        # =================================

        result_type = None

        result_margin = None

        if "by" in outcome:

            by_info = outcome["by"]

            if "runs" in by_info:

                result_type = "runs"

                result_margin = by_info["runs"]

            elif "wickets" in by_info:

                result_type = "wickets"

                result_margin = by_info["wickets"]

        # =================================
        # SUPER OVER RESULT
        # =================================

        if (

            outcome.get("result") == "tie"

            and outcome.get("eliminator")

        ):

            result_type = "super_over"

            result_margin = 1

        # =================================
        # TOSS
        # =================================

        toss = info.get(
            "toss",
            {}
        )

        toss_winner = toss.get(
            "winner"
        )

        toss_decision = toss.get(
            "decision"
        )

        # =================================
        # UMPIRES
        # =================================

        umpires = info.get(

            "officials",
            {}

        ).get(

            "umpires",
            []
        )

        umpire1 = (

            umpires[0]

            if len(umpires) > 0

            else None
        )

        umpire2 = (

            umpires[1]

            if len(umpires) > 1

            else None
        )

        # =================================
        # DATES
        # =================================

        dates = info.get(
            "dates",
            []
        )

        # =================================
        # TARGET INFO
        # =================================

        target_runs = None

        target_overs = None

        if len(innings) > 1:

            target_info = innings[1].get(

                "target",
                {}
            )

            target_runs = target_info.get(
                "runs"
            )

            target_overs = target_info.get(
                "overs"
            )

        # =================================
        # SUPER OVER FLAG
        # =================================

        super_over = any(

            inning.get(
                "super_over",
                False
            )

            for inning in innings
        )

        # =================================
        # MATCH ROW
        # =================================

        match_row = {

            "match_id": int(filename),

            "season": season,

            "match_date": (

                dates[0]

                if dates

                else None
            ),

            "city": info.get(
                "city"
            ),

            "venue": info.get(
                "venue"
            ),

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

            "super_over": super_over,

            "match_stage": "League",

            "is_playoff": False,

            "umpire1": umpire1,

            "umpire2": umpire2
        }

        all_matches.append(match_row)

    # =====================================
    # CREATE DATAFRAME
    # =====================================

    df = pd.DataFrame(all_matches)

    # =====================================
    # EMPTY CHECK
    # =====================================

    if df.empty:

        print(

            "No new matches found."
        )

        return

    # =====================================
    # FIX DATE COLUMN
    # =====================================

    df["match_date"] = pd.to_datetime(

        df["match_date"]
    )

    # =====================================
    # SORT MATCHES
    # =====================================

    df = df.sort_values(

        by=[

            "season",

            "match_date",

            "match_id"
        ],

        ascending=True

    ).reset_index(drop=True)

    # =====================================
    # ASSIGN PLAYOFF STAGES
    # =====================================

    for season, stage_names in CLEAN_STAGE_MAP.items():

        season_df = df[

            df["season"] == season

        ].copy()

        if season_df.empty:

            continue

        season_df = season_df.sort_values(

            by=[

                "match_date",

                "match_id"
            ],

            ascending=True
        )

        playoff_count = len(stage_names)

        playoff_matches = season_df.tail(

            playoff_count
        )

        for idx, stage in zip(

            playoff_matches.index,

            stage_names

        ):

            df.loc[

                idx,
                "match_stage"

            ] = stage

            df.loc[

                idx,
                "is_playoff"

            ] = True

    # =====================================
    # DATABASE INSERT
    # =====================================

    conn = get_connection()

    success_count = 0

    error_count = 0

    for _, row in df.iterrows():

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

            if (

                "duplicate key"

                in str(e).lower()

            ):

                continue

            error_count += 1

            print("\n=================================")

            print(
                "ERROR INSERTING MATCH"
            )

            print(
                "=================================\n"
            )

            print(row)

            print("\nERROR:\n")

            print(e)

            print(
                "\n=================================\n"
            )

    # =====================================
    # COMMIT & CLOSE
    # =====================================

    conn.commit()

    conn.close()

    # =====================================
    # FINAL STATUS
    # =====================================

    print("\n=================================")

    print(
        "MATCH LOADING COMPLETED"
    )

    print(
        "================================="
    )

    print(

        f"Successful Inserts : "
        f"{success_count}"
    )

    print(

        f"Failed Inserts     : "
        f"{error_count}"
    )

    print(
        "=================================\n"
    )

# =========================================
# MAIN
# =========================================

if __name__ == "__main__":

    load_matches()