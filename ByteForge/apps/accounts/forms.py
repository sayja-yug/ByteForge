"""
Authentication Forms
====================
Forms for user registration, login, and profile management.
"""

from django import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, StudentProfile, TeacherProfile, ParentProfile
from apps.analytics.models import TeacherMark
from apps.learning.models import Topic


class StudentRegistrationForm(UserCreationForm):
    """Student registration form with profile fields"""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    phone = forms.CharField(max_length=15, required=False)
    
    # Student-specific fields
    grade_level = forms.CharField(max_length=20, required=True)
    school_name = forms.CharField(max_length=200, required=False)
    learning_style = forms.ChoiceField(
        choices=StudentProfile.LEARNING_STYLE_CHOICES,
        initial='mixed'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data.get('phone', '')
        
        if commit:
            user.save()
            # Create student profile
            StudentProfile.objects.create(
                user=user,
                grade_level=self.cleaned_data['grade_level'],
                school_name=self.cleaned_data.get('school_name', ''),
                learning_style=self.cleaned_data['learning_style']
            )
        return user


class TeacherRegistrationForm(UserCreationForm):
    """Teacher registration form with profile fields"""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    phone = forms.CharField(max_length=15, required=False)
    
    # Teacher-specific fields
    qualification = forms.CharField(max_length=200, required=True)
    experience_years = forms.IntegerField(min_value=0, required=True)
    school_name = forms.CharField(max_length=200, required=False)
    specialization = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text='Enter subjects separated by commas (e.g., Mathematics, Physics)',
        required=True
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'teacher'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data.get('phone', '')
        
        if commit:
            user.save()
            # Create teacher profile
            specialization_list = [s.strip() for s in self.cleaned_data['specialization'].split(',')]
            TeacherProfile.objects.create(
                user=user,
                qualification=self.cleaned_data['qualification'],
                experience_years=self.cleaned_data['experience_years'],
                school_name=self.cleaned_data.get('school_name', ''),
                specialization=specialization_list
            )
        return user


class ParentRegistrationForm(UserCreationForm):
    """Parent registration form with profile fields"""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    phone = forms.CharField(max_length=15, required=True)
    
    # Parent-specific fields
    notification_frequency = forms.ChoiceField(
        choices=ParentProfile._meta.get_field('notification_frequency').choices,
        initial='weekly'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'parent'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        
        if commit:
            user.save()
            # Create parent profile
            ParentProfile.objects.create(
                user=user,
                notification_frequency=self.cleaned_data['notification_frequency']
            )
        return user


class CustomLoginForm(AuthenticationForm):
    """Custom login form with additional styling"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )



class TeacherMarkForm(forms.ModelForm):
    """Form for teachers to input student marks"""
    
    class Meta:
        model = TeacherMark
        fields = ['student', 'topic', 'marks_obtained', 'total_marks', 'assessment_title', 'assessment_date', 'notes']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'topic': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'marks_obtained': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Marks Obtained',
                'min': '0',
                'step': '0.01'
            }),
            'total_marks': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Total Marks',
                'min': '0',
                'step': '0.01'
            }),
            'assessment_title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Chapter 5 Test, Mid-term Exam'
            }),
            'assessment_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Optional feedback or notes for the student...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        
        # Filter students to show all active students
        self.fields['student'].queryset = StudentProfile.objects.filter(
            user__is_active=True
        ).select_related('user')
        
        # Filter topics to show all available topics
        self.fields['topic'].queryset = Topic.objects.all()
        
        # Make notes optional
        self.fields['notes'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        marks_obtained = cleaned_data.get('marks_obtained')
        total_marks = cleaned_data.get('total_marks')
        
        if marks_obtained is not None and total_marks is not None:
            if marks_obtained > total_marks:
                raise forms.ValidationError('Marks obtained cannot be greater than total marks.')
            if total_marks <= 0:
                raise forms.ValidationError('Total marks must be greater than zero.')
        
        return cleaned_data


class ConnectChildForm(forms.Form):
    """Form for parents to connect to a child account"""
    
    identifier = forms.CharField(
        max_length=255,
        label="Student Email or Username",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter child\'s email or username'
        })
    )

    def clean_identifier(self):
        identifier = self.cleaned_data.get('identifier')
        try:
            # Check for student role specifically
            child_user = User.objects.get(
                models.Q(email=identifier) | models.Q(username=identifier),
                role='student'
            )
            return child_user
        except User.DoesNotExist:
            raise forms.ValidationError("No student found with this email or username.")
