
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load MongoDB credentials from root .env
load_dotenv(BASE_DIR / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in .env")

# Safety switch: preview only
DRY_RUN = True

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=5000
)

try:
    # Verify MongoDB connection
    client.admin.command("ping")

    db = client["CivicMind"]
    collection = db["complaints"]

    # Find old records where location is still a string
    old_documents = list(
        collection.find({"location": {"$type": "string"}})
    )

    print("Total complaints:", collection.count_documents({}))
    print("Old-format locations found:", len(old_documents))

    for document in old_documents:
        old_location = document["location"]

        new_location = {
            "address": old_location,
            "latitude": None,
            "longitude": None
        }

        print("\nComplaint ID:", document["_id"])
        print("Old location:", old_location)
        print("New location:", new_location)

        if not DRY_RUN:
            result = collection.update_one(
                {
                    "_id": document["_id"],
                    "location": old_location
                },
                {
                    "$set": {"location": new_location}
                }
            )

            print("Modified:", result.modified_count)

    if DRY_RUN:
        print("\nDRY RUN COMPLETE - No database changes made.")
    else:
        remaining = collection.count_documents(
            {"location": {"$type": "string"}}
        )
        print("\nMigration complete!")
        print("Remaining old-format locations:", remaining)

finally:
    client.close()
