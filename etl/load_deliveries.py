from pathlib import Path
import sys
import json
import os


# =========================
# PROJECT ROOT SETUP
# =========================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from database.insert_deliveries import insert_deliveries
from database.insert_wickets import insert_wickets


# =========================
# HELPERS
# =========================

def make_delivery_key(match_id, innings, over_no, ball_no):

    return f"{match_id}_{innings}_{over_no}_{ball_no}"


# =========================
# MAIN
# =========================

folder = PROJECT_ROOT / "raw_data" / "json_matches"

files = [

    f for f in os.listdir(folder)

    if f.endswith(".json")
]

print(f"Total files: {len(files)}")


# =========================
# BATCH STORAGE
# =========================

all_deliveries = []

all_wickets = []


# =========================
# PROCESS FILES
# =========================

for file in files:

    path = os.path.join(folder, file)

    with open(path, "r", encoding="utf-8") as f:

        data = json.load(f)

    match_id = int(file.replace(".json", ""))

    info = data.get("info", {})

    teams = info.get("teams", [])

    innings_data = data.get("innings", [])

    # =========================
    # LOOP INNINGS
    # =========================

    for innings_no, inning in enumerate(

        innings_data,

        start=1
    ):

        # Skip super overs for now
        if innings_no > 2:
            continue

        batting_team = inning.get("team")

        bowling_team = [

            t for t in teams

            if t != batting_team

        ][0]

        overs = inning.get("overs", [])

        # =========================
        # LOOP OVERS
        # =========================

        for over in overs:

            over_no = over.get("over")

            deliveries = over.get(

                "deliveries",

                []
            )

            # =========================
            # LOOP DELIVERIES
            # =========================

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

                # =========================
                # RUNS
                # =========================

                runs = delivery.get("runs", {})

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

                    runs.get("non_boundary", 0)
                )

                # =========================
                # EXTRAS
                # =========================

                extras = delivery.get(

                    "extras",

                    {}
                )

                extra_type = (

                    ",".join(extras.keys())

                    if extras

                    else None
                )

                # =========================
                # DELIVERY ROW
                # =========================

                all_deliveries.append({

                    "delivery_key": delivery_key,

                    "match_id": match_id,

                    "innings": innings_no,

                    "over_no": over_no,

                    "ball_no": ball_no,

                    "batter": delivery.get("batter"),

                    "bowler": delivery.get("bowler"),

                    "non_striker": delivery.get(
                        "non_striker"
                    ),

                    "batting_team": batting_team,

                    "bowling_team": bowling_team,

                    "batsman_run": batsman_run,

                    "extras_run": extras_run,

                    "total_run": total_run,

                    "extra_type": extra_type,

                    "phase": (

                        "powerplay"

                        if over_no <= 5

                        else "middle"

                        if over_no <= 14

                        else "death"
                    ),

                    "is_boundary": (
                        batsman_run in [4, 6]
                    ),

                    "is_dot_ball": (
                        total_run == 0
                    ),

                    "non_boundary": non_boundary,

                    "is_super_over": (
                        innings_no > 2
                    )
                })

                # =========================
                # WICKETS
                # =========================

                wickets = delivery.get(

                    "wickets",

                    []
                )

                if wickets:

                    w = wickets[0]

                    fielders_data = w.get(

                        "fielders",

                        []
                    )

                    fielders = (

                        ",".join(

                            [

                                x.get("name")

                                for x in fielders_data
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

                # =========================
                # BATCH INSERT
                # =========================

                if len(all_deliveries) >= 10000:

                    insert_deliveries(
                        all_deliveries
                    )

                    all_deliveries.clear()

                    print(
                        "Inserted 10,000 deliveries"
                    )

                if len(all_wickets) >= 1000:

                    insert_wickets(
                        all_wickets
                    )

                    all_wickets.clear()

                    print(
                        "Inserted 1,000 wickets"
                    )

    print(f"Processed match {match_id}")


# =========================
# FINAL INSERT
# =========================

if all_deliveries:

    insert_deliveries(all_deliveries)

    print(
        f"Final insert: "
        f"{len(all_deliveries)} deliveries"
    )

if all_wickets:

    insert_wickets(all_wickets)

    print(
        f"Final insert: "
        f"{len(all_wickets)} wickets"
    )


print("\nDONE - Deliveries loaded")