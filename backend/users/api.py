from typing import Any
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import Router, File, Form
from ninja.files import UploadedFile
from core.auth import AuthBearer, create_access_token, create_refresh_token
from core.schemas import (
    TokenSchema,
    UserCreate,
    UserOut,
    UserUpdate,
    Message
)

router = Router(tags=["auth"])
User = get_user_model()

@router.post("/register", auth=None, response={201: UserOut, 400: Message})
def register(
    request,
    payload: UserCreate = Form(...),
    avatar: UploadedFile = File(None)
) -> Any:
    """Register a new user."""
    try:
        user = User.objects.create_user(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            bio=payload.bio,
            avatar=avatar
        )
        return 201, user
    except Exception as e:
        return 400, {"detail": str(e)}

@router.post("/login", auth=None, response={200: TokenSchema, 400: Message})
def login(request, username: str, password: str) -> Any:
    """Login and get access token."""
    user = get_object_or_404(User, username=username)
    if not user.check_password(password):
        return 400, {"detail": "Invalid password"}
    
    return 200, {
        "access_token": create_access_token(user_id=user.id),
        "token_type": "bearer"
    }

@router.get("/me", response=UserOut, auth=AuthBearer())
def get_me(request) -> Any:
    """Get current user info."""
    return request.auth

@router.put("/me", response=UserOut, auth=AuthBearer())
def update_me(
    request,
    payload: UserUpdate,
    avatar: UploadedFile = File(None)
) -> Any:
    """Update current user info."""
    user = request.auth
    
    if payload.bio is not None:
        user.bio = payload.bio
    
    if avatar:
        user.avatar = avatar
    
    user.save()
    return user
