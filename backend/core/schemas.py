from datetime import datetime
from typing import Optional
from ninja import Schema
from pydantic import EmailStr, Field, BaseModel

class TokenSchema(Schema):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    exp: int
    sub: str

class UserCreate(Schema):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    bio: Optional[str] = None

class UserOut(Schema):
    id: int
    username: str
    email: str  
    bio: Optional[str] = None
    avatar: Optional[str] = None
    date_joined: datetime = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

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
