"""
Analytics and Gamification Models
==================================
This module handles platform analytics, gamification features,
and audit logging.

Key Features:
- Student gamification (XP, badges, streaks)
- Platform-wide analytics
- Audit logging for security
- Teacher intervention tracking
"""

from django.db import models
from django.core.validators import MinValueValidator
from apps.accounts.models import User, StudentProfile, TeacherProfile


class GamificationProfile(models.Model):
    """
    Student gamification data.
    
    Why: Increases engagement through game mechanics (XP, badges, levels)
    
    Supports: Motivation, habit formation, friendly competition
    """
    
    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='gamification',
        help_text="Student's gamification profile"
    )
    
    # Experience Points
    total_xp = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total experience points earned"
    )
    
    current_level = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Current level (calculated from XP)"
    )
    
    xp_to_next_level = models.IntegerField(
        default=100,
        help_text="XP needed to reach next level"
    )
    
    # Streaks
    current_streak = models.IntegerField(
        default=0,
        help_text="Consecutive days of activity"
    )
    
    longest_streak = models.IntegerField(
        default=0,
        help_text="Best streak ever achieved"
    )
    
    last_activity_date = models.DateField(
        null=True,
        blank=True,
        help_text="Last day student was active"
    )
    
    # Achievements
    badges_earned = models.JSONField(
        default=list,
        help_text="List of badge IDs earned (e.g., ['first_quiz', 'week_streak', 'topic_master'])"
    )
    
    total_badges = models.IntegerField(
        default=0,
        help_text="Count of unique badges"
    )
    
    # Activity Stats
    total_quizzes_completed = models.IntegerField(
        default=0,
        help_text="Number of quizzes finished"
    )
    
    total_resources_viewed = models.IntegerField(
        default=0,
        help_text="Number of learning resources accessed"
    )
    
    total_topics_mastered = models.IntegerField(
        default=0,
        help_text="Topics with >80% proficiency"
    )
    
    # Leaderboard
    rank_in_class = models.IntegerField(
        null=True,
        blank=True,
        help_text="Position in class leaderboard"
    )
    
    rank_globally = models.IntegerField(
        null=True,
        blank=True,
        help_text="Position in global leaderboard"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gamification_profiles'
        ordering = ['-total_xp']
    
    def __str__(self):
        return f"{self.student.user.username} - Level {self.current_level} ({self.total_xp} XP)"
    
    def add_xp(self, points, reason=""):
        """Add XP and check for level up"""
        self.total_xp += points
        
        # Simple level calculation (100 XP per level, increasing)
        new_level = 1 + (self.total_xp // 100)
        if new_level > self.current_level:
            self.current_level = new_level
            # Award level-up badge
            badge_id = f"level_{new_level}"
            if badge_id not in self.badges_earned:
                self.badges_earned.append(badge_id)
                self.total_badges += 1
        
        self.xp_to_next_level = (self.current_level * 100) - self.total_xp
        self.save()


class Badge(models.Model):
    """
    Achievement badges that students can earn.
    
    Why: Provides clear goals and recognition for accomplishments
    
    Supports: Motivation, progress visualization
    """
    
    CATEGORY_CHOICES = [
        ('streak', 'Streak Achievement'),
        ('quiz', 'Quiz Achievement'),
        ('topic', 'Topic Mastery'),
        ('level', 'Level Achievement'),
        ('special', 'Special Achievement'),
    ]
    
    badge_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique identifier (e.g., 'first_quiz', '7_day_streak')"
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Badge name (e.g., 'Quiz Master')"
    )
    
    description = models.TextField(
        help_text="How to earn this badge"
    )
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text="Badge category"
    )
    
    icon = models.CharField(
        max_length=50,
        help_text="Icon class or emoji"
    )
    
    xp_reward = models.IntegerField(
        default=0,
        help_text="Bonus XP for earning this badge"
    )
    
    # Rarity
    is_rare = models.BooleanField(
        default=False,
        help_text="Is this a rare/special badge?"
    )
    
    times_awarded = models.IntegerField(
        default=0,
        help_text="How many students have earned this"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'badges'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.badge_id})"


class AuditLog(models.Model):
    """
    System audit trail for security and compliance.
    
    Why: Tracks all important actions for security, debugging, and compliance
    
    Supports: Security monitoring, user behavior analysis, debugging
    """
    
    ACTION_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('create', 'Create Record'),
        ('update', 'Update Record'),
        ('delete', 'Delete Record'),
        ('view', 'View Record'),
        ('download', 'Download File'),
        ('submit', 'Submit Assessment'),
        ('grade', 'Grade Assessment'),
        ('recommend', 'Generate Recommendation'),
    ]
    
    # Who
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        help_text="User who performed action"
    )
    
    # What
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text="Action performed"
    )
    
    model_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Django model affected (e.g., 'StudentProfile')"
    )
    
    object_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID of affected record"
    )
    
    description = models.TextField(
        help_text="Human-readable description of action"
    )
    
    # Context
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="User's IP address"
    )
    
    user_agent = models.CharField(
        max_length=300,
        blank=True,
        help_text="Browser/device information"
    )
    
    # Data
    changes = models.JSONField(
        default=dict,
        help_text="Before/after values for updates"
    )
    
    # When
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When action occurred"
    )
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown'} - {self.action} - {self.timestamp}"


class TeacherIntervention(models.Model):
    """
    Tracks teacher interventions for struggling students.
    
    Why: Monitors teacher support actions and their effectiveness
    
    Supports: Teacher analytics, intervention effectiveness measurement
    """
    
    INTERVENTION_TYPE_CHOICES = [
        ('one_on_one', 'One-on-One Session'),
        ('remedial', 'Remedial Class'),
        ('resource', 'Additional Resources'),
        ('parent_contact', 'Parent Contact'),
        ('peer_tutoring', 'Peer Tutoring'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='interventions',
        help_text="Teacher providing intervention"
    )
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='interventions',
        help_text="Student receiving help"
    )
    
    # Intervention Details
    intervention_type = models.CharField(
        max_length=20,
        choices=INTERVENTION_TYPE_CHOICES,
        help_text="Type of intervention"
    )
    
    reason = models.TextField(
        help_text="Why intervention was needed (e.g., 'Low quiz scores in Algebra')"
    )
    
    description = models.TextField(
        help_text="What was done during intervention"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        help_text="Current status"
    )
    
    # Timing
    scheduled_date = models.DateField(
        help_text="When intervention is/was scheduled"
    )
    
    completed_date = models.DateField(
        null=True,
        blank=True,
        help_text="When intervention was completed"
    )
    
    # Outcome
    outcome = models.TextField(
        blank=True,
        help_text="Results of intervention"
    )
    
    was_effective = models.BooleanField(
        null=True,
        blank=True,
        help_text="Did intervention help? (measured by subsequent performance)"
    )
    
    follow_up_needed = models.BooleanField(
        default=False,
        help_text="Does student need additional support?"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teacher_interventions'
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"{self.teacher.user.username} → {self.student.user.username} ({self.intervention_type})"


class TeacherMark(models.Model):
    """
    Manual marks/grades entered by teachers for students.
    
    Why: Allows teachers to record manual assessments, class tests, and provide direct feedback
    
    Supports: Teacher-student feedback loop, comprehensive grade tracking
    """
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='teacher_marks',
        help_text="Student receiving the mark"
    )
    
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='marks_given',
        help_text="Teacher who entered the mark"
    )
    
    topic = models.ForeignKey(
        'learning.Topic',
        on_delete=models.CASCADE,
        related_name='teacher_marks',
        help_text="Topic/subject for this assessment"
    )
    
    # Marks
    marks_obtained = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Marks scored by student"
    )
    
    total_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Maximum marks possible"
    )
    
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Calculated percentage (auto-computed)"
    )
    
    # Assessment Details
    assessment_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional title (e.g., 'Unit Test 1', 'Class Quiz')"
    )
    
    assessment_date = models.DateField(
        help_text="Date when assessment was conducted"
    )
    
    # Feedback
    notes = models.TextField(
        blank=True,
        help_text="Teacher's comments/feedback for student"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teacher_marks'
        ordering = ['-assessment_date', '-created_at']
        indexes = [
            models.Index(fields=['student', '-assessment_date']),
            models.Index(fields=['teacher', '-assessment_date']),
        ]
    
    def __str__(self):
        return f"{self.student.user.username} - {self.topic.name} ({self.percentage}%)"
    
    def save(self, *args, **kwargs):
        """Auto-calculate percentage before saving"""
        if self.total_marks > 0:
            self.percentage = (self.marks_obtained / self.total_marks) * 100
        else:
            self.percentage = 0
        super().save(*args, **kwargs)


class ReportCard(models.Model):
    """
    Formal academic report card document.
    
    Why: Provides a permanent record of term-wise performance and behavior
    
    Supports: Term-to-term progress analysis, parent-teacher reviews
    """
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='report_cards',
        help_text="Student receiving this report card"
    )
    
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name='issued_report_cards',
        help_text="Teacher issuing the report card"
    )
    
    # Context
    term = models.CharField(
        max_length=50,
        help_text="e.g., 'Term 1', 'Mid-Term', 'Final Exam'"
    )
    
    academic_session = models.CharField(
        max_length=20,
        help_text="e.g., '2025-26'"
    )
    
    # Performance Data
    # Format: {"Subject Name": {"marks": 85, "total": 100, "grade": "A"}}
    grades_data = models.JSONField(
        default=dict,
        help_text="Subject-wise marks and grades"
    )
    
    total_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Overall performance percentage"
    )
    
    # Feedback
    remarks = models.TextField(
        help_text="Teacher's overall evaluation and behavioral notes"
    )
    
    attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Student's attendance for the term"
    )
    
    # Status
    is_published = models.BooleanField(
        default=False,
        help_text="Is the report card visible to student and parent?"
    )
    
    issued_date = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'report_cards'
        ordering = ['-issued_date']
        unique_together = ['student', 'term', 'academic_session']
    
    def __str__(self):
        return f"Report Card: {self.student.user.username} - {self.term} ({self.academic_session})"
