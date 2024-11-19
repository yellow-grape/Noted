from typing import Any, List
from django.shortcuts import get_object_or_404
from ninja import Router, File
from ninja.files import UploadedFile
from core.auth import AuthBearer
from core.schemas import ImageCreate, ImageOut, ImageUpdate, Message
from .models import Image

router = Router(tags=["images"])

@router.get("/", response=List[ImageOut], auth=AuthBearer())
def list_images(request) -> Any:
    """List all images for the current user."""
    return Image.objects.filter(user=request.auth)

@router.post("/", response={201: ImageOut, 400: Message}, auth=AuthBearer())
def create_image(
    request,
    payload: ImageCreate,
    image: UploadedFile = File(...)
) -> Any:
    """Create a new image."""
    try:
        image_obj = Image.objects.create(
            user=request.auth,
            title=payload.title,
            description=payload.description,
            image=image
        )
        return 201, image_obj
    except Exception as e:
        return 400, {"detail": str(e)}

@router.get("/{image_id}", response={200: ImageOut, 404: Message}, auth=AuthBearer())
def get_image(request, image_id: int) -> Any:
    """Get a specific image."""
    image = get_object_or_404(Image, id=image_id, user=request.auth)
    return image

@router.put("/{image_id}", response={200: ImageOut, 404: Message}, auth=AuthBearer())
def update_image(request, image_id: int, payload: ImageUpdate) -> Any:
    """Update an image."""
    image = get_object_or_404(Image, id=image_id, user=request.auth)
    
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(image, attr, value)
    
    image.save()
    return image

@router.delete("/{image_id}", response={204: None, 404: Message}, auth=AuthBearer())
def delete_image(request, image_id: int) -> Any:
    """Delete an image."""
    image = get_object_or_404(Image, id=image_id, user=request.auth)
    image.delete()
    return 204, None
