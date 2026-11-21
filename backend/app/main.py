
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database.mongodb import client

from app.routes.complaint import router as complaints_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify MongoDB connection when the application starts
    try:
        client.admin.command("ping")
        print("Successfully connected to MongoDB Atlas!")
    except Exception as e:
        print("MongoDB connection failed:", e)
        raise

    yield

    # Close MongoDB connection when the application shuts down
    client.close()
    print("MongoDB connection closed.")


# Create the FastAPI application
app = FastAPI(
    title="CivicMind API",
    description="An intelligent civic complaint management system",
    version="1.0.0",
    lifespan=lifespan
)
app.include_router(complaints_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to CivicMind!",
        "status": "Backend is running successfully"
    }
