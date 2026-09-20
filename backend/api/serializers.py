from rest_framework import serializers
from .models import MedicalReport


class MedicalReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalReport
        fields = [
            'id', 
            'file_name', 
            'file_size', 
            'created_at', 
            'extracted_text', 
            'processed_data',
            # ===== NEW FIELDS =====
            'ai_explanation',
            'medications',
            'follow_up',
            'confidence',
            # =====================
        ]
        read_only_fields = ['id', 'created_at', 'user']