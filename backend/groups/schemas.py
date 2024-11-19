from datetime import datetime
from typing import List, Optional
from ninja import Schema
from core.schemas import UserOut

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
    avatar: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: List[MessageOut]
