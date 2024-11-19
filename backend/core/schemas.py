from datetime import datetime
from typing import Optional
from ninja import Schema
from pydantic import EmailStr, Field

class TokenSchema(Schema):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(Schema):
    sub: Optional[int] = None
    exp: Optional[datetime] = None

class UserCreate(Schema):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    bio: Optional[str] = None

class UserOut(Schema):
    id: int
    username: str
    email: EmailStr
    bio: Optional[str]
    avatar: Optional[str]
    created_at: datetime

class UserUpdate(Schema):
    bio: Optional[str] = None
    avatar: Optional[str] = None

class ImageCreate(Schema):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

class ImageOut(Schema):
    id: int
    title: str
    description: Optional[str]
    image: str
    created_at: datetime
    user: UserOut

class ImageUpdate(Schema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None

class Message(Schema):
    detail: str
