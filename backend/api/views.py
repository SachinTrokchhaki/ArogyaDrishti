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
import os
import re
import time

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
    
    # Email and username are intentionally NOT updated here
    
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
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if avatar.content_type not in allowed_types:
            return Response(
                {'error': 'Invalid file type. Use JPEG, PNG, GIF, or WEBP'},
                status=400
            )
        
        # Validate file size (5MB max)
        if avatar.size > 5 * 1024 * 1024:
            return Response({'error': 'File too large. Max 5MB'}, status=400)
        
        # Delete old avatar file (don't fail if it doesn't exist)
        if user_profile.avatar:
            try:
                user_profile.avatar.delete(save=False)
            except Exception:
                pass
        
        # Save new avatar
        user_profile.avatar = avatar
        user_profile.save()
        
        # Build full URL with cache-busting timestamp
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
    """Change user password"""
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    if not old_password or not new_password or not confirm_password:
        return Response({'error': 'All fields are required'}, status=400)
    
    if not user.check_password(old_password):
        return Response({'error': 'Current password is incorrect'}, status=400)
    
    if new_password != confirm_password:
        return Response({'error': 'New passwords do not match'}, status=400)
    
    if len(new_password) < 8:
        return Response({'error': 'Password must be at least 8 characters'}, status=400)
    
    if not re.search(r'[A-Z]', new_password):
        return Response({'error': 'Must contain uppercase letter'}, status=400)
    
    if not re.search(r'[a-z]', new_password):
        return Response({'error': 'Must contain lowercase letter'}, status=400)
    
    if not re.search(r'\d', new_password):
        return Response({'error': 'Must contain a number'}, status=400)
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
        return Response({'error': 'Must contain special character'}, status=400)
    
    user.set_password(new_password)
    user.save()
    
    return Response({'message': 'Password changed successfully!'})


# ============================================================
# ============ AUTHENTICATION VIEWS ============
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    password2 = request.data.get('password2')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    
    errors = {}
    
    if not username:
        errors['username'] = ['Username is required.']
    elif User.objects.filter(username=username).exists():
        errors['username'] = ['This username is already taken.']
    
    if not email:
        errors['email'] = ['Email is required.']
    elif User.objects.filter(email=email).exists():
        errors['email'] = ['This email is already registered.']
    
    if not password:
        errors['password'] = ['Password is required.']
    else:
        if len(password) < 8:
            errors['password'] = ['Password must be at least 8 characters long.']
        elif not re.search(r'[A-Z]', password):
            errors['password'] = ['Password must contain at least one uppercase letter.']
        elif not re.search(r'[a-z]', password):
            errors['password'] = ['Password must contain at least one lowercase letter.']
        elif not re.search(r'\d', password):
            errors['password'] = ['Password must contain at least one number.']
        elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors['password'] = ['Password must contain at least one special character.']
    
    if not password2:
        errors['password2'] = ['Please confirm your password.']
    elif password and password != password2:
        errors['password2'] = ['Passwords do not match.']
    
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
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
            'message': 'Registration successful!'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Registration failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
# ============ HELPER FUNCTIONS ============
# ============================================================

def extract_patient_info(text):
    """Extract patient information from report text"""
    patient_info = {
        'name': 'Unknown',
        'age': 'Unknown',
        'gender': 'Unknown'
    }
    
    if not text:
        return patient_info
    
    text = ' '.join(text.split())
    
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
        'ocr': 94,
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
    """Upload and process a medical report"""
    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
    
    allowed_extensions = ['pdf', 'png', 'jpg', 'jpeg']
    file_extension = file.name.split('.')[-1].lower()
    
    if file_extension not in allowed_extensions:
        return Response(
            {'error': f'File type not supported. Allowed: {", ".join(allowed_extensions)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if file.size > 10 * 1024 * 1024:
        return Response({'error': 'File too large. Maximum size: 10MB'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        saved_path = default_storage.save(f'reports/{file.name}', ContentFile(file.read()))
        file_path = default_storage.path(saved_path)
        
        with open(file_path, 'rb') as f:
            from django.core.files import File
            file_obj = File(f, name=file.name)
            extracted_text = OCRProcessor.extract_text(file_obj)
        
        processed_results = ReportProcessor.extract_medical_values(extracted_text)
        summary = ReportProcessor.get_summary(processed_results)
        patient_info = extract_patient_info(extracted_text)
        
        medications = generate_medications(processed_results)
        follow_up = generate_follow_up(processed_results)
        confidence = generate_confidence(processed_results, extracted_text)
        
        ai_explainer = AIExplainer()
        ai_explanation = ai_explainer.generate_explanation(
            processed_results, 
            summary, 
            patient_info
        )
        
        report = MedicalReport.objects.create(
            file=saved_path,
            file_name=file.name,
            file_size=file.size,
            extracted_text=extracted_text,
            processed_data={
                'results': processed_results,
                'summary': summary,
                'patient_info': patient_info
            },
            ai_explanation=ai_explanation,
            medications=medications,
            follow_up=follow_up,
            confidence=confidence,
            user=request.user
        )
        
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
    
    # Create CSV
    response = HttpResponse(content_type='text/csv')
    filename = f"report_{report.id}_{report.created_at.strftime('%Y%m%d')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    # Header
    writer.writerow(['ArogyaDrishti - Medical Report'])
    writer.writerow([])
    writer.writerow(['Patient Name', patient_info.get('name', 'Unknown')])
    writer.writerow(['Age', patient_info.get('age', 'Unknown')])
    writer.writerow(['Gender', patient_info.get('gender', 'Unknown')])
    writer.writerow(['Report Date', report.created_at.strftime('%Y-%m-%d')])
    writer.writerow(['File', report.file_name])
    writer.writerow([])
    
    # Results table
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
    
    # Summary
    writer.writerow([])
    writer.writerow(['Summary'])
    summary = processed.get('summary', {})
    writer.writerow(['Total Tests', summary.get('total_tests', 0)])
    writer.writerow(['Normal', summary.get('normal', 0)])
    writer.writerow(['High', summary.get('high', 0)])
    writer.writerow(['Low', summary.get('low', 0)])
    
    # AI explanation (stripped of markdown)
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
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm,
    )
    
    # Styles
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
    
    # Build content
    story = []
    
    # Header
    story.append(Paragraph("♥ ArogyaDrishti", title_style))
    story.append(Paragraph("REPORT ANALYSIS · Medical Report Summary", subtitle_style))
    
    # Meta info
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
    
    # Summary stats
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
    
    # Lab Results table
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
    
    # Color abnormal rows
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
    
    # AI Explanation
    if ai_exp.get('explanation'):
        story.append(Paragraph("AI Explanation", h2_style))
        # Clean markdown
        text = ai_exp['explanation']
        # Convert markdown headings
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
                # Replace bold markdown
                clean = stripped.replace('**', '')
                story.append(Paragraph(clean, body_style))
        story.append(Spacer(1, 4*mm))
    
    # Medications
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
    
    # Follow-up
    if follow_up:
        story.append(Paragraph("Recommended Follow-up", h2_style))
        for item in follow_up:
            story.append(Paragraph(f"• {item}", body_style))
        story.append(Spacer(1, 4*mm))
    
    # Disclaimer
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
    
    # Build PDF
    doc.build(story)
    
    # Return PDF
    buffer.seek(0)
    filename = f"report_{report.id}_{report.created_at.strftime('%Y%m%d')}.pdf"
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response