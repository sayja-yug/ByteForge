"""
Admin Panel Configuration for Assessments
==========================================
Customized admin interfaces for Assessments, Questions, and Quiz Attempts.
"""

from django.contrib import admin
from .models import Assessment, Question, QuizAttempt, QuestionResponse


class QuestionInline(admin.TabularInline):
    """Inline editing for questions within assessments"""
    model = Question
    extra = 1
    fields = ['order', 'question_text', 'question_type', 'difficulty', 'bloom_level', 'marks']
    ordering = ['order']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    """Assessment management with inline questions"""
    
    list_display = ['title', 'topic', 'assessment_type', 'difficulty', 'total_marks', 'is_adaptive', 'is_published', 'created_by']
    list_filter = ['assessment_type', 'difficulty', 'is_adaptive', 'is_ai_generated', 'is_published', 'topic__subject']
    search_fields = ['title', 'description', 'topic__name']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['title', 'description', 'topic']
        }),
        ('Assessment Type', {
            'fields': ['assessment_type', 'difficulty']
        }),
        ('Configuration', {
            'fields': ['total_marks', 'passing_marks', 'time_limit_minutes']
        }),
        ('AI Features', {
            'fields': ['is_adaptive', 'is_ai_generated']
        }),
        ('Bloom\'s Taxonomy', {
            'fields': ['bloom_distribution'],
            'description': 'Question distribution by cognitive levels'
        }),
        ('Curation', {
            'fields': ['created_by', 'is_published', 'is_active']
        }),
    ]
    
    inlines = [QuestionInline]
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['publish_assessments']
    
    def publish_assessments(self, request, queryset):
        """Bulk publish assessments"""
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} assessment(s) published successfully.')
    publish_assessments.short_description = 'Publish selected assessments'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Question management"""
    
    list_display = ['assessment', 'order', 'question_type', 'difficulty', 'bloom_level', 'marks', 'success_rate']
    list_filter = ['question_type', 'difficulty', 'bloom_level', 'assessment__topic__subject']
    search_fields = ['question_text', 'assessment__title']
    ordering = ['assessment', 'order']
    
    fieldsets = [
        ('Assessment', {
            'fields': ['assessment', 'order']
        }),
        ('Question Content', {
            'fields': ['question_text', 'question_type']
        }),
        ('Answer Options (MCQ)', {
            'fields': ['options', 'correct_answer'],
            'description': 'For MCQ: options as JSON array, correct_answer as index'
        }),
        ('Metadata', {
            'fields': ['marks', 'difficulty', 'bloom_level']
        }),
        ('Explanation', {
            'fields': ['explanation']
        }),
        ('Analytics', {
            'fields': ['times_attempted', 'times_correct']
        }),
    ]
    
    readonly_fields = ['times_attempted', 'times_correct', 'created_at']


class QuestionResponseInline(admin.TabularInline):
    """Inline editing for question responses"""
    model = QuestionResponse
    extra = 0
    fields = ['question', 'student_answer', 'is_correct', 'marks_awarded', 'time_taken_seconds']
    readonly_fields = ['answered_at']


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    """Quiz attempt management with inline responses"""
    
    list_display = ['student', 'assessment', 'status', 'percentage', 'correct_answers', 'wrong_answers', 'suspicious_activity', 'started_at']
    list_filter = ['status', 'suspicious_activity', 'assessment__topic__subject', 'started_at']
    search_fields = ['student__user__username', 'assessment__title']
    date_hierarchy = 'started_at'
    
    fieldsets = [
        ('Attempt Details', {
            'fields': ['student', 'assessment', 'status']
        }),
        ('Performance', {
            'fields': ['score', 'percentage', 'correct_answers', 'wrong_answers', 'skipped_questions']
        }),
        ('Timing', {
            'fields': ['started_at', 'submitted_at', 'time_taken_minutes']
        }),
        ('Analysis', {
            'fields': ['mistakes', 'weak_topics']
        }),
        ('Feedback', {
            'fields': ['teacher_feedback']
        }),
        ('Academic Integrity', {
            'fields': ['suspicious_activity', 'activity_log'],
            'description': 'Cheating detection and activity patterns'
        }),
    ]
    
    inlines = [QuestionResponseInline]
    readonly_fields = ['started_at', 'submitted_at', 'percentage']
    
    actions = ['flag_suspicious']
    
    def flag_suspicious(self, request, queryset):
        """Flag attempts as suspicious"""
        updated = queryset.update(suspicious_activity=True)
        self.message_user(request, f'{updated} attempt(s) flagged for review.')
    flag_suspicious.short_description = 'Flag as suspicious'


@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    """Individual question response management"""
    
    list_display = ['attempt', 'question', 'is_correct', 'marks_awarded', 'time_taken_seconds', 'confidence_level']
    list_filter = ['is_correct', 'confidence_level', 'answered_at']
    search_fields = ['attempt__student__user__username', 'question__question_text']
    
    fieldsets = [
        ('Response Details', {
            'fields': ['attempt', 'question']
        }),
        ('Answer', {
            'fields': ['student_answer', 'is_correct', 'marks_awarded']
        }),
        ('Timing & Confidence', {
            'fields': ['time_taken_seconds', 'confidence_level', 'answered_at']
        }),
    ]
    
    readonly_fields = ['answered_at']
