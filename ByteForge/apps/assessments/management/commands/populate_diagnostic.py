from django.core.management.base import BaseCommand
from apps.learning.models import Subject, Topic
from apps.assessments.models import Assessment, Question

class Command(BaseCommand):
    help = 'Populates diagnostic data for Math, Physics, and Chemistry'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating diagnostic data...')

        # Subjects
        subjects_data = [
            {'name': 'Mathematics', 'color': '#3498db', 'icon': 'fas fa-calculator'},
            {'name': 'Physics', 'color': '#e74c3c', 'icon': 'fas fa-atom'},
            {'name': 'Chemistry', 'color': '#9b59b6', 'icon': 'fas fa-flask'}
        ]

        # Topics mapping
        topics_data = {
            'Mathematics': [
                {'name': 'Algebra', 'desc': 'Core algebra concepts'},
                {'name': 'Geometry', 'desc': 'Shapes and properties'},
                {'name': 'Calculus', 'desc': 'Limits and derivatives'}
            ],
            'Physics': [
                {'name': 'Mechanics', 'desc': 'Motion and forces'},
                {'name': 'Thermodynamics', 'desc': 'Heat and energy'},
                {'name': 'Electromagnetism', 'desc': 'Electricity and magnetism'}
            ],
            'Chemistry': [
                {'name': 'Organic Chemistry', 'desc': 'Carbon-based compounds'},
                {'name': 'Inorganic Chemistry', 'desc': 'Elements and minerals'},
                {'name': 'Physical Chemistry', 'desc': 'Chemical systems'}
            ]
        }

        # Questions (Sample - 3 per topic for brevity in this initial seed)
        questions_pool = {
            'Algebra': [
                {
                    'text': 'Solve for x: 2x + 5 = 15',
                    'options': ['x = 5', 'x = 10', 'x = 2', 'x = 7'],
                    'correct': 'x = 5',
                    'diff': 'easy',
                    'bloom': 'apply'
                },
                {
                    'text': 'What is the quadratic formula?',
                    'options': ['-b ± √(b² - 4ac) / 2a', '-b ± √(b² + 4ac) / 2a', 'b ± √(b² - 4ac) / 2a', 'None of these'],
                    'correct': '-b ± √(b² - 4ac) / 2a',
                    'diff': 'medium',
                    'bloom': 'remember'
                }
            ],
            'Mechanics': [
                {
                    'text': 'What represents Newton\'s Second Law?',
                    'options': ['F = ma', 'E = mc²', 'F = GmM/r²', 'v = d/t'],
                    'correct': 'F = ma',
                    'diff': 'easy',
                    'bloom': 'remember'
                }
            ],
            'Organic Chemistry': [
                {
                    'text': 'Which element is the basis of organic chemistry?',
                    'options': ['Carbon', 'Oxygen', 'Nitrogen', 'Hydrogen'],
                    'correct': 'Carbon',
                    'diff': 'easy',
                    'bloom': 'remember'
                }
            ]
        }

        for sub_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                name=sub_data['name'],
                defaults={'color_code': sub_data['color'], 'icon': sub_data['icon']}
            )
            if created:
                self.stdout.write(f'Created subject: {subject.name}')

            for topic_data in topics_data.get(subject.name, []):
                topic, t_created = Topic.objects.get_or_create(
                    subject=subject,
                    name=topic_data['name'],
                    defaults={'description': topic_data['desc']}
                )
                
                # specific checks for diagnostic assessment
                assessment, a_created = Assessment.objects.get_or_create(
                    topic=topic,
                    assessment_type='diagnostic',
                    title=f'Diagnostic Test - {topic.name}',
                    defaults={
                        'description': 'Initial diagnostic assessment',
                        'total_marks': 10,
                        'passing_marks': 4,
                        'is_published': True
                    }
                )

                # Add questions if none exist
                if assessment.questions.count() == 0:
                    q_list = questions_pool.get(topic.name, [])
                    # Fallback generic question if no specific pool
                    if not q_list:
                        q_list = [{
                            'text': f'Basic concept of {topic.name}',
                            'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                            'correct': 'Option A',
                            'diff': 'easy',
                            'bloom': 'understand'
                        }]
                    
                    for i, q in enumerate(q_list):
                        Question.objects.create(
                            assessment=assessment,
                            question_text=q['text'],
                            question_type='mcq',
                            options=q['options'],
                            correct_answer=q['correct'],
                            difficulty=q['diff'],
                            bloom_level=q['bloom'],
                            order=i+1,
                            marks=5
                        )
                    self.stdout.write(f'  Added questions to {assessment.title}')

        self.stdout.write(self.style.SUCCESS('Successfully populated diagnostic data'))
