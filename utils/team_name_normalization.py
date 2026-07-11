# =========================================
# TEAM NAME NORMALIZER
# =========================================

TEAM_NAME_MAP = {

    # =====================================
    # RCB
    # =====================================

    "Royal Challengers Bangalore":
    "Royal Challengers Bengaluru",

    # =====================================
    # DELHI
    # =====================================

    "Delhi Daredevils":
    "Delhi Capitals",

    # =====================================
    # PUNJAB
    # =====================================

    "Kings XI Punjab":
    "Punjab Kings",

    # =====================================
    # DECCAN
    # =====================================

    "Deccan Chargers":
    "Sunrisers Hyderabad"

}


def normalize_team_name(team_name):

    return TEAM_NAME_MAP.get(

        team_name,

        team_name
    )
