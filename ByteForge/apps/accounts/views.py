"""
Authentication Views
====================
Views for user registration, login, logout, and role-based dashboards.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Q, Count, Sum
from .forms import StudentRegistrationForm, TeacherRegistrationForm, ParentRegistrationForm, CustomLoginForm, TeacherMarkForm
from .models import User
from apps.analytics.models import TeacherMark


def home(request):
    """Landing page"""
    if request.user.is_authenticated:
        # Redirect to role-based dashboard
        return redirect('accounts:dashboard')
    return render(request, 'home.html')


def register_choice(request):
    """Registration role selection page"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return render(request, 'accounts/register_choice.html')


def register_student(request):
    """Student registration"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.first_name}! Your student account has been created.')
            return redirect('accounts:dashboard')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'accounts/register_student.html', {'form': form})


def register_teacher(request):
    """Teacher registration"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.first_name}! Your teacher account has been created and is pending verification.')
            return redirect('accounts:dashboard')
    else:
        form = TeacherRegistrationForm()
    
    return render(request, 'accounts/register_teacher.html', {'form': form})


def register_parent(request):
    """Parent registration"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = ParentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.first_name}! Your parent account has been created.')
            return redirect('accounts:dashboard')
    else:
        form = ParentRegistrationForm()
    
    return render(request, 'accounts/register_parent.html', {'form': form})


def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('accounts:dashboard')
    else:
        form = CustomLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard(request):
    """Role-based dashboard redirect"""
    user = request.user
    
    if user.role == 'student':
        return redirect('accounts:student_dashboard')
    elif user.role == 'teacher':
        return redirect('accounts:teacher_dashboard')
    elif user.role == 'parent':
        return redirect('accounts:parent_dashboard')
    elif user.role == 'admin':
        return redirect('/admin/')
    # Safety catch for superusers/staff who might not have a specific 'role' set
    elif user.is_staff or user.is_superuser:
        return redirect('/admin/')
    else:
        # Crucial fix for redirect loop: 
        # If role is invalid, log them out BEFORE redirecting to home
        # otherwise home -> dashboard -> home -> dashboard...
        logout(request)
        messages.error(request, 'Invalid user role - Please contact support.')
        return redirect('home')


@login_required
def student_dashboard(request):
    """Student dashboard with AI recommendations and analytics"""
    if request.user.role != 'student':
        messages.error(request, 'Access denied. Students only.')
        return redirect('accounts:dashboard')
    
    student_profile = request.user.student_profile
    
    # Redirect new students to diagnostic assessment
    if not student_profile.has_taken_diagnostic:
        messages.info(request, "Welcome! Please complete this diagnostic assessment to personalize your learning path.")
        return redirect('assessments:diagnostic_assessment')
    
    # Import recommendation engine and adaptive learning
    from apps.recommendations.services import RecommendationEngine, StudentAnalytics
    from apps.learning.adaptive_learning import (
        AdaptivePracticeEngine, ProgressTracker, RevisionScheduler, LearningFeedback
    )
    
    # Initialize adaptive learning engines
    progress_tracker = ProgressTracker(student_profile)
    revision_scheduler = RevisionScheduler(student_profile)
    learning_feedback = LearningFeedback(student_profile)
    
    # Fetch content from teachers
    from apps.learning.models import LearningResource
    from apps.assessments.models import Assessment
    
    teacher_resources = LearningResource.objects.filter(
        created_by__role='teacher',
        is_active=True,
        is_verified=True
    ).filter(
        Q(topic__grade_level=student_profile.grade_level) | 
        Q(topic__grade_level='all')
    ).select_related('topic', 'topic__subject', 'created_by').order_by('-created_at')[:4]
    
    teacher_assignments = Assessment.objects.filter(
        created_by__isnull=False,  # Created by teachers
        is_published=True
    ).filter(
        Q(topic__grade_level=student_profile.grade_level) |
        Q(topic__grade_level='all')
    ).select_related('topic', 'topic__subject', 'created_by').order_by('-created_at')[:4]
    
    # Get or create recommendations
    from apps.recommendations.models import Recommendation
    active_recommendations = Recommendation.objects.filter(
        student=student_profile,
        recommended_date__lte=timezone.now().date(),
        is_viewed=False
    ).order_by('-priority', '-recommended_date')[:5]
    
    # If no recommendations, generate them
    if not active_recommendations.exists():
        engine = RecommendationEngine(student_profile)
        engine.generate_all_recommendations()
        active_recommendations = Recommendation.objects.filter(
            student=student_profile,
            recommended_date__lte=timezone.now().date()
        ).order_by('-priority', '-recommended_date')[:5]
    
    # Get analytics
    analytics = StudentAnalytics(student_profile)
    strengths_weaknesses = analytics.get_strengths_and_weaknesses()
    engagement_score = analytics.get_engagement_score()
    detected_pace = analytics.detect_learning_pace()
    
    # Get learning paths
    from apps.recommendations.models import LearningPath
    learning_paths = LearningPath.objects.filter(
        student=student_profile
    ).order_by('-created_at')[:3]
    
    # Get recent activities
    from apps.learning.models import LearningActivity
    recent_activities = LearningActivity.objects.filter(
        student=student_profile
    ).order_by('-started_at')[:5]
    
    # Get gamification data
    from apps.analytics.models import GamificationProfile
    try:
        gamification = student_profile.gamification
    except GamificationProfile.DoesNotExist:
        # Create gamification profile if it doesn't exist
        gamification = GamificationProfile.objects.create(student=student_profile)
    
    # Get adaptive learning data
    topic_progress = progress_tracker.get_topic_progress()
    accuracy_trend = progress_tracker.get_accuracy_trend()
    predicted_trend = progress_tracker.get_predicted_score_trend()
    improvement_metrics = progress_tracker.get_improvement_metrics()
    
    # AI Success Probability (simulated ML model)
    success_probability = min(99.9, max(5.0, (engagement_score * 0.3) + (float(improvement_metrics['average_score']) * 0.7)))
    
    revision_due = revision_scheduler.get_revision_due_topics()
    weak_topics = revision_scheduler.get_weak_topics_for_practice()
    
    # Get feedback and motivation
    motivational_message = learning_feedback.get_motivational_message()
    daily_tip = learning_feedback.get_daily_tip()
    next_action = learning_feedback.get_next_learning_action()
    
    # Get teacher marks for this student
    teacher_marks = TeacherMark.objects.filter(
        student=student_profile
    ).select_related('teacher__user', 'topic').order_by('-assessment_date')[:10]
    
    context = {
        'student': student_profile,
        'user': request.user,
        'recommendations': active_recommendations,
        'strengths': strengths_weaknesses['strengths'][:3],
        'weaknesses': strengths_weaknesses['weaknesses'][:3],
        'engagement_score': engagement_score,
        'detected_pace': detected_pace,
        'learning_paths': learning_paths,
        'recent_activities': recent_activities,
        'gamification': gamification,
        'success_probability': success_probability,
        # Adaptive learning data
        'topic_progress': topic_progress,
        'accuracy_trend': accuracy_trend,
        'predicted_trend': predicted_trend,
        'improvement_metrics': improvement_metrics,
        'revision_due': revision_due[:3],  # Top 3 revision-due topics
        'weak_topics': weak_topics[:3],    # Top 3 weak topics
        'motivational_message': motivational_message,
        'daily_tip': daily_tip,
        'next_action': next_action,
        'teacher_resources': teacher_resources,
        'teacher_assignments': teacher_assignments,
        'teacher_marks': teacher_marks,
    }
    return render(request, 'dashboard/student_dashboard.html', context)


@login_required
def teacher_dashboard(request):
    """Teacher dashboard with class analytics"""
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied. Teachers only.')
        return redirect('accounts:dashboard')
    
    teacher_profile = request.user.teacher_profile
    
    # Get all students (in a real app, this would be filtered by teacher's classes)
    from apps.accounts.models import StudentProfile
    from apps.learning.models import StudentPerformance
    from apps.assessments.models import QuizAttempt
    
    students = StudentProfile.objects.all().order_by('user__first_name')
    
    # Get recent quiz attempts
    recent_attempts = QuizAttempt.objects.filter(
        assessment__created_by=teacher_profile
    ).select_related('student', 'assessment').order_by('-started_at')[:10]
    
    # Calculate class average
    class_avg = StudentPerformance.objects.filter(
        student__in=students
    ).aggregate(avg=Avg('percentage'))['avg'] or 0
    
    # Class Performance Trend (last 30 days)
    start_date = timezone.now() - timedelta(days=30)
    all_performances = StudentPerformance.objects.filter(
        assessed_at__gte=start_date
    ).order_by('assessed_at')
    
    class_trend_dict = {}
    for perf in all_performances:
        date_str = perf.assessed_at.strftime('%Y-%m-%d')
        if date_str not in class_trend_dict:
            class_trend_dict[date_str] = []
        class_trend_dict[date_str].append(perf.percentage)
        
    class_trend = []
    for date_str in sorted(class_trend_dict.keys()):
        avg = sum(class_trend_dict[date_str]) / len(class_trend_dict[date_str])
        class_trend.append({
            'date': date_str,
            'score': round(float(avg), 2)
        })

    # Enrich students with performance data
    students_with_performance = []
    struggling_students = []
    top_performers = []
    
    for student in students:
        avg_score = StudentPerformance.objects.filter(
            student=student
        ).aggregate(avg=Avg('percentage'))['avg'] or 0
        
        student_data = {
            'student': student,
            'avg_score': avg_score,
            'performance_count': StudentPerformance.objects.filter(student=student).count()
        }
        students_with_performance.append(student_data)
        
        if avg_score < 60 and avg_score > 0:
            struggling_students.append(student_data)
        elif avg_score >= 80:
            top_performers.append(student_data)
    
    # --- Content Performance Analytics ---
    from apps.learning.models import LearningResource
    from apps.assessments.models import Assessment
    
    # Teacher's resources stats
    teacher_resources = LearningResource.objects.filter(created_by=request.user)
    total_resource_views = teacher_resources.aggregate(total=Sum('view_count'))['total'] or 0
    top_resource = teacher_resources.order_by('-view_count').first()
    
    # Teacher's assignments stats
    teacher_assignments = Assessment.objects.filter(created_by=teacher_profile)
    assignment_stats = []
    for assignment in teacher_assignments:
        attempts = QuizAttempt.objects.filter(assessment=assignment, status='completed')
        if attempts.exists():
            avg_score = attempts.aggregate(avg=Avg('percentage'))['avg'] or 0
            assignment_stats.append({
                'assignment': assignment,
                'avg_score': avg_score,
                'total_completions': attempts.count()
            })
    
    # Top performing assignment (highest avg score)
    top_assignment = max(assignment_stats, key=lambda x: x['avg_score'], default=None) if assignment_stats else None

    context = {
        'teacher': teacher_profile,
        'user': request.user,
        'total_students': students.count(),
        'class_avg': class_avg,
        'class_trend': class_trend,
        'all_students': students_with_performance,
        'recent_attempts': recent_attempts,
        'struggling_students': struggling_students[:5],
        'top_performers': top_performers[:5],
        # Analytics data
        'total_resource_views': total_resource_views,
        'top_resource': top_resource,
        'assignment_stats': assignment_stats[:5],
        'top_assignment': top_assignment,
    }
    return render(request, 'dashboard/teacher_dashboard.html', context)


@login_required
def parent_dashboard(request):
    """Parent dashboard - basic view of children's progress"""
    if request.user.role != 'parent':
        messages.error(request, 'Access denied. Parents only.')
        return redirect('accounts:dashboard')
    
    parent_profile = request.user.parent_profile
    children_profiles = request.user.children.all()
    
    from .forms import ConnectChildForm
    connect_form = ConnectChildForm()
    
    context = {
        'parent': parent_profile,
        'children': children_profiles,
        'connect_form': connect_form,
        'user': request.user,
    }
    return render(request, 'dashboard/parent_dashboard.html', context)


