from pydantic import BaseModel, EmailStr

from app.schemas.admin import AdminIdentityResponse
from app.schemas.bootstrap import UserProfileResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    fullName: str
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    token: str
    user: UserProfileResponse


class AdminAuthResponse(BaseModel):
    token: str
    user: AdminIdentityResponse
