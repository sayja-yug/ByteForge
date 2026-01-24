"""
Recommendations app URL patterns
"""
from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('', views.recommendations_list, name='list'),
    path('<int:recommendation_id>/', views.recommendation_detail, name='detail'),
    path('<int:recommendation_id>/feedback/', views.recommendation_feedback, name='feedback'),
    path('path/<int:path_id>/', views.learning_path_detail, name='path_detail'),
]
