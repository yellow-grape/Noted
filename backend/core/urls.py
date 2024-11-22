"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ninja import NinjaAPI
from users.api import router as users_router
from images.api import router as images_router
from groups.api import router as groups_router
from core.auth import AuthBearer
from groups.views import ChatTestView

api = NinjaAPI(
    title="Noted API",
    version="1.0.0",
    description="API for managing notes and images",
    auth=AuthBearer(),
    csrf=False,
)

# Add routers
api.add_router("/auth/", users_router)
api.add_router("/images/", images_router)
api.add_router("/groups/", groups_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path('test/chat/', ChatTestView.as_view(), name='chat_test'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
