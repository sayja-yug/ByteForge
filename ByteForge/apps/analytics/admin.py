"""
Admin Panel Configuration for Analytics
========================================
Customized admin interfaces for Gamification, Badges, Audit Logs, and Interventions.
"""

from django.contrib import admin
from .models import GamificationProfile, Badge, AuditLog, TeacherIntervention, TeacherMark


@admin.register(GamificationProfile)
class GamificationProfileAdmin(admin.ModelAdmin):
    """Gamification profile management"""
    
    list_display = ['student', 'current_level', 'total_xp', 'current_streak', 'longest_streak', 'total_badges', 'rank_in_class']
    list_filter = ['current_level', 'current_streak']
    search_fields = ['student__user__username']
    ordering = ['-total_xp']
    
    fieldsets = [
        ('Student', {
            'fields': ['student']
        }),
        ('Experience Points', {
            'fields': ['total_xp', 'current_level', 'xp_to_next_level']
        }),
        ('Streaks', {
            'fields': ['current_streak', 'longest_streak', 'last_activity_date']
        }),
        ('Achievements', {
            'fields': ['badges_earned', 'total_badges']
        }),
        ('Activity Stats', {
            'fields': ['total_quizzes_completed', 'total_resources_viewed', 'total_topics_mastered']
        }),
        ('Leaderboard', {
            'fields': ['rank_in_class', 'rank_globally']
        }),
    ]
    
    readonly_fields = ['updated_at']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Badge definition management"""
    
    list_display = ['name', 'badge_id', 'category', 'xp_reward', 'is_rare', 'times_awarded']
    list_filter = ['category', 'is_rare']
    search_fields = ['name', 'badge_id', 'description']
    
    fieldsets = [
        ('Badge Information', {
            'fields': ['badge_id', 'name', 'description']
        }),
        ('Category & Icon', {
            'fields': ['category', 'icon']
        }),
        ('Rewards', {
            'fields': ['xp_reward', 'is_rare']
        }),
        ('Statistics', {
            'fields': ['times_awarded']
        }),
    ]
    
    readonly_fields = ['times_awarded', 'created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Audit log for security and compliance"""
    
    list_display = ['user', 'action', 'model_name', 'object_id', 'ip_address', 'timestamp']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'description', 'ip_address']
    date_hierarchy = 'timestamp'
    
    fieldsets = [
        ('Who', {
            'fields': ['user']
        }),
        ('What', {
            'fields': ['action', 'model_name', 'object_id', 'description']
        }),
        ('Context', {
            'fields': ['ip_address', 'user_agent']
        }),
        ('Data', {
            'fields': ['changes']
        }),
        ('When', {
            'fields': ['timestamp']
        }),
    ]
    
    readonly_fields = ['timestamp']
    
    # Make audit logs read-only (no editing/deleting)
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TeacherIntervention)
class TeacherInterventionAdmin(admin.ModelAdmin):
    """Teacher intervention tracking"""
    
    list_display = ['teacher', 'student', 'intervention_type', 'status', 'scheduled_date', 'was_effective', 'follow_up_needed']
    list_filter = ['intervention_type', 'status', 'was_effective', 'follow_up_needed', 'scheduled_date']
    search_fields = ['teacher__user__username', 'student__user__username', 'reason', 'description']
    date_hierarchy = 'scheduled_date'
    
    fieldsets = [
        ('Participants', {
            'fields': ['teacher', 'student']
        }),
        ('Intervention Details', {
            'fields': ['intervention_type', 'reason', 'description']
        }),
        ('Status', {
            'fields': ['status']
        }),
        ('Timing', {
            'fields': ['scheduled_date', 'completed_date']
        }),
        ('Outcome', {
            'fields': ['outcome', 'was_effective', 'follow_up_needed']
        }),
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['mark_as_completed']
    
    def mark_as_completed(self, request, queryset):
        """Bulk mark interventions as completed"""
        from django.utils import timezone
        updated = queryset.update(status='completed', completed_date=timezone.now().date())
        self.message_user(request, f'{updated} intervention(s) marked as completed.')
    mark_as_completed.short_description = 'Mark as completed'


@admin.register(TeacherMark)
class TeacherMarkAdmin(admin.ModelAdmin):
    """Teacher marks/grades management"""
    
    list_display = ['student', 'teacher', 'topic', 'marks_obtained', 'total_marks', 'percentage', 'assessment_date', 'created_at']
    list_filter = ['assessment_date', 'topic', 'teacher']
    search_fields = ['student__user__username', 'teacher__user__username', 'topic__name', 'assessment_title']
    date_hierarchy = 'assessment_date'
    
    fieldsets = [
        ('Participants', {
            'fields': ['student', 'teacher', 'topic']
        }),
        ('Marks', {
            'fields': ['marks_obtained', 'total_marks', 'percentage']
        }),
        ('Assessment Details', {
            'fields': ['assessment_title', 'assessment_date']
        }),
        ('Feedback', {
            'fields': ['notes']
        }),
    ]
    
    readonly_fields = ['percentage', 'created_at', 'updated_at']
    
    def get_readonly_fields(self, request, obj=None):
        """Make percentage always readonly as it's auto-calculated"""
        return self.readonly_fields
