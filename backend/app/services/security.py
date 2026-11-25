
from pwdlib import PasswordHash


# Create a secure password hashing system
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Convert a plain password into a secure hash."""
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """Check whether the entered password matches the stored hash."""
    return password_hash.verify(plain_password, hashed_password)


import os
import jwt

from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv


load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY not found in .env file")

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)


def create_access_token(user_id: str) -> str:
    """Generate a signed JWT access token."""

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token


def verify_access_token(token: str) -> dict:
    """Verify a JWT token and return its payload."""

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        user_id = payload.get("sub")

        if not user_id:
            raise ValueError("Token subject is missing")

        return payload

    except jwt.InvalidTokenError:
        raise ValueError("Invalid or expired access token")
