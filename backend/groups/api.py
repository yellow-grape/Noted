from typing import Any, List, Optional
from django.shortcuts import get_object_or_404
from ninja import Router, File
from ninja.files import UploadedFile
from core.auth import AuthBearer
from core.schemas import Message as ErrorMessage
from .models import Group, Message
from .schemas import (
    GroupCreate,
    GroupOut,
    GroupUpdate,
    MessageCreate,
    MessageOut,
)

router = Router(tags=["groups"])

@router.get("/", response=List[GroupOut], auth=AuthBearer())
def list_groups(request) -> Any:
    """List all groups the user is a member of."""
    return request.auth.joined_groups.all()

@router.post("/", response={201: GroupOut, 400: ErrorMessage}, auth=AuthBearer())
def create_group(
    request,
    payload: GroupCreate,
    avatar: Optional[UploadedFile] = File(None)
) -> Any:
    """Create a new group."""
    try:
        group = Group.objects.create(
            owner=request.auth,
            name=payload.name,
            goal=payload.goal,
            description=payload.description,
            avatar=avatar
        )
        group.members.add(request.auth)  # Add owner as a member
        return 201, group
    except Exception as e:
        return 400, {"detail": str(e)}

@router.get("/{group_id}", response={200: GroupOut, 404: ErrorMessage}, auth=AuthBearer())
def get_group(request, group_id: int) -> Any:
    """Get a specific group."""
    group = get_object_or_404(Group, id=group_id, members=request.auth)
    return group

@router.put("/{group_id}", response={200: GroupOut, 404: ErrorMessage}, auth=AuthBearer())
def update_group(request, group_id: int, payload: GroupUpdate) -> Any:
    """Update a group."""
    group = get_object_or_404(Group, id=group_id, owner=request.auth)
    
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(group, attr, value)
    
    group.save()
    return group

@router.delete("/{group_id}", response={204: None, 404: ErrorMessage}, auth=AuthBearer())
def delete_group(request, group_id: int) -> Any:
    """Delete a group."""
    group = get_object_or_404(Group, id=group_id, owner=request.auth)
    group.delete()
    return 204, None

@router.post("/{group_id}/join", response={200: GroupOut, 404: ErrorMessage}, auth=AuthBearer())
def join_group(request, group_id: int) -> Any:
    """Join a group."""
    group = get_object_or_404(Group, id=group_id)
    group.members.add(request.auth)
    return group

@router.post("/{group_id}/leave", response={200: GroupOut, 404: ErrorMessage}, auth=AuthBearer())
def leave_group(request, group_id: int) -> Any:
    """Leave a group."""
    group = get_object_or_404(Group, id=group_id, members=request.auth)
    if group.owner != request.auth:
        group.members.remove(request.auth)
        return group
    return 400, {"detail": "Owner cannot leave the group"}

@router.post("/{group_id}/messages", response={201: MessageOut, 404: ErrorMessage}, auth=AuthBearer())
def create_message(request, group_id: int, payload: MessageCreate) -> Any:
    """Create a new message in a group."""
    group = get_object_or_404(Group, id=group_id, members=request.auth)
    message = Message.objects.create(
        group=group,
        sender=request.auth,
        content=payload.content
    )
    return 201, message

@router.get("/{group_id}/messages", response=List[MessageOut], auth=AuthBearer())
def list_messages(request, group_id: int) -> Any:
    """List all messages in a group."""
    group = get_object_or_404(Group, id=group_id, members=request.auth)
    return Message.objects.filter(group=group)
