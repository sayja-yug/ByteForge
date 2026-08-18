"""
Assessment Generator Service
=============================
AI-powered quiz and assessment generation based on topics and difficulty.
"""

import random
from decimal import Decimal
from django.db.models import Sum, Count
from apps.learning.models import Topic, LearningResource, StudentPerformance
from apps.assessments.models import Assessment, Question, QuizAttempt
from apps.recommendations.models import Recommendation, LearningPath, LearningPathStep
import json
import logging
from django.conf import settings
from django.db import transaction
class QuizGenerator:
    """Generate quizzes automatically based on topic and difficulty"""
    
    # Sample question templates for different subjects
    MATH_TEMPLATES = [
        "Solve for x: {equation}",
        "What is the value of {expression}?",
        "Calculate: {problem}",
        "If {condition}, what is {question}?",
    ]
    
    SCIENCE_TEMPLATES = [
        "What is the definition of {concept}?",
        "Which of the following best describes {topic}?",
        "What happens when {scenario}?",
        "Identify the {element} in this {context}.",
    ]
    
    def __init__(self, topic, difficulty='medium', num_questions=10):
        self.topic = topic
        self.difficulty = difficulty
        self.num_questions = num_questions
    
    def generate_assessment(self, created_by):
        """
        Generate a complete assessment with questions.
        
        Args:
            created_by: TeacherProfile who is creating the assessment
        
        Returns:
            Assessment object with generated questions
        """
        # Create assessment
        assessment = Assessment.objects.create(
            title=f"{self.topic.name} - Auto-Generated Quiz",
            description=f"AI-generated quiz covering {self.topic.name} concepts",
            topic=self.topic,
            assessment_type='quiz',
            difficulty=self.difficulty,
            total_marks=self.num_questions * 10,
            passing_marks=self.num_questions * 6,
            time_limit_minutes=self.num_questions * 2,
            created_by=created_by,
            is_ai_generated=True,
            is_published=False  # Needs review before publishing
        )
        
        # Generate questions
        for i in range(self.num_questions):
            self._generate_question(assessment, i + 1)
        
        return assessment
    
    def _generate_question(self, assessment, order):
        """Generate a single MCQ question"""
        
        # Determine bloom level based on difficulty
        bloom_levels = {
            'easy': ['remember', 'understand'],
            'medium': ['understand', 'apply'],
            'hard': ['apply', 'analyze', 'evaluate']
        }
        bloom_level = random.choice(bloom_levels.get(self.difficulty, ['understand']))
        
        # Generate question based on subject
        subject_name = assessment.topic.subject.name.lower()
        
        if 'math' in subject_name:
            question_text = self._generate_math_question()
            options, correct = self._generate_math_options()
        elif 'science' in subject_name or 'physics' in subject_name or 'chemistry' in subject_name:
            question_text = self._generate_science_question()
            options, correct = self._generate_science_options()
        else:
            question_text = f"Question {order} about {assessment.topic.name}"
            options, correct = self._generate_generic_options()
        
        # Create question
        Question.objects.create(
            assessment=assessment,
            question_text=question_text,
            question_type='mcq',
            options=options,
            correct_answer=str(correct),
            marks=10,
            difficulty=self.difficulty,
            bloom_level=bloom_level,
            explanation=f"This tests your understanding of {assessment.topic.name}.",
            order=order
        )
    
    def _generate_math_question(self):
        """Generate a math question"""
        templates = [
            f"What is the value of {random.randint(10, 50)} + {random.randint(10, 50)}?",
            f"Solve: {random.randint(5, 20)}x = {random.randint(50, 200)}",
            f"Calculate {random.randint(2, 9)} × {random.randint(2, 9)}",
        ]
        return random.choice(templates)
    
    def _generate_science_question(self):
        """Generate a science question"""
        templates = [
            f"What is the primary function of {random.choice(['mitochondria', 'chloroplast', 'nucleus'])}?",
            f"Which law states that {random.choice(['energy is conserved', 'force equals mass times acceleration'])}?",
            f"What is the chemical formula for {random.choice(['water', 'carbon dioxide', 'methane'])}?",
        ]
        return random.choice(templates)
    
    def _generate_math_options(self):
        """Generate options for math question"""
        correct = random.randint(50, 150)
        options = [
            str(correct),
            str(correct + random.randint(5, 20)),
            str(correct - random.randint(5, 20)),
            str(correct + random.randint(25, 50))
        ]
        random.shuffle(options)
        correct_index = options.index(str(correct))
        return options, correct_index
    
    def _generate_science_options(self):
        """Generate options for science question"""
        options = [
            "Energy production",
            "Protein synthesis",
            "DNA storage",
            "Cell division"
        ]
        random.shuffle(options)
        return options, 0
    
    def _generate_generic_options(self):
        """Generate generic options"""
        options = ["Option A", "Option B", "Option C", "Option D"]
        return options, 0


