from bson import ObjectId
from fastapi import APIRouter, status, HTTPException

from app.database.mongodb import db
from app.models.complaint import Complaint, ComplaintUpdate

router = APIRouter(
    prefix="/complaints",
    tags=["Complaints"]
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_complaint(complaint: Complaint):

    # Convert the Pydantic model into a Python dictionary
    complaint_data = complaint.model_dump()

    # Insert the complaint into MongoDB
    result = db["complaints"].insert_one(complaint_data)

    return {
        "message": "Complaint submitted successfully!",
        "complaint_id": str(result.inserted_id),
        "complaint": complaint.model_dump(mode="json")
    }

@router.get("")
def get_complaints():

    complaints = list(
        db["complaints"].find({"is_deleted": {"$ne": True}})
    )

    for complaint in complaints:
        complaint["_id"] = str(complaint["_id"])

    return {
        "total_complaints": len(complaints),
        "complaints": complaints
    }

@router.get("/{complaint_id}")
def get_complaint_by_id(complaint_id: str):

    if not ObjectId.is_valid(complaint_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid complaint ID"
        )

    complaint = db["complaints"].find_one({
        "_id": ObjectId(complaint_id),
        "is_deleted": {"$ne": True}
    })

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    complaint["_id"] = str(complaint["_id"])

    return complaint

@router.patch("/{complaint_id}")
def update_complaint(complaint_id: str, updates: ComplaintUpdate):

    # Validate the complaint ID
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

    # Update the complaint in MongoDB
    result = db["complaints"].update_one(
    {
        "_id": ObjectId(complaint_id),
        "is_deleted": {"$ne": True}
    },
    {"$set": update_data}
)

    # Check whether the complaint exists
    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    # Retrieve the updated complaint
    updated_complaint = db["complaints"].find_one(
    {
        "_id": ObjectId(complaint_id),
        "is_deleted": {"$ne": True}
    }
)

    if not updated_complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )
    updated_complaint["_id"] = str(updated_complaint["_id"])

    return {
        "message": "Complaint updated successfully!",
        "complaint": updated_complaint
    }

@router.delete("/{complaint_id}")
def soft_delete_complaint(complaint_id: str):

    if not ObjectId.is_valid(complaint_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid complaint ID"
        )

    result = db["complaints"].update_one(
        {
            "_id": ObjectId(complaint_id),
            "is_deleted": {"$ne": True}
        },
        {
            "$set": {"is_deleted": True}
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    return {
        "message": "Complaint moved to deleted records"
    }