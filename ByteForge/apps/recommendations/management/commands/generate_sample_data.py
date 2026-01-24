"""
Generate Sample Data for Testing
=================================
Creates realistic sample data to demonstrate the AI recommendation system.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from apps.accounts.models import User, StudentProfile, TeacherProfile
from apps.learning.models import Subject, Topic, LearningResource, StudentPerformance, LearningActivity
from apps.assessments.models import Assessment, Question, QuizAttempt, QuestionResponse
from apps.analytics.models import GamificationProfile, Badge
from apps.recommendations.services import RecommendationEngine


class Command(BaseCommand):
    help = 'Generate sample data for testing the AI recommendation system'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Generating sample data...'))
        
        # Create subjects
        subjects = self._create_subjects()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(subjects)} subjects'))
        
        # Create topics
        topics = self._create_topics(subjects)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(topics)} topics'))
        
        # Create teacher
        teacher = self._create_teacher()
        self.stdout.write(self.style.SUCCESS('✓ Created teacher account'))
        
        # Create learning resources
        resources = self._create_resources(topics, teacher)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(resources)} learning resources'))
        
        # Create sample student
        student = self._create_sample_student()
        self.stdout.write(self.style.SUCCESS('✓ Created sample student'))
        
        # Create student activities
        self._create_student_activities(student, resources)
        self.stdout.write(self.style.SUCCESS('✓ Created student activities'))
        
        # Create assessments
        assessments = self._create_assessments(topics, teacher)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(assessments)} assessments'))
        
        # Create student performance data
        self._create_student_performance(student, topics)
        self.stdout.write(self.style.SUCCESS('✓ Created performance data'))
        
        # Create quiz attempts
        self._create_quiz_attempts(student, assessments)
        self.stdout.write(self.style.SUCCESS('✓ Created quiz attempts'))
        
        # Create badges
        self._create_badges()
        self.stdout.write(self.style.SUCCESS('✓ Created badges'))
        
        # Generate AI recommendations
        engine = RecommendationEngine(student.student_profile)
        recommendations = engine.generate_all_recommendations()
        self.stdout.write(self.style.SUCCESS(f'✓ Generated {len(recommendations)} AI recommendations'))
        
        # Generate learning path
        path = engine.generate_learning_path('Mathematics', 'Master high school mathematics')
        if path:
            self.stdout.write(self.style.SUCCESS(f'✓ Generated learning path: {path.name}'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Sample data generation complete!'))
        self.stdout.write(self.style.SUCCESS(f'\nTest Student Login:'))
        self.stdout.write(self.style.SUCCESS(f'  Username: demo_student'))
        self.stdout.write(self.style.SUCCESS(f'  Password: demo123'))
        self.stdout.write(self.style.SUCCESS(f'\nTest Teacher Login:'))
        self.stdout.write(self.style.SUCCESS(f'  Username: demo_teacher'))
        self.stdout.write(self.style.SUCCESS(f'  Password: demo123'))
    
    def _create_subjects(self):
        subjects_data = [
            {'name': 'Mathematics', 'description': 'Core mathematical concepts', 'icon': 'fas fa-calculator', 'color_code': '#3498db'},
            {'name': 'Physics', 'description': 'Understanding the physical world', 'icon': 'fas fa-atom', 'color_code': '#e74c3c'},
            {'name': 'Chemistry', 'description': 'Study of matter and reactions', 'icon': 'fas fa-flask', 'color_code': '#2ecc71'},
            {'name': 'Computer Science', 'description': 'Programming and algorithms', 'icon': 'fas fa-laptop-code', 'color_code': '#9b59b6'},
        ]
        
        subjects = []
        for data in subjects_data:
            subject, created = Subject.objects.get_or_create(name=data['name'], defaults=data)
            subjects.append(subject)
        return subjects
    
    def _create_topics(self, subjects):
        topics_data = {
            'Mathematics': [
                ('Algebra Basics', 'beginner', 'Introduction to algebraic expressions', 8),
                ('Linear Equations', 'beginner', 'Solving linear equations', 10),
                ('Quadratic Equations', 'intermediate', 'Solving quadratic equations', 12),
                ('Trigonometry', 'intermediate', 'Trigonometric functions and identities', 15),
                ('Calculus Fundamentals', 'advanced', 'Introduction to derivatives and integrals', 20),
            ],
            'Physics': [
                ('Motion and Forces', 'beginner', 'Newtons laws of motion', 10),
                ('Energy and Work', 'intermediate', 'Conservation of energy', 12),
                ('Electricity', 'intermediate', 'Electric circuits and current', 14),
            ],
            'Chemistry': [
                ('Atomic Structure', 'beginner', 'Understanding atoms and molecules', 8),
                ('Chemical Bonding', 'intermediate', 'Ionic and covalent bonds', 10),
            ],
            'Computer Science': [
                ('Python Basics', 'beginner', 'Introduction to Python programming', 12),
                ('Data Structures', 'intermediate', 'Arrays, lists, and trees', 16),
                ('Data Science', 'intermediate', 'Data analysis, visualization, and statistical modeling', 20),
                ('Machine Learning', 'advanced', 'Supervised and unsupervised learning algorithms', 25),
            ],
        }
        
        topics = []
        for subject in subjects:
            if subject.name in topics_data:
                for idx, (name, difficulty, desc, hours) in enumerate(topics_data[subject.name], 1):
                    topic, created = Topic.objects.get_or_create(
                        subject=subject,
                        name=name,
                        defaults={
                            'description': desc,
                            'difficulty_level': difficulty,
                            'estimated_hours': hours,
                            'order': idx
                        }
                    )
                    topics.append(topic)
        return topics
    
    def _create_teacher(self):
        user, created = User.objects.get_or_create(
            username='demo_teacher',
            defaults={
                'email': 'teacher@demo.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'teacher',
                'is_verified': True
            }
        )
        if created:
            user.set_password('demo123')
            user.save()
            TeacherProfile.objects.create(
                user=user,
                qualification='M.Sc. in Mathematics',
                experience_years=8,
                school_name='Demo High School',
                specialization=['Mathematics', 'Physics'],
                is_verified_teacher=True
            )
        return user
    
    def _create_resources(self, topics, teacher):
        resource_types = ['video', 'article', 'pdf', 'quiz']
        difficulties = ['easy', 'medium', 'hard']
        
        resources = []
        for topic in topics[:8]:  # Create resources for first 8 topics
            for i in range(3):  # 3 resources per topic
                resource, created = LearningResource.objects.get_or_create(
                    topic=topic,
                    title=f"{topic.name} - {['Introduction', 'Deep Dive', 'Practice'][i]}",
                    defaults={
                        'description': f"Comprehensive {resource_types[i % 4]} on {topic.name}",
                        'resource_type': resource_types[i % 4],
                        'difficulty': difficulties[i],
                        'url': f'https://example.com/{topic.name.lower().replace(" ", "-")}-{i}',
                        'duration_minutes': random.randint(10, 60),
                        'author': 'Demo Author',
                        'average_rating': round(random.uniform(3.5, 5.0), 2),
                        'view_count': random.randint(50, 500),
                        'created_by': teacher,
                        'is_verified': True
                    }
                )
                resources.append(resource)
        return resources
    
    def _create_sample_student(self):
        user, created = User.objects.get_or_create(
            username='demo_student',
            defaults={
                'email': 'student@demo.com',
                'first_name': 'Alex',
                'last_name': 'Smith',
                'role': 'student',
                'is_verified': True
            }
        )
        if created:
            user.set_password('demo123')
            user.save()
            StudentProfile.objects.create(
                user=user,
                grade_level='10th Grade',
                school_name='Demo High School',
                learning_style='visual',
                learning_pace='average',
                target_subjects=['Mathematics', 'Physics'],
                current_streak=5,
                longest_streak=12,
                total_study_time=450
            )
            # Create gamification profile
            GamificationProfile.objects.create(
                student=user.student_profile,
                total_xp=850,
                current_level=5,
                current_streak=5,
                longest_streak=12
            )
        return user
    
    def _create_student_activities(self, student, resources):
        for resource in random.sample(resources, min(10, len(resources))):
            LearningActivity.objects.get_or_create(
                student=student.student_profile,
                resource=resource,
                defaults={
                    'status': random.choice(['completed', 'in_progress', 'completed']),
                    'time_spent_minutes': random.randint(10, 60),
                    'progress_percentage': random.randint(50, 100),
                    'revisit_count': random.randint(0, 3),
                    'rating': random.randint(3, 5),
                    'was_helpful': random.choice([True, True, False])
                }
            )
    
    def _create_assessments(self, topics, teacher):
        assessments = []
        for topic in topics[:5]:
            assessment, created = Assessment.objects.get_or_create(
                title=f"{topic.name} Quiz",
                topic=topic,
                defaults={
                    'description': f"Test your knowledge of {topic.name}",
                    'assessment_type': 'quiz',
                    'difficulty': topic.difficulty_level,
                    'total_marks': 100,
                    'passing_marks': 60,
                    'time_limit_minutes': 30,
                    'created_by': teacher.teacher_profile,
                    'is_published': True
                }
            )
            
            if created:
                # Create 5 questions
                for i in range(5):
                    Question.objects.create(
                        assessment=assessment,
                        question_text=f"Question {i+1} about {topic.name}",
                        question_type='mcq',
                        options=['Option A', 'Option B', 'Option C', 'Option D'],
                        correct_answer='0',
                        marks=20,
                        difficulty=random.choice(['easy', 'medium', 'hard']),
                        bloom_level=random.choice(['remember', 'understand', 'apply']),
                        explanation=f"Explanation for question {i+1}",
                        order=i+1
                    )
            
            assessments.append(assessment)
        return assessments
    
    def _create_student_performance(self, student, topics):
        # Create varied performance - some strong, some weak
        for topic in topics[:8]:
            # Simulate different performance levels
            if 'Algebra' in topic.name or 'Python' in topic.name:
                score = random.uniform(40, 55)  # Weak areas
            elif 'Linear' in topic.name:
                score = random.uniform(85, 95)  # Strong areas
            else:
                score = random.uniform(60, 80)  # Average
            
            StudentPerformance.objects.get_or_create(
                student=student.student_profile,
                topic=topic,
                defaults={
                    'score': score,
                    'max_score': 100,
                    'percentage': score,
                    'assessment_type': 'quiz',
                    'difficulty_level': topic.difficulty_level,
                    'time_taken_minutes': random.randint(20, 40),
                    'strengths': ['Basic concepts'] if score > 70 else [],
                    'weaknesses': ['Advanced problems'] if score < 60 else []
                }
            )
    
    def _create_quiz_attempts(self, student, assessments):
        for assessment in random.sample(assessments, min(3, len(assessments))):
            score = random.uniform(45, 75)
            QuizAttempt.objects.get_or_create(
                student=student.student_profile,
                assessment=assessment,
                defaults={
                    'status': 'submitted',
                    'score': score,
                    'percentage': score,
                    'time_taken_minutes': random.randint(20, 30),
                    'correct_answers': int(score / 20),
                    'wrong_answers': 5 - int(score / 20)
                }
            )
    
    def _create_badges(self):
        badges_data = [
            ('first_quiz', 'First Quiz', 'Complete your first quiz', 'quiz', '🎯', 10),
            ('7_day_streak', '7 Day Streak', 'Maintain a 7-day learning streak', 'streak', '🔥', 50),
            ('topic_master', 'Topic Master', 'Score 90%+ on any topic', 'topic', '🏆', 100),
            ('level_5', 'Level 5', 'Reach level 5', 'level', '⭐', 25),
        ]
        
        for badge_id, name, desc, category, icon, xp in badges_data:
            Badge.objects.get_or_create(
                badge_id=badge_id,
                defaults={
                    'name': name,
                    'description': desc,
                    'category': category,
                    'icon': icon,
                    'xp_reward': xp
                }
            )
