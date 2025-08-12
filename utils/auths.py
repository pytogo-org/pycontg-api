

from datetime import datetime, timedelta
import os

import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from datas import auth_user
import jwt


load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES"))

async def authenticate_user(email: str, password: str):
    user = auth_user(email, password)

    if user is None:
        return None

    user_data = {
        "id": user.get("id"),
        "email": user.get("email"),
        "full_name": user.get("full_name", ""),
        "role": user.get("role", "staff"),
    }
    return user_data


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + (
        expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Invalid credentials")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {
            "email": payload.get("sub"),
            "user_id": payload.get("user_id"),
            "full_name": payload.get("full_name"),
            "role": payload.get("role"),
        }
    except Exception:
        raise credentials_exception

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hashed password.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )

def _sorted(items: list, order: dict, sorted_by: list):
    sponsors_sorted = sorted(
            items,
            key=lambda s: order.get(s.get(sorted_by, ""), 99)
        )
    
    return sponsors_sorted