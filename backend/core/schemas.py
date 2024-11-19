from datetime import datetime
from typing import List, Optional
from ninja import Schema, File
from ninja.files import UploadedFile
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

class UserUpdate(Schema):
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

class GroupBase(Schema):
    name: str
    goal: str
    description: str

class GroupCreate(GroupBase):
    pass

class GroupUpdate(Schema):
    name: Optional[str] = None
    goal: Optional[str] = None
    description: Optional[str] = None

class MessageBase(Schema):
    content: str

class MessageCreate(MessageBase):
    pass

class MessageOut(MessageBase):
    id: int
    sender: UserOut
    created_at: datetime

class GroupOut(GroupBase):
    id: int
    owner: UserOut
    members: List[UserOut]
    avatar: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[MessageOut]

class Message(Schema):
    detail: str

class ImageCreate(Schema):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

class ImageUpdate(Schema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None

class ImageOut(Schema):
    id: int
    title: str
    description: Optional[str]
    image: str
    created_at: datetime
    user: UserOut
