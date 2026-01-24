"""
Notification System
===================
Email and alert notifications for parents and students.
"""

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class NotificationService:
    """Handle all platform notifications"""
    
    @staticmethod
    def send_parent_weekly_summary(parent_profile):
        """
        Send weekly progress summary to parents.
        
        Args:
            parent_profile: ParentProfile object
        """
        children = parent_profile.user.children.all()
        
        if not children:
            return
        
        # Build email content
        subject = "Weekly Learning Progress Summary"
        message = f"Dear {parent_profile.user.first_name},\n\n"
        message += "Here's your weekly summary of your children's learning progress:\n\n"
        
        for child in children:
            message += f"\n{child.user.get_full_name()} ({child.grade_level}):\n"
            message += f"  - Study Time: {child.total_study_time} minutes\n"
            message += f"  - Current Streak: {child.current_streak} days\n"
            
            # Get recent performance
            from apps.learning.models import StudentPerformance
            recent_perf = StudentPerformance.objects.filter(
                student=child
            ).order_by('-assessed_at')[:3]
            
            if recent_perf:
                message += "  - Recent Scores:\n"
                for perf in recent_perf:
                    message += f"    • {perf.topic.name}: {perf.percentage:.0f}%\n"
        
        message += "\n\nBest regards,\nSmartShiksha Team"
        
        # Send email (in production, this would actually send)
        if parent_profile.email_notifications:
            # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [parent_profile.user.email])
            print(f"Email sent to {parent_profile.user.email}: {subject}")
    
    @staticmethod
    def send_low_score_alert(student_profile, topic, score):
        """
        Alert parent when student scores below threshold.
        
        Args:
            student_profile: StudentProfile object
            topic: Topic object
            score: Score percentage
        """
        if not student_profile.parent:
            return
        
        parent = student_profile.parent
        
        subject = f"Alert: Low Score in {topic.name}"
        message = f"Dear {parent.user.first_name},\n\n"
        message += f"{student_profile.user.first_name} scored {score:.0f}% in {topic.name}, "
        message += f"which is below the expected level.\n\n"
        message += "We recommend:\n"
        message += f"- Reviewing {topic.name} concepts together\n"
        message += "- Encouraging daily practice\n"
        message += "- Checking recommended resources on the platform\n\n"
        message += "Best regards,\nSmartShiksha Team"
        
        if parent.email_notifications:
            # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [parent.user.email])
            print(f"Alert sent to {parent.user.email}: Low score alert")
    
    @staticmethod
    def send_streak_achievement(student_profile, days):
        """
        Celebrate streak milestones.
        
        Args:
            student_profile: StudentProfile object
            days: Number of days in streak
        """
        if days in [7, 14, 30, 60, 100]:  # Milestone days
            subject = f"🎉 {days}-Day Streak Achievement!"
            message = f"Congratulations {student_profile.user.first_name}!\n\n"
            message += f"You've maintained a {days}-day learning streak! Keep up the great work!\n\n"
            message += "Best regards,\nSmartShiksha Team"
            
            # Notify student
            print(f"Streak notification for {student_profile.user.username}: {days} days")
            
            # Notify parent
            if student_profile.parent and student_profile.parent.email_notifications:
                parent_message = f"Great news! {student_profile.user.first_name} has achieved a {days}-day learning streak!"
                print(f"Parent notified about streak achievement")
    
    @staticmethod
    def send_inactivity_alert(student_profile, days_inactive):
        """
        Alert when student is inactive for too long.
        
        Args:
            student_profile: StudentProfile object
            days_inactive: Number of days since last activity
        """
        if not student_profile.parent:
            return
        
        parent = student_profile.parent
        
        subject = f"Reminder: {student_profile.user.first_name}'s Learning Activity"
        message = f"Dear {parent.user.first_name},\n\n"
        message += f"{student_profile.user.first_name} hasn't been active on the platform for {days_inactive} days.\n\n"
        message += "Regular practice is important for learning progress. "
        message += "Please encourage them to spend some time on the platform.\n\n"
        message += "Best regards,\nSmartShiksha Team"
        
        if parent.email_notifications:
            print(f"Inactivity alert sent to parent")


class EarlyWarningSystem:
    """Detect and alert about potential learning issues"""
    
    @staticmethod
    def check_student_warnings(student_profile):
        """
        Check for early warning signs.
        
        Returns:
            list: Warning messages
        """
        warnings = []
        
        # Check 1: Declining performance
        from apps.learning.models import StudentPerformance
        recent_scores = StudentPerformance.objects.filter(
            student=student_profile
        ).order_by('-assessed_at')[:5]
        
        if len(recent_scores) >= 3:
            scores = [p.percentage for p in recent_scores]
            if all(scores[i] > scores[i+1] for i in range(len(scores)-1)):
                warnings.append({
                    'type': 'declining_performance',
                    'severity': 'high',
                    'message': 'Performance is consistently declining',
                    'action': 'Consider scheduling a teacher intervention'
                })
        
        # Check 2: Low engagement
        if student_profile.current_streak == 0:
            last_active = student_profile.last_active
            if last_active:
                days_inactive = (timezone.now().date() - last_active).days
                if days_inactive > 7:
                    warnings.append({
                        'type': 'low_engagement',
                        'severity': 'medium',
                        'message': f'No activity for {days_inactive} days',
                        'action': 'Send encouragement notification'
                    })
        
        # Check 3: Struggling with multiple topics
        weak_topics = StudentPerformance.objects.filter(
            student=student_profile,
            percentage__lt=50
        ).count()
        
        if weak_topics >= 3:
            warnings.append({
                'type': 'multiple_weak_topics',
                'severity': 'high',
                'message': f'Struggling with {weak_topics} topics',
                'action': 'Recommend personalized tutoring'
            })
        
        return warnings
