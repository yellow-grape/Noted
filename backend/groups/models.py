from django.db import models
from django.conf import settings

# Create your models here.

class Group(models.Model):
    """Model for user groups with chat capabilities."""
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_groups'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='joined_groups'
    )
    goal = models.TextField()
    description = models.TextField()
    avatar = models.ImageField(
        upload_to='group_avatars/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Message(models.Model):
    """Model for group chat messages."""
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
