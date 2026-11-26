
from bson import ObjectId
from fastapi import APIRouter, status, HTTPException, Depends

from app.routes.auth import get_current_user
from app.database.mongodb import db
from app.models.complaint import Complaint, ComplaintUpdate

router = APIRouter(
    prefix="/complaints",
    tags=["Complaints"]
)


# Create a new complaint
@router.post("", status_code=status.HTTP_201_CREATED)
def create_complaint(
    complaint: Complaint,
    current_user: dict = Depends(get_current_user)
):
    # Convert Pydantic model into dictionary
    complaint_data = complaint.model_dump()

    # Attach logged-in user's ID
    complaint_data["user_id"] = ObjectId(current_user["id"])

    # Insert complaint into MongoDB
    result = db["complaints"].insert_one(complaint_data)

    # Prepare response with string IDs
    complaint_data["_id"] = str(result.inserted_id)
    complaint_data["user_id"] = str(complaint_data["user_id"])

    return {
        "message": "Complaint submitted successfully!",
        "complaint_id": str(result.inserted_id),
        "complaint": complaint_data
    }


# Get all active complaints
@router.get("")
def get_complaints(
    current_user: dict = Depends(get_current_user)
):
    query = {
        "is_deleted": {"$ne": True}
    }

    # Citizens can only see their own complaints
    # Admins can see all active complaints
    if current_user["role"] != "admin":
        query["user_id"] = ObjectId(current_user["id"])

    complaints = list(db["complaints"].find(query))

    for complaint in complaints:
        complaint["_id"] = str(complaint["_id"])

        if "user_id" in complaint:
            complaint["user_id"] = str(complaint["user_id"])

    return {
        "total_complaints": len(complaints),
        "complaints": complaints
    }


# Get a specific complaint by ID
@router.get("/{complaint_id}")
def get_complaint_by_id(
    complaint_id: str,
    current_user: dict = Depends(get_current_user)
):
    if not ObjectId.is_valid(complaint_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid complaint ID"
        )

    query = {
        "_id": ObjectId(complaint_id),
        "is_deleted": {"$ne": True}
    }

    if current_user["role"] != "admin":
        query["user_id"] = ObjectId(current_user["id"])

    complaint = db["complaints"].find_one(query)

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    complaint["_id"] = str(complaint["_id"])

    if "user_id" in complaint:
        complaint["user_id"] = str(complaint["user_id"])

    return complaint


# Update an existing complaint
@router.patch("/{complaint_id}")
def update_complaint(
    complaint_id: str,
    updates: ComplaintUpdate,
    current_user: dict = Depends(get_current_user)
):
    if not ObjectId.is_valid(complaint_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid complaint ID"
        )

    # Get only the fields supplied by the user
    update_data = updates.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No update information provided"
        )

    query = {
        "_id": ObjectId(complaint_id),
        "is_deleted": {"$ne": True}
    }

    if current_user["role"] != "admin":
        query["user_id"] = ObjectId(current_user["id"])

    result = db["complaints"].update_one(
        query,
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    # Retrieve the updated complaint using the same ownership filter
    updated_complaint = db["complaints"].find_one(query)

    updated_complaint["_id"] = str(updated_complaint["_id"])

    if "user_id" in updated_complaint:
        updated_complaint["user_id"] = str(updated_complaint["user_id"])

    return {
        "message": "Complaint updated successfully!",
        "complaint": updated_complaint
    }


# Soft delete a complaint
@router.delete("/{complaint_id}")
def soft_delete_complaint(
    complaint_id: str,
    current_user: dict = Depends(get_current_user)
):
    if not ObjectId.is_valid(complaint_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid complaint ID"
        )

    query = {
        "_id": ObjectId(complaint_id),
        "is_deleted": {"$ne": True}
    }

    if current_user["role"] != "admin":
        query["user_id"] = ObjectId(current_user["id"])

    result = db["complaints"].update_one(
        query,
        {"$set": {"is_deleted": True}}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    return {
        "message": "Complaint moved to deleted records"
    }
