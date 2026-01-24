"""
AI Recommendation System Models
================================
This module handles personalized learning recommendations,
adaptive learning paths, and student feedback.

Core AI Features:
- Personalized resource recommendations
- Adaptive learning paths
- Knowledge gap identification
- Continuous feedback loop
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import StudentProfile
from apps.learning.models import Topic, LearningResource


class Recommendation(models.Model):
    """
    AI-generated personalized recommendations for students.
    
    Why: Core of the personalization engine - suggests resources
    based on performance, behavior, and preferences.
    
    Supports: Explainable AI (shows WHY recommendation was made)
    """
    
    RECOMMENDATION_TYPE_CHOICES = [
        ('resource', 'Learning Resource'),
        ('topic', 'Topic to Study'),
        ('revision', 'Revision Reminder'),
        ('practice', 'Practice Exercise'),
        ('project', 'Hands-on Project'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('urgent', 'Urgent'),
    ]
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='recommendations',
        help_text="Student receiving recommendation"
    )
    
    recommendation_type = models.CharField(
        max_length=20,
        choices=RECOMMENDATION_TYPE_CHOICES,
        help_text="Type of recommendation"
    )
    
    # Recommended Content
    resource = models.ForeignKey(
        LearningResource,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='recommendations',
        help_text="Recommended resource (if type is 'resource')"
    )
    
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='recommendations',
        help_text="Recommended topic (if type is 'topic')"
    )
    
    # Recommendation Details
    title = models.CharField(
        max_length=300,
        help_text="Recommendation title"
    )
    
    description = models.TextField(
        help_text="What student should do"
    )
    
    # EXPLAINABLE AI - Critical for judges and users
    reason = models.TextField(
        help_text="WHY this recommendation was made (transparency)"
    )
    
    reasoning_factors = models.JSONField(
        default=dict,
        help_text="Data points used in recommendation logic (e.g., {'low_score': 45, 'topic': 'Algebra'})"
    )
    
    # Priority & Timing
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Urgency level"
    )
    
    recommended_date = models.DateField(
        help_text="When to show this recommendation"
    )
    
    expires_at = models.DateField(
        null=True,
        blank=True,
        help_text="When recommendation becomes irrelevant"
    )
    
    # Engagement Tracking
    is_viewed = models.BooleanField(
        default=False,
        help_text="Has student seen this?"
    )
    
    is_acted_upon = models.BooleanField(
        default=False,
        help_text="Did student follow the recommendation?"
    )
    
    viewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When student viewed recommendation"
    )
    
    acted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When student took action"
    )
    
    # Feedback Loop
    was_helpful = models.BooleanField(
        null=True,
        blank=True,
        help_text="Student feedback - improves future recommendations"
    )
    
    student_feedback = models.TextField(
        blank=True,
        help_text="Student's comments on recommendation"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'recommendations'
        ordering = ['-priority', '-recommended_date']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.title}"


class LearningPath(models.Model):
    """
    Personalized learning roadmap for each student.
    
    Why: Provides structured progression through topics based on
    student's level, goals, and performance.
    
    Supports: Adaptive difficulty, prerequisite tracking, goal achievement
    """
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='learning_paths',
        help_text="Student following this path"
    )
    
    # Path Definition
    name = models.CharField(
        max_length=200,
        help_text="Path name (e.g., 'Master Algebra')"
    )
    
    description = models.TextField(
        help_text="What this path will achieve"
    )
    
    topics = models.ManyToManyField(
        Topic,
        through='LearningPathStep',
        related_name='learning_paths',
        help_text="Topics in this learning path"
    )
    
    # Progress Tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started',
        help_text="Current path status"
    )
    
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall completion percentage"
    )
    
    current_step = models.IntegerField(
        default=1,
        help_text="Which step student is currently on"
    )
    
    # Timing
    estimated_completion_days = models.IntegerField(
        help_text="Expected days to complete path"
    )
    
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When student began this path"
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When student finished path"
    )
    
    # AI Generation
    is_ai_generated = models.BooleanField(
        default=True,
        help_text="Was this path auto-generated by AI?"
    )
    
    generation_criteria = models.JSONField(
        default=dict,
        help_text="Factors used to create this path (for transparency)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_paths'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.name}"


class LearningPathStep(models.Model):
    """
    Individual step within a learning path.
    
    Why: Breaks down learning path into manageable chunks with
    clear progression and prerequisites.
    
    Supports: Step-by-step guidance, progress visualization
    """
    
    STATUS_CHOICES = [
        ('locked', 'Locked'),
        ('available', 'Available'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    learning_path = models.ForeignKey(
        LearningPath,
        on_delete=models.CASCADE,
        related_name='steps',
        help_text="Parent learning path"
    )
    
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        help_text="Topic for this step"
    )
    
    # Step Details
    step_number = models.IntegerField(
        help_text="Order in the learning path"
    )
    
    title = models.CharField(
        max_length=200,
        help_text="Step title"
    )
    
    description = models.TextField(
        help_text="What to achieve in this step"
    )
    
    # Progress
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='locked',
        help_text="Current step status"
    )
    
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Step completion percentage"
    )
    
    # Recommended Resources
    recommended_resources = models.ManyToManyField(
        LearningResource,
        blank=True,
        related_name='path_steps',
        help_text="Resources to complete this step"
    )
    
    # Timing
    estimated_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Expected time to complete step"
    )
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'learning_path_steps'
        ordering = ['learning_path', 'step_number']
        unique_together = ['learning_path', 'step_number']
    
    def __str__(self):
        return f"{self.learning_path.name} - Step {self.step_number}: {self.title}"


class Feedback(models.Model):
    """
    Student and teacher feedback on recommendations and system.
    
    Why: Continuous improvement - feedback loop refines AI recommendations
    
    Supports: Model improvement, user satisfaction tracking
    """
    
    FEEDBACK_TYPE_CHOICES = [
        ('recommendation', 'Recommendation Feedback'),
        ('resource', 'Resource Feedback'),
        ('system', 'System Feedback'),
        ('teacher', 'Teacher Feedback'),
    ]
    
    RATING_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    # Who gave feedback
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='feedbacks',
        help_text="Student providing feedback"
    )
    
    # What feedback is about
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPE_CHOICES,
        help_text="Type of feedback"
    )
    
    recommendation = models.ForeignKey(
        Recommendation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='feedbacks',
        help_text="Related recommendation (if applicable)"
    )
    
    resource = models.ForeignKey(
        LearningResource,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='feedbacks',
        help_text="Related resource (if applicable)"
    )
    
    # Feedback Content
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        help_text="Numerical rating"
    )
    
    comment = models.TextField(
        blank=True,
        help_text="Detailed feedback"
    )
    
    # Specific Questions
    was_helpful = models.BooleanField(
        help_text="Did this help your learning?"
    )
    
    was_accurate = models.BooleanField(
        null=True,
        blank=True,
        help_text="Was the recommendation accurate to your needs?"
    )
    
    difficulty_appropriate = models.BooleanField(
        null=True,
        blank=True,
        help_text="Was the difficulty level appropriate?"
    )
    
    # Action Taken
    is_reviewed = models.BooleanField(
        default=False,
        help_text="Has admin/teacher reviewed this feedback?"
    )
    
    admin_response = models.TextField(
        blank=True,
        help_text="Response from admin/teacher"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'feedbacks'
        ordering = ['-created_at']
        verbose_name_plural = 'Feedbacks'
    
    def __str__(self):
        return f"{self.feedback_type} - Rating: {self.rating}/5"
