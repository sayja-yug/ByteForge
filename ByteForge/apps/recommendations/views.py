"""
Recommendations Views
====================
Views for browsing and managing AI recommendations.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Recommendation, LearningPath, LearningPathStep
from .services import RecommendationEngine


@login_required
def recommendations_list(request):
    """List all recommendations for the logged-in student"""
    if request.user.role != 'student':
        messages.error(request, 'Access denied. Students only.')
        return redirect('accounts:dashboard')
    
    student = request.user.student_profile
    
    # Get all recommendations
    recommendations = Recommendation.objects.filter(
        student=student
    ).order_by('-priority', '-recommended_date')
    
    # Mark as viewed
    for rec in recommendations:
        if not rec.is_viewed:
            rec.is_viewed = True
            rec.viewed_at = timezone.now()
            rec.save()
    
    context = {
        'recommendations': recommendations,
        'total': recommendations.count(),
    }
    return render(request, 'recommendations/recommendations_list.html', context)


@login_required
def recommendation_detail(request, recommendation_id):
    """View details of a specific recommendation"""
    if request.user.role != 'student':
        messages.error(request, 'Access denied. Students only.')
        return redirect('accounts:dashboard')
    
    recommendation = get_object_or_404(
        Recommendation,
        id=recommendation_id,
        student=request.user.student_profile
    )
    
    # Mark as viewed
    if not recommendation.is_viewed:
        recommendation.is_viewed = True
        recommendation.viewed_at = timezone.now()
        recommendation.save()
    
    # Redirect to resource or topic based on recommendation type
    if recommendation.resource:
        return redirect('learning:resource_detail', recommendation.resource.id)
    elif recommendation.topic:
        return redirect('learning:topic_detail', recommendation.topic.id)
    else:
        messages.info(request, 'This recommendation has no associated content.')
        return redirect('recommendations:list')


@login_required
def recommendation_feedback(request, recommendation_id):
    """Submit feedback on a recommendation"""
    if request.user.role != 'student':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    recommendation = get_object_or_404(
        Recommendation,
        id=recommendation_id,
        student=request.user.student_profile
    )
    
    if request.method == 'POST':
        helpful = request.POST.get('helpful')
        feedback = request.POST.get('feedback', '')
        
        recommendation.was_helpful = helpful == 'yes'
        recommendation.student_feedback = feedback
        recommendation.save()
        
        messages.success(request, 'Thank you for your feedback! It helps us improve recommendations.')
        return redirect('recommendations:list')
    
    return redirect('recommendations:list')


@login_required
def learning_path_detail(request, path_id):
    """View details of a specific learning path"""
    if request.user.role != 'student':
        messages.error(request, 'Access denied. Students only.')
        return redirect('accounts:dashboard')
    
    path = get_object_or_404(
        LearningPath,
        id=path_id,
        student=request.user.student_profile
    )
    
    # Mark path as in progress if it was not started
    if path.status == 'not_started':
        path.status = 'in_progress'
        path.started_at = timezone.now()
        path.save()
        
        # Also mark the first step as available
        first_step = path.steps.filter(step_number=1).first()
        if first_step and first_step.status == 'locked':
            first_step.status = 'available'
            first_step.save()
    
    steps = path.steps.all().select_related('topic', 'topic__subject').prefetch_related('recommended_resources')
    
    context = {
        'path': path,
        'steps': steps,
    }
    return render(request, 'recommendations/learning_path_detail.html', context)
