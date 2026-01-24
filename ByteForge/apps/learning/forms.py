"""
Learning App Forms
==================
Forms for creating and managing learning resources.
"""

from django import forms
from .models import LearningResource, Topic, Subject


class SubjectForm(forms.ModelForm):
    """Form for creating/editing academic subjects"""
    
    class Meta:
        model = Subject
        fields = [
            'name',
            'description',
            'icon',
            'color_code',
            'grade_level',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Advanced Mathematics'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Objectives and overview of the subject'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. fas fa-atom'
            }),
            'color_code': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'grade_level': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 10th'
            }),
        }


class TopicForm(forms.ModelForm):
    """Form for creating/editing subject topics"""
    
    class Meta:
        model = Topic
        fields = [
            'subject',
            'name',
            'description',
            'difficulty_level',
            'estimated_hours',
            'order',
            'grade_level',
        ]
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Introduction to Calculus'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'What will students learn in this topic?'
            }),
            'difficulty_level': forms.Select(attrs={'class': 'form-control'}),
            'estimated_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 0.5,
                'min': 0.5
            }),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'grade_level': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 11th'
            }),
        }


class ResourceForm(forms.ModelForm):
    """Form for creating/editing learning resources"""
    
    class Meta:
        model = LearningResource
        fields = [
            'topic',
            'title',
            'description',
            'resource_type',
            'difficulty',
            'url',
            'file',
            'duration_minutes',
            'author',
        ]
        widgets = {
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter resource title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Explain what this resource covers'
            }),
            'resource_type': forms.Select(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. https://www.youtube.com/watch?v=...'
            }),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Estimated time in minutes'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Original creator name'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only active topics
        self.fields['topic'].queryset = Topic.objects.filter(is_active=True)
        
    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get('url')
        file = cleaned_data.get('file')
        resource_type = cleaned_data.get('resource_type')

        # Basic validation for types
        if resource_type == 'video' and not url:
            self.add_error('url', 'URL is required for video tutorials.')
        
        if resource_type == 'pdf' and not file and not url:
            self.add_error('file', 'Either a file upload or a URL is required for PDF documents.')

        return cleaned_data
