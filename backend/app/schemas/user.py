from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
import json


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool
    is_active: bool
    full_name: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    website_url: Optional[str] = None
    location: Optional[str] = None
    email_public: Optional[str] = None
    resume_data: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    website_url: Optional[str] = None
    location: Optional[str] = None
    email_public: Optional[str] = None
    resume_data: Optional[str] = None   # JSON string

    @field_validator("resume_data")
    @classmethod
    def validate_resume_json(cls, v):
        if v is not None:
            try:
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("resume_data 必须是合法的 JSON 字符串")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
