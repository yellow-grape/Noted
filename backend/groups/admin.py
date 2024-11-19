from django.contrib import admin
from .models import Group, Message

# Register your models here.

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('members',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'sender', 'created_at')
    list_filter = ('created_at', 'group')
    search_fields = ('content', 'sender__username', 'group__name')
    readonly_fields = ('created_at',)
