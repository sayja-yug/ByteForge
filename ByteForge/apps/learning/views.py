"""
Learning App Views
==================
Views for browsing subjects, topics, and learning resources.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.utils import timezone
import re

from .models import Subject, Topic, LearningResource, LearningActivity, StudentPerformance


def get_youtube_embed_url(url, origin=None):
    """
    Convert YouTube URL to embed format (using nocookie for better compatibility)
    """
    if not url:
        return None
    
    # regex for all common youtube formats
    patterns = [
        r'(?:v=|v/|embed/|shorts/|live/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            # Use youtube-nocookie.com for maximum compatibility and privacy
            embed_url = f'https://www.youtube-nocookie.com/embed/{video_id}'
            
            # Add origin for reliable initialization (local and production)
            if origin:
                embed_url += f'?origin={origin}'
            
            return embed_url
    
    return url


def browse_subjects(request):
    """Browse all available subjects"""
    subjects = Subject.objects.filter(is_active=True).annotate(
        topic_count=Count('topics')
    )
    
    context = {
        'subjects': subjects,
    }
    return render(request, 'learning/browse_subjects.html', context)


def subject_detail(request, subject_id):
    """View subject details and topics"""
    subject = get_object_or_404(Subject, id=subject_id, is_active=True)
    topics = Topic.objects.filter(
        subject=subject,
        is_active=True
    ).order_by('order')
    
    # Get student progress if logged in - simplified for template compatibility
    topics_with_progress = []
    if request.user.is_authenticated and request.user.role == 'student':
        student = request.user.student_profile
        for topic in topics:
            # Calculate progress based on performance
            performances = StudentPerformance.objects.filter(
                student=student,
                topic=topic
            )
            topic_data = {'topic': topic}
            if performances.exists():
                avg_score = performances.aggregate(Avg('percentage'))['percentage__avg']
                topic_data['score'] = avg_score
                if avg_score >= 80:
                    topic_data['status'] = 'mastered'
                elif avg_score >= 60:
                    topic_data['status'] = 'learning'
                else:
                    topic_data['status'] = 'needs_work'
            # Add teacher resource count
            topic_data['teacher_resource_count'] = LearningResource.objects.filter(
                topic=topic,
                created_by__role='teacher',
                is_verified=True
            ).count()
            topics_with_progress.append(topic_data)
    else:
        for topic in topics:
            topics_with_progress.append({
                'topic': topic,
                'teacher_resource_count': LearningResource.objects.filter(
                    topic=topic,
                    created_by__role='teacher',
                    is_verified=True
                ).count()
            })
    
    context = {
        'subject': subject,
        'topics_with_progress': topics_with_progress,
    }
    return render(request, 'learning/subject_detail.html', context)


def topic_detail(request, topic_id):
    """View topic details and resources"""
    topic = get_object_or_404(Topic, id=topic_id, is_active=True)
    
    # Get resources
    resources = LearningResource.objects.filter(
        topic=topic,
        is_active=True,
        is_verified=True
    ).select_related('created_by').order_by('-average_rating', '-view_count')
    
    # Get assessments (teacher-created quizzes/tests)
    from apps.assessments.models import Assessment
    assessments = Assessment.objects.filter(
        topic=topic,
        is_published=True
    ).select_related('created_by').order_by('-created_at')
    
    # Filter by type if requested
    resource_type = request.GET.get('type')
    if resource_type:
        resources = resources.filter(resource_type=resource_type)
    
    # Get student data if logged in
    student_data = None
    if request.user.is_authenticated and request.user.role == 'student':
        student = request.user.student_profile
        
        # Get performance
        performances = StudentPerformance.objects.filter(
            student=student,
            topic=topic
        )
        avg_score = performances.aggregate(Avg('percentage'))['percentage__avg'] or 0
        
        # Get activities
        activities = LearningActivity.objects.filter(
            student=student,
            resource__topic=topic
        )
        
        student_data = {
            'avg_score': avg_score,
            'total_time': activities.aggregate(total=Count('time_spent_minutes'))['total'] or 0,
            'completed_resources': activities.filter(status='completed').count(),
        }
    
    context = {
        'topic': topic,
        'resources': resources,
        'assessments': assessments,
        'student_data': student_data,
        'resource_types': LearningResource.RESOURCE_TYPE_CHOICES,
    }
    return render(request, 'learning/topic_detail.html', context)


@login_required
def resource_detail(request, resource_id):
    """View and track resource usage"""
    resource = get_object_or_404(LearningResource, id=resource_id, is_active=True)
    
    if request.user.role != 'student':
        # Teachers and others can view but not track
        context = {'resource': resource}
        return render(request, 'learning/resource_detail.html', context)
    
    student = request.user.student_profile
    
    # Get or create activity
    activity, created = LearningActivity.objects.get_or_create(
        student=student,
        resource=resource,
        defaults={'status': 'started'}
    )
    
    if created:
        # Increment view count
        resource.view_count += 1
        resource.save()
    
    # Handle POST (update activity)
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'complete':
            activity.status = 'completed'
            activity.completed_at = timezone.now()
            activity.progress_percentage = 100
            activity.save()
            
            # Award XP
            from apps.analytics.models import GamificationProfile
            try:
                gamification = student.gamification
                gamification.add_xp(10, f"Completed {resource.title}")
                gamification.total_resources_viewed += 1
                gamification.save()
            except GamificationProfile.DoesNotExist:
                pass
            
            messages.success(request, f'Great job! You completed "{resource.title}" and earned 10 XP!')
            
        elif action == 'rate':
            rating = int(request.POST.get('rating', 0))
            feedback = request.POST.get('feedback', '')
            was_helpful = request.POST.get('was_helpful') == 'true'
            
            activity.rating = rating
            activity.feedback = feedback
            activity.was_helpful = was_helpful
            activity.save()
            
            # Update resource average rating
            all_ratings = LearningActivity.objects.filter(
                resource=resource,
                rating__isnull=False
            ).aggregate(Avg('rating'))
            resource.average_rating = all_ratings['rating__avg'] or 0
            resource.save()
            
            messages.success(request, 'Thank you for your feedback!')
        
        return redirect('learning:resource_detail', resource_id=resource_id)
    
    context = {
        'resource': resource,
        'activity': activity,
        'embed_url': get_youtube_embed_url(resource.url, origin=request.build_absolute_uri('/')[:-1]) if resource.resource_type == 'video' else None,
    }
    return render(request, 'learning/resource_detail.html', context)


@login_required
def my_learning(request):
    """Student's learning dashboard"""
    if request.user.role != 'student':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    student = request.user.student_profile
    
    # Get recent activities
    recent_activities = LearningActivity.objects.filter(
        student=student
    ).select_related('resource', 'resource__topic').order_by('-started_at')[:10]
    
    # Get in-progress resources (both started and in_progress)
    in_progress = LearningActivity.objects.filter(
        student=student,
        status__in=['started', 'in_progress']
    ).select_related('resource', 'resource__topic')
    
    # Get completed count
    completed_count = LearningActivity.objects.filter(
        student=student,
        status='completed'
    ).count()
    
    context = {
        'recent_activities': recent_activities,
        'in_progress': in_progress,
        'completed_count': completed_count,
    }
    return render(request, 'learning/my_learning.html', context)


