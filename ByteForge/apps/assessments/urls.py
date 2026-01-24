"""
Assessments App URLs
====================
URL patterns for quiz generation and assessment management.
"""

from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    # Quiz/Assessment taking (student-facing)
    path('generate-quiz/<int:topic_id>/', views.generate_quiz, name='generate_quiz'),
    path('quiz/<int:assessment_id>/', views.take_quiz, name='take_quiz'),
    path('quiz/<int:assessment_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('results/<int:attempt_id>/', views.quiz_results, name='quiz_results'),
    
    # Diagnostic
    path('diagnostic/', views.diagnostic_assessment, name='diagnostic_assessment'),
    path('diagnostic/results/', views.diagnostic_results, name='diagnostic_results'),
    
    # Assignment management (teacher-facing)
    path('create/', views.create_assignment, name='create_assignment'),
    path('my-assignments/', views.teacher_assignments, name='teacher_assignments'),
    path('<int:assignment_id>/edit/', views.edit_assignment, name='edit_assignment'),
    path('<int:assignment_id>/delete/', views.delete_assignment, name='delete_assignment'),
    path('<int:assignment_id>/add-question/', views.add_question, name='add_question'),
    path('<int:assignment_id>/toggle-publish/', views.toggle_publish, name='toggle_publish'),
]

