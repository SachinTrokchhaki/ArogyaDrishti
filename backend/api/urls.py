from django.urls import path
from . import views, admin_views

urlpatterns = [
    # ============ HEALTH ============
    path('health/', views.health_check, name='health_check'),

    # ============ USER AUTH ============
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),

    # ============ USER PROFILE ============
    path('auth/profile/', views.get_user_profile, name='get_user_profile'),
    path('auth/profile/update/', views.update_user_profile, name='update_user_profile'),
    path('auth/profile/upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('auth/change-password/', views.change_password, name='change_password'),

    # ============ USER REPORTS ============
    path('upload/', views.upload_report, name='upload_report'),
    path('reports/', views.user_reports, name='user_reports'),
    path('reports/trend/', views.report_trend, name='report_trend'),
    path('reports/<int:report_id>/', views.get_report_detail, name='report_detail'),
    path('reports/<int:report_id>/delete/', views.delete_report, name='delete_report'),
    path('reports/<int:report_id>/export/csv/', views.export_report_csv, name='export_report_csv'),
    path('reports/<int:report_id>/export/pdf/', views.export_report_pdf, name='export_report_pdf'),

    # ============ ADMIN ============
    path('admin/login/', admin_views.admin_login, name='admin_login'),
    path('admin/stats/', admin_views.admin_stats, name='admin_stats'),
    path('admin/users/', admin_views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/', admin_views.admin_user_detail, name='admin_user_detail'),
    path('admin/users/<int:user_id>/toggle-active/', admin_views.admin_toggle_user_active, name='admin_toggle_user_active'),
    path('admin/reports/', admin_views.admin_reports, name='admin_reports'),
    path('admin/reports/<int:report_id>/', admin_views.admin_report_detail, name='admin_report_detail'),
    path('admin/reports/<int:report_id>/delete/', admin_views.admin_delete_report, name='admin_delete_report'),
]