@login_required
def teacher_mark_entry(request):
    """Teacher mark entry view for inputting student marks"""
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied. Teachers only.')
        return redirect('accounts:dashboard')
    
    teacher_profile = request.user.teacher_profile
    
    if request.method == 'POST':
        form = TeacherMarkForm(request.POST, teacher=teacher_profile)
        if form.is_valid():
            mark = form.save(commit=False)
            mark.teacher = teacher_profile
            mark.save()
            messages.success(request, f'Mark successfully recorded for {mark.student.user.get_full_name()}.')
            return redirect('accounts:teacher_mark_entry')
    else:
        form = TeacherMarkForm(teacher=teacher_profile)
    
    # Get recent marks entered by this teacher
    recent_marks = TeacherMark.objects.filter(
        teacher=teacher_profile
    ).select_related('student__user', 'topic').order_by('-created_at')[:10]
    
    context = {
        'form': form,
        'recent_marks': recent_marks,
        'teacher': teacher_profile,
        'user': request.user,
    }
    return render(request, 'dashboard/teacher_mark_entry.html', context)


@login_required
def connect_child(request):
    """View for parents to connect their account with a student account"""
    if request.user.role != 'parent':
        messages.error(request, 'Only parents can connect children accounts.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        from .forms import ConnectChildForm
        form = ConnectChildForm(request.POST)
        if form.is_valid():
            child_user = form.cleaned_data['identifier']
            
            # Check if already connected
            if child_user.student_profile.parent == request.user:
                messages.info(request, f"{child_user.get_full_name()} is already connected to your account.")
            else:
                # Link the child
                student_profile = child_user.student_profile
                student_profile.parent = request.user
                student_profile.save()
                
                messages.success(request, f"Successfully connected with {child_user.get_full_name()}!")
            
            return redirect('accounts:parent_dashboard')
    else:
        # If somehow accessed via GET, just redirect back
        return redirect('accounts:parent_dashboard')


@login_required
def parent_support_guide(request):
    """Guide for parents on how to support their child"""
    if request.user.role != 'parent':
        messages.error(request, 'Access denied. Parents only.')
        return redirect('accounts:dashboard')
    
    return render(request, 'dashboard/parent_support_guide.html', {'page_title': 'How to Support Your Child'})


@login_required
def parent_progress_guide(request):
    """Guide for parents on understanding progress metrics"""
    if request.user.role != 'parent':
        messages.error(request, 'Access denied. Parents only.')
        return redirect('accounts:dashboard')
    
    return render(request, 'dashboard/parent_progress_guide.html', {'page_title': 'Understanding Learning Progress'})
