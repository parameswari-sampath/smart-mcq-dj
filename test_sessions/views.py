from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.utils import timezone
from datetime import timezone as dt_timezone
from .models import TestSession
from tests.models import Test


def teacher_required(view_func):
    """Decorator to ensure only teachers can access certain views"""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.groups.filter(name='Teachers').exists():
            messages.error(request, 'Access denied. Teachers only.')
            return redirect('accounts:teacher_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@teacher_required
def session_list(request):
    """Display list of test sessions created by the teacher"""
    sessions = TestSession.objects.filter(created_by=request.user).order_by('-start_time')
    return render(request, 'test_sessions/session_list.html', {'sessions': sessions})


@teacher_required
def session_create(request):
    """Create a new test session"""
    if request.method == 'POST':
        test_id = request.POST.get('test')
        start_time = request.POST.get('start_time')
        
        if not test_id or not start_time:
            messages.error(request, 'Please select a test and start time.')
            return redirect('test_sessions:session_create')
        
        try:
            test = Test.objects.get(id=test_id, created_by=request.user)
            
            # Convert start_time to timezone-aware datetime
            # The datetime-local input gives us time in user's local timezone
            start_datetime = timezone.datetime.fromisoformat(start_time.replace('T', ' '))
            # Make it timezone-aware in the current timezone, then convert to UTC
            if timezone.is_naive(start_datetime):
                start_datetime = timezone.make_aware(start_datetime, timezone.get_current_timezone())
            # Convert to UTC for storage
            start_datetime = start_datetime.astimezone(dt_timezone.utc)
            
            # Validate that start time is not in the past
            if start_datetime <= timezone.now():
                messages.error(request, 'Start time must be in the future. Please select a future date and time.')
                return redirect('test_sessions:session_create')
            
            session = TestSession.objects.create(
                test=test,
                session_name=request.POST.get('session_name', '').strip(),
                start_time=start_datetime,
                created_by=request.user
            )
            
            messages.success(request, f'Test session created successfully! Access code: {session.access_code}')
            return redirect('test_sessions:session_detail', pk=session.pk)
            
        except Test.DoesNotExist:
            messages.error(request, 'Invalid test selected.')
        except ValueError:
            messages.error(request, 'Invalid date/time format.')
    
    # Get teacher's tests for selection
    tests = Test.objects.filter(created_by=request.user, is_active=True)
    return render(request, 'test_sessions/session_form.html', {
        'tests': tests,
        'action': 'Create'
    })


@teacher_required
def session_detail(request, pk):
    """Display test session details"""
    session = get_object_or_404(TestSession, pk=pk, created_by=request.user)
    return render(request, 'test_sessions/session_detail.html', {'session': session})


@teacher_required
def session_edit(request, pk):
    """Edit an existing test session"""
    session = get_object_or_404(TestSession, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        
        if not start_time:
            messages.error(request, 'Please provide a start time.')
            return redirect('test_sessions:session_edit', pk=pk)
        
        try:
            # Convert start_time to timezone-aware datetime
            # The datetime-local input gives us time in user's local timezone
            start_datetime = timezone.datetime.fromisoformat(start_time.replace('T', ' '))
            # Make it timezone-aware in the current timezone, then convert to UTC
            if timezone.is_naive(start_datetime):
                start_datetime = timezone.make_aware(start_datetime, timezone.get_current_timezone())
            # Convert to UTC for storage
            start_datetime = start_datetime.astimezone(dt_timezone.utc)
            
            # Validate that start time is not in the past
            if start_datetime <= timezone.now():
                messages.error(request, 'Start time must be in the future. Please select a future date and time.')
                return redirect('test_sessions:session_edit', pk=pk)
            
            session.session_name = request.POST.get('session_name', '').strip()
            session.start_time = start_datetime
            session.save()
            
            messages.success(request, 'Test session updated successfully!')
            return redirect('test_sessions:session_detail', pk=session.pk)
            
        except ValueError:
            messages.error(request, 'Invalid date/time format.')
    
    return render(request, 'test_sessions/session_form.html', {
        'session': session,
        'action': 'Edit'
    })


@teacher_required
def session_delete(request, pk):
    """Delete a test session (soft delete by setting is_active=False)"""
    session = get_object_or_404(TestSession, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        session.is_active = False
        session.save()
        messages.success(request, 'Test session deleted successfully!')
        return redirect('test_sessions:session_list')
    
    return render(request, 'test_sessions/session_confirm_delete.html', {'session': session})
