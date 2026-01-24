"""
Assessment Forms
================
Forms for creating and managing assessments/assignments.
"""

from django import forms
from django.utils import timezone
from .models import Assessment, Question
from apps.learning.models import Topic


class AssignmentForm(forms.ModelForm):
    """Form for creating/editing assignments"""
    
    due_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        help_text="Optional deadline for assignment submission"
    )
    
    class Meta:
        model = Assessment
        fields = [
            'title',
            'description',
            'topic',
            'assessment_type',
            'difficulty',
            'total_marks',
            'passing_marks',
            'time_limit_minutes',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter assignment title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the assignment objectives and instructions'
            }),
            'topic': forms.Select(attrs={
                'class': 'form-control'
            }),
            'assessment_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-control'
            }),
            'total_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'passing_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'time_limit_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Leave empty for no time limit'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only active topics
        self.fields['topic'].queryset = Topic.objects.filter(is_active=True)
        # Set default to assignment
        self.fields['assessment_type'].initial = 'assignment'
    
    def clean(self):
        cleaned_data = super().clean()
        total_marks = cleaned_data.get('total_marks')
        passing_marks = cleaned_data.get('passing_marks')
        
        if total_marks and passing_marks:
            if passing_marks > total_marks:
                raise forms.ValidationError(
                    "Passing marks cannot be greater than total marks."
                )
        
        return cleaned_data


class QuestionForm(forms.ModelForm):
    """Form for adding questions to an assignment"""
    
    class Meta:
        model = Question
        fields = [
            'question_text',
            'question_type',
            'options',
            'correct_answer',
            'marks',
            'difficulty',
            'bloom_level',
            'explanation',
        ]
        widgets = {
            'question_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter the question'
            }),
            'question_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'options': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'For MCQ: Enter options as JSON array, e.g., ["Option A", "Option B", "Option C", "Option D"]'
            }),
            'correct_answer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'For MCQ: enter option index (0, 1, 2, 3), for others: enter the answer text'
            }),
            'marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-control'
            }),
            'bloom_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'explanation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Explanation of the correct answer (optional)'
            }),
        }
