from pathlib import Path
import requests
import zipfile
import sys
import os
import shutil

# =========================================
# PROJECT ROOT
# =========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(0, str(PROJECT_ROOT))

# =========================================
# IMPORTS
# =========================================

from etl.load_matches import load_matches

from etl.load_deliveries import load_deliveries

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
# CLEAN OLD ZIP
# =========================================

if DOWNLOAD_PATH.exists():

    DOWNLOAD_PATH.unlink()

# =========================================
# DOWNLOAD ZIP
# =========================================

print("\n=========================================")
print("DOWNLOADING LATEST IPL DATA")
print("=========================================\n")

try:

    response = requests.get(

        CRICSHEET_URL,

        timeout=120
    )

    response.raise_for_status()

except Exception as e:

    print(

        f"Download failed:\n{e}"
    )

    sys.exit()

with open(DOWNLOAD_PATH, "wb") as f:

    f.write(response.content)

print("Download completed.")

# =========================================
# CLEAN OLD JSON FOLDER
# =========================================

print("\nCleaning old extracted files...")

# =========================================
# CLEAN OLD JSON FILES
# =========================================

print("\nCleaning old extracted files...")

EXTRACT_PATH.mkdir(

    parents=True,

    exist_ok=True
)

for file in os.listdir(EXTRACT_PATH):

    file_path = EXTRACT_PATH / file

    try:

        if file_path.is_file():

            os.remove(file_path)

    except Exception as e:

        print(f"Could not delete {file}: {e}")

print("Old files removed.")

# =========================================
# EXTRACT ZIP
# =========================================

print("\nExtracting ZIP file...")

try:

    with zipfile.ZipFile(

        DOWNLOAD_PATH,

        "r"

    ) as zip_ref:

        zip_ref.extractall(EXTRACT_PATH)

except Exception as e:

    print(

        f"ZIP extraction failed:\n{e}"
    )

    sys.exit()

print("Extraction completed.")

# =========================================
# GET ALL JSON FILES
# =========================================

json_files = sorted([

    f for f in os.listdir(EXTRACT_PATH)

    if (
        f.endswith(".json")
        and
        f.replace(".json", "").isdigit()
    )

])

print(

    f"\nJSON files found: "
    f"{len(json_files)}"
)

# =========================================
# EMPTY CHECK
# =========================================

if not json_files:

    print(

        "\nNo valid JSON files found."
    )

    sys.exit()

# =========================================
# LOAD MATCHES
# =========================================

print("\n=========================================")
print("LOADING MATCHES")
print("=========================================\n")

try:

    load_matches(json_files)

    print("\nMatches loaded successfully.")

except Exception as e:

    print(

        f"\nMatch loading failed:\n{e}"
    )

    sys.exit()

# =========================================
# LOAD DELIVERIES
# =========================================

print("\n=========================================")
print("LOADING DELIVERIES")
print("=========================================\n")

try:

    load_deliveries(json_files)

    print("\nDeliveries loaded successfully.")

except Exception as e:

    print(

        f"\nDelivery loading failed:\n{e}"
    )

    sys.exit()

# =========================================
# FINISHED
# =========================================

print("\n=========================================")
print("IPL DATABASE UPDATE COMPLETED")
print("=========================================\n")