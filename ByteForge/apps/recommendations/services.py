"""
AI Recommendation Engine Service
==================================
Rule-based recommendation system with explainable AI.

This service analyzes student performance, learning behavior, and preferences
to generate personalized recommendations.
"""

from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Count, Q
from apps.accounts.models import StudentProfile
from apps.learning.models import Topic, LearningResource, StudentPerformance, LearningActivity
from apps.recommendations.models import Recommendation, LearningPath, LearningPathStep
from apps.assessments.models import QuizAttempt


class RecommendationEngine:
    """
    Core AI recommendation engine.
    
    Uses rule-based logic to generate personalized recommendations
    based on student data analysis.
    """
    
    def __init__(self, student_profile):
        self.student = student_profile
        self.user = student_profile.user
    
    def generate_all_recommendations(self):
        """
        Generate all types of recommendations for a student.
        
        Returns:
            list: Created recommendation objects
        """
        recommendations = []
        
        # 1. Performance-based recommendations
        recommendations.extend(self._recommend_weak_topics())
        
        # 2. Learning style recommendations
        recommendations.extend(self._recommend_by_learning_style())
        
        # 3. Revision reminders
        recommendations.extend(self._recommend_revision())
        
        # 4. Practice recommendations
        recommendations.extend(self._recommend_practice())
        
        return recommendations
    
    def _recommend_weak_topics(self):
        """
        Identify weak topics and recommend resources.
        
        Logic:
        - Find topics where average performance < 60%
        - Match resources to student's learning style
        - Prioritize by how weak the topic is
        """
        recommendations = []
        
        # Get average performance per topic
        weak_topics = StudentPerformance.objects.filter(
            student=self.student,
            percentage__lt=60
        ).values('topic').annotate(
            avg_score=Avg('percentage'),
            attempt_count=Count('id')
        ).order_by('avg_score')[:5]  # Top 5 weakest topics
        
        for topic_data in weak_topics:
            topic = Topic.objects.get(id=topic_data['topic'])
            avg_score = topic_data['avg_score']
            
            # Find appropriate resources
            resources = self._find_matching_resources(topic, difficulty='easy')
            
            if resources:
                resource = resources[0]  # Take best match
                
                # Create recommendation
                rec = Recommendation.objects.create(
                    student=self.student,
                    recommendation_type='resource',
                    resource=resource,
                    topic=topic,
                    title=f"Improve Your {topic.name} Skills",
                    description=f"We noticed you're struggling with {topic.name}. This {resource.get_resource_type_display()} will help you understand the basics better.",
                    reason=f"Your average score in {topic.name} is {avg_score:.1f}%, which is below the target of 60%. This resource matches your {self.student.get_learning_style_display()} learning style.",
                    reasoning_factors={
                        'topic': topic.name,
                        'average_score': float(avg_score),
                        'target_score': 60,
                        'learning_style': self.student.learning_style,
                        'resource_type': resource.resource_type,
                        'difficulty': resource.difficulty
                    },
                    priority='high' if avg_score < 40 else 'medium',
                    recommended_date=timezone.now().date()
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _recommend_by_learning_style(self):
        """
        Recommend resources matching student's learning style.
        
        Logic:
        - Match resource type to learning style
        - Prioritize highly-rated resources
        - Focus on target subjects
        """
        recommendations = []
        
        # Map learning styles to resource types
        style_to_type = {
            'visual': 'video',
            'reading': 'article',
            'practice': 'quiz',
            'mixed': None  # All types
        }
        
        preferred_type = style_to_type.get(self.student.learning_style)
        
        # Get target subjects
        target_subjects = self.student.target_subjects or []
        
        if target_subjects:
            for subject_name in target_subjects[:3]:  # Top 3 subjects
                # Find topics in this subject
                topics = Topic.objects.filter(
                    subject__name__icontains=subject_name,
                    is_active=True
                )[:2]
                
                for topic in topics:
                    # Find resources
                    query = Q(topic=topic, is_verified=True, is_active=True)
                    if preferred_type:
                        query &= Q(resource_type=preferred_type)
                    
                    resources = LearningResource.objects.filter(query).order_by('-average_rating', '-view_count')[:1]
                    
                    if resources:
                        resource = resources[0]
                        rec = Recommendation.objects.create(
                            student=self.student,
                            recommendation_type='resource',
                            resource=resource,
                            topic=topic,
                            title=f"Explore {topic.name}",
                            description=f"Based on your interest in {subject_name}, we recommend this {resource.get_resource_type_display()}.",
                            reason=f"This resource matches your {self.student.get_learning_style_display()} learning style and aligns with your goal to learn {subject_name}.",
                            reasoning_factors={
                                'learning_style': self.student.learning_style,
                                'target_subject': subject_name,
                                'resource_type': resource.resource_type,
                                'rating': float(resource.average_rating)
                            },
                            priority='medium',
                            recommended_date=timezone.now().date()
                        )
                        recommendations.append(rec)
        
        return recommendations
    
    def _recommend_revision(self):
        """
        Recommend revision for topics studied long ago.
        
        Logic:
        - Find topics studied > 7 days ago
        - Check if performance was good but needs reinforcement
        """
        recommendations = []
        
        # Find old activities
        week_ago = timezone.now() - timedelta(days=7)
        old_activities = LearningActivity.objects.filter(
            student=self.student,
            status='completed',
            completed_at__lt=week_ago
        ).values('resource__topic').annotate(
            last_studied=Count('id')
        )[:3]
        
        for activity_data in old_activities:
            if activity_data['resource__topic']:
                topic = Topic.objects.get(id=activity_data['resource__topic'])
                
                rec = Recommendation.objects.create(
                    student=self.student,
                    recommendation_type='revision',
                    topic=topic,
                    title=f"Time to Revise {topic.name}",
                    description=f"It's been a while since you studied {topic.name}. A quick revision will help reinforce your knowledge.",
                    reason=f"You last studied this topic over a week ago. Regular revision helps with long-term retention.",
                    reasoning_factors={
                        'topic': topic.name,
                        'days_since_study': 7,
                        'revision_importance': 'high'
                    },
                    priority='low',
                    recommended_date=timezone.now().date()
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _recommend_practice(self):
        """
        Recommend practice quizzes for topics with low confidence.
        
        Logic:
        - Find topics where student needs more practice
        - Recommend adaptive quizzes
        """
        recommendations = []
        
        # Find topics with low quiz scores
        low_quiz_topics = QuizAttempt.objects.filter(
            student=self.student,
            percentage__lt=70
        ).values('assessment__topic').annotate(
            avg_score=Avg('percentage')
        ).order_by('avg_score')[:3]
        
        for topic_data in low_quiz_topics:
            if topic_data['assessment__topic']:
                topic = Topic.objects.get(id=topic_data['assessment__topic'])
                avg_score = topic_data['avg_score']
                
                rec = Recommendation.objects.create(
                    student=self.student,
                    recommendation_type='practice',
                    topic=topic,
                    title=f"Practice {topic.name}",
                    description=f"Strengthen your understanding of {topic.name} with targeted practice questions.",
                    reason=f"Your quiz average in {topic.name} is {avg_score:.1f}%. More practice will help you master this topic.",
                    reasoning_factors={
                        'topic': topic.name,
                        'quiz_average': float(avg_score),
                        'target_score': 70
                    },
                    priority='medium',
                    recommended_date=timezone.now().date()
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _find_matching_resources(self, topic, difficulty='easy'):
        """
        Find resources matching student's learning style and difficulty.
        
        Args:
            topic: Topic object
            difficulty: Resource difficulty level
        
        Returns:
            QuerySet of matching resources
        """
        # Map learning styles to resource types
        style_to_type = {
            'visual': ['video', 'interactive'],
            'reading': ['article', 'pdf'],
            'practice': ['quiz', 'project'],
            'mixed': None  # All types
        }
        
        preferred_types = style_to_type.get(self.student.learning_style)
        
        query = Q(topic=topic, difficulty=difficulty, is_verified=True, is_active=True)
        
        if preferred_types:
            query &= Q(resource_type__in=preferred_types)
        
        return LearningResource.objects.filter(query).order_by('-average_rating', '-view_count')
    
    def generate_learning_path(self, subject_name, goal_description=""):
        """
        Generate a personalized learning path for a subject.
        
        Args:
            subject_name: Name of the subject
            goal_description: Student's learning goal
        
        Returns:
            LearningPath object
        """
        from apps.learning.models import Subject
        
        try:
            subject = Subject.objects.get(name__iexact=subject_name)
        except Subject.DoesNotExist:
            return None
        
        # Get topics in order
        topics = Topic.objects.filter(
            subject=subject,
            is_active=True
        ).order_by('order')
        
        # Create learning path
        path = LearningPath.objects.create(
            student=self.student,
            name=f"Master {subject.name}",
            description=goal_description or f"Complete learning path for {subject.name}",
            status='not_started',
            estimated_completion_days=len(topics) * 7,  # 1 week per topic
            is_ai_generated=True,
            generation_criteria={
                'subject': subject.name,
                'student_level': self.student.grade_level,
                'learning_pace': self.student.learning_pace,
                'total_topics': len(topics)
            }
        )
        
        # Create steps
        for idx, topic in enumerate(topics, 1):
            step = LearningPathStep.objects.create(
                learning_path=path,
                topic=topic,
                step_number=idx,
                title=f"Learn {topic.name}",
                description=topic.description,
                status='locked' if idx > 1 else 'available',
                estimated_hours=float(topic.estimated_hours)
            )
            
            # Add recommended resources
            resources = self._find_matching_resources(topic, difficulty=topic.difficulty_level)[:3]
            step.recommended_resources.set(resources)
        
        return path


class StudentAnalytics:
    """
    Analyze student learning patterns and performance.
    """
    
    def __init__(self, student_profile):
        self.student = student_profile
    
    def get_strengths_and_weaknesses(self):
        """
        Identify student's strong and weak topics.
        
        Returns:
            dict: {'strengths': [...], 'weaknesses': [...]}
        """
        performances = StudentPerformance.objects.filter(
            student=self.student
        ).values('topic__name').annotate(
            avg_score=Avg('percentage')
        )
        
        strengths = []
        weaknesses = []
        
        for perf in performances:
            topic_name = perf['topic__name']
            avg_score = perf['avg_score']
            
            if avg_score >= 80:
                strengths.append({'topic': topic_name, 'score': avg_score})
            elif avg_score < 60:
                weaknesses.append({'topic': topic_name, 'score': avg_score})
        
        return {
            'strengths': sorted(strengths, key=lambda x: x['score'], reverse=True),
            'weaknesses': sorted(weaknesses, key=lambda x: x['score'])
        }
    
    def detect_learning_pace(self):
        """
        Detect if student's actual learning pace matches their profile.
        
        Returns:
            str: 'fast', 'average', or 'slow'
        """
        # Analyze time spent vs progress
        activities = LearningActivity.objects.filter(
            student=self.student,
            status='completed'
        )
        
        if not activities.exists():
            return self.student.learning_pace
        
        avg_time = activities.aggregate(Avg('time_spent_minutes'))['time_spent_minutes__avg']
        avg_progress = activities.aggregate(Avg('progress_percentage'))['progress_percentage__avg']
        
        # Simple heuristic
        if avg_progress > 80 and avg_time < 30:
            return 'fast'
        elif avg_progress < 50 or avg_time > 60:
            return 'slow'
        else:
            return 'average'
    
    def get_engagement_score(self):
        """
        Calculate student engagement score (0-100).
        
        Factors:
        - Current streak
        - Activity frequency
        - Completion rate
        
        Returns:
            int: Engagement score
        """
        score = 0
        
        # Streak contribution (0-40 points)
        streak_score = min(self.student.current_streak * 4, 40)
        score += streak_score
        
        # Activity frequency (0-30 points)
        week_ago = timezone.now() - timedelta(days=7)
        recent_activities = LearningActivity.objects.filter(
            student=self.student,
            started_at__gte=week_ago
        ).count()
        activity_score = min(recent_activities * 5, 30)
        score += activity_score
        
        # Completion rate (0-30 points)
        total_activities = LearningActivity.objects.filter(student=self.student).count()
        if total_activities > 0:
            completed = LearningActivity.objects.filter(
                student=self.student,
                status='completed'
            ).count()
            completion_rate = (completed / total_activities) * 30
            score += completion_rate
        
        return min(int(score), 100)
