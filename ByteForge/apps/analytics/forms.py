"""
Analytics App Forms
====================
Forms for student report cards and manual grading.
"""

from django import forms
from .models import ReportCard, TeacherMark
from apps.accounts.models import StudentProfile


class ReportCardForm(forms.ModelForm):
    """Form for teachers to issue student report cards"""
    
    # We add a hidden field for the JSON data which will be managed by JS in the template
    grades_json = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = ReportCard
        fields = [
            'term',
            'academic_session',
            'total_percentage',
            'attendance_percentage',
            'remarks',
            'is_published',
        ]
        widgets = {
            'term': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. First Term, Final Exam'
            }),
            'academic_session': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 2025-26'
            }),
            'total_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 0.01,
                'min': 0,
                'max': 100
            }),
            'attendance_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 0.01,
                'min': 0,
                'max': 100
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter overall performance and behavioral observations'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