class TeachingMaterialRecommender:
    """Recommend teaching materials based on class performance"""
    
    def __init__(self, teacher_profile):
        self.teacher = teacher_profile
    
    def get_recommendations(self):
        """
        Get AI-suggested teaching materials based on class needs.
        
        Returns:
            list: Recommended resources and topics to focus on
        """
        from apps.accounts.models import StudentProfile
        from apps.learning.models import StudentPerformance, LearningResource
        from django.db.models import Avg
        
        recommendations = []
        
        # Get all students (in real app, filter by teacher's classes)
        students = StudentProfile.objects.all()[:20]
        
        # Find topics where class average is low
        from apps.learning.models import Topic
        topics = Topic.objects.all()
        
        for topic in topics:
            performances = StudentPerformance.objects.filter(
                student__in=students,
                topic=topic
            )
            
            if performances.exists():
                avg_score = performances.aggregate(Avg('percentage'))['percentage__avg']
                
                if avg_score < 65:  # Class struggling with this topic
                    # Find good resources for this topic
                    resources = LearningResource.objects.filter(
                        topic=topic,
                        is_verified=True,
                        average_rating__gte=4.0
                    ).order_by('-average_rating')[:3]
                    
                    recommendations.append({
                        'topic': topic,
                        'class_average': avg_score,
                        'reason': f'Class average is {avg_score:.1f}% - below target',
                        'suggested_resources': resources,
                        'priority': 'high' if avg_score < 50 else 'medium'
                    })
        
        # Sort by priority and average
        recommendations.sort(key=lambda x: (x['priority'] == 'high', -x['class_average']), reverse=True)
        
        
        return recommendations[:5]  # Top 5 recommendations


class DiagnosticService:
    @staticmethod
    def calculate_scores(student_profile, attempt):
        """
        Analyzes the diagnostic attempt and returns detailed scoring.
        """
        # Calculate subject-wise performance
        # This assumes the diagnostic covers multiple topics linked to subjects
        
        # In this simplified version, we iterate through questions and group by topic/subject
        results = {
            'total_score': attempt.percentage,
            'subjects': {},
            'weak_topics': [],
            'strong_topics': []
        }
        
        # Analyze responses
        responses = attempt.responses.all()
        topic_performance = {}

        for response in responses:
            topic = response.question.assessment.topic
            subject = topic.subject.name
            
            if subject not in results['subjects']:
                results['subjects'][subject] = {'total': 0, 'correct': 0, 'score': 0}
            
            if topic.name not in topic_performance:
                topic_performance[topic.name] = {'total': 0, 'correct': 0, 'obj': topic}
            
            results['subjects'][subject]['total'] += 1
            topic_performance[topic.name]['total'] += 1
            
            if response.is_correct:
                results['subjects'][subject]['correct'] += 1
                topic_performance[topic.name]['correct'] += 1

        # Calculate percentages
        for sub, data in results['subjects'].items():
            if data['total'] > 0:
                data['score'] = (data['correct'] / data['total']) * 100
        
        for topic_name, data in topic_performance.items():
            score = 0
            if data['total'] > 0:
                score = (data['correct'] / data['total']) * 100
            
            if score < 60:
                results['weak_topics'].append(data['obj'])
            elif score >= 80:
                results['strong_topics'].append(data['obj'])

            # Save StudentPerformance record
            StudentPerformance.objects.create(
                student=student_profile,
                topic=data['obj'],
                score=score,
                max_score=100,
                percentage=score,
                assessment_type='diagnostic',
                difficulty_level='medium',
                time_taken_minutes=attempt.time_taken_minutes # Approximation
            )
            
        return results

    @staticmethod
    def classify_student(score):
        """
        Classifies student level based on score.
        """
        if score < 40:
            return 'Beginner'
        elif 40 <= score <= 70:
            return 'Intermediate'
        return 'Advanced'

    @staticmethod
    def generate_recommendations(student_profile, analysis_results):
        """
        Generates recommendations and learning path based on analysis.
        """
        level = DiagnosticService.classify_student(analysis_results['total_score'])
        
        # 1. Generate Recommendations for Weak Topics
        for topic in analysis_results['weak_topics']:
            # Find resources
            resources = LearningResource.objects.filter(topic=topic)
            
            rec_type_map = {
                'Beginner': 'video', 
                'Intermediate': 'article',
                'Advanced': 'project' # or practice
            }
            preferred_type = rec_type_map.get(level, 'video')
            
            target_resource = resources.filter(resource_type=preferred_type).first()
            if not target_resource and resources.exists():
                target_resource = resources.first()
            
            if target_resource:
                Recommendation.objects.create(
                    student=student_profile,
                    recommendation_type='resource',
                    resource=target_resource,
                    title=f"Improve your {topic.name} skills",
                    description=f"We noticed you struggled with {topic.name}. This {preferred_type} will help.",
                    reason=f"Score in {topic.name} was low during diagnostic.",
                    priority='high',
                    recommended_date=student_profile.updated_at.date() # Today
                )

        # 2. Generate 7-Day Starter Plan
        path = LearningPath.objects.create(
            student=student_profile,
            name="7-Day Personalized Kickstart",
            description=f"A {level} level plan to get you started.",
            estimated_completion_days=7,
            is_ai_generated=True,
            generation_criteria={'level': level, 'score': float(analysis_results['total_score'])}
        )

        # Add steps - simplified logic: 1 step per weak topic, then general topics
        step_num = 1
        topics_to_cover = analysis_results['weak_topics'][:3] # Prioritize up to 3 weak topics
        
        # If not enough weak topics, fill with others
        if len(topics_to_cover) < 7:
            remaining = 7 - len(topics_to_cover)
            other_topics = Topic.objects.exclude(id__in=[t.id for t in topics_to_cover])[:remaining]
            topics_to_cover.extend(list(other_topics))
        
        for topic in topics_to_cover:
            if level == 'Beginner':
                step_title = f"Day {step_num}: {topic.name} Basics"
                step_desc = f"Focus on {topic.name} to build your foundation."
            elif level == 'Intermediate':
                step_title = f"Day {step_num}: Intermediate {topic.name}"
                step_desc = f"Strengthen your understanding of {topic.name} concepts."
            else:
                step_title = f"Day {step_num}: Advanced {topic.name}"
                step_desc = f"Master complex problems and applications in {topic.name}."
                
            step = LearningPathStep.objects.create(
                learning_path=path,
                topic=topic,
                step_number=step_num,
                title=step_title,
                description=step_desc,
                status='available' if step_num == 1 else 'locked',
                estimated_hours=1.5
            )
            step_num += 1
            
        return path

    @staticmethod
    def finalize_diagnostic(student_profile, attempts):
        """
        Aggregates results from multiple diagnostic attempts (one per topic)
        and generates a unified report and study plan.
        """
        aggregated_results = {
            'total_score': 0,
            'subjects': {},
            'weak_topics': [],
            'strong_topics': []
        }
        
        total_max_score = 0
        total_score_obtained = 0
        
        for attempt in attempts:
            # Re-use calculate_scores logic or just extract from attempt
            # Since calculate_scores saves StudentPerformance, we should call it for each attempt first if not done
            # But here we assume attempts are processed.
            
            # We can re-calculate or just use the attempt data
            # Let's simple aggregation here
            topic = attempt.assessment.topic
            subject = topic.subject.name
            
            if subject not in aggregated_results['subjects']:
                aggregated_results['subjects'][subject] = {'total': 0, 'correct': 0, 'score': 0}
            
            aggregated_results['subjects'][subject]['total'] += attempt.assessment.questions.count()
            aggregated_results['subjects'][subject]['correct'] += attempt.correct_answers
            
            total_max_score += attempt.assessment.total_marks
            total_score_obtained += attempt.score
            
            topic_percentage = attempt.percentage
            if topic_percentage < 60:
                aggregated_results['weak_topics'].append(topic)
            elif topic_percentage >= 80:
                aggregated_results['strong_topics'].append(topic)
                
            # Create StudentPerformance if not exists (assuming view handles it or we do it here)
            # ideally the view calls calculate_scores for each, then this.
            
        # Finalize subject scores
        for sub, data in aggregated_results['subjects'].items():
            if data['total'] > 0:
                data['score'] = (data['correct'] / data['total']) * 100
                
        # Overall score
        if total_max_score > 0:
            aggregated_results['total_score'] = (total_score_obtained / total_max_score) * 100
            
        # Generate Recommendations & Path
        return DiagnosticService.generate_recommendations(student_profile, aggregated_results)

class DiagnosticGenerator:
    """Generate personalized diagnostic tests using Groq AI"""
    
    @staticmethod
    def generate_personalized_diagnostic(student_profile):
        """
        Dynamically generates a diagnostic assessment for the student using Groq AI,
        based on their grade level.
        """
        from apps.learning.models import Topic
        import os
        
        # Try to use groq client
        try:
            from groq import Groq
            api_key = getattr(settings, 'GROQ_API_KEY', None) or os.environ.get('GROQ_API_KEY')
            if not api_key:
                logging.warning("No GROQ_API_KEY found, falling back to static generation")
                return []
                
            client = Groq(api_key=api_key)
            
            # Select 2 random topics for the diagnostic
            topics = Topic.objects.all().order_by('?')[:2]
            if not topics:
                return []
                
            assessments = []
            
            for topic in topics:
                # Ask Groq to generate 3 MCQs
                prompt = f"""You are an expert educator.
Generate 3 multiple choice questions for a student in {student_profile.grade_level} on the topic of "{topic.name}" ({topic.subject.name}).
Return the response strictly as a JSON array of objects, with no markdown formatting.
Each object must have these keys:
"question_text" (string)
"options" (array of 4 string options)
"correct_answer" (string, exact match of one of the options)
"explanation" (string)
"""
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "You output JSON arrays ONLY."},
                            {"role": "user", "content": prompt}
                        ],
                        model="openai/gpt-oss-20b",
                        temperature=0.7,
                        max_tokens=1000,
                    )
                    
                    response_text = chat_completion.choices[0].message.content.strip()
                    # Clean up possible markdown code block
                    if response_text.startswith("```json"):
                        response_text = response_text[7:-3].strip()
                    elif response_text.startswith("```"):
                        response_text = response_text[3:-3].strip()
                        
                    questions_data = json.loads(response_text)
                    
                    # Create assessment
                    with transaction.atomic():
                        assessment = Assessment.objects.create(
                            title=f"Diagnostic: {topic.name} ({student_profile.user.username})",
                            description=f"Personalized diagnostic test for {student_profile.user.get_full_name()}",
                            topic=topic,
                            assessment_type='diagnostic',
                            difficulty='medium',
                            total_marks=len(questions_data) * 10,
                            passing_marks=len(questions_data) * 6,
                            is_ai_generated=True,
                            is_published=True # Must be published to be visible
                        )
                        
                        for i, q_data in enumerate(questions_data):
                            Question.objects.create(
                                assessment=assessment,
                                question_text=q_data['question_text'],
                                question_type='mcq',
                                options=q_data['options'],
                                correct_answer=q_data['correct_answer'],
                                marks=10,
                                difficulty='medium',
                                bloom_level='understand',
                                explanation=q_data.get('explanation', ''),
                                order=i + 1
                            )
                        
                        assessments.append(assessment)
                except Exception as e:
                    logging.error(f"Groq API error for topic {topic.name}: {str(e)}")
                    continue
                    
            return assessments
        except ImportError:
            logging.error("Groq package not installed")
            return []

