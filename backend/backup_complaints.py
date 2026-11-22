
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from bson import json_util

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load MongoDB credentials from root .env
load_dotenv(BASE_DIR / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in .env")

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=5000
)

try:
    # Verify database connection
    client.admin.command("ping")

    db = client["CivicMind"]
    collection = db["complaints"]

    # Fetch ALL documents, including soft-deleted ones
    documents = list(collection.find({}))

    # Save backup
    backup_dir = BASE_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)

    backup_file = backup_dir / "complaints_backup.json"

    backup_file.write_text(
        json_util.dumps(documents, indent=2),
        encoding="utf-8"
    )

    print("Backup completed successfully!")
    print("Total documents backed up:", len(documents))
    print("Backup file:", backup_file)

finally:
    client.close()
