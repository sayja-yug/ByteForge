"""
Assessment and Quiz Models
===========================
This module handles quizzes, tests, and adaptive assessments.

Key Features:
- Multi-format questions (MCQ, True/False, Short Answer)
- Adaptive difficulty
- Bloom's taxonomy support
- Automatic evaluation
- Mistake tracking for targeted practice
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import StudentProfile, TeacherProfile
from apps.learning.models import Topic


class Assessment(models.Model):
    """
    Quiz/Test container.
    
    Why: Organizes questions into assessments for structured evaluation
    
    Supports: Teacher-created tests, AI-generated quizzes, adaptive assessments
    """
    
    ASSESSMENT_TYPE_CHOICES = [
        ('quiz', 'Quick Quiz'),
        ('test', 'Test'),
        ('assignment', 'Assignment'),
        ('practice', 'Practice Set'),
        ('exam', 'Exam'),
        ('diagnostic', 'Diagnostic Assessment'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('mixed', 'Mixed Difficulty'),
    ]
    
    title = models.CharField(
        max_length=300,
        help_text="Assessment title"
    )
    
    description = models.TextField(
        help_text="Assessment overview and instructions"
    )
    
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='assessments',
        help_text="Topic being assessed"
    )
    
    assessment_type = models.CharField(
        max_length=20,
        choices=ASSESSMENT_TYPE_CHOICES,
        help_text="Type of assessment"
    )
    
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium',
        help_text="Overall difficulty level"
    )
    
    # Configuration
    total_marks = models.IntegerField(
        help_text="Maximum possible score"
    )
    
    passing_marks = models.IntegerField(
        help_text="Minimum score to pass"
    )
    
    time_limit_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text="Time limit (null = no limit)"
    )
    
    # AI Features
    is_adaptive = models.BooleanField(
        default=False,
        help_text="Does difficulty adjust based on performance?"
    )
    
    is_ai_generated = models.BooleanField(
        default=False,
        help_text="Was this assessment auto-generated?"
    )
    
    # Bloom's Taxonomy Distribution
    bloom_distribution = models.JSONField(
        default=dict,
        help_text="Question distribution by Bloom's levels (e.g., {'remember': 30, 'understand': 40, 'apply': 30})"
    )
    
    # Curation
    created_by = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assessments',
        help_text="Teacher who created this assessment"
    )
    
    is_published = models.BooleanField(
        default=False,
        help_text="Is assessment available to students?"
    )
    
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Deadline for assignment submission (optional)"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assessments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.topic.name})"


class Question(models.Model):
    """
    Individual assessment question.
    
    Why: Supports multiple question types and Bloom's taxonomy
    
    Supports: Adaptive quizzes, mistake-based practice, knowledge assessment
    """
    
    QUESTION_TYPE_CHOICES = [
        ('mcq', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
        ('fill_blank', 'Fill in the Blank'),
    ]
    
    BLOOM_LEVEL_CHOICES = [
        ('remember', 'Remember'),
        ('understand', 'Understand'),
        ('apply', 'Apply'),
        ('analyze', 'Analyze'),
        ('evaluate', 'Evaluate'),
        ('create', 'Create'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='questions',
        help_text="Parent assessment"
    )
    
    # Question Content
    question_text = models.TextField(
        help_text="The question being asked"
    )
    
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        help_text="Question format"
    )
    
    # For MCQ questions
    options = models.JSONField(
        default=list,
        help_text="Answer options for MCQ (e.g., ['Option A', 'Option B', 'Option C', 'Option D'])"
    )
    
    correct_answer = models.TextField(
        help_text="Correct answer (option index for MCQ, text for others)"
    )
    
    # Metadata
    marks = models.IntegerField(
        default=1,
        help_text="Points for this question"
    )
    
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium',
        help_text="Question difficulty"
    )
    
    bloom_level = models.CharField(
        max_length=20,
        choices=BLOOM_LEVEL_CHOICES,
        default='understand',
        help_text="Bloom's taxonomy level"
    )
    
    # Explanation
    explanation = models.TextField(
        blank=True,
        help_text="Explanation of correct answer (shown after submission)"
    )
    
    # Analytics
    times_attempted = models.IntegerField(
        default=0,
        help_text="How many times this question was answered"
    )
    
    times_correct = models.IntegerField(
        default=0,
        help_text="How many times answered correctly"
    )
    
    # Order
    order = models.IntegerField(
        default=0,
        help_text="Question order in assessment"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['assessment', 'order']
    
    def __str__(self):
        return f"{self.assessment.title} - Q{self.order}"
    
    @property
    def success_rate(self):
        """Calculate percentage of correct answers"""
        if self.times_attempted == 0:
            return 0
        return (self.times_correct / self.times_attempted) * 100


class QuizAttempt(models.Model):
    """
    Student's attempt at an assessment.
    
    Why: Tracks individual assessment attempts for progress monitoring
    
    Supports: Performance analytics, retry tracking, improvement measurement
    """
    
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('evaluated', 'Evaluated'),
    ]
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        help_text="Student taking the assessment"
    )
    
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='attempts',
        help_text="Assessment being attempted"
    )
    
    # Attempt Details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        help_text="Current attempt status"
    )
    
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Score achieved"
    )
    
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Percentage score"
    )
    
    # Timing
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When attempt began"
    )
    
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When attempt was submitted"
    )
    
    time_taken_minutes = models.IntegerField(
        default=0,
        help_text="Total time spent"
    )
    
    # Analysis
    correct_answers = models.IntegerField(
        default=0,
        help_text="Number of correct answers"
    )
    
    wrong_answers = models.IntegerField(
        default=0,
        help_text="Number of wrong answers"
    )
    
    skipped_questions = models.IntegerField(
        default=0,
        help_text="Number of unanswered questions"
    )
    
    # Mistake Tracking (for targeted practice)
    mistakes = models.JSONField(
        default=list,
        help_text="List of question IDs answered incorrectly"
    )
    
    weak_topics = models.JSONField(
        default=list,
        help_text="Topics where student struggled"
    )
    
    # Feedback
    teacher_feedback = models.TextField(
        blank=True,
        help_text="Teacher's comments on attempt"
    )
    
    # Cheating Detection
    suspicious_activity = models.BooleanField(
        default=False,
        help_text="Flag for unusual patterns (e.g., too fast, random guessing)"
    )
    
    activity_log = models.JSONField(
        default=list,
        help_text="Timestamps of actions for pattern analysis"
    )
    
    class Meta:
        db_table = 'quiz_attempts'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.assessment.title} ({self.percentage}%)"


class QuestionResponse(models.Model):
    """
    Student's answer to a specific question.
    
    Why: Granular tracking of each answer for detailed analytics
    
    Supports: Mistake-based practice, question difficulty calibration
    """
    
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='responses',
        help_text="Parent quiz attempt"
    )
    
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='responses',
        help_text="Question being answered"
    )
    
    # Response
    student_answer = models.TextField(
        blank=True,
        help_text="Student's submitted answer"
    )
    
    is_correct = models.BooleanField(
        default=False,
        help_text="Whether answer was correct"
    )
    
    marks_awarded = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Marks given for this answer"
    )
    
    # Timing
    time_taken_seconds = models.IntegerField(
        default=0,
        help_text="Time spent on this question"
    )
    
    answered_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When answer was submitted"
    )
    
    # Confidence (optional feature)
    confidence_level = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Student's confidence in their answer (1-5)"
    )
    
    class Meta:
        db_table = 'question_responses'
        unique_together = ['attempt', 'question']
    
    def __str__(self):
        status = "✓" if self.is_correct else "✗"
        return f"{status} {self.attempt.student.user.username} - Q{self.question.order}"
