"""
Management command to add sample YouTube videos to learning resources
"""
from django.core.management.base import BaseCommand
from apps.learning.models import LearningResource, Topic, Subject


class Command(BaseCommand):
    help = 'Add sample YouTube video resources for learning topics'

    def handle(self, *args, **options):
        # Get or create Mathematics subject
        subject, created = Subject.objects.get_or_create(
            name='Mathematics',
            defaults={
                'description': 'Core mathematical concepts',
                'icon': 'fas fa-calculator',
                'color_code': '#3498db'
            }
        )

        # Get Algebra Basics topic
        try:
            algebra_topic = Topic.objects.get(name='Algebra Basics', subject=subject)
        except Topic.DoesNotExist:
            self.stdout.write(self.style.ERROR('Algebra Basics topic not found'))
            return

        # Sample YouTube videos for Algebra Basics - Using REAL Khan Academy video IDs
        videos = [
            {
                'title': 'Algebra Basics - Introduction to Variables',
                'description': 'Learn the basics of algebra including variables, constants, and simple expressions. Perfect for beginners.',
                'url': 'https://www.youtube.com/watch?v=NybHckSEQBI',
                'duration_minutes': 12,
                'difficulty': 'easy',
                'author': 'Khan Academy'
            },
            {
                'title': 'Solving Linear Equations',
                'description': 'Master the fundamentals of solving linear equations step by step with clear examples.',
                'url': 'https://www.youtube.com/watch?v=bAerID24QJ0',
                'duration_minutes': 15,
                'difficulty': 'easy',
                'author': 'Khan Academy'
            },
            {
                'title': 'Algebraic Expressions and Simplification',
                'description': 'Learn how to simplify algebraic expressions using the distributive property and combining like terms.',
                'url': 'https://www.youtube.com/watch?v=jRWaSbsH_CU',
                'duration_minutes': 18,
                'difficulty': 'easy',
                'author': 'Khan Academy'
            },
            {
                'title': 'Two-step equations',
                'description': 'Solving two-step linear equations step by step with clear examples.',
                'url': 'https://www.youtube.com/watch?v=a2tiBszKg_E',
                'duration_minutes': 20,
                'difficulty': 'medium',
                'author': 'Khan Academy'
            },
            {
                'title': 'Introduction to Polynomials',
                'description': 'Understand polynomials, their terms, degree, and how to work with them algebraically.',
                'url': 'https://www.youtube.com/watch?v=Vm7H0VTsG2E',
                'duration_minutes': 22,
                'difficulty': 'medium',
                'author': 'Khan Academy'
            },
        ]

        # Create or update video resources
        created_count = 0
        updated_count = 0

        for video in videos:
            # Keep URL as watch URL
            url = video['url']

            resource, created = LearningResource.objects.update_or_create(
                topic=algebra_topic,
                title=video['title'],
                defaults={
                    'description': video['description'],
                    'resource_type': 'video',
                    'url': url,
                    'duration_minutes': video['duration_minutes'],
                    'difficulty': video['difficulty'],
                    'author': video['author'],
                    'is_verified': True,
                    'is_active': True,
                    'average_rating': 4.5
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {resource.title}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'✓ Updated: {resource.title}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully added/updated {created_count} new and {updated_count} existing YouTube videos!'
            )
        )
