
from fastapi import APIRouter, HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.database.mongodb import db
from app.models.user import UserCreate, UserInDB, UserPublic
from app.services.security import hash_password

from app.models.user import UserLogin
from app.services.security import verify_password, create_access_token

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
from bson.errors import InvalidId

from app.services.security import verify_access_token

oauth2_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = verify_access_token(token)
        user_id = payload.get("sub")

        if not isinstance(user_id, str):
            raise credentials_exception

        user_object_id = ObjectId(user_id)

    except (ValueError, InvalidId):
        raise credentials_exception

    current_user = db["users"].find_one({
        "_id": user_object_id
    })

    if not current_user:
        raise credentials_exception

    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    return {
        "id": str(current_user["_id"]),
        "full_name": current_user["full_name"],
        "email": current_user["email"],
        "role": current_user["role"],
        "created_at": current_user["created_at"],
        "is_active": current_user["is_active"]
    }

def require_admin(
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublic
)
def register_user(user: UserCreate):

    # Normalize email to lowercase
    email = str(user.email).lower()

    # Hash the password
    hashed_password = hash_password(user.password)

    # Prepare user data for MongoDB
    user_data = UserInDB(
        full_name=user.full_name,
        email=email,
        password_hash=hashed_password,
        role="citizen"
    )

    try:
        result = db["users"].insert_one(
            user_data.model_dump()
        )

    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )

    # Return only public user information
    return UserPublic(
        id=str(result.inserted_id),
        full_name=user_data.full_name,
        email=user_data.email,
        role=user_data.role,
        created_at=user_data.created_at,
        is_active=user_data.is_active
    )


@router.post("/login")
def login_user(user: UserLogin):

    # Normalize email
    email = str(user.email).lower()

    # Find user in MongoDB
    existing_user = db["users"].find_one({
        "email": email
    })

    # Check email and password
    if not existing_user or not verify_password(
        user.password,
        existing_user["password_hash"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Check whether account is active
    if not existing_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Generate JWT access token
    access_token = create_access_token(
        str(existing_user["_id"])
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserPublic)
def get_me(current_user: dict = Depends(get_current_user)):
    return UserPublic(**current_user)

@router.get("/admin-check")
def admin_check(
    current_user: dict = Depends(require_admin)
):
    return {
        "message": "Admin access granted",
        "user": current_user["email"]
    }