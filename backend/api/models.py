from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid

class UserProfile(models.Model):
    """Extended user profile with avatar and additional info"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True
    )
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class MedicalReport(models.Model):
    """Model to store uploaded medical reports for users"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reports',
        null=True,
        blank=True
    )
        
    file = models.FileField(upload_to='reports/%Y/%m/%d/', null=True, blank=True)
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField()
    extracted_text = models.TextField(blank=True)
    processed_data = models.JSONField(default=dict, blank=True)
    
    # =====Store AI analysis data =====
    ai_explanation = models.JSONField(default=dict, blank=True)
    medications = models.JSONField(default=list, blank=True)
    follow_up = models.JSONField(default=list, blank=True)
    confidence = models.JSONField(default=dict, blank=True)
    
    # NEW: Share token for email notifications
    share_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} - {self.user.username if self.user else 'Unknown'} - {self.created_at.strftime('%Y-%m-%d')}"

# Automatically create UserProfile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
        

class ChatMessage(models.Model):
    """Store AI Assistant Q&A per report per user."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    report = models.ForeignKey(
        MedicalReport,
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    question = models.TextField()
    answer = models.TextField()
    provider = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Q: {self.question[:50]}..."

class EmailVerification(models.Model):
    """Stores a 6-digit verification code for a pending registration."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='email_verification'
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user.email} — {self.code}"