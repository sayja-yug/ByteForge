"""
Admin Panel Configuration for Learning Content
===============================================
Customized admin interfaces for Subject, Topic, Resources, and Activities.
"""

from django.contrib import admin
from .models import Subject, Topic, LearningResource, LearningActivity, StudentPerformance


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Subject management"""
    
    list_display = ['name', 'is_active', 'topic_count', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'description']
        }),
        ('Display Settings', {
            'fields': ['icon', 'color_code']
        }),
        ('Status', {
            'fields': ['is_active']
        }),
    ]
    
    def topic_count(self, obj):
        """Display number of topics"""
        return obj.topics.count()
    topic_count.short_description = 'Topics'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """Topic management with prerequisites"""
    
    list_display = ['name', 'subject', 'difficulty_level', 'estimated_hours', 'order', 'is_active']
    list_filter = ['subject', 'difficulty_level', 'is_active']
    search_fields = ['name', 'description', 'subject__name']
    ordering = ['subject', 'order']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['subject', 'name', 'description']
        }),
        ('Difficulty & Time', {
            'fields': ['difficulty_level', 'estimated_hours']
        }),
        ('Prerequisites', {
            'fields': ['prerequisites']
        }),
        ('Display', {
            'fields': ['order', 'is_active']
        }),
    ]
    
    filter_horizontal = ['prerequisites']


@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    """Learning resource management"""
    
    list_display = ['title', 'topic', 'resource_type', 'difficulty', 'average_rating', 'view_count', 'is_verified']
    list_filter = ['resource_type', 'difficulty', 'is_verified', 'is_active', 'topic__subject']
    search_fields = ['title', 'description', 'author', 'topic__name']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['topic', 'title', 'description']
        }),
        ('Content Type', {
            'fields': ['resource_type', 'difficulty']
        }),
        ('Content Location', {
            'fields': ['url', 'file']
        }),
        ('Metadata', {
            'fields': ['duration_minutes', 'author']
        }),
        ('Quality Metrics', {
            'fields': ['view_count', 'average_rating']
        }),
        ('Curation', {
            'fields': ['created_by', 'is_verified', 'is_active']
        }),
    ]
    
    readonly_fields = ['view_count', 'average_rating']
    
    actions = ['verify_resources']
    
    def verify_resources(self, request, queryset):
        """Bulk verify resources"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} resource(s) verified successfully.')
    verify_resources.short_description = 'Verify selected resources'


@admin.register(LearningActivity)
class LearningActivityAdmin(admin.ModelAdmin):
    """Student learning activity tracking"""
    
    list_display = ['student', 'resource', 'status', 'progress_percentage', 'time_spent_minutes', 'started_at']
    list_filter = ['status', 'resource__resource_type', 'started_at']
    search_fields = ['student__user__username', 'resource__title']
    date_hierarchy = 'started_at'
    
    fieldsets = [
        ('Activity Details', {
            'fields': ['student', 'resource', 'status']
        }),
        ('Progress Tracking', {
            'fields': ['started_at', 'completed_at', 'time_spent_minutes', 'progress_percentage']
        }),
        ('Engagement Metrics', {
            'fields': ['revisit_count']
        }),
        ('Feedback', {
            'fields': ['rating', 'feedback', 'was_helpful']
        }),
    ]
    
    readonly_fields = ['started_at', 'updated_at']


@admin.register(StudentPerformance)
class StudentPerformanceAdmin(admin.ModelAdmin):
    """Student performance tracking"""
    
    list_display = ['student', 'topic', 'percentage', 'assessment_type', 'difficulty_level', 'assessed_at']
    list_filter = ['assessment_type', 'difficulty_level', 'assessed_at']
    search_fields = ['student__user__username', 'topic__name']
    date_hierarchy = 'assessed_at'
    
    fieldsets = [
        ('Assessment Details', {
            'fields': ['student', 'topic', 'assessment_type', 'difficulty_level']
        }),
        ('Performance Metrics', {
            'fields': ['score', 'max_score', 'percentage']
        }),
        ('Timing', {
            'fields': ['time_taken_minutes', 'assessed_at']
        }),
        ('Analysis', {
            'fields': ['strengths', 'weaknesses', 'teacher_feedback']
        }),
    ]
    
    readonly_fields = ['percentage', 'assessed_at']
