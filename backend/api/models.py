from django.db import models

class MedicalReport(models.Model):
    """Model to store uploaded medical reports"""
    file = models.FileField(upload_to='reports/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField()
    extracted_text = models.TextField(blank=True)
    processed_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.file_name} - {self.created_at.strftime('%Y-%m-%d')}"