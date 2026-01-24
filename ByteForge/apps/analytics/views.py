from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
import json

from apps.accounts.models import StudentProfile, User
from .models import ReportCard
from .forms import ReportCardForm


@login_required
def issue_report_card(request, student_id):
    """View for teachers to issue a new report card to a student"""
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can issue report cards.')
        return redirect('home')
    
    student = get_object_or_404(StudentProfile, id=student_id)
    
    if request.method == 'POST':
        form = ReportCardForm(request.POST)
        if form.is_valid():
            report_card = form.save(commit=False)
            report_card.student = student
            report_card.teacher = request.user.teacher_profile
            
            # Process grades JSON from hidden field
            grades_json = form.cleaned_data.get('grades_json', '{}')
            try:
                report_card.grades_data = json.loads(grades_json)
            except json.JSONDecodeError:
                report_card.grades_data = {}
            
            report_card.save()
            messages.success(request, f'Report card issued successfully for {student.user.get_full_name()}.')
            return redirect('accounts:teacher_dashboard')
    else:
        form = ReportCardForm()
    
    context = {
        'form': form,
        'student': student,
        'page_title': f'Issue Report Card - {student.user.get_full_name()}',
    }
    return render(request, 'analytics/report_card_form.html', context)


@login_required
def report_card_detail(request, report_id):
    """View details of a specific report card"""
    report = get_object_or_404(ReportCard, id=report_id)
    
    # Permission check
    if request.user.role == 'student' and report.student.user != request.user:
        messages.error(request, 'Access denied.')
        return redirect('home')
    elif request.user.role == 'parent' and report.student.parent != request.user:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Hide unpublished reports from students/parents
    if not report.is_published and request.user.role in ['student', 'parent']:
        messages.error(request, 'This report card is not yet available.')
        return redirect('home')
    
    context = {
        'report': report,
        'grades': report.grades_data,
    }
    return render(request, 'analytics/report_card_detail.html', context)


@login_required
def my_reports(request):
    """View list of student's own report cards"""
    if request.user.role != 'student':
        messages.error(request, 'This view is only for students.')
        return redirect('home')
    
    reports = ReportCard.objects.filter(
        student__user=request.user,
        is_published=True
    ).order_by('-issued_date')
    
    context = {
        'reports': reports,
        'page_title': 'My Report Cards',
    }
    return render(request, 'analytics/report_card_list.html', context)
