from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .utils.ai_explainer import AIExplainer
import os
import re

from .models import MedicalReport
from .serializers import MedicalReportSerializer
from .utils.ocr import OCRProcessor
from .utils.processor import ReportProcessor

# Helper functions for dynamic data
def extract_patient_info(text):
    """Extract patient information from report text"""
    patient_info = {
        'name': 'Unknown',
        'age': 'Unknown',
        'gender': 'Unknown'
    }
    
    if not text:
        return patient_info
    
    # Clean the text first - remove extra spaces and newlines
    text = ' '.join(text.split())
    
    # Try to find patient name
    name_patterns = [
        r'Name\s*[:]\s*([A-Za-z\s.]+?)(?:\s+Age|\s+[0-9]|\s*$)',
        r'Patient\s*[:]\s*([A-Za-z\s.]+?)(?:\s+Age|\s+[0-9]|\s*$)',
        r'Patient\s+Name\s*[:]\s*([A-Za-z\s.]+?)(?:\s+Age|\s+[0-9]|\s*$)',
        r'Patient\s+([A-Za-z\s.]+?)(?:\s+Age|\s+[0-9]|\s*$)',
        r'Name\s+([A-Za-z\s.]+?)(?:\s+Age|\s+[0-9]|\s*$)',
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            patient_info['name'] = match.group(1).strip()
            break
    
    # Try to find age
    age_patterns = [
        r'Age\s*[:]\s*(\d+)',
        r'Age\s+(\d+)',
        r'(\d+)\s*Years',
        r'(\d+)\s*years',
        r'Age\s+(\d+)\s*[Yy]',
    ]
    for pattern in age_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            patient_info['age'] = match.group(1).strip()
            break
    
    # Try to find gender
    gender_patterns = [
        r'Gender\s*[:]\s*([A-Za-z]+)',
        r'Sex\s*[:]\s*([A-Za-z]+)',
        r'Gender\s+([A-Za-z]+)',
        r'Sex\s+([A-Za-z]+)',
    ]
    for pattern in gender_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            gender = match.group(1).strip().lower()
            if gender in ['male', 'female', 'm', 'f']:
                patient_info['gender'] = gender.capitalize()
            break
    
    return patient_info

def generate_medications(results):
    """Generate medications based on test results"""
    medications = []
    
    if not results:
        return medications
    
    # Check for anemia indicators (Hemoglobin low)
    for r in results:
        if r.get('test_name', '').lower() == 'hemoglobin':
            try:
                if float(r.get('value', 0)) < 13.0:
                    medications.append({
                        'name': 'Ferrous Ascorbate',
                        'dosage': '100 mg',
                        'frequency': 'Once daily',
                        'instructions': 'After breakfast'
                    })
                    medications.append({
                        'name': 'Folic Acid',
                        'dosage': '5 mg',
                        'frequency': 'Once daily',
                        'instructions': 'With water, after a meal'
                    })
                    break
            except:
                pass
    
    # Check for fever/infection indicators (WBC high)
    for r in results:
        if r.get('test_name', '').lower() in ['wbc', 'total leucocyte count', 'tlc']:
            try:
                if float(r.get('value', 0)) > 11000:
                    medications.append({
                        'name': 'Paracetamol',
                        'dosage': '500 mg',
                        'frequency': 'As needed',
                        'instructions': 'Maximum 3 times a day'
                    })
                    break
            except:
                pass
    
    # Check for cholesterol indicators (Total Cholesterol high)
    for r in results:
        if r.get('test_name', '').lower() == 'total cholesterol':
            try:
                if float(r.get('value', 0)) > 200:
                    medications.append({
                        'name': 'Atorvastatin',
                        'dosage': '10 mg',
                        'frequency': 'Once daily',
                        'instructions': 'Take at bedtime'
                    })
                    break
            except:
                pass
    
    # If no medications detected, add a message
    if not medications:
        medications.append({
            'name': 'No medications detected',
            'dosage': '-',
            'frequency': '-',
            'instructions': 'Consult your doctor for any prescribed medications'
        })
    
    return medications

def generate_follow_up(results):
    """Generate follow-up recommendations based on results"""
    follow_up = []
    
    if not results:
        return follow_up
    
    abnormal_count = sum(1 for r in results if r.get('status') in ['HIGH', 'LOW'])
    
    if abnormal_count > 0:
        follow_up.append("Discuss abnormal results with a qualified healthcare professional.")
        follow_up.append("Keep previous reports available so trends can be compared.")
        follow_up.append("Bring the original report when consulting your healthcare provider.")
        follow_up.append("Follow any instructions already written on the report by the issuing laboratory.")
        
        # Specific follow-ups based on abnormal values
        for r in results:
            test_name = r.get('test_name', '').lower()
            status = r.get('status', '')
            
            if status == 'HIGH':
                if 'cholesterol' in test_name:
                    follow_up.append("Consider dietary changes and exercise to manage cholesterol levels.")
                if 'glucose' in test_name or 'sugar' in test_name:
                    follow_up.append("Monitor blood sugar levels regularly and consult an endocrinologist.")
                if 'creatinine' in test_name or 'urea' in test_name:
                    follow_up.append("Schedule a kidney function follow-up test.")
                if 'bilirubin' in test_name or 'sgpt' in test_name or 'sgot' in test_name:
                    follow_up.append("Consider a liver function follow-up test.")
            
            if status == 'LOW':
                if 'hemoglobin' in test_name:
                    follow_up.append("Consider iron-rich foods and vitamin supplements.")
                if 'albumin' in test_name:
                    follow_up.append("Review protein intake and consult a nutritionist.")
                if 'platelet' in test_name:
                    follow_up.append("Monitor platelet levels and consult a hematologist.")
    else:
        follow_up.append("All values are within normal range. Continue maintaining a healthy lifestyle.")
        follow_up.append("Schedule regular check-ups as recommended by your healthcare provider.")
        follow_up.append("Keep this report for future reference and comparison.")
    
    return follow_up

def generate_confidence(results, extracted_text):
    """Generate confidence scores based on extraction quality"""
    confidence = {
        'ocr': 94,
        'extraction': 91,
        'classification': 96
    }
    
    # Adjust OCR confidence based on text length
    if extracted_text:
        text_length = len(extracted_text)
        if text_length > 1000:
            confidence['ocr'] = 96
        elif text_length > 500:
            confidence['ocr'] = 92
        else:
            confidence['ocr'] = 85
    
    # Adjust extraction confidence based on number of tests found
    if results:
        if len(results) > 20:
            confidence['extraction'] = 95
        elif len(results) > 10:
            confidence['extraction'] = 90
        else:
            confidence['extraction'] = 80
        
        # Adjust classification confidence
        confidence['classification'] = 94 if len(results) > 15 else 88
    
    return confidence

@api_view(['GET'])
def health_check(request):
    """Check if API is running"""
    return Response({
        'status': 'ok',
        'message': 'ArogyaDrishti API is running!',
        'version': '1.0.0'
    })

@api_view(['POST'])
def upload_report(request):
    """
    Upload and process a medical report
    """
    # Check if file is in request
    file = request.FILES.get('file')
    if not file:
        return Response(
            {'error': 'No file uploaded'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check file extension
    allowed_extensions = ['pdf', 'png', 'jpg', 'jpeg']
    file_extension = file.name.split('.')[-1].lower()
    
    if file_extension not in allowed_extensions:
        return Response(
            {'error': f'File type not supported. Allowed: {", ".join(allowed_extensions)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check file size (10MB max)
    if file.size > 10 * 1024 * 1024:
        return Response(
            {'error': 'File too large. Maximum size: 10MB'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Save file
        saved_path = default_storage.save(
            f'reports/{file.name}', 
            ContentFile(file.read())
        )
        
        # Get the full path
        file_path = default_storage.path(saved_path)
        
        # Re-open file for OCR processing
        with open(file_path, 'rb') as f:
            from django.core.files import File
            file_obj = File(f, name=file.name)
            
            # Extract text using OCR
            extracted_text = OCRProcessor.extract_text(file_obj)
        
        # Process the extracted text to find medical values
        processed_results = ReportProcessor.extract_medical_values(extracted_text)
        summary = ReportProcessor.get_summary(processed_results)
        
        # Extract patient information
        patient_info = extract_patient_info(extracted_text)
        
        # Generate dynamic data
        medications = generate_medications(processed_results)
        follow_up = generate_follow_up(processed_results)
        confidence = generate_confidence(processed_results, extracted_text)
        
        # Create database entry
        report = MedicalReport.objects.create(
            file=saved_path,
            file_name=file.name,
            file_size=file.size,
            extracted_text=extracted_text,
            processed_data={
                'results': processed_results,
                'summary': summary,
                'patient_info': patient_info
            }
        )
        
        # Generate AI Explanation
        ai_explainer = AIExplainer()
        ai_explanation = ai_explainer.generate_explanation(
            processed_results, 
            summary, 
            patient_info
        )
        
        # Prepare response with all dynamic data
        response_data = {
            'id': report.id,
            'file_name': report.file_name,
            'file_size': report.file_size,
            'created_at': report.created_at,
            'extracted_text': extracted_text[:500] + '...' if len(extracted_text) > 500 else extracted_text,
            'processed_data': {
                'results': processed_results,
                'summary': summary,
                'patient_info': patient_info
            },
            'medications': medications,
            'follow_up': follow_up,
            'confidence': confidence,
            'ai_explanation': ai_explanation
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Processing failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )