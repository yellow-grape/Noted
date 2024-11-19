from django.contrib import admin
from .models import Image

# Register your models here.

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
