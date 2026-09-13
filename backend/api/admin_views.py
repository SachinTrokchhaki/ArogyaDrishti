from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import MedicalReport
from .serializers import MedicalReportSerializer


# ============================================================
# ============ ADMIN LOGIN ============
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """Separate login endpoint for admin/staff users only"""
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email and password are required.'}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid email or password.'}, status=401)

    user = authenticate(request, username=user.username, password=password)
    if not user:
        return Response({'error': 'Invalid email or password.'}, status=401)

    if not user.is_staff:
        return Response({
            'error': 'Access denied. You do not have administrator privileges.'
        }, status=403)

    if not user.is_active:
        return Response({'error': 'This account is inactive.'}, status=401)
        
    # ✅ Get avatar URL
    avatar_url = None
    try:
        if user.profile.avatar:
            avatar_url = request.build_absolute_uri(user.profile.avatar.url)
    except Exception:
        pass
    
    refresh = RefreshToken.for_user(user)

    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'avatar': avatar_url,
        },
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'message': 'Admin login successful!'
    })


# ============================================================
# ============ ADMIN STATS ============
# ============================================================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_stats(request):
    """Overview stats for admin dashboard"""
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()

    total_reports = MedicalReport.objects.count()

    week_ago = timezone.now() - timedelta(days=7)
    reports_this_week = MedicalReport.objects.filter(created_at__gte=week_ago).count()

    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    reports_today = MedicalReport.objects.filter(created_at__gte=today_start).count()

    total_abnormal = 0
    for report in MedicalReport.objects.only('processed_data'):
        results = (report.processed_data or {}).get('results', [])
        total_abnormal += sum(1 for r in results if r.get('status') in ['HIGH', 'LOW'])

    daily_activity = []
    for i in range(13, -1, -1):
        day_start = (timezone.now() - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = MedicalReport.objects.filter(created_at__gte=day_start, created_at__lt=day_end).count()
        daily_activity.append({
            'date': day_start.strftime('%d %b'),
            'count': count,
        })

    return Response({
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'total_reports': total_reports,
        'reports_this_week': reports_this_week,
        'reports_today': reports_today,
        'total_abnormal_values': total_abnormal,
        'daily_activity': daily_activity,
    })


# ============================================================
# ============ ADMIN USERS ============
# ============================================================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_users(request):
    """List all users with report counts"""
    search = request.GET.get('search', '').strip()
    filter_type = request.GET.get('filter', 'all')

    users = User.objects.all().order_by('-date_joined')

    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    if filter_type == 'active':
        users = users.filter(is_active=True)
    elif filter_type == 'inactive':
        users = users.filter(is_active=False)
    elif filter_type == 'staff':
        users = users.filter(is_staff=True)

    users = users.annotate(report_count=Count('reports'))

    user_list = []
    for u in users:
        avatar_url = None
        try:
            if u.profile.avatar:
                avatar_url = request.build_absolute_uri(u.profile.avatar.url)
        except Exception:
            pass

        user_list.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'is_active': u.is_active,
            'is_staff': u.is_staff,
            'date_joined': u.date_joined,
            'last_login': u.last_login,
            'report_count': u.report_count,
            'avatar': avatar_url,
        })

    return Response({
        'count': len(user_list),
        'users': user_list,
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_user_detail(request, user_id):
    """Get details of a specific user + their reports"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    reports = MedicalReport.objects.filter(user=user).order_by('-created_at')

    avatar_url = None
    try:
        if user.profile.avatar:
            avatar_url = request.build_absolute_uri(user.profile.avatar.url)
    except Exception:
        pass

    reports_list = []
    for r in reports:
        results = (r.processed_data or {}).get('results', [])
        abnormal_count = sum(1 for x in results if x.get('status') in ['HIGH', 'LOW'])
        reports_list.append({
            'id': r.id,
            'file_name': r.file_name,
            'file_size': r.file_size,
            'created_at': r.created_at,
            'abnormal_count': abnormal_count,
            'total_tests': len(results),
        })

    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
        'avatar': avatar_url,
        'reports': reports_list,
        'report_count': len(reports_list),
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_toggle_user_active(request, user_id):
    """Activate or deactivate a user"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    if user.id == request.user.id:
        return Response({'error': 'You cannot deactivate your own account'}, status=400)

    user.is_active = not user.is_active
    user.save()

    return Response({
        'message': f"User {'activated' if user.is_active else 'deactivated'} successfully!",
        'is_active': user.is_active,
    })


# ============================================================
# ============ ADMIN REPORTS ============
# ============================================================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_reports(request):
    """List all reports"""
    search = request.GET.get('search', '').strip()
    filter_type = request.GET.get('filter', 'all')

    reports = MedicalReport.objects.select_related('user').order_by('-created_at')

    if search:
        reports = reports.filter(
            Q(file_name__icontains=search) |
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search)
        )

    report_list = []
    for r in reports:
        results = (r.processed_data or {}).get('results', [])
        abnormal_count = sum(1 for x in results if x.get('status') in ['HIGH', 'LOW'])
        has_results = len(results) > 0

        if filter_type == 'analyzed' and not has_results:
            continue
        if filter_type == 'processing' and has_results:
            continue

        report_list.append({
            'id': r.id,
            'file_name': r.file_name,
            'file_size': r.file_size,
            'created_at': r.created_at,
            'user_id': r.user.id if r.user else None,
            'username': r.user.username if r.user else 'Unknown',
            'user_email': r.user.email if r.user else 'Unknown',
            'total_tests': len(results),
            'abnormal_count': abnormal_count,
            'status': 'analyzed' if has_results else 'processing',
        })

    return Response({
        'count': len(report_list),
        'reports': report_list,
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_report_detail(request, report_id):
    """Get any report (admin only)"""
    try:
        report = MedicalReport.objects.get(id=report_id)
    except MedicalReport.DoesNotExist:
        return Response({'error': 'Report not found'}, status=404)

    serializer = MedicalReportSerializer(report)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def admin_delete_report(request, report_id):
    """Delete any report (admin only)"""
    try:
        report = MedicalReport.objects.get(id=report_id)
        report.delete()
        return Response({'message': 'Report deleted successfully!'})
    except MedicalReport.DoesNotExist:
        return Response({'error': 'Report not found'}, status=404)