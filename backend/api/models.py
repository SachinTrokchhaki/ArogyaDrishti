from django.db import models
from django.contrib.auth.models import User

class MedicalReport(models.Model):
    """Model to store uploaded medical reports for users"""
    # Associate each report with a user
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reports',
        null=True,
        blank=True
    )
    
    file = models.FileField(upload_to='reports/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField()
    extracted_text = models.TextField(blank=True)
    processed_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.file_name} - {self.user.username if self.user else 'Unknown'} - {self.created_at.strftime('%Y-%m-%d')}"