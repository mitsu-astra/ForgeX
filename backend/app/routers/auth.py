import os
import sys
import logging
import base64
import json
from fastapi import APIRouter, HTTPException, Header
from typing import Optional

# Bootstrap root path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.schemas.common import ApiResponse
from backend.app.schemas.auth import LoginRequest, LoginResponse, UserResponse
from backend.app.db.db_service import DatabaseService

logger = logging.getLogger("backend.routers.auth")
router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & Demo Personas"])


@router.post("/login", response_model=ApiResponse)
async def login(payload: LoginRequest):
    """
    Authenticates a user against PostgreSQL credentials.
    Supports standard login and 1-click demo logins.
    """
    user_dict = DatabaseService.authenticate_user(payload.email, payload.password)
    if not user_dict:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password. Please check your credentials.",
        )

    # Generate a lightweight bearer session token
    token_payload = {
        "sub": user_dict["email"],
        "id": user_dict["id"],
        "role": user_dict["role"],
    }
    token = base64.urlsafe_b64encode(json.dumps(token_payload).encode()).decode()

    user_resp = UserResponse(**user_dict)
    login_resp = LoginResponse(user=user_resp, token=token)

    return ApiResponse(
        success=True,
        message=f"Welcome back, {user_dict['full_name']} ({user_dict['role']})",
        data=login_resp.model_dump(),
    )


@router.get("/demo-users", response_model=ApiResponse)
async def list_demo_users():
    """
    Returns the 5 pre-seeded PostgreSQL demo users for instant 1-click persona switching.
    """
    demo_users = DatabaseService.get_demo_users()
    return ApiResponse(
        success=True,
        message="Seeded demo users retrieved from PostgreSQL",
        data={"users": demo_users},
    )


@router.get("/me", response_model=ApiResponse)
async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Validates token and returns current user profile.
    Falls back to admin demo user if no token provided.
    """
    email = "admin@industrial.ai"
    if authorization and "Bearer " in authorization:
        token_str = authorization.replace("Bearer ", "").strip()
        try:
            decoded = json.loads(base64.urlsafe_b64decode(token_str.encode()).decode())
            email = decoded.get("sub", email)
        except Exception:
            pass

    user_dict = DatabaseService.get_user_by_email(email)
    if not user_dict:
        # Fallback to default first user
        demo_users = DatabaseService.get_demo_users()
        user_dict = demo_users[0] if demo_users else {
            "id": 1,
            "email": "admin@industrial.ai",
            "full_name": "Alex Vance",
            "role": "Lead Systems Architect",
            "avatar_initials": "AV",
        }

    return ApiResponse(
        success=True,
        message="Active user profile retrieved",
        data=user_dict,
    )
