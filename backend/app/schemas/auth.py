from pydantic import BaseModel, EmailStr
from typing import Optional, List


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    avatar_initials: str
    created_at: Optional[str] = None


class LoginResponse(BaseModel):
    user: UserResponse
    token: str
    token_type: str = "bearer"


class DemoUserItem(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    avatar_initials: str
    demo_password: str


class GuardrailCreateRequest(BaseModel):
    rule_name: str
    rule_text: str
    category: str = "Safety"
    severity: str = "strict_block"


class GuardrailToggleRequest(BaseModel):
    is_active: bool