# ============================================================================
# RESOURCE MANAGEMENT VIEWS (Teacher-facing)
# ============================================================================

@login_required
def create_resource(request):
    """Create a new learning resource (teachers only)"""
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can add resources.')
        return redirect('home')
    
    if request.method == 'POST':
        from .forms import ResourceForm
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.created_by = request.user
            # Automatically verify so students can see it immediately
            resource.is_verified = True
            resource.save()
            
            messages.success(request, f'Resource "{resource.title}" added successfully!')
            return redirect('learning:teacher_resources')
    else:
        from .forms import ResourceForm
        form = ResourceForm()
    
    context = {
        'form': form,
        'page_title': 'Add Learning Resource',
    }
    return render(request, 'learning/create_resource.html', context)


@login_required
def create_subject(request):
    """Create a new academic subject (teachers only)"""
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can add subjects.')
        return redirect('home')
    
    if request.method == 'POST':
        from .forms import SubjectForm
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.created_by = request.user
            subject.save()
            
            messages.success(request, f'Subject "{subject.name}" added successfully! Students can now learn this course.')
            return redirect('accounts:teacher_dashboard')
    else:
        from .forms import SubjectForm
        form = SubjectForm()
    
    context = {
        'form': form,
        'page_title': 'Add New Subject',
    }
    return render(request, 'learning/create_subject.html', context)


@login_required
def create_topic(request):
    """Create a new subject topic (teachers only)"""
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can add topics.')
        return redirect('home')
    
    if request.method == 'POST':
        from .forms import TopicForm
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.created_by = request.user
            topic.save()
            
            messages.success(request, f'Topic "{topic.name}" added successfully to "{topic.subject.name}".')
            return redirect('accounts:teacher_dashboard')
    else:
        from .forms import TopicForm
        form = TopicForm()
    
    context = {
        'form': form,
        'page_title': 'Add New Topic',
    }
    return render(request, 'learning/create_topic.html', context)


@login_required
def teacher_resources(request):
    """List all resources created by the teacher"""
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can view this page.')
        return redirect('home')
    
    # Get all resources created by this teacher
    resources = LearningResource.objects.filter(
        created_by=request.user
    ).select_related('topic', 'topic__subject').order_by('-created_at')
    
    context = {
        'resources': resources,
    }
    return render(request, 'learning/teacher_resources.html', context)


@login_required
def edit_resource(request, resource_id):
    """Edit an existing learning resource"""
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can edit resources.')
        return redirect('home')
    
    resource = get_object_or_404(LearningResource, id=resource_id)
    
    # Check permission
    if resource.created_by != request.user:
        messages.error(request, 'You can only edit your own resources.')
        return redirect('learning:teacher_resources')
    
    if request.method == 'POST':
        from .forms import ResourceForm
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, f'Resource "{resource.title}" updated successfully!')
            return redirect('learning:teacher_resources')
    else:
        from .forms import ResourceForm
        form = ResourceForm(instance=resource)
    
    context = {
        'form': form,
        'resource': resource,
        'page_title': 'Edit Resource',
    }
    return render(request, 'learning/edit_resource.html', context)


@login_required
def delete_resource(request, resource_id):
    """Delete a learning resource"""
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can delete resources.')
        return redirect('home')
    
    resource = get_object_or_404(LearningResource, id=resource_id)
    
    # Check permission
    if resource.created_by != request.user:
        messages.error(request, 'You can only delete your own resources.')
        return redirect('learning:teacher_resources')
    
    if request.method == 'POST':
        title = resource.title
        resource.delete()
        messages.success(request, f'Resource "{title}" deleted successfully!')
        return redirect('learning:teacher_resources')
    
    context = {
        'resource': resource,
    }
    return render(request, 'learning/delete_resource_confirm.html', context)

