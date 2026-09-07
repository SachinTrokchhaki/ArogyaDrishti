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

from .models import MedicalReport
from .serializers import MedicalReportSerializer
from .utils.ocr import OCRProcessor
from .utils.processor import ReportProcessor

# ============ AUTHENTICATION VIEWS ============

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user
    """
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    password2 = request.data.get('password2')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    
    # Validation
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
        # Password strength validation
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
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Generate tokens
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
    """
    Login user and return JWT tokens
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'error': 'Email and password are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get user by email
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            'error': 'Invalid email or password.'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Authenticate using username and password
    user = authenticate(request, username=user.username, password=password)
    
    if not user:
        return Response({
            'error': 'Invalid email or password.'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.is_active:
        return Response({
            'error': 'This account is inactive.'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Generate tokens
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
    """
    Logout user by blacklisting refresh token
    """
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get current user profile
    """
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'date_joined': user.date_joined,
        'is_active': user.is_active,
    })


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update user profile
    """
    user = request.user
    data = request.data
    
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'username' in data:
        if User.objects.exclude(id=user.id).filter(username=data['username']).exists():
            return Response({
                'error': 'This username is already taken.'
            }, status=status.HTTP_400_BAD_REQUEST)
        user.username = data['username']
    if 'email' in data:
        if User.objects.exclude(id=user.id).filter(email=data['email']).exists():
            return Response({
                'error': 'This email is already registered.'
            }, status=status.HTTP_400_BAD_REQUEST)
        user.email = data['email']
    
    user.save()
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'message': 'Profile updated successfully!'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_reports(request):
    """
    Get all reports for the logged-in user
    """
    reports = MedicalReport.objects.filter(user=request.user).order_by('-created_at')
    serializer = MedicalReportSerializer(reports, many=True)
    return Response({
        'count': reports.count(),
        'reports': serializer.data
    })


# ============ HELPER FUNCTIONS ============

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


# ============ REPORT ANALYSIS VIEWS ============

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
@permission_classes([IsAuthenticated])  # Require authentication for report upload
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
        
        # Create database entry with user association
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
            user=request.user  # Associate with the logged-in user
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