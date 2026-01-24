"""
Adaptive Learning System
=======================
Provides intelligent question difficulty adjustment and learning analytics
"""

from django.db.models import Avg, Q, F
from apps.learning.models import StudentPerformance, LearningActivity
from apps.assessments.models import QuizAttempt
from datetime import datetime, timedelta
from django.utils import timezone


class AdaptivePracticeEngine:
    """Generates adaptive questions based on student performance"""
    
    def __init__(self, student_profile):
        self.student = student_profile
        self.performance_threshold = {
            'easy': 80,      # If scoring above 80%, move to medium
            'medium': 75,    # If scoring above 75%, move to hard
            'hard': 85,      # If scoring below 85%, stay at hard
        }
    
    def get_next_difficulty(self, topic):
        """Determine appropriate difficulty for next question"""
        recent_performance = StudentPerformance.objects.filter(
            student=self.student,
            topic=topic
        ).order_by('-assessed_at')[:5]
        
        if not recent_performance.exists():
            return 'easy'
        
        avg_score = recent_performance.aggregate(avg=Avg('percentage'))['avg']
        current_difficulty = recent_performance.first().difficulty_level or 'easy'
        
        if current_difficulty == 'easy' and avg_score >= self.performance_threshold['easy']:
            return 'medium'
        elif current_difficulty == 'medium' and avg_score >= self.performance_threshold['medium']:
            return 'hard'
        elif current_difficulty == 'hard' and avg_score < self.performance_threshold['hard']:
            return 'medium'
        
        return current_difficulty
    
    def get_personalized_explanation(self, question, is_correct, student_answer):
        """Generate AI-powered explanations for answers"""
        if is_correct:
            explanations = [
                "🎯 Excellent! You nailed this. Keep it up!",
                "✨ Perfect! Your understanding is crystal clear.",
                "🌟 Brilliant answer! You're mastering this concept.",
                "💪 Spot on! You're making great progress.",
            ]
        else:
            explanations = [
                "📚 Not quite. The key concept here is: " + question.explanation,
                "🤔 Let's break it down. Remember: " + question.explanation,
                "💡 Good attempt! The correct approach is: " + question.explanation,
                "🎓 This relates to: " + question.explanation,
            ]
        
        import random
        return random.choice(explanations)


class ProgressTracker:
    """Tracks and analyzes student learning progress"""
    
    def __init__(self, student_profile):
        self.student = student_profile
    
    def get_topic_progress(self):
        """Get completion status and performance for each topic"""
        from apps.learning.models import Topic, StudentPerformance, Subject
        from django.db.models import Q
        
        # Filter subjects by student's grade level
        student_grade = self.student.grade_level
        active_subjects = Subject.objects.filter(
            is_active=True
        ).filter(
            Q(grade_level='all') | Q(grade_level=student_grade)
        )
        
        # Get topics that student has interacted with OR all topics from active subjects
        # First, get all topics from active subjects for this grade level
        topics = Topic.objects.filter(
            subject__in=active_subjects,
            is_active=True
        ).filter(
            Q(grade_level='all') | Q(grade_level=student_grade)
        ).order_by('subject__name', 'order', 'name')
        
        # But prioritize topics the student has actually attempted
        student_topic_ids = StudentPerformance.objects.filter(
            student=self.student
        ).values_list('topic_id', flat=True).distinct()
        
        topic_progress = []
        seen_topics = set()
        
        # First add topics the student has interacted with
        for topic in topics:
            if topic.id in student_topic_ids and topic.id not in seen_topics:
                seen_topics.add(topic.id)
                performances = StudentPerformance.objects.filter(
                    student=self.student,
                    topic=topic
                )
                
                if performances.exists():
                    avg_score = performances.aggregate(avg=Avg('percentage'))['avg']
                    total_attempts = performances.count()
                    last_attempted = performances.latest('assessed_at').assessed_at
                    
                    # Determine status
                    if avg_score >= 80:
                        status = 'mastered'
                    elif avg_score >= 60:
                        status = 'learning'
                    else:
                        status = 'struggling'
                    
                    topic_progress.append({
                        'topic': topic,
                        'avg_score': avg_score,
                        'total_attempts': total_attempts,
                        'last_attempted': last_attempted,
                        'status': status,
                        'completion_percentage': min((total_attempts / 5) * 100, 100),
                    })
        
        # Then add other topics from active subjects with no data (limit to prevent clutter)
        other_topics_count = 0
        for topic in topics:
            if topic.id not in seen_topics and other_topics_count < 5:  # Limit to 5 new topics
                seen_topics.add(topic.id)
                other_topics_count += 1
                topic_progress.append({
                    'topic': topic,
                    'avg_score': 0,
                    'total_attempts': 0,
                    'last_attempted': None,
                    'status': 'not_started',
                    'completion_percentage': 0,
                })
        
        return topic_progress
    
    def get_accuracy_trend(self, days=30):
        """Get accuracy trend over last N days"""
        from apps.learning.models import StudentPerformance
        
        start_date = timezone.now() - timedelta(days=days)
        performances = StudentPerformance.objects.filter(
            student=self.student,
            assessed_at__gte=start_date
        ).order_by('assessed_at')
        
        trend_data = {}
        for perf in performances:
            date_str = perf.assessed_at.strftime('%Y-%m-%d')
            if date_str not in trend_data:
                trend_data[date_str] = []
            trend_data[date_str].append(perf.percentage)
        
        # Calculate daily averages
        daily_trend = []
        for date_str in sorted(trend_data.keys()):
            avg = sum(trend_data[date_str]) / len(trend_data[date_str])
            daily_trend.append({
                'date': date_str,
                'average_accuracy': round(float(avg), 2)
            })
        
        return daily_trend

    def get_predicted_score_trend(self, days_into_future=7):
        """
        AI-driven linear regression to predict future scores based on historical data.
        Returns a list of predicted data points.
        """
        daily_trend = self.get_accuracy_trend(days=30)
        if len(daily_trend) < 3:  # Need at least 3 points for a meaningful trend
            return []
        
        try:
            from datetime import datetime
            
            x_vals = []
            y_vals = []
            
            first_date = datetime.strptime(daily_trend[0]['date'], '%Y-%m-%d')
            
            for item in daily_trend:
                current_date = datetime.strptime(item['date'], '%Y-%m-%d')
                x_vals.append((current_date - first_date).days)
                y_vals.append(float(item['average_accuracy']))
                
            # Basic Linear Regression: y = mx + b
            n = len(x_vals)
            sum_x = sum(x_vals)
            sum_y = sum(y_vals)
            sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
            sum_xx = sum(x * x for x in x_vals)
            
            denominator = (n * sum_xx - sum_x**2)
            if denominator == 0:
                return []
                
            slope = (n * sum_xy - sum_x * sum_y) / denominator
            intercept = (sum_y - slope * sum_x) / n
            
            # Predict future
            future_trend = []
            last_day = x_vals[-1]
            
            for i in range(1, days_into_future + 1):
                future_day = last_day + i
                predicted_score = slope * future_day + intercept
                # Bound between 0 and 100
                predicted_score = max(0, min(100, predicted_score))
                
                future_date = first_date + timedelta(days=future_day)
                future_trend.append({
                    'date': future_date.strftime('%Y-%m-%d'),
                    'score': round(predicted_score, 2),
                    'is_predicted': True
                })
                
            return future_trend
        except Exception as e:
            print(f"Prediction Error: {e}")
            return []
    
    def get_improvement_metrics(self):
        """Calculate overall improvement metrics"""
        from apps.learning.models import StudentPerformance
        
        performances = StudentPerformance.objects.filter(
            student=self.student
        ).order_by('assessed_at')
        
        if performances.count() < 2:
            return {
                'overall_improvement': 0,
                'total_attempts': performances.count(),
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0,
            }
        
        first_five = performances[:5].aggregate(avg=Avg('percentage'))['avg'] or 0
        last_five = performances.reverse()[:5]
        last_five_avg = last_five.aggregate(avg=Avg('percentage'))['avg'] or 0
        
        improvement = last_five_avg - first_five
        
        highest = performances.aggregate(highest=Max('percentage'))['highest'] or 0
        lowest = performances.aggregate(lowest=Min('percentage'))['lowest'] or 0
        
        return {
            'overall_improvement': round(improvement, 2),
            'total_attempts': performances.count(),
            'average_score': round(performances.aggregate(avg=Avg('percentage'))['avg'], 2),
            'highest_score': round(float(highest), 2) if highest else 0,
            'lowest_score': round(float(lowest), 2) if lowest else 0,
            'prediction_available': performances.count() >= 3
        }


class RevisionScheduler:
    """Generates smart revision schedule and reminders"""
    
    def __init__(self, student_profile):
        self.student = student_profile
    
    def get_revision_due_topics(self):
        """Identify topics that need revision"""
        from apps.learning.models import StudentPerformance, Topic
        
        # Topics not reviewed in last 7 days
        seven_days_ago = timezone.now() - timedelta(days=7)
        
        revision_needed = []
        seen_topics = set()
        
        # Get latest performance for each topic that's old enough for revision
        performances = StudentPerformance.objects.filter(
            student=self.student,
            assessed_at__lt=seven_days_ago
        ).order_by('-topic', '-assessed_at')
        
        for perf in performances:
            # Skip if we already have this topic
            if perf.topic_id in seen_topics:
                continue
            
            seen_topics.add(perf.topic_id)
            
            # Only suggest revision if performance was good but might fade
            if perf.percentage >= 70:
                revision_needed.append({
                    'topic': perf.topic,
                    'last_reviewed': perf.assessed_at,
                    'last_score': perf.percentage,
                    'days_since_review': (timezone.now() - perf.assessed_at).days,
                })
        
        return sorted(revision_needed, key=lambda x: x['days_since_review'], reverse=True)
    
    def get_weak_topics_for_practice(self):
        """Identify weak topics that need more practice"""
        from apps.learning.models import StudentPerformance, Topic
        
        weak_topics = []
        
        topics_data = StudentPerformance.objects.filter(
            student=self.student
        ).values('topic').annotate(avg=Avg('percentage')).filter(avg__lt=60)
        
        for item in topics_data:
            try:
                # item['topic'] is the topic ID
                topic_obj = Topic.objects.get(id=item['topic'])
                weak_topics.append({
                    'topic': topic_obj,
                    'average_score': round(item['avg'], 2),
                    'practice_recommended': True,
                })
            except Topic.DoesNotExist:
                continue
        
        return weak_topics


class LearningFeedback:
    """Generates AI-powered personalized feedback and motivation"""
    
    def __init__(self, student_profile):
        self.student = student_profile
    
    def get_motivational_message(self):
        """Generate personalized motivational message"""
        from apps.learning.models import StudentPerformance
        
        performances = StudentPerformance.objects.filter(
            student=self.student
        ).order_by('-assessed_at')[:1]
        
        if not performances.exists():
            messages = [
                "🚀 Ready to start your learning journey? Pick a topic and begin!",
                "📚 New here? Explore different subjects and find what interests you!",
            ]
        else:
            last_perf = performances.first()
            
            if last_perf.percentage >= 90:
                messages = [
                    f"🌟 Outstanding! You scored {last_perf.percentage}% - You're a true scholar!",
                    f"🎯 Incredible performance at {last_perf.percentage}%! Keep pushing!",
                    f"💫 Wow! {last_perf.percentage}% is exceptional!",
                ]
            elif last_perf.percentage >= 75:
                messages = [
                    f"✨ Great job! {last_perf.percentage}% shows solid progress!",
                    f"📈 Nice work! Your {last_perf.percentage}% score is improving!",
                    f"👏 Well done! {last_perf.percentage}% is a strong performance!",
                ]
            elif last_perf.percentage >= 60:
                messages = [
                    f"📚 Good effort! {last_perf.percentage}% - you're on the right track!",
                    f"🎓 {last_perf.percentage}% is a solid start. Keep practicing!",
                    f"💪 You scored {last_perf.percentage}% - keep working towards mastery!",
                ]
            else:
                messages = [
                    f"🤝 {last_perf.percentage}% - Let's review this together. You'll improve!",
                    f"📖 {last_perf.percentage}% shows room to grow. Review the concepts!",
                    f"🌱 {last_perf.percentage}% is the start. Let's master this topic!",
                ]
        
        import random
        return random.choice(messages)
    
    def get_daily_tip(self):
        """Get a random daily learning tip"""
        tips = [
            "💡 Tip: Review previously learned topics regularly to reinforce memory.",
            "⏱️ Tip: Study in focused 25-minute sessions with 5-minute breaks.",
            "🎯 Tip: Set specific learning goals for each study session.",
            "📝 Tip: Take notes while learning to improve retention.",
            "🤔 Tip: Try to explain concepts in your own words.",
            "🔄 Tip: Practice problems similar to what you just learned.",
            "😴 Tip: Get enough sleep - it helps your brain consolidate learning!",
            "🤝 Tip: Discuss topics with peers to deepen understanding.",
        ]
        
        import random
        return random.choice(tips)
    
    def get_next_learning_action(self):
        """Suggest next action based on student progress"""
        revision_scheduler = RevisionScheduler(self.student)
        
        weak_topics = revision_scheduler.get_weak_topics_for_practice()
        revision_topics = revision_scheduler.get_revision_due_topics()
        
        if weak_topics:
            topic = weak_topics[0]['topic']
            return {
                'action': 'practice_weak_topic',
                'message': f"Practice '{topic.name}' - Your average is only {weak_topics[0]['average_score']}%",
                'topic': topic,
                'priority': 'high',
            }
        elif revision_topics:
            topic = revision_topics[0]['topic']
            return {
                'action': 'revise_topic',
                'message': f"Time to revise '{topic.name}' - Last reviewed {revision_topics[0]['days_since_review']} days ago",
                'topic': topic,
                'priority': 'medium',
            }
        else:
            return {
                'action': 'explore_new_topic',
                'message': "Great! Why not explore a new topic?",
                'topic': None,
                'priority': 'low',
            }


# Import at end to avoid circular imports
from django.db.models import Max, Min
