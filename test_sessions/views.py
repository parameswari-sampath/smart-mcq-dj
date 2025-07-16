from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.utils import timezone
from datetime import timezone as dt_timezone
from django.core.paginator import Paginator
from .models import TestSession
from tests.models import Test
import pytz


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
    """Display list of test sessions created by the teacher with pagination"""
    sessions = TestSession.objects.filter(created_by=request.user).order_by('-start_time')
    
    # Pagination
    paginator = Paginator(sessions, 10)  # Show 10 sessions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'test_sessions/session_list.html', {
        'sessions': page_obj,
        'page_obj': page_obj
    })


@teacher_required
def session_create(request):
    """Create a new test session"""
    if request.method == 'POST':
        test_id = request.POST.get('test')
        start_time = request.POST.get('start_time')
        user_timezone = request.POST.get('user_timezone', 'UTC')
        
        if not test_id or not start_time:
            messages.error(request, 'Please select a test and start time.')
            return redirect('test_sessions:session_create')
        
        try:
            test = Test.objects.get(id=test_id, created_by=request.user)
            
            # INDUSTRY STANDARD: Proper timezone conversion (Google Calendar/Zoom pattern)
            # Step 1: Parse naive datetime from user input
            start_datetime_naive = timezone.datetime.fromisoformat(start_time.replace('T', ' '))
            
            # Step 2: Get user's timezone 
            try:
                user_tz = pytz.timezone(user_timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                # Fallback to UTC if invalid timezone
                user_tz = pytz.UTC
                messages.warning(request, f'Unknown timezone {user_timezone}, using UTC.')
            
            # Step 3: Localize to user's timezone (this is the key fix!)
            start_datetime_local = user_tz.localize(start_datetime_naive)
            
            # Step 4: Convert to UTC for database storage
            start_datetime_utc = start_datetime_local.astimezone(pytz.UTC)
            
            # Validate that start time is not in the past (compare in UTC)
            if start_datetime_utc <= timezone.now():
                messages.error(request, f'Start time must be in the future. Please select a future date and time in your timezone ({user_timezone}).')
                return redirect('test_sessions:session_create')
            
            # INDUSTRY STANDARD: Prevent duplicate sessions (double-click protection)
            # Check for existing session with same test, teacher, and start time (within 1 minute)
            time_tolerance = timezone.timedelta(minutes=1)
            existing_session = TestSession.objects.filter(
                test=test,
                created_by=request.user,
                start_time__range=(
                    start_datetime_utc - time_tolerance,
                    start_datetime_utc + time_tolerance
                ),
                is_active=True
            ).first()
            
            if existing_session:
                messages.warning(request, 
                    f'A similar session already exists for this test at {start_local_str}. '
                    f'Access code: {existing_session.access_code}')
                return redirect('test_sessions:session_detail', pk=existing_session.pk)
            
            session = TestSession.objects.create(
                test=test,
                session_name=request.POST.get('session_name', '').strip(),
                start_time=start_datetime_utc,  # Store UTC time
                created_by=request.user
            )
            
            # Success message with timezone info
            start_local_str = start_datetime_local.strftime('%b %d, %Y %I:%M %p %Z')
            start_utc_str = start_datetime_utc.strftime('%b %d, %Y %I:%M %p UTC')
            messages.success(request, 
                f'Test session created successfully! Access code: {session.access_code}<br>'
                f'Local time: {start_local_str}<br>'
                f'UTC time: {start_utc_str}')
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
        user_timezone = request.POST.get('user_timezone', 'UTC')
        
        if not start_time:
            messages.error(request, 'Please provide a start time.')
            return redirect('test_sessions:session_edit', pk=pk)
        
        try:
            # INDUSTRY STANDARD: Proper timezone conversion (same as create)
            # Step 1: Parse naive datetime from user input
            start_datetime_naive = timezone.datetime.fromisoformat(start_time.replace('T', ' '))
            
            # Step 2: Get user's timezone 
            try:
                user_tz = pytz.timezone(user_timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                user_tz = pytz.UTC
                messages.warning(request, f'Unknown timezone {user_timezone}, using UTC.')
            
            # Step 3: Localize to user's timezone
            start_datetime_local = user_tz.localize(start_datetime_naive)
            
            # Step 4: Convert to UTC for database storage
            start_datetime_utc = start_datetime_local.astimezone(pytz.UTC)
            
            # Validate that start time is not in the past
            if start_datetime_utc <= timezone.now():
                messages.error(request, f'Start time must be in the future. Please select a future date and time in your timezone ({user_timezone}).')
                return redirect('test_sessions:session_edit', pk=pk)
            
            session.session_name = request.POST.get('session_name', '').strip()
            session.start_time = start_datetime_utc
            session.save()
            
            # Success message with timezone info
            start_local_str = start_datetime_local.strftime('%b %d, %Y %I:%M %p %Z')
            start_utc_str = start_datetime_utc.strftime('%b %d, %Y %I:%M %p UTC')
            messages.success(request, 
                f'Test session updated successfully!<br>'
                f'Local time: {start_local_str}<br>'
                f'UTC time: {start_utc_str}')
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
