"""
User Authentication and Profile Models
=======================================
This module handles multi-role user management for the learning platform.

Roles:
- Student: Primary learners using the platform
- Teacher: Educators managing classes and content
- Parent: Guardians monitoring student progress
- Admin: Platform administrators

Each role has a dedicated profile model with role-specific fields.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """
    Extended User model supporting multiple roles.
    
    Why: Django's default User model doesn't support role-based access.
    We extend it to add role identification and common fields.
    """
    
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES,
        help_text="User's primary role in the system"
    )
    
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        help_text="Contact number for notifications"
    )
    
    profile_picture = models.ImageField(
        upload_to='profiles/', 
        blank=True, 
        null=True,
        help_text="User avatar for personalization"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="Email/phone verification status"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class StudentProfile(models.Model):
    """
    Student-specific profile data.
    
    Why: Students need unique fields like grade level, learning preferences,
    and academic goals that don't apply to other roles.
    
    Supports: Personalization engine, learning path generation
    """
    
    LEARNING_STYLE_CHOICES = [
        ('visual', 'Visual Learner'),
        ('reading', 'Reading/Writing Learner'),
        ('practice', 'Practice-Heavy Learner'),
        ('mixed', 'Mixed Learning Style'),
    ]
    
    LEARNING_PACE_CHOICES = [
        ('fast', 'Fast Learner'),
        ('average', 'Average Pace'),
        ('slow', 'Needs More Time'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='student_profile',
        help_text="Link to user account"
    )
    
    # Academic Information
    grade_level = models.CharField(
        max_length=20,
        help_text="Current grade/class (e.g., '10th Grade', 'College Year 1')"
    )
    
    school_name = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Educational institution name"
    )
    
    # Learning Preferences (for AI personalization)
    learning_style = models.CharField(
        max_length=20,
        choices=LEARNING_STYLE_CHOICES,
        default='mixed',
        help_text="Preferred learning method - drives content recommendations"
    )
    
    learning_pace = models.CharField(
        max_length=20,
        choices=LEARNING_PACE_CHOICES,
        default='average',
        help_text="Learning speed - affects difficulty progression"
    )
    
    # Academic Goals
    target_subjects = models.JSONField(
        default=list,
        help_text="List of subjects student wants to focus on"
    )
    
    academic_goals = models.TextField(
        blank=True,
        help_text="Student's learning objectives and aspirations"
    )
    
    # Engagement Tracking
    total_study_time = models.IntegerField(
        default=0,
        help_text="Total minutes spent learning (for analytics)"
    )
    
    current_streak = models.IntegerField(
        default=0,
        help_text="Consecutive days of activity (gamification)"
    )

    has_taken_diagnostic = models.BooleanField(
        default=False,
        help_text="Whether student has completed the initial diagnostic assessment"
    )
    
    longest_streak = models.IntegerField(
        default=0,
        help_text="Best streak achieved (motivation)"
    )
    
    last_active = models.DateTimeField(
        auto_now=True,
        help_text="Last platform interaction (for dropout detection)"
    )
    
    # Parent Connection
    parent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        limit_choices_to={'role': 'parent'},
        help_text="Connected parent account for monitoring"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_profiles'
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.grade_level}"


class TeacherProfile(models.Model):
    """
    Teacher-specific profile data.
    
    Why: Teachers need fields for specialization, experience,
    and class management that are unique to their role.
    
    Supports: Class analytics, teaching recommendations
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        help_text="Link to user account"
    )
    
    # Professional Information
    specialization = models.JSONField(
        default=list,
        help_text="List of subjects/topics teacher specializes in"
    )
    
    qualification = models.CharField(
        max_length=200,
        help_text="Educational qualifications (e.g., 'M.Ed in Mathematics')"
    )
    
    experience_years = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Years of teaching experience"
    )
    
    school_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Current institution"
    )
    
    # Teaching Preferences
    teaching_style = models.TextField(
        blank=True,
        help_text="Description of teaching methodology"
    )
    
    # Platform Stats
    total_students = models.IntegerField(
        default=0,
        help_text="Number of students taught on platform"
    )
    
    total_assessments_created = models.IntegerField(
        default=0,
        help_text="Assessments created (for contribution tracking)"
    )
    
    # Verification
    is_verified_teacher = models.BooleanField(
        default=False,
        help_text="Admin verification status for quality control"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teacher_profiles'
        verbose_name = 'Teacher Profile'
        verbose_name_plural = 'Teacher Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {', '.join(self.specialization[:2])}"


class ParentProfile(models.Model):
    """
    Parent-specific profile data.
    
    Why: Parents need read-only access to monitor their children's
    progress without interfering with the learning process.
    
    Supports: Parent dashboard, progress notifications
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='parent_profile',
        help_text="Link to user account"
    )
    
    # Notification Preferences
    email_notifications = models.BooleanField(
        default=True,
        help_text="Receive email updates about child's progress"
    )
    
    sms_notifications = models.BooleanField(
        default=False,
        help_text="Receive SMS alerts for critical issues"
    )
    
    notification_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily Summary'),
            ('weekly', 'Weekly Report'),
            ('critical', 'Critical Alerts Only'),
        ],
        default='weekly',
        help_text="How often to receive progress updates"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'parent_profiles'
        verbose_name = 'Parent Profile'
        verbose_name_plural = 'Parent Profiles'
    
    def __str__(self):
        children_count = self.user.children.count()
        return f"{self.user.get_full_name()} ({children_count} children)"
