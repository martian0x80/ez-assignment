from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models import UserType


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str
    user_type: UserType


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    user_type: str
    is_verified: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    user_type: Optional[str] = None


# File Schemas
class FileBase(BaseModel):
    original_filename: str
    file_size: int
    file_type: str


class FileCreate(FileBase):
    filename: str
    file_path: str
    uploader_id: int


class FileResponse(FileBase):
    id: int
    filename: str
    uploader_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class FileListResponse(BaseModel):
    files: List[FileResponse]
    total: int


# Download Token Schemas
class DownloadTokenCreate(BaseModel):
    file_id: int
    client_id: int
    token: str
    expires_at: datetime


class DownloadTokenResponse(BaseModel):
    download_link: str
    message: str


# Email Verification
class EmailVerification(BaseModel):
    email: EmailStr
    verification_token: str


# Response Schemas
class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
