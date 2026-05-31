from pathlib import Path
import sys
import os
import json

# Ensure the project root is always importable, even when running from inside etl/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.insert_matches import insert_match


# =========================================
# CLEAN IPL SEASON FORMAT
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
# FOLDER
# =========================================

folder = PROJECT_ROOT / "raw_data" / "json_matches"

# =========================================
# PROCESS ONLY 1 FILE FOR TESTING
# =========================================

for file in os.listdir(folder):

    if not file.endswith(".json"):
        continue

    path = os.path.join(folder, file)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    info = data.get("info", {})

    teams = info.get("teams", [])

    team1 = teams[0] if len(teams) > 0 else None
    team2 = teams[1] if len(teams) > 1 else None

    season = clean_season(info.get("season"))

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

    umpires = info.get("officials", {}).get("umpires", [])

    umpire1 = umpires[0] if len(umpires) > 0 else None
    umpire2 = umpires[1] if len(umpires) > 1 else None

    toss = info.get("toss", {})

    toss_winner = toss.get("winner")
    toss_decision = toss.get("decision")

    dates = info.get("dates", [])

    innings = data.get("innings", [])

    target_runs = None
    target_overs = None

    if len(innings) > 1:

        target_info = innings[1].get("target", {})

        target_runs = target_info.get("runs")
        target_overs = target_info.get("overs")

    match_row = {

        "match_id": int(file.replace(".json", "")),

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
            info.get("player_of_match", [None])[0]
        ),

        "result_type": result_type,

        "result_margin": result_margin,

        "target_runs": target_runs,

        "target_overs": target_overs,

        "super_over": len(innings) > 2,

        "match_stage": "League",

        "is_playoff": False,

        "umpire1": umpire1,

        "umpire2": umpire2
    }

    insert_match(match_row)
    print(f"Processed {match_row['match_id']}")

    print(
        f"Inserted match {match_row['match_id']}"
    )

print("\nDone")