from django.urls import path
from . import views

urlpatterns = [
    # Health check (public)
    path('health/', views.health_check, name='health_check'),
    
    # Report upload (requires authentication)
    path('upload/', views.upload_report, name='upload_report'),
    
    # User reports history
    path('reports/', views.user_reports, name='user_reports'),
    
    # ============ AUTHENTICATION ENDPOINTS ============
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/profile/', views.user_profile, name='profile'),
    path('auth/profile/update/', views.update_profile, name='update_profile'),
]