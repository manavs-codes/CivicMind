
from backend.app.database.mongodb import db

# Get the users collection
users_collection = db["users"]

# Create a unique index on email
users_collection.create_index(
    "email",
    unique=True
)

print("Users collection is ready.")
print("Unique email index created successfully.")
