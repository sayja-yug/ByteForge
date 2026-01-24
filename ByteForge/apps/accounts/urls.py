"""
Accounts App URLs
=================
URL patterns for authentication and user management.
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Registration
    path('register/', views.register_choice, name='register_choice'),
    path('register/student/', views.register_student, name='register_student'),
    path('register/teacher/', views.register_teacher, name='register_teacher'),
    path('register/parent/', views.register_parent, name='register_parent'),
    
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/parent/', views.parent_dashboard, name='parent_dashboard'),
    path('dashboard/parent/guide/support/', views.parent_support_guide, name='parent_support_guide'),
    path('dashboard/parent/guide/progress/', views.parent_progress_guide, name='parent_progress_guide'),
    
    path('connect-child/', views.connect_child, name='connect_child'),
    
    # Teacher Features
    path('teacher/mark-entry/', views.teacher_mark_entry, name='teacher_mark_entry'),
]
