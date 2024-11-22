from typing import Any, List, Optional, Union
from django.shortcuts import get_object_or_404
from ninja import Router, File, Schema, Path, Query
from ninja.files import UploadedFile
from ninja.pagination import paginate
from core.auth import AuthBearer
from core.schemas import Message as ErrorMessage, GroupOut
from django.db.models import Count, Q, F, Value, FloatField, Case, When
from django.db.models.functions import Cast, Greatest
from .models import Group, Message
from .schemas import (
    GroupCreate,
    GroupUpdate,
    MessageCreate,
    MessageOut,
)
import logging
import re

logger = logging.getLogger(__name__)

router = Router(tags=["groups"])

class SearchParams(Schema):
    query: Optional[str] = None
    public_only: Optional[bool] = False

@router.get("/search", response=List[GroupOut], auth=AuthBearer())
def search_groups(
    request,
    params: SearchParams = Query(...),
) -> Any:
    """
    Search groups by query string.
    If no parameters are provided, returns all groups the user is a member of and public groups.
    Results are ordered by relevance to the search query.
    """
    logger.info(f"Search request - query: {params.query}, public_only: {params.public_only}, raw query params: {request.GET}")
    
    groups_query = Group.objects.annotate(
        member_count=Count('members')
    )
    
    # Convert string 'true'/'false' to boolean if needed
    if isinstance(params.public_only, str):
        params.public_only = params.public_only.lower() == 'true'
        logger.info(f"Converted public_only to bool: {params.public_only}")
    
    if params.public_only:
        groups_query = groups_query.filter(public=True)
        logger.info("Filtering public groups only")
    else:
        # Show groups user is member of and public groups
        groups_query = groups_query.filter(
            Q(public=True) | Q(members=request.auth)
        )
        logger.info("Filtering public groups and user's groups")

    if params.query:
        # Normalize query to lowercase for case-insensitive search
        query = params.query.lower()
        logger.info(f"Searching with query: {query}")
        
        # Split query into words for word-based matching
        words = query.split()
        
        # Add relevance scoring based on various matches
        groups_query = groups_query.annotate(
            exact_match=Cast(
                Q(name__iexact=query) | Q(goal__iexact=query) | Q(description__iexact=query),
                output_field=FloatField()
            ) * Value(1.0),
            exact_word_match=Cast(
                Q(name__iregex=r'(?:^|\s)' + query + r'(?:\s|$)') |
                Q(goal__iregex=r'(?:^|\s)' + query + r'(?:\s|$)') |
                Q(description__iregex=r'(?:^|\s)' + query + r'(?:\s|$)'),
                output_field=FloatField()
            ) * Value(0.8),
            starts_with_word=Cast(
                Q(name__istartswith=query) |
                Q(goal__istartswith=query) |
                Q(description__istartswith=query),
                output_field=FloatField()
            ) * Value(0.6),
            contains_word=Cast(
                Q(name__icontains=query) |
                Q(goal__icontains=query) |
                Q(description__icontains=query),
                output_field=FloatField()
            ) * Value(0.4),
            relevance=Greatest(
                F('exact_match'),
                F('exact_word_match'),
                F('starts_with_word'),
                F('contains_word'),
                Value(0.0)
            )
        ).filter(relevance__gt=0)
        
        logger.info("Added relevance scoring")
    else:
        # If no query, set a default relevance of 1.0 for all groups
        groups_query = groups_query.annotate(
            relevance=Value(1.0, output_field=FloatField())
        )
        logger.info("No query provided, using default relevance")

    # Order by relevance (if search query provided), then by member count, then by name
    groups_query = groups_query.order_by('-relevance', '-member_count', 'name')
    logger.info("Ordered results")

    return groups_query

@router.get("/public/", response=List[GroupOut], auth=AuthBearer())
def list_public_groups(request) -> Any:
    """List all public groups, ordered by member count."""
    return Group.objects.filter(public=True).annotate(member_count=Count('members')).order_by('-member_count')[:10]

@router.get("/private/", response=List[GroupOut], auth=AuthBearer())
def list_private_groups(request) -> Any:
    """List all groups the user is a member of (excluding public groups they're not a member of)."""
    return Group.objects.filter(members=request.auth, public=False)

@router.get("/member/", response=List[GroupOut], auth=AuthBearer())
def list_member_groups(request) -> Any:
    """List all groups the user is a member of, both public and private."""
    return Group.objects.filter(members=request.auth)

@router.get("/", response=List[GroupOut], auth=AuthBearer())
def list_groups(request) -> Any:
    """List all groups the user is a member of and all public groups."""
    user_groups = request.auth.joined_groups.all()
    public_groups = Group.objects.filter(public=True).exclude(members=request.auth)
    return list(user_groups) + list(public_groups)

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
            avatar=avatar,
            public=payload.public
        )
        group.members.add(request.auth)  # Add owner as a member
        return 201, group
    except Exception as e:
        return 400, {"detail": str(e)}

@router.get("/{group_id}", response={200: GroupOut, 404: ErrorMessage}, auth=AuthBearer())
def get_group(request, group_id: int = Path(...)) -> Any:
    """Get a specific group."""
    group = get_object_or_404(Group, id=group_id, members=request.auth)
    return group

@router.put("/{group_id}", response={200: GroupOut, 404: ErrorMessage}, auth=AuthBearer())
def update_group(request, payload: GroupUpdate, group_id: int = Path(...)) -> Any:
    """Update a group."""
    group = get_object_or_404(Group, id=group_id, owner=request.auth)
    
    if payload.name is not None:
        group.name = payload.name
    if payload.goal is not None:
        group.goal = payload.goal
    if payload.description is not None:
        group.description = payload.description
    if payload.public is not None:
        group.public = payload.public
    
    group.save()
    return group

@router.delete("/{group_id}", response={204: None, 404: ErrorMessage}, auth=AuthBearer())
def delete_group(request, group_id: int = Path(...)) -> Any:
    """Delete a group."""
    group = get_object_or_404(Group, id=group_id, owner=request.auth)
    group.delete()
    return 204, None

@router.post("/{group_id}/join", response={200: GroupOut, 404: ErrorMessage}, auth=AuthBearer())
def join_group(request, group_id: int = Path(...)) -> Any:
    """Join a group."""
    group = get_object_or_404(Group, id=group_id)
    group.members.add(request.auth)
    return group

@router.post("/{group_id}/leave", response={200: GroupOut, 404: ErrorMessage}, auth=AuthBearer())
def leave_group(request, group_id: int = Path(...)) -> Any:
    """Leave a group."""
    group = get_object_or_404(Group, id=group_id, members=request.auth)
    if group.owner != request.auth:
        group.members.remove(request.auth)
        return group
    return {"detail": "Group owner cannot leave the group"}

@router.get("/{group_id}/members", response=List[dict], auth=AuthBearer())
def list_group_members(request, group_id: int = Path(...)) -> Any:
    """List all members of a group."""
    group = get_object_or_404(Group, id=group_id)
    # Check if user is a member or if the group is public
    if not (group.public or request.auth in group.members.all()):
        return {"detail": "Not authorized to view this group's members"}
    
    members = group.members.all().values('id', 'username', 'avatar')
    owner_id = group.owner_id
    
    # Convert ValuesQuerySet to list and add owner info
    members_list = list(members)
    for member in members_list:
        member['owner_id'] = owner_id
    
    return members_list

@router.post("/{group_id}/messages", response={201: MessageOut, 400: ErrorMessage}, auth=AuthBearer())
def create_message(request, payload: MessageCreate, group_id: int = Path(...)) -> Any:
    """Create a new message in a group."""
    group = get_object_or_404(Group, id=group_id, members=request.auth)
    message = Message.objects.create(
        group=group,
        sender=request.auth,
        content=payload.content
    )
    return 201, message

@router.get("/{group_id}/messages", response=List[MessageOut], auth=AuthBearer())
def list_messages(request, group_id: int = Path(...)) -> Any:
    """List all messages in a group."""
    group = get_object_or_404(Group, id=group_id, members=request.auth)
    return Message.objects.filter(group=group)
