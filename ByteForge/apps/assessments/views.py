"""
Assessment Views
================
Views for quiz generation, taking quizzes, and viewing results.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum

from apps.learning.models import Topic, StudentPerformance
from apps.recommendations.models import LearningPath
from .models import Assessment, Question, QuizAttempt, QuestionResponse
from .services import QuizGenerator


@login_required
def generate_quiz(request, topic_id):
    """Generate a quiz for a topic (teacher only)"""
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can generate quizzes.')
        return redirect('home')
    
    topic = get_object_or_404(Topic, id=topic_id)
    
    if request.method == 'POST':
        difficulty = request.POST.get('difficulty', 'medium')
        num_questions = int(request.POST.get('num_questions', 10))
        
        # Generate quiz
        generator = QuizGenerator(topic, difficulty, num_questions)
        assessment = generator.generate_assessment(request.user.teacher_profile)
        
        messages.success(request, f'Quiz "{assessment.title}" generated successfully! Review and publish it in the admin panel.')
        return redirect('/admin/assessments/assessment/')
    
    context = {
        'topic': topic,
    }
    return render(request, 'assessments/generate_quiz.html', context)


@login_required
def take_quiz(request, assessment_id):
    """Take a quiz"""
    if request.user.role != 'student':
        messages.error(request, 'Only students can take quizzes.')
        return redirect('home')
    
    assessment = get_object_or_404(
        Assessment.objects.select_related('created_by', 'created_by__user', 'topic', 'topic__subject'), 
        id=assessment_id, 
        is_published=True
    )
    student = request.user.student_profile
    
    # Check if already attempted
    existing_attempt = QuizAttempt.objects.filter(
        student=student,
        assessment=assessment,
        status='in_progress'
    ).first()
    
    if existing_attempt:
        attempt = existing_attempt
    else:
        # Create new attempt
        attempt = QuizAttempt.objects.create(
            student=student,
            assessment=assessment,
            status='in_progress'
        )
    
    # Get questions
    questions = Question.objects.filter(assessment=assessment).order_by('order')
    
    context = {
        'assessment': assessment,
        'questions': questions,
        'attempt': attempt,
    }
    return render(request, 'assessments/take_quiz.html', context)


@login_required
def submit_quiz(request, assessment_id):
    """Submit quiz answers"""
    if request.user.role != 'student':
        return redirect('home')
    
    if request.method != 'POST':
        return redirect('assessments:take_quiz', assessment_id=assessment_id)
    
    assessment = get_object_or_404(
        Assessment.objects.select_related('created_by', 'created_by__user'), 
        id=assessment_id
    )
    student = request.user.student_profile
    
    # Get or create attempt
    attempt = QuizAttempt.objects.filter(
        student=student,
        assessment=assessment,
        status='in_progress'
    ).first()
    
    if not attempt:
        messages.error(request, 'No active quiz attempt found.')
        return redirect('home')
    
    # Process answers
    questions = Question.objects.filter(assessment=assessment)
    correct_count = 0
    wrong_count = 0
    total_marks = 0
    
    for question in questions:
        answer = request.POST.get(f'question_{question.id}')
        
        if answer:
            is_correct = answer == question.correct_answer
            marks = question.marks if is_correct else 0
            
            QuestionResponse.objects.create(
                attempt=attempt,
                question=question,
                student_answer=answer,
                is_correct=is_correct,
                marks_awarded=marks
            )
            
            if is_correct:
                correct_count += 1
            else:
                wrong_count += 1
            
            total_marks += marks
    
    # Update attempt
    attempt.status = 'submitted'
    attempt.submitted_at = timezone.now()
    attempt.score = total_marks
    attempt.percentage = (total_marks / assessment.total_marks) * 100 if assessment.total_marks > 0 else 0
    attempt.correct_answers = correct_count
    attempt.wrong_answers = wrong_count
    attempt.save()
    
    # Award XP
    from apps.analytics.models import GamificationProfile
    try:
        gamification = student.gamification
        xp_earned = int(attempt.percentage / 10)  # 1 XP per 10%
        gamification.add_xp(xp_earned, f"Completed {assessment.title}")
        gamification.total_quizzes_completed += 1
        gamification.save()
    except GamificationProfile.DoesNotExist:
        pass
    
    messages.success(request, f'Quiz submitted! You scored {attempt.percentage:.0f}% and earned {xp_earned} XP!')
    return redirect('assessments:quiz_results', attempt_id=attempt.id)


@login_required
def quiz_results(request, attempt_id):
    """View quiz results"""
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related('assessment', 'assessment__created_by', 'assessment__created_by__user', 'assessment__topic'), 
        id=attempt_id
    )
    
    # Check permission
    if request.user.role == 'student' and attempt.student.user != request.user:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get responses
    responses = QuestionResponse.objects.filter(attempt=attempt).select_related('question')
    
    context = {
        'attempt': attempt,
        'responses': responses,
    }
    return render(request, 'assessments/quiz_results.html', context)


# ============================================================================
# ASSIGNMENT MANAGEMENT VIEWS (Teacher-facing)
# ============================================================================

@login_required
def create_assignment(request):
    """Create a new assignment (teachers only)"""
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can create assignments.')
        return redirect('home')
    
    if request.method == 'POST':
        from .forms import AssignmentForm
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user.teacher_profile
            assignment.is_ai_generated = False
            assignment.save()
            
            messages.success(request, f'Assignment "{assignment.title}" created successfully! Now add questions to it.')
            return redirect('assessments:add_question', assignment_id=assignment.id)
    else:
        from .forms import AssignmentForm
        form = AssignmentForm()
    
    context = {
        'form': form,
        'page_title': 'Create Assignment',
    }
    return render(request, 'assessments/create_assignment.html', context)


@login_required
def teacher_assignments(request):
    """List all assignments created by the teacher"""
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can view this page.')
        return redirect('home')
    
    teacher_profile = request.user.teacher_profile
    
    # Get all assignments created by this teacher
    assignments = Assessment.objects.filter(
        created_by=teacher_profile
    ).select_related('topic').order_by('-created_at')
    
    # Filter by type if requested
    filter_type = request.GET.get('type')
    if filter_type:
        assignments = assignments.filter(assessment_type=filter_type)
    
    # Add question count to each assignment
    assignments_with_counts = []
    for assignment in assignments:
        question_count = Question.objects.filter(assessment=assignment).count()
        assignments_with_counts.append({
            'assignment': assignment,
            'question_count': question_count,
        })
    
    context = {
        'assignments_with_counts': assignments_with_counts,
        'filter_type': filter_type,
    }
    return render(request, 'assessments/teacher_assignments.html', context)


@login_required
def edit_assignment(request, assignment_id):
    """Edit an existing assignment"""
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can edit assignments.')
        return redirect('home')
    
    assignment = get_object_or_404(Assessment, id=assignment_id)
    
    # Check permission - only creator can edit
    if assignment.created_by != request.user.teacher_profile:
        messages.error(request, 'You can only edit your own assignments.')
        return redirect('assessments:teacher_assignments')
    
    if request.method == 'POST':
        from .forms import AssignmentForm
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, f'Assignment "{assignment.title}" updated successfully!')
            return redirect('assessments:teacher_assignments')
    else:
        from .forms import AssignmentForm
        form = AssignmentForm(instance=assignment)
    
    context = {
        'form': form,
        'assignment': assignment,
        'page_title': 'Edit Assignment',
    }
    return render(request, 'assessments/edit_assignment.html', context)


@login_required
def delete_assignment(request, assignment_id):
    """Delete an assignment"""
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can delete assignments.')
        return redirect('home')
    
    assignment = get_object_or_404(Assessment, id=assignment_id)
    
    # Check permission - only creator can delete
    if assignment.created_by != request.user.teacher_profile:
        messages.error(request, 'You can only delete your own assignments.')
        return redirect('assessments:teacher_assignments')
    
    if request.method == 'POST':
        title = assignment.title
        assignment.delete()
        messages.success(request, f'Assignment "{title}" deleted successfully!')
        return redirect('assessments:teacher_assignments')
    
    context = {
        'assignment': assignment,
    }
    return render(request, 'assessments/delete_assignment_confirm.html', context)


@login_required
def add_question(request, assignment_id):
    """Add questions to an assignment"""
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can add questions.')
        return redirect('home')
    
    assignment = get_object_or_404(Assessment, id=assignment_id)
    
    # Check permission
    if assignment.created_by != request.user.teacher_profile:
        messages.error(request, 'You can only add questions to your own assignments.')
        return redirect('assessments:teacher_assignments')
    
    if request.method == 'POST':
        from .forms import QuestionForm
        import json
        
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.assessment = assignment
            
            # Set order
            last_question = Question.objects.filter(assessment=assignment).order_by('-order').first()
            question.order = (last_question.order + 1) if last_question else 1
            
            # Parse options if MCQ
            if question.question_type == 'mcq':
                try:
                    # Try to parse as JSON if it's a string
                    if isinstance(question.options, str):
                        question.options = json.loads(question.options)
                except json.JSONDecodeError:
                    messages.error(request, 'Invalid JSON format for options. Please use format: ["Option A", "Option B", "Option C"]')
                    context = {
                        'form': form,
                        'assignment': assignment,
                        'questions': Question.objects.filter(assessment=assignment).order_by('order'),
                    }
                    return render(request, 'assessments/add_question.html', context)
            
            question.save()
            messages.success(request, 'Question added successfully!')
            
            # Check if user wants to add another question
            if 'add_another' in request.POST:
                return redirect('assessments:add_question', assignment_id=assignment_id)
            else:
                return redirect('assessments:teacher_assignments')
    else:
        from .forms import QuestionForm
        form = QuestionForm()
    
    # Get existing questions
    questions = Question.objects.filter(assessment=assignment).order_by('order')
    
    context = {
        'form': form,
        'assignment': assignment,
        'questions': questions,
    }
    return render(request, 'assessments/add_question.html', context)


@login_required
def toggle_publish(request, assignment_id):
    """Toggle assignment publish status"""
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can publish assignments.')
        return redirect('home')
    
    assignment = get_object_or_404(Assessment, id=assignment_id)
    
    # Check permission
    if assignment.created_by != request.user.teacher_profile:
        messages.error(request, 'You can only publish your own assignments.')
        return redirect('assessments:teacher_assignments')
    
    assignment.is_published = not assignment.is_published
    assignment.save()
    
    status = "published" if assignment.is_published else "unpublished"
    messages.success(request, f'Assignment "{assignment.title}" {status} successfully!')
    
    return redirect('assessments:teacher_assignments')

@login_required
def diagnostic_assessment(request):
    """
    Unified Diagnostic Assessment View.
    Presents questions from all diagnostic assessments in a single form.
    """
    student = request.user.student_profile
    if student.has_taken_diagnostic:
        messages.info(request, "You have already completed the diagnostic assessment.")
        return redirect('accounts:dashboard') # Or wherever

    # Fetch all diagnostic assessments
    assessments = Assessment.objects.filter(
        assessment_type='diagnostic', is_published=True
    ).select_related('topic', 'topic__subject').prefetch_related('questions')

    if request.method == 'POST':
        attempts = []
        
        for assessment in assessments:
            # Create attempt
            attempt = QuizAttempt.objects.create(
                student=student,
                assessment=assessment,
                status='submitted',
                submitted_at=timezone.now()
            )
            
            questions = assessment.questions.all()
            correct_count = 0
            wrong_count = 0
            total_marks = 0
            
            for question in questions:
                answer = request.POST.get(f'question_{question.id}')
                if answer:
                    is_correct = answer == question.correct_answer
                    marks = question.marks if is_correct else 0
                    
                    QuestionResponse.objects.create(
                        attempt=attempt,
                        question=question,
                        student_answer=answer,
                        is_correct=is_correct,
                        marks_awarded=marks
                    )
                    
                    if is_correct:
                        correct_count += 1
                    else:
                        wrong_count += 1
                    total_marks += marks
            
            # Update attempt stats
            attempt.score = total_marks
            attempt.percentage = (total_marks / assessment.total_marks) * 100 if assessment.total_marks > 0 else 0
            attempt.correct_answers = correct_count
            attempt.wrong_answers = wrong_count
            attempt.save()
            
            # Analyze individual attempt (create StudentPerformance)
            from .services import DiagnosticService
            DiagnosticService.calculate_scores(student, attempt)
            attempts.append(attempt)
        
        # Finalize and Generate Path
        DiagnosticService.finalize_diagnostic(student, attempts)
        
        # Mark profile
        student.has_taken_diagnostic = True
        student.save()
        
        messages.success(request, "Diagnostic completed! Your personalized learning path is ready.")
        return redirect('assessments:diagnostic_results')

    questions_list = []
    for assessment in assessments:
        for q in assessment.questions.all():
            questions_list.append({
                'obj': q,
                'assessment': assessment
            })

    context = {
        'assessments': assessments,
        'questions_list': questions_list
    }
    return render(request, 'assessments/diagnostic_test.html', context)


@login_required
def diagnostic_results(request):
    """
    Shows the results of the diagnostic and the generated path.
    """
    student = request.user.student_profile
    if not student.has_taken_diagnostic:
        return redirect('assessments:diagnostic_assessment')

    # Get the generated path
    learning_path = LearningPath.objects.filter(
        student=student, is_ai_generated=True
    ).order_by('-created_at').first()
    
    # Get strength/weakness summary from Performance records
    performances = StudentPerformance.objects.filter(
        student=student, assessment_type='diagnostic'
    ).select_related('topic', 'topic__subject')
    
    weak_topics = performances.filter(percentage__lt=60)
    strong_topics = performances.filter(percentage__gte=80)
    
    classification = "Learner"
    if learning_path:
        # We stored level in generation_criteria
        classification = learning_path.generation_criteria.get('level', 'Learner')

    context = {
        'student': student,
        'learning_path': learning_path,
        'weak_topics': weak_topics,
        'strong_topics': strong_topics,
        'classification': classification
    }
    return render(request, 'assessments/diagnostic_results.html', context)
