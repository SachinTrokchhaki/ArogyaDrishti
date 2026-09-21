from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .utils.ai_explainer import AIExplainer
from .utils.classifier import classify_document
from .utils.security import validate_upload, scan_for_malware
from .utils.validation import validate_report_data
import os
import re
import json

from .models import MedicalReport, UserProfile
from .serializers import MedicalReportSerializer
from .utils.ocr import OCRProcessor
from .utils.processor import ReportProcessor

import csv
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# ============================================================
# ============ USER PROFILE VIEWS ============
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get user profile with avatar, bio, and phone"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    avatar_url = None
    if profile.avatar:
        avatar_url = request.build_absolute_uri(profile.avatar.url)
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'date_joined': user.date_joined,
        'bio': profile.bio,
        'phone': profile.phone,
        'avatar': avatar_url,
    })


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """Update user profile — email and username cannot be changed"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    data = request.data
    
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'bio' in data:
        profile.bio = data['bio']
    if 'phone' in data:
        profile.phone = data['phone']
    
    user.save()
    profile.save()
    
    avatar_url = None
    if profile.avatar:
        avatar_url = request.build_absolute_uri(profile.avatar.url)
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'bio': profile.bio,
        'phone': profile.phone,
        'avatar': avatar_url,
        'message': 'Profile updated successfully!'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    """Upload user profile picture"""
    try:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        avatar = request.FILES.get('avatar')
        if not avatar:
            return Response({'error': 'No avatar file provided'}, status=400)
        
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if avatar.content_type not in allowed_types:
            return Response(
                {'error': 'Invalid file type. Use JPEG, PNG, GIF, or WEBP'},
                status=400
            )
        
        if avatar.size > 5 * 1024 * 1024:
            return Response({'error': 'File too large. Max 5MB'}, status=400)
        
        if user_profile.avatar:
            try:
                user_profile.avatar.delete(save=False)
            except Exception:
                pass
        
        user_profile.avatar = avatar
        user_profile.save()
        
        avatar_url = request.build_absolute_uri(user_profile.avatar.url)
        
        return Response({
            'message': 'Avatar uploaded successfully!',
            'avatar_url': avatar_url,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change the authenticated user's password."""
    old_password = request.data.get('old_password')
    password = request.data.get('new_password')
    password2 = request.data.get('confirm_password')
    errors = {}

    if not old_password or not request.user.check_password(old_password):
        errors['old_password'] = ['Current password is incorrect.']
    if not password:
        errors['password'] = ['Password is required.']
    elif len(password) < 8:
        errors['password'] = ['Password must be at least 8 characters long.']
    if password != password2:
        errors['password2'] = ['Passwords do not match.']
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    request.user.set_password(password)
    request.user.save(update_fields=['password'])
    return Response({'message': 'Password changed successfully.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a user and return JWT tokens."""
    username = request.data.get('username') or request.data.get('email')
    email = request.data.get('email')
    password = request.data.get('password')
    password2 = request.data.get('password2') or request.data.get('confirm_password')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    errors = {}

    if not username:
        errors['username'] = ['Username is required.']
    if not email:
        errors['email'] = ['Email is required.']
    if not password:
        errors['password'] = ['Password is required.']
    elif len(password) < 8:
        errors['password'] = ['Password must be at least 8 characters long.']
    if password != password2:
        errors['password2'] = ['Passwords do not match.']
    if username and User.objects.filter(username=username).exists():
        errors['username'] = ['A user with this username already exists.']
    if email and User.objects.filter(email=email).exists():
        errors['email'] = ['A user with this email already exists.']
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=username, email=email, password=password,
        first_name=first_name, last_name=last_name,
    )
    refresh = RefreshToken.for_user(user)
    return Response({
        'user': {
            'id': user.id, 'username': user.username, 'email': user.email,
            'first_name': user.first_name, 'last_name': user.last_name,
        },
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'message': 'Registration successful!',
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login user and return JWT tokens"""
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'error': 'Email and password are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            'error': 'Invalid email or password.'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    user = authenticate(request, username=user.username, password=password)
    
    if not user:
        return Response({
            'error': 'Invalid email or password.'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.is_active:
        return Response({
            'error': 'This account is inactive.'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'message': 'Login successful!'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout user by blacklisting refresh token"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({
            'message': 'Logout successful!'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# ============ REPORTS VIEWS ============
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_reports(request):
    """Get all reports for the logged-in user"""
    reports = MedicalReport.objects.filter(user=request.user).order_by('-created_at')
    serializer = MedicalReportSerializer(reports, many=True)
    return Response({
        'count': reports.count(),
        'reports': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_report_detail(request, report_id):
    """Get specific report details"""
    try:
        report = MedicalReport.objects.get(id=report_id, user=request.user)
        serializer = MedicalReportSerializer(report)
        return Response(serializer.data)
    except MedicalReport.DoesNotExist:
        return Response({'error': 'Report not found'}, status=404)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_report(request, report_id):
    """Delete a report"""
    try:
        report = MedicalReport.objects.get(id=report_id, user=request.user)
        report.delete()
        return Response({'message': 'Report deleted successfully!'})
    except MedicalReport.DoesNotExist:
        return Response({'error': 'Report not found'}, status=404)


# ============================================================
# ============ REPORT TREND VIEWS ============
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_trend(request):
    """Get trend data for a specific test across all user's reports."""
    test_name = request.GET.get('test', 'hemoglobin').lower()
    
    reports = MedicalReport.objects.filter(
        user=request.user
    ).order_by('created_at')
    
    trend_data = []
    unit = None
    
    for report in reports:
        processed = report.processed_data or {}
        results = processed.get('results', [])
        
        for r in results:
            r_name = r.get('test_name', '').lower()
            if test_name in r_name or r_name in test_name:
                try:
                    value = float(r.get('value', 0))
                    trend_data.append({
                        'date': report.created_at.strftime('%Y-%m-%d'),
                        'display_date': report.created_at.strftime('%d %b'),
                        'value': value,
                        'status': r.get('status', 'UNKNOWN'),
                        'unit': r.get('unit', ''),
                    })
                    if not unit:
                        unit = r.get('unit', '')
                    break
                except (ValueError, TypeError):
                    pass
    
    return Response({
        'test_name': test_name.capitalize(),
        'unit': unit or '',
        'data': trend_data,
        'count': len(trend_data),
    })


# ============================================================
# ============ PATIENT INFO EXTRACTION (HYBRID) ============
# ============================================================

def extract_patient_info_regex(text):
    """
    Extract patient info using regex (fast, free, works ~70% of the time).
    """
    patient_info = {
        'name': 'Unknown',
        'age': 'Unknown',
        'gender': 'Unknown'
    }
    
    if not text:
        return patient_info
    
    # Clean markdown artifacts
    cleaned = re.sub(r'#+\s*', '', text)
    cleaned = re.sub(r'\*\*(.+?)\*\*', r'\1', cleaned)
    cleaned = re.sub(r'\*(.+?)\*', r'\1', cleaned)
    cleaned = re.sub(r'=+\s*Page \d+\s*=+', '', cleaned)
    
    flat = ' '.join(cleaned.split())
    lines = [ln.strip() for ln in cleaned.split('\n') if ln.strip()]
    
    skip_words = {
        'patient', 'name', 'date', 'report', 'sample', 'hospital',
        'clinic', 'doctor', 'lab', 'test', 'age', 'gender', 'sex',
        'male', 'female', 'registration', 'id', 'mrn', 'uhid', 'pid',
        'laboratory', 'diagnostic', 'center', 'centre', 'medical',
        'no', 'number', 'ref', 'reference', 'collected', 'received',
        'investigation', 'result', 'value', 'unit', 'primary', 'type',
        'complete', 'blood', 'count', 'cbc', 'drlogy', 'www',
        'haemoglobin', 'hemoglobin', 'rbc', 'wbc', 'platelet', 'total',
        'registered', 'reported', 'thanks', 'interpretation', 'instruments',
        'shan', 'shah', 'hiren', 'payal', 'vimal', 'pathologist', 'technician',
        'dr', 'md', 'dmlt', 'bmlt',
    }
    
    def is_valid_name(candidate):
        if not candidate or len(candidate) < 3 or len(candidate) > 50:
            return False
        words = [w.strip('.,;:-') for w in candidate.split()]
        words_lower = [w.lower() for w in words]
        if any(w in skip_words for w in words_lower):
            return False
        if not all(re.match(r'^[A-Z]\.?$|^[A-Za-z][a-z]+$', w) for w in words if w):
            return False
        return True
    
    def clean_name(candidate):
        candidate = re.sub(r'[.,;:\-\s]+$', '', candidate.strip())
        candidate = re.sub(r'\s+', ' ', candidate)
        return ' '.join(
            p.capitalize() if len(p) > 1 else p.upper()
            for p in candidate.split()
        )
    
    # Name patterns
    name_patterns = [
        r'patient\s*(?:name)?\s*[:.\-]?\s*([A-Z][a-zA-Z]+(?:\s+[A-Z]\.?\s+)?[A-Z][a-zA-Z]+)',
        r'\bname\s*[:.\-]?\s*([A-Z][a-zA-Z]+(?:\s+[A-Z]\.?\s+)?[A-Z][a-zA-Z]+)',
    ]
    for pattern in name_patterns:
        match = re.search(pattern, flat)
        if match:
            candidate = match.group(1).strip()
            if is_valid_name(candidate):
                patient_info['name'] = clean_name(candidate)
                break
    
    # Fallback: standalone name line
    if patient_info['name'] == 'Unknown':
        for i, line in enumerate(lines):
            stripped = line.strip()
            if re.match(r'^([A-Z][a-zA-Z]+\.?\s+){1,3}[A-Z][a-zA-Z]+\.?$', stripped):
                next_line = lines[i + 1] if i + 1 < len(lines) else ''
                if re.search(r'\b(?:age|sex|gender|dob|mrn|pid)\b', next_line, re.IGNORECASE):
                    if is_valid_name(stripped):
                        patient_info['name'] = clean_name(stripped)
                        break
    
    # Age
    age_patterns = [
        r'\bage\s*[:.\-]?\s*(\d{1,3})\s*(?:years?|yrs?|y|ears?)?',
        r'\b(\d{1,3})\s*(?:years?|yrs?|y\.?o\.?|y/o|ears?)\s*(?:old)?\b',
        r'\b(\d{1,3})\s*[Yy]\b',
    ]
    for pattern in age_patterns:
        match = re.search(pattern, flat, re.IGNORECASE)
        if match:
            try:
                age_num = int(match.group(1))
                if 0 < age_num <= 120:
                    patient_info['age'] = str(age_num)
                    break
            except (ValueError, TypeError):
                pass
    
    # Gender
    gender_patterns = [
        r'\b(?:sex|gender)\s*[:.\-]?\s*(male|female|m|f|other|non-binary)\b',
        r'\b(?:sex|gender)\s*[:.\-]?\s*\|\s*(male|female|m|f)\b',
        r'\b(Male|Female)\b',
    ]
    for pattern in gender_patterns:
        match = re.search(pattern, flat, re.IGNORECASE)
        if match:
            g = match.group(1).strip().lower()
            if g in ('male', 'm'):
                patient_info['gender'] = 'Male'
                break
            elif g in ('female', 'f'):
                patient_info['gender'] = 'Female'
                break
            elif g == 'other':
                patient_info['gender'] = 'Other'
                break
    
    return patient_info


def extract_patient_info_ai(text):
    """
    Extract patient info using AI (Groq first, Gemini fallback).
    Accurate for any format but slower (~1s).
    """
    try:
        header = text[:1500]
        
        prompt = f"""Extract patient information from this medical report header.

Return ONLY a valid JSON object with these exact keys:
{{"name": "...", "age": "...", "gender": "..."}}

STRICT RULES:
- If a field is not clearly found, use "Unknown"
- Age must be just a number as a string (e.g., "24", not "24 years")
- Gender must be exactly "Male", "Female", or "Other"
- DO NOT confuse doctor names (Dr. X, MD, Pathologist) with the patient
- The patient name is usually near "Age:", "Sex:", "PID:", or "Patient:"
- Ignore addresses, hospital names, and lab names

Report header:
{header}

JSON:"""
        
        # Try Groq first
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key:
            try:
                from groq import Groq
                client = Groq(api_key=groq_key)
                response = client.chat.completions.create(
                    model='qwen/qwen3.8-27b',
                    messages=[
                        {'role': 'system', 'content': 'You extract structured data. Return only valid JSON.'},
                        {'role': 'user', 'content': prompt},
                    ],
                    temperature=0.1,
                    max_tokens=100,
                )
                content = response.choices[0].message.content.strip()
                content = re.sub(r'^```json\s*', '', content)
                content = re.sub(r'^```\s*', '', content)
                content = re.sub(r'\s*```$', '', content)
                result = json.loads(content)
                print(f"✅ AI (Groq) patient info: {result}")
                return {
                    'name': str(result.get('name', 'Unknown') or 'Unknown').strip(),
                    'age': str(result.get('age', 'Unknown') or 'Unknown').strip(),
                    'gender': str(result.get('gender', 'Unknown') or 'Unknown').strip(),
                }
            except Exception as e:
                print(f"⚠️  Groq patient extraction failed: {e}")
        
        # Fallback to Gemini
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            try:
                from google import genai as google_genai
                client = google_genai.Client(api_key=gemini_key)
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt,
                )
                content = response.text.strip()
                content = re.sub(r'^```json\s*', '', content)
                content = re.sub(r'^```\s*', '', content)
                content = re.sub(r'\s*```$', '', content)
                result = json.loads(content)
                print(f"✅ AI (Gemini) patient info: {result}")
                return {
                    'name': str(result.get('name', 'Unknown') or 'Unknown').strip(),
                    'age': str(result.get('age', 'Unknown') or 'Unknown').strip(),
                    'gender': str(result.get('gender', 'Unknown') or 'Unknown').strip(),
                }
            except Exception as e:
                print(f"⚠️  Gemini patient extraction failed: {e}")
    
    except Exception as e:
        print(f"❌ AI patient extraction failed: {e}")
    
    return {'name': 'Unknown', 'age': 'Unknown', 'gender': 'Unknown'}


def extract_patient_info(text):
    """
    Hybrid patient extraction:
    1. Regex first (fast, free)
    2. AI fallback if any field is Unknown
    AI overrides regex when confident.
    """
    # Step 1: Try regex
    info = extract_patient_info_regex(text)
    
    # Step 2: If any field is Unknown, use AI to fill gaps
    missing = [k for k in ('name', 'age', 'gender') if info[k] == 'Unknown']
    
    if missing:
        print(f"🔍 Regex found: {info}")
        print(f"🔍 Missing: {missing} — calling AI...")
        ai_info = extract_patient_info_ai(text)
        
        # Merge: AI takes priority when it finds a value
        for key in ('name', 'age', 'gender'):
            ai_val = ai_info.get(key, 'Unknown')
            if ai_val and ai_val != 'Unknown':
                info[key] = ai_val
        
        print(f"✅ Final patient info: {info}")
    
    return info


# ============================================================
# ============ HELPER FUNCTIONS ============
# ============================================================

def generate_medications(results):
    """Generate medications based on test results"""
    medications = []
    
    if not results:
        return medications
    
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
        
        for r in results:
            test_name = r.get('test_name', '').lower()
            status_val = r.get('status', '')
            
            if status_val == 'HIGH':
                if 'cholesterol' in test_name:
                    follow_up.append("Consider dietary changes and exercise to manage cholesterol levels.")
                if 'glucose' in test_name or 'sugar' in test_name:
                    follow_up.append("Monitor blood sugar levels regularly and consult an endocrinologist.")
                if 'creatinine' in test_name or 'urea' in test_name:
                    follow_up.append("Schedule a kidney function follow-up test.")
                if 'bilirubin' in test_name or 'sgpt' in test_name or 'sgot' in test_name:
                    follow_up.append("Consider a liver function follow-up test.")
            
            if status_val == 'LOW':
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
        'ocr': OCRProcessor.estimate_confidence(extracted_text),
        'extraction': 91,
        'classification': 96
    }
    
    if extracted_text:
        text_length = len(extracted_text)
        if text_length > 1000:
            confidence['ocr'] = 96
        elif text_length > 500:
            confidence['ocr'] = 92
        else:
            confidence['ocr'] = 85
    
    if results:
        if len(results) > 20:
            confidence['extraction'] = 95
        elif len(results) > 10:
            confidence['extraction'] = 90
        else:
            confidence['extraction'] = 80
        
        confidence['classification'] = 94 if len(results) > 15 else 88
    
    return confidence


# ============================================================
# ============ REPORT ANALYSIS VIEWS ============
# ============================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Check if API is running"""
    return Response({
        'status': 'ok',
        'message': 'ArogyaDrishti API is running!',
        'version': '1.0.0'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_report(request):
    """
    Upload and process a medical report.
    - Validates upload
    - Runs OCR + classification + extraction
    - Extracts patient info (regex + AI fallback)
    - Generates AI explanation
    - SAVES file to disk AND report to database
    """
    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        content = file.read()
        
        # 1. Validate upload
        valid, validation_error = validate_upload(file.name, file.content_type, content)
        if not valid:
            return Response({'error': validation_error}, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. Optional malware scan
        clean, scan_message = scan_for_malware(content)
        if not clean:
            return Response({'error': scan_message}, status=status.HTTP_400_BAD_REQUEST)
        
        # 3. Save file to disk
        saved_path = default_storage.save(
            f'reports/{file.name}',
            ContentFile(content)
        )
        
        # 4. OCR extraction
        from django.core.files import File
        from io import BytesIO
        file_obj = File(BytesIO(content), name=file.name)
        extracted_text, ocr_confidence = OCRProcessor.extract_text_with_confidence(file_obj)
        
        # 5. Classify document type
        classification = classify_document(extracted_text)
        
        # 6. Extract structured medical values
        processed_results = ReportProcessor.extract_medical_values(extracted_text)
        summary = ReportProcessor.get_summary(processed_results)
        
        # 7. Extract patient info (hybrid: regex + AI fallback)
        patient_info = extract_patient_info(extracted_text)
        
        # 8. Validate report data
        validation = validate_report_data(
            classification['document_type'],
            processed_results,
            summary,
            extracted_text
        )
        
        # 9. Generate medications, follow-up, confidence
        medications = generate_medications(processed_results)
        follow_up = generate_follow_up(processed_results)
        confidence = generate_confidence(processed_results, extracted_text)
        confidence['ocr'] = ocr_confidence
        confidence['classification'] = classification['confidence']
        
        # 10. Generate AI explanation
        ai_explainer = AIExplainer()
        ai_explanation = ai_explainer.generate_explanation(
            processed_results,
            summary,
            patient_info
        )
        
        # 11. Prepare processed_data
        processed_data = {
            'results': processed_results,
            'summary': summary,
            'patient_info': patient_info,
            'document_type': classification['document_type'],
            'classification': classification,
            'validation': validation,
            'privacy': {
                'malware_scan': scan_message,
            },
        }
        
        # 12. Save to database
        report = MedicalReport.objects.create(
            file=saved_path,
            file_name=file.name,
            file_size=file.size,
            extracted_text=extracted_text,
            processed_data=processed_data,
            ai_explanation=ai_explanation,
            medications=medications,
            follow_up=follow_up,
            confidence=confidence,
            user=request.user
        )
        
        # 13. Return full response
        response_data = {
            'id': report.id,
            'file_name': file.name,
            'file_size': file.size,
            'created_at': report.created_at,
            'extracted_text': extracted_text[:500] + '...' if len(extracted_text) > 500 else extracted_text,
            'processed_data': processed_data,
            'medications': medications,
            'follow_up': follow_up,
            'confidence': confidence,
            'ai_explanation': ai_explanation
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Processing failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================
# ============ REPORT EXPORT VIEWS ============
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_report_csv(request, report_id):
    """Export report as CSV"""
    try:
        report = MedicalReport.objects.get(id=report_id, user=request.user)
    except MedicalReport.DoesNotExist:
        return Response({'error': 'Report not found'}, status=404)
    
    processed = report.processed_data or {}
    results = processed.get('results', [])
    patient_info = processed.get('patient_info', {})
    
    response = HttpResponse(content_type='text/csv')
    filename = f"report_{report.id}_{report.created_at.strftime('%Y%m%d')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    writer.writerow(['ArogyaDrishti - Medical Report'])
    writer.writerow([])
    writer.writerow(['Patient Name', patient_info.get('name', 'Unknown')])
    writer.writerow(['Age', patient_info.get('age', 'Unknown')])
    writer.writerow(['Gender', patient_info.get('gender', 'Unknown')])
    writer.writerow(['Report Date', report.created_at.strftime('%Y-%m-%d')])
    writer.writerow(['File', report.file_name])
    writer.writerow([])
    
    writer.writerow(['Test Name', 'Value', 'Unit', 'Reference Range', 'Status'])
    for r in results:
        ref = '—'
        if r.get('min_range') is not None and r.get('max_range') is not None:
            ref = f"{r.get('min_range')} – {r.get('max_range')}"
        
        writer.writerow([
            r.get('test_name', ''),
            r.get('value', ''),
            r.get('unit', ''),
            ref,
            r.get('status', ''),
        ])
    
    writer.writerow([])
    writer.writerow(['Summary'])
    summary = processed.get('summary', {})
    writer.writerow(['Total Tests', summary.get('total_tests', 0)])
    writer.writerow(['Normal', summary.get('normal', 0)])
    writer.writerow(['High', summary.get('high', 0)])
    writer.writerow(['Low', summary.get('low', 0)])
    
    ai_exp = report.ai_explanation or {}
    if ai_exp.get('explanation'):
        writer.writerow([])
        writer.writerow(['AI Explanation'])
        explanation = ai_exp['explanation'].replace('##', '').replace('**', '').replace('###', '')
        writer.writerow([explanation])
    
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_report_pdf(request, report_id):
    """Export report as PDF"""
    try:
        report = MedicalReport.objects.get(id=report_id, user=request.user)
    except MedicalReport.DoesNotExist:
        return Response({'error': 'Report not found'}, status=404)
    
    processed = report.processed_data or {}
    results = processed.get('results', [])
    summary = processed.get('summary', {})
    patient_info = processed.get('patient_info', {})
    medications = report.medications or []
    follow_up = report.follow_up or []
    ai_exp = report.ai_explanation or {}
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm,
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#0d5c63'),
        spaceAfter=4,
        alignment=TA_LEFT,
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=12,
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=12,
        spaceAfter=6,
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#475569'),
        leading=13,
    )
    
    story = []
    
    story.append(Paragraph("♥ ArogyaDrishti", title_style))
    story.append(Paragraph("REPORT ANALYSIS · Medical Report Summary", subtitle_style))
    
    meta_data = [
        ['Patient', patient_info.get('name', 'Unknown'),
         'Age', str(patient_info.get('age', 'Unknown'))],
        ['Gender', patient_info.get('gender', 'Unknown'),
         'Date', report.created_at.strftime('%d %b %Y')],
        ['File', report.file_name, 'Status', 'Analyzed'],
    ]
    meta_table = Table(meta_data, colWidths=[25*mm, 60*mm, 25*mm, 60*mm])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor('#0f172a')),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8*mm))
    
    story.append(Paragraph("Summary", h2_style))
    summary_data = [
        ['Total Tests', 'Normal', 'High', 'Low'],
        [
            str(summary.get('total_tests', 0)),
            str(summary.get('normal', 0)),
            str(summary.get('high', 0)),
            str(summary.get('low', 0)),
        ]
    ]
    summary_table = Table(summary_data, colWidths=[42.5*mm]*4)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0fdfa')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0d5c63')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 16),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#0f172a')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 6*mm))
    
    story.append(Paragraph("Lab Results", h2_style))
    
    results_data = [['Test Name', 'Value', 'Unit', 'Reference', 'Status']]
    for r in results:
        ref = '—'
        if r.get('min_range') is not None and r.get('max_range') is not None:
            ref = f"{r.get('min_range')} – {r.get('max_range')}"
        
        status = r.get('status', '')
        results_data.append([
            Paragraph(r.get('test_name', ''), body_style),
            str(r.get('value', '')),
            r.get('unit', ''),
            ref,
            status,
        ])
    
    results_table = Table(
        results_data,
        colWidths=[60*mm, 25*mm, 25*mm, 40*mm, 25*mm],
        repeatRows=1,
    )
    
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d5c63')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]
    
    for i, r in enumerate(results, start=1):
        status = r.get('status', '').upper()
        if status == 'HIGH':
            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#fef2f2')))
            table_style.append(('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#dc2626')))
        elif status == 'LOW':
            table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#eff6ff')))
            table_style.append(('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#2563eb')))
    
    results_table.setStyle(TableStyle(table_style))
    story.append(results_table)
    story.append(Spacer(1, 6*mm))
    
    if ai_exp.get('explanation'):
        story.append(Paragraph("AI Explanation", h2_style))
        text = ai_exp['explanation']
        lines = text.split('\n')
        for line in lines:
            stripped = line.strip()
            if not stripped:
                story.append(Spacer(1, 2*mm))
                continue
            
            if stripped.startswith('## '):
                story.append(Paragraph(stripped[3:], h2_style))
            elif stripped.startswith('### '):
                story.append(Paragraph(stripped[4:], h2_style))
            elif stripped.startswith('* ') or stripped.startswith('- '):
                story.append(Paragraph(f"• {stripped[2:].replace('**', '')}", body_style))
            else:
                clean = stripped.replace('**', '')
                story.append(Paragraph(clean, body_style))
        story.append(Spacer(1, 4*mm))
    
    if medications and medications[0].get('name') != 'No medications detected':
        story.append(Paragraph("Medications", h2_style))
        med_data = [['Medication', 'Dosage', 'Frequency', 'Instructions']]
        for med in medications:
            med_data.append([
                med.get('name', ''),
                med.get('dosage', ''),
                med.get('frequency', ''),
                med.get('instructions', ''),
            ])
        
        med_table = Table(med_data, colWidths=[40*mm, 25*mm, 35*mm, 75*mm], repeatRows=1)
        med_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d5c63')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        story.append(med_table)
        story.append(Spacer(1, 4*mm))
    
    if follow_up:
        story.append(Paragraph("Recommended Follow-up", h2_style))
        for item in follow_up:
            story.append(Paragraph(f"• {item}", body_style))
        story.append(Spacer(1, 4*mm))
    
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#92400e'),
        leading=12,
        backColor=colors.HexColor('#fffbeb'),
        borderPadding=8,
        borderColor=colors.HexColor('#fde68a'),
        borderWidth=1,
        borderRadius=4,
    )
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "<b>Disclaimer:</b> This report is generated by ArogyaDrishti for educational purposes "
        "only and is not a medical diagnosis. Always consult a qualified healthcare professional "
        "for medical advice.",
        disclaimer_style
    ))
    
    doc.build(story)
    
    buffer.seek(0)
    filename = f"report_{report.id}_{report.created_at.strftime('%Y%m%d')}.pdf"
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response