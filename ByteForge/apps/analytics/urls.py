"""
Analytics App URLs
==================
URL patterns for student report cards and monitoring.
"""

from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Report Cards
    path('student/<int:student_id>/report-card/issue/', views.issue_report_card, name='issue_report_card'),
    path('report-card/<int:report_id>/', views.report_card_detail, name='report_card_detail'),
    path('my-reports/', views.my_reports, name='my_reports'),
]
