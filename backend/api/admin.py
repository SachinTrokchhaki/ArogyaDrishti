from django.contrib import admin
from .models import MedicalReport

@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'file_size', 'created_at']
    search_fields = ['file_name']
    readonly_fields = ['created_at']