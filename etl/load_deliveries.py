from pathlib import Path
import sys
import json
import os


# =========================================
# PROJECT ROOT SETUP
# =========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(0, str(PROJECT_ROOT))


from database.insert_deliveries import insert_deliveries
from database.insert_wickets import insert_wickets


# =========================================
# HELPERS
# =========================================

def make_delivery_key(

    match_id,
    innings,
    over_no,
    ball_no
):

    return f"{match_id}_{innings}_{over_no}_{ball_no}"


# =========================================
# MAIN
# =========================================

folder = PROJECT_ROOT / "raw_data" / "json_matches"

files = [

    f for f in os.listdir(folder)

    if f.endswith(".json")
]

print(f"Total files: {len(files)}")


# =========================================
# BATCH STORAGE
# =========================================

all_deliveries = []

all_wickets = []


# =========================================
# PROCESS FILES
# =========================================

for file in files:

    path = os.path.join(folder, file)

    with open(path, "r", encoding="utf-8") as f:

        data = json.load(f)

    match_id = int(
        file.replace(".json", "")
    )

    info = data.get("info", {})

    teams = info.get("teams", [])

    innings_data = data.get(
        "innings",
        []
    )

    # =====================================
    # LOOP INNINGS
    # =====================================

    for innings_no, inning in enumerate(

        innings_data,

        start=1
    ):

        batting_team = inning.get("team")

        # =================================
        # BOWLING TEAM
        # =================================

        bowling_team_list = [

            t for t in teams

            if t != batting_team
        ]

        bowling_team = (

            bowling_team_list[0]

            if bowling_team_list

            else None
        )

        overs = inning.get(
            "overs",
            []
        )

        # =================================
        # LOOP OVERS
        # =================================

        for over in overs:

            over_no = over.get("over")

            deliveries = over.get(

                "deliveries",

                []
            )

            # =================================
            # LOOP DELIVERIES
            # =================================

            for ball_no, delivery in enumerate(

                deliveries,

                start=1
            ):

                delivery_key = make_delivery_key(

                    match_id,
                    innings_no,
                    over_no,
                    ball_no
                )

                # =============================
                # RUNS
                # =============================

                runs = delivery.get(
                    "runs",
                    {}
                )

                batsman_run = runs.get(
                    "batter",
                    0
                )

                extras_run = runs.get(
                    "extras",
                    0
                )

                total_run = runs.get(
                    "total",
                    0
                )

                non_boundary = bool(

                    runs.get(
                        "non_boundary",
                        0
                    )
                )

                # =============================
                # EXTRAS
                # =============================

                extras = delivery.get(
                    "extras",
                    {}
                )

                extra_type = (

                    ",".join(extras.keys())

                    if extras

                    else None
                )

                # =============================
                # MATCH PHASE
                # =============================

                if over_no <= 5:

                    phase = "powerplay"

                elif over_no <= 14:

                    phase = "middle"

                else:

                    phase = "death"

                # =============================
                # DELIVERY ROW
                # =============================

                all_deliveries.append({

                    "delivery_key": delivery_key,

                    "match_id": match_id,

                    "innings": innings_no,

                    "over_no": over_no,

                    "ball_no": ball_no,

                    "batter": delivery.get(
                        "batter"
                    ),

                    "bowler": delivery.get(
                        "bowler"
                    ),

                    "non_striker": delivery.get(
                        "non_striker"
                    ),

                    "batting_team": batting_team,

                    "bowling_team": bowling_team,

                    "batsman_run": batsman_run,

                    "extras_run": extras_run,

                    "total_run": total_run,

                    "extra_type": extra_type,

                    "phase": phase,

                    "is_boundary": (
                        batsman_run in [4, 6]
                    ),

                    "is_dot_ball": (
                        total_run == 0
                    ),

                    "non_boundary": non_boundary,

                    # TEMPORARY
                    "is_super_over": False
                })

                # =============================
                # WICKETS
                # =============================

                wickets = delivery.get(
                    "wickets",
                    []
                )

                if wickets:

                    for w in wickets:

                        fielders_data = w.get(
                            "fielders",
                            []
                        )

                        fielders = (

                            ",".join(

                                [

                                    x.get("name")

                                    for x in fielders_data

                                    if x.get("name")
                                ]
                            )

                            if fielders_data

                            else None
                        )

                        all_wickets.append({

                            "delivery_key": delivery_key,

                            "player_out": w.get(
                                "player_out"
                            ),

                            "dismissal_kind": w.get(
                                "kind"
                            ),

                            "fielders_involved": fielders
                        })

                # =============================
                # BATCH INSERT DELIVERIES
                # =============================

                if len(all_deliveries) >= 10000:

                    insert_deliveries(
                        all_deliveries
                    )

                    print(
                        f"Inserted "
                        f"{len(all_deliveries)} deliveries"
                    )

                    all_deliveries.clear()

    print(f"Processed match {match_id}")


# =========================================
# FINAL INSERT DELIVERIES
# =========================================

if all_deliveries:

    insert_deliveries(
        all_deliveries
    )

    print(

        f"Final insert: "
        f"{len(all_deliveries)} deliveries"
    )


# =========================================
# FINAL INSERT WICKETS
# =========================================

if all_wickets:

    insert_wickets(
        all_wickets
    )

    print(

        f"Final insert: "
        f"{len(all_wickets)} wickets"
    )


print("\nDONE - Deliveries and Wickets loaded")