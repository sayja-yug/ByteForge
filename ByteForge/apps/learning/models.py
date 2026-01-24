"""
Learning Content and Activity Models
====================================
This module manages the core learning content structure and tracks
student interactions with learning materials.

Key Components:
- Subject/Topic hierarchy
- Learning resources (videos, articles, PDFs)
- Student activity tracking
- Performance monitoring
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import User, StudentProfile, TeacherProfile


class Subject(models.Model):
    """
    Top-level academic subject.
    
    Why: Organizes content hierarchically (Subject → Topic → Subtopic)
    
    Supports: Learning path generation, subject-wise analytics
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Subject name (e.g., 'Mathematics', 'Physics')"
    )
    
    description = models.TextField(
        help_text="Subject overview and learning objectives"
    )
    
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon class for UI (e.g., 'fas fa-calculator')"
    )
    
    color_code = models.CharField(
        max_length=7,
        default='#3498db',
        help_text="Hex color for visual identification"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether subject is currently offered"
    )
    
    grade_level = models.CharField(
        max_length=50,
        default='all',
        help_text="Grade level (e.g., '9th', '10th', '11th', 'all')"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_subjects',
        help_text="Teacher who created this subject"
    )
    
    class Meta:
        db_table = 'subjects'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Topic(models.Model):
    """
    Subject subdivision (e.g., 'Algebra' under 'Mathematics').
    
    Why: Enables granular progress tracking and targeted recommendations
    
    Supports: Topic-wise analytics, knowledge gap identification
    """
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='topics',
        help_text="Parent subject"
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Topic name (e.g., 'Linear Equations')"
    )
    
    description = models.TextField(
        help_text="What students will learn in this topic"
    )
    
    difficulty_level = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='beginner',
        help_text="Base difficulty - used for adaptive learning"
    )
    
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='dependent_topics',
        help_text="Topics that should be learned first"
    )
    
    estimated_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        help_text="Expected time to master this topic"
    )
    
    order = models.IntegerField(
        default=0,
        help_text="Display order within subject"
    )
    
    grade_level = models.CharField(
        max_length=50,
        default='all',
        help_text="Grade level (e.g., '9th', '10th', '11th', 'all')"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_topics',
        help_text="Teacher who created this topic"
    )
    
    class Meta:
        db_table = 'topics'
        ordering = ['subject', 'order', 'name']
        unique_together = ['subject', 'name']
    
    def __str__(self):
        return f"{self.subject.name} - {self.name}"


class LearningResource(models.Model):
    """
    Individual learning materials (videos, PDFs, articles, etc.).
    
    Why: Provides diverse content formats to match student preferences
    
    Supports: Personalized resource recommendations, learning style matching
    """
    
    RESOURCE_TYPE_CHOICES = [
        ('video', 'Video Tutorial'),
        ('article', 'Article/Blog'),
        ('pdf', 'PDF Document'),
        ('quiz', 'Practice Quiz'),
        ('project', 'Hands-on Project'),
        ('interactive', 'Interactive Demo'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='resources',
        help_text="Associated topic"
    )
    
    title = models.CharField(
        max_length=300,
        help_text="Resource title"
    )
    
    description = models.TextField(
        help_text="What this resource covers"
    )
    
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPE_CHOICES,
        help_text="Content format - matches learning styles"
    )
    
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium',
        help_text="Resource difficulty for adaptive recommendations"
    )
    
    # Content Location
    url = models.URLField(
        blank=True,
        help_text="External link (YouTube, article, etc.)"
    )
    
    file = models.FileField(
        upload_to='resources/',
        blank=True,
        null=True,
        help_text="Uploaded file (PDF, etc.)"
    )
    
    # Metadata
    duration_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text="Estimated time to complete (for videos/articles)"
    )
    
    author = models.CharField(
        max_length=200,
        blank=True,
        help_text="Content creator"
    )
    
    # Quality Metrics
    view_count = models.IntegerField(
        default=0,
        help_text="Number of times accessed"
    )
    
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="User ratings (0-5 stars)"
    )
    
    # Curation
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_resources',
        help_text="Teacher who added this resource"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="Admin-approved quality content"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_resources'
        ordering = ['-average_rating', '-view_count']
    
    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"


class LearningActivity(models.Model):
    """
    Tracks every student interaction with learning content.
    
    Why: Critical for AI recommendations - analyzes behavior patterns,
    engagement, and learning pace.
    
    Supports: Personalization engine, dropout detection, time analytics
    """
    
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='activities',
        help_text="Student performing the activity"
    )
    
    resource = models.ForeignKey(
        LearningResource,
        on_delete=models.CASCADE,
        related_name='activities',
        help_text="Resource being studied"
    )
    
    # Activity Tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='started',
        help_text="Current activity state"
    )
    
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When student began this resource"
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When student finished (null if incomplete)"
    )
    
    time_spent_minutes = models.IntegerField(
        default=0,
        help_text="Total time spent on this resource"
    )
    
    # Engagement Metrics
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="How much of the resource was consumed"
    )
    
    revisit_count = models.IntegerField(
        default=0,
        help_text="Number of times student returned to this resource"
    )
    
    # Feedback
    rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Student's rating of this resource"
    )
    
    feedback = models.TextField(
        blank=True,
        help_text="Student's comments about the resource"
    )
    
    # AI Analysis
    was_helpful = models.BooleanField(
        null=True,
        blank=True,
        help_text="Did this resource help the student? (for recommendations)"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_activities'
        ordering = ['-started_at']
        verbose_name_plural = 'Learning Activities'
    
    def __str__(self):
        return f"{self.student.user.username} - {self.resource.title}"


class StudentPerformance(models.Model):
    """
    Tracks academic performance and test scores.
    
    Why: Core data for AI recommendations - identifies strengths,
    weaknesses, and learning trends.
    
    Supports: Knowledge gap detection, difficulty adaptation, progress tracking
    """
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='performances',
        help_text="Student being evaluated"
    )
    
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='performances',
        help_text="Topic being assessed"
    )
    
    # Performance Metrics
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score achieved (0-100)"
    )
    
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100,
        help_text="Maximum possible score"
    )
    
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Calculated percentage"
    )
    
    # Context
    assessment_type = models.CharField(
        max_length=50,
        choices=[
            ('quiz', 'Quiz'),
            ('test', 'Test'),
            ('assignment', 'Assignment'),
            ('project', 'Project'),
            ('exam', 'Exam'),
        ],
        help_text="Type of assessment"
    )
    
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
        ],
        help_text="Assessment difficulty"
    )
    
    # Timing
    time_taken_minutes = models.IntegerField(
        help_text="Time spent on assessment"
    )
    
    assessed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When assessment was completed"
    )
    
    # Analysis
    strengths = models.JSONField(
        default=list,
        help_text="Subtopics where student excelled"
    )
    
    weaknesses = models.JSONField(
        default=list,
        help_text="Subtopics needing improvement"
    )
    
    teacher_feedback = models.TextField(
        blank=True,
        help_text="Teacher's comments"
    )
    
    class Meta:
        db_table = 'student_performances'
        ordering = ['-assessed_at']
        verbose_name_plural = 'Student Performances'
    
    def save(self, *args, **kwargs):
        # Auto-calculate percentage
        if self.max_score > 0:
            self.percentage = (self.score / self.max_score) * 100
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.user.username} - {self.topic.name}: {self.percentage}%"
