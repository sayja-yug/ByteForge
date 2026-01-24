"""
Learning App URLs
=================
URL patterns for learning content browsing.
"""

from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    path('subjects/', views.browse_subjects, name='browse_subjects'),
    path('subjects/create/', views.create_subject, name='create_subject'),
    path('topics/create/', views.create_topic, name='create_topic'),
    path('subject/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('resource/<int:resource_id>/', views.resource_detail, name='resource_detail'),
    path('my-learning/', views.my_learning, name='my_learning'),
    
    # Resource management (teacher-facing)
    path('resources/create/', views.create_resource, name='create_resource'),
    path('resources/my/', views.teacher_resources, name='teacher_resources'),
    path('resources/<int:resource_id>/edit/', views.edit_resource, name='edit_resource'),
    path('resources/<int:resource_id>/delete/', views.delete_resource, name='delete_resource'),
]

