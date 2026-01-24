"""
Management command to generate lecture PDF resources for topics
"""
from django.core.management.base import BaseCommand
from apps.learning.models import LearningResource, Topic, Subject


class Command(BaseCommand):
    help = 'Generate lecture PDF resources for learning topics'

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

        # Sample PDF lecture resources
        pdfs = [
            {
                'title': 'Algebra Basics - Complete Lecture Notes',
                'description': 'Comprehensive lecture notes covering all fundamental concepts of algebra including variables, expressions, and equations.',
                'difficulty': 'easy',
                'author': 'Math Education Team',
                'duration_minutes': 45,
            },
            {
                'title': 'Variables and Expressions - Study Guide',
                'description': 'Detailed study guide on understanding variables, constants, and algebraic expressions with practice problems.',
                'difficulty': 'easy',
                'author': 'Math Education Team',
                'duration_minutes': 35,
            },
            {
                'title': 'Solving Equations - Complete Tutorial',
                'description': 'Step-by-step tutorial on solving linear equations with multiple examples and practice problems included.',
                'difficulty': 'medium',
                'author': 'Math Education Team',
                'duration_minutes': 50,
            },
            {
                'title': 'Algebraic Manipulation Techniques',
                'description': 'Advanced techniques for manipulating algebraic expressions including factoring, expanding, and simplifying.',
                'difficulty': 'medium',
                'author': 'Math Education Team',
                'duration_minutes': 40,
            },
            {
                'title': 'Polynomials and Factoring Guide',
                'description': 'Complete guide to understanding polynomials, their properties, and various factoring techniques.',
                'difficulty': 'medium',
                'author': 'Math Education Team',
                'duration_minutes': 55,
            },
        ]

        # Create PDF resources
        created_count = 0
        updated_count = 0

        for pdf in pdfs:
            resource, created = LearningResource.objects.update_or_create(
                topic=algebra_topic,
                title=pdf['title'],
                resource_type='pdf',
                defaults={
                    'description': pdf['description'],
                    'difficulty': pdf['difficulty'],
                    'author': pdf['author'],
                    'duration_minutes': pdf['duration_minutes'],
                    'url': '',  # No URL for generated PDFs
                    'is_verified': True,
                    'is_active': True,
                    'average_rating': 4.6
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
                f'\n✓ Successfully added/updated {created_count} new and {updated_count} existing PDF lecture resources!'
            )
        )
