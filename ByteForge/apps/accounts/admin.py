"""
Admin Panel Configuration for User Accounts
============================================
Customized admin interfaces for User and Profile models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentProfile, TeacherProfile, ParentProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced User admin with role-based filtering"""
    
    list_display = ['username', 'email', 'role', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['role', 'is_verified', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'phone', 'profile_picture', 'is_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'email', 'phone')
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Student profile management"""
    
    list_display = ['user', 'grade_level', 'learning_style', 'learning_pace', 'current_streak', 'last_active']
    list_filter = ['learning_style', 'learning_pace', 'grade_level']
    search_fields = ['user__username', 'user__email', 'school_name']
    
    fieldsets = [
        ('User Information', {
            'fields': ['user']
        }),
        ('Academic Information', {
            'fields': ['grade_level', 'school_name', 'target_subjects', 'academic_goals']
        }),
        ('Learning Preferences', {
            'fields': ['learning_style', 'learning_pace']
        }),
        ('Engagement Metrics', {
            'fields': ['total_study_time', 'current_streak', 'longest_streak', 'last_active']
        }),
        ('Parent Connection', {
            'fields': ['parent']
        }),
    ]
    
    readonly_fields = ['last_active']


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    """Teacher profile management"""
    
    list_display = ['user', 'experience_years', 'is_verified_teacher', 'total_students', 'total_assessments_created']
    list_filter = ['is_verified_teacher', 'experience_years']
    search_fields = ['user__username', 'user__email', 'school_name', 'qualification']
    
    fieldsets = [
        ('User Information', {
            'fields': ['user']
        }),
        ('Professional Information', {
            'fields': ['specialization', 'qualification', 'experience_years', 'school_name']
        }),
        ('Teaching Details', {
            'fields': ['teaching_style']
        }),
        ('Platform Statistics', {
            'fields': ['total_students', 'total_assessments_created']
        }),
        ('Verification', {
            'fields': ['is_verified_teacher']
        }),
    ]
    
    actions = ['verify_teachers']
    
    def verify_teachers(self, request, queryset):
        """Bulk verify teachers"""
        updated = queryset.update(is_verified_teacher=True)
        self.message_user(request, f'{updated} teacher(s) verified successfully.')
    verify_teachers.short_description = 'Verify selected teachers'


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    """Parent profile management"""
    
    list_display = ['user', 'email_notifications', 'sms_notifications', 'notification_frequency', 'children_count']
    list_filter = ['email_notifications', 'sms_notifications', 'notification_frequency']
    search_fields = ['user__username', 'user__email']
    
    fieldsets = [
        ('User Information', {
            'fields': ['user']
        }),
        ('Notification Preferences', {
            'fields': ['email_notifications', 'sms_notifications', 'notification_frequency']
        }),
    ]
    
    def children_count(self, obj):
        """Display number of connected children"""
        return obj.user.children.count()
    children_count.short_description = 'Children'
