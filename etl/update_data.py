from pathlib import Path
import requests
import zipfile
import sys
import os

# =========================================
# PROJECT ROOT
# =========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.database import get_connection
from etl.load_matches import load_matches

# =========================================
# URL
# =========================================

CRICSHEET_URL = (

    "https://cricsheet.org/downloads/ipl_json.zip"
)


# =========================================
# PATHS
# =========================================

DOWNLOAD_PATH = (

    PROJECT_ROOT / "raw_data" / "ipl_json.zip"
)

EXTRACT_PATH = (

    PROJECT_ROOT / "raw_data" / "json_matches"
)


# =========================================
# DOWNLOAD ZIP
# =========================================

print("Downloading latest IPL data...")

response = requests.get(CRICSHEET_URL)

with open(DOWNLOAD_PATH, "wb") as f:

    f.write(response.content)

print("Download completed.")


# =========================================
# EXTRACT ZIP
# =========================================

print("Extracting ZIP file...")

with zipfile.ZipFile(

    DOWNLOAD_PATH,

    "r"

) as zip_ref:

    zip_ref.extractall(EXTRACT_PATH)

print("Extraction completed.")

# =========================================
# EXISTING MATCH IDS
# =========================================

print("Fetching existing match IDs...")

conn = get_connection()

cursor = conn.cursor()

cursor.execute("""

    SELECT match_id

    FROM matches

""")

existing_match_ids = {

    row[0]

    for row in cursor.fetchall()
}

cursor.close()

conn.close()

print(

    f"Existing matches found: "

    f"{len(existing_match_ids)}"

)

# =========================================
# EXISTING MATCH IDS
# =========================================

print("Fetching existing match IDs...")

conn = get_connection()

cursor = conn.cursor()

cursor.execute("""

    SELECT match_id

    FROM matches

""")

existing_match_ids = {

    row[0]

    for row in cursor.fetchall()
}

cursor.close()

conn.close()

print(

    f"Existing matches found: "

    f"{len(existing_match_ids)}"

)


# =========================================
# FIND NEW MATCH FILES
# =========================================

JSON_FOLDER = (

    PROJECT_ROOT / "raw_data" / "json_matches"
)

json_files = [

    f for f in os.listdir(JSON_FOLDER)

    if f.endswith(".json")
]

new_files = []

for file in json_files:

    match_id = int(

        file.replace(".json", "")
    )

    if match_id not in existing_match_ids:

        new_files.append(file)

print(

    f"New match files found: "

    f"{len(new_files)}"

)

# LOAD ONLY NEW MATCHES
if new_files:
    print("Loading new matches into database...")
    load_matches(new_files)
else:
    print("Database already up to date.")