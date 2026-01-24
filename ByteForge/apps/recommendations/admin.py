"""
Admin Panel Configuration for AI Recommendations
================================================
Customized admin interfaces for Recommendations and Learning Paths.
"""

from django.contrib import admin
from .models import Recommendation, LearningPath, LearningPathStep, Feedback


class LearningPathStepInline(admin.TabularInline):
    """Inline editing for learning path steps"""
    model = LearningPathStep
    extra = 1
    fields = ['step_number', 'topic', 'title', 'status', 'progress_percentage', 'estimated_hours']
    ordering = ['step_number']


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    """AI recommendation management"""
    
    list_display = ['student', 'recommendation_type', 'title', 'priority', 'recommended_date', 'is_viewed', 'is_acted_upon', 'was_helpful']
    list_filter = ['recommendation_type', 'priority', 'is_viewed', 'is_acted_upon', 'was_helpful', 'recommended_date']
    search_fields = ['student__user__username', 'title', 'description', 'reason']
    date_hierarchy = 'recommended_date'
    
    fieldsets = [
        ('Student & Type', {
            'fields': ['student', 'recommendation_type']
        }),
        ('Recommended Content', {
            'fields': ['resource', 'topic', 'title', 'description']
        }),
        ('Explainable AI', {
            'fields': ['reason', 'reasoning_factors'],
            'description': 'Transparency: Why this recommendation was made'
        }),
        ('Priority & Timing', {
            'fields': ['priority', 'recommended_date', 'expires_at']
        }),
        ('Engagement Tracking', {
            'fields': ['is_viewed', 'viewed_at', 'is_acted_upon', 'acted_at']
        }),
        ('Feedback Loop', {
            'fields': ['was_helpful', 'student_feedback']
        }),
    ]
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    """Learning path management with inline steps"""
    
    list_display = ['student', 'name', 'status', 'progress_percentage', 'current_step', 'is_ai_generated']
    list_filter = ['status', 'is_ai_generated', 'started_at']
    search_fields = ['student__user__username', 'name', 'description']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['student', 'name', 'description']
        }),
        ('Progress Tracking', {
            'fields': ['status', 'progress_percentage', 'current_step']
        }),
        ('Timing', {
            'fields': ['estimated_completion_days', 'started_at', 'completed_at']
        }),
        ('AI Generation', {
            'fields': ['is_ai_generated', 'generation_criteria'],
            'description': 'Transparency: How this path was created'
        }),
    ]
    
    inlines = [LearningPathStepInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LearningPathStep)
class LearningPathStepAdmin(admin.ModelAdmin):
    """Individual learning path step management"""
    
    list_display = ['learning_path', 'step_number', 'topic', 'status', 'progress_percentage']
    list_filter = ['status', 'learning_path__student']
    search_fields = ['learning_path__name', 'topic__name', 'title']
    ordering = ['learning_path', 'step_number']
    
    fieldsets = [
        ('Path & Topic', {
            'fields': ['learning_path', 'topic', 'step_number']
        }),
        ('Step Details', {
            'fields': ['title', 'description', 'status']
        }),
        ('Progress', {
            'fields': ['progress_percentage', 'estimated_hours']
        }),
        ('Resources', {
            'fields': ['recommended_resources']
        }),
        ('Timing', {
            'fields': ['started_at', 'completed_at']
        }),
    ]
    
    filter_horizontal = ['recommended_resources']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """User feedback management"""
    
    list_display = ['student', 'feedback_type', 'rating', 'was_helpful', 'is_reviewed', 'created_at']
    list_filter = ['feedback_type', 'rating', 'was_helpful', 'is_reviewed', 'created_at']
    search_fields = ['student__user__username', 'comment', 'admin_response']
    date_hierarchy = 'created_at'
    
    fieldsets = [
        ('Feedback Source', {
            'fields': ['student', 'feedback_type']
        }),
        ('Related Items', {
            'fields': ['recommendation', 'resource']
        }),
        ('Feedback Content', {
            'fields': ['rating', 'comment']
        }),
        ('Specific Questions', {
            'fields': ['was_helpful', 'was_accurate', 'difficulty_appropriate']
        }),
        ('Admin Review', {
            'fields': ['is_reviewed', 'admin_response']
        }),
    ]
    
    readonly_fields = ['created_at']
    
    actions = ['mark_as_reviewed']
    
    def mark_as_reviewed(self, request, queryset):
        """Bulk mark feedback as reviewed"""
        updated = queryset.update(is_reviewed=True)
        self.message_user(request, f'{updated} feedback(s) marked as reviewed.')
    mark_as_reviewed.short_description = 'Mark as reviewed'
