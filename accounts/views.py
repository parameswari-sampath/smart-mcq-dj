from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db import models
from .models import Profile
from test_sessions.models import TestSession, StudentTestAttempt, TestAttempt, Answer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from smart_mcq.constants import UserRoles
import json
import logging
import os
from datetime import datetime

# Configure auto-submit logger
auto_submit_logger = logging.getLogger('auto_submit')
auto_submit_logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
logs_dir = 'logs'
if not os.path.exists(logs_dir):
    try:
        os.makedirs(logs_dir, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create logs directory: {e}")
        # Fall back to current directory
        logs_dir = '.'

# Create file handler for auto-submit logs
log_file = os.path.join(logs_dir, f'auto_submit_{datetime.now().strftime("%Y_%m_%d")}.log')
try:
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
except Exception as e:
    print(f"Warning: Could not create log file handler: {e}")
    # Use console handler only
    file_handler = None

# Create console handler for immediate feedback
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add handlers to logger
if file_handler:
    file_handler.setFormatter(formatter)
    auto_submit_logger.addHandler(file_handler)

console_handler.setFormatter(formatter)
auto_submit_logger.addHandler(console_handler)


class CustomLoginView(LoginView):
    """Custom login view that redirects authenticated users"""
    template_name = 'accounts/login.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


def register_view(request):
    """User registration with role selection"""
    # Redirect if user is already logged in
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']
        
        # Basic validation
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'accounts/register.html')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Create profile
        profile = Profile.objects.create(
            user=user,
            role=role,
            is_active=True
        )
        
        # Add user to appropriate group (auto-create if missing)
        group_name = UserRoles.GROUP_STUDENTS if role == UserRoles.STUDENT else UserRoles.GROUP_TEACHERS
        group, created = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
        
        messages.success(request, f'Account created successfully as {role}')
        
        # Auto login
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
    
    return render(request, 'accounts/register.html')


def dashboard_view(request):
    """Dashboard based on user role"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        profile = request.user.profile
        context = {
            'user': request.user,
            'profile': profile,
        }
        
        if profile.role == 'teacher':
            # For teachers, get their test sessions for result viewing (v1.4)
            teacher_sessions = TestSession.objects.filter(
                created_by=request.user,
                is_active=True
            ).select_related('test').prefetch_related(
                'studenttestattempt_set__attempt_detail'
            ).order_by('-created_at')
            
            # Add result statistics to each session
            for session in teacher_sessions:
                completed_attempts = TestAttempt.objects.filter(
                    student_test_attempt__test_session=session,
                    is_submitted=True
                )
                session.total_attempts = completed_attempts.count()
                session.has_results = session.total_attempts > 0
                
                if session.has_results:
                    scores = []
                    for attempt in completed_attempts:
                        total_questions = attempt.total_questions
                        correct_answers = attempt.answers.filter(is_correct=True).count()
                        score_percentage = round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
                        scores.append(score_percentage)
                    
                    session.average_score = round(sum(scores) / len(scores)) if scores else 0
            
            # Pagination for teacher sessions on dashboard
            from django.core.paginator import Paginator
            paginator = Paginator(teacher_sessions, 8)  # Show 8 sessions per page on dashboard
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context['teacher_sessions'] = page_obj
            context['page_obj'] = page_obj
            return render(request, 'accounts/teacher_dashboard.html', context)
        else:
            # For students, get ONLY test sessions they have joined via access code
            # SECURITY: Students should never see all sessions - only joined ones
            current_time = timezone.now()
            
            # Get student's test attempts (only sessions they've joined)
            student_attempts = StudentTestAttempt.objects.filter(student=request.user).select_related('test_session')
            joined_session_ids = set(attempt.test_session.id for attempt in student_attempts)
            
            # Get only the sessions the student has joined
            all_sessions = TestSession.objects.filter(
                id__in=joined_session_ids,
                is_active=True
            ).select_related('test', 'created_by')
            
            # Get student's completed test attempts for result viewing (v1.3.1)
            completed_attempts = TestAttempt.objects.filter(
                student_test_attempt__student=request.user,
                is_submitted=True
            ).select_related(
                'student_test_attempt__test_session__test',
                'student_test_attempt__test_session__created_by'
            ).order_by('-submitted_at')
            
            # Categorize sessions by status
            upcoming_sessions = []
            ongoing_sessions = []
            completed_sessions = []
            
            for session in all_sessions:
                # Add joined status to session object
                session.has_joined = session.id in joined_session_ids
                
                if session.status == 'upcoming':
                    upcoming_sessions.append(session)
                elif session.status == 'active':
                    ongoing_sessions.append(session)
                # expired sessions are not shown in student dashboard
            
            # Add completed attempts as completed sessions with result data
            for attempt in completed_attempts:
                session = attempt.student_test_attempt.test_session
                # Calculate basic results for dashboard display
                total_questions = attempt.total_questions
                correct_answers = attempt.answers.filter(is_correct=True).count()
                score_percentage = round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
                
                # Add result data to session object for template
                session.attempt_id = attempt.id
                session.score_percentage = score_percentage
                session.correct_answers = correct_answers
                session.total_questions = total_questions
                session.submitted_at = attempt.submitted_at
                
                completed_sessions.append(session)
            
            # Pagination for completed sessions on student dashboard
            from django.core.paginator import Paginator
            paginator = Paginator(completed_sessions, 10)  # Show 10 completed tests per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context.update({
                'upcoming_sessions': upcoming_sessions,
                'ongoing_sessions': ongoing_sessions,
                'completed_sessions': page_obj,
                'completed_page_obj': page_obj,
            })
            
            return render(request, 'accounts/student_dashboard.html', context)
            
    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found. Please contact administrator.')
        return redirect('login')


@login_required
def join_test_session(request):
    """Handle student joining a test session via access code"""
    if request.method == 'POST':
        access_code = request.POST.get('access_code', '').strip().upper()
        
        if not access_code:
            messages.error(request, 'Please enter an access code.')
            return redirect('dashboard')
        
        # Validate access code format (6-character alphanumeric)
        if len(access_code) != 6 or not access_code.isalnum():
            messages.error(request, 'Access code must be 6 alphanumeric characters.')
            return redirect('dashboard')
        
        try:
            # Find the test session
            session = TestSession.objects.get(access_code=access_code, is_active=True)
            
            # Check if student has already joined this test session
            existing_attempt = StudentTestAttempt.objects.filter(
                student=request.user,
                test_session=session
            ).first()
            
            if existing_attempt:
                messages.warning(request, f'You have already joined this test: {session.test.title}. Each test can only be joined once.')
                return redirect('dashboard')
            
            # Check session status
            if session.status == 'upcoming':
                start_time_local = timezone.localtime(session.start_time)
                messages.warning(request, f'Test has not started yet. Please join at {start_time_local.strftime("%b %d, %Y %I:%M %p")}.')
                return redirect('dashboard')
            elif session.status == 'expired':
                messages.error(request, 'This test session has expired and is no longer available.')
                return redirect('dashboard')
            elif session.status == 'active':
                # Create student test attempt record
                student_attempt = StudentTestAttempt.objects.create(
                    student=request.user,
                    test_session=session
                )
                # Create test attempt detail record
                test_attempt = TestAttempt.objects.create(
                    student_test_attempt=student_attempt
                )
                # Redirect to test taking interface
                return redirect('take_test', attempt_id=test_attempt.id)
            else:
                messages.error(request, 'This test session is not available.')
                return redirect('dashboard')
                
        except TestSession.DoesNotExist:
            messages.error(request, 'Invalid access code. Please check and try again.')
            return redirect('dashboard')
    
    # If not POST, redirect to dashboard
    return redirect('dashboard')


@login_required
def view_test_details(request, session_id):
    """Display test session details for students - ONLY if they have joined via access code"""
    try:
        # SECURITY: Students can only view details of sessions they have joined
        session = TestSession.objects.select_related('test', 'created_by').get(
            id=session_id, 
            is_active=True
        )
        
        # Check if student has joined this test (REQUIRED for access)
        has_joined = StudentTestAttempt.objects.filter(
            student=request.user,
            test_session=session
        ).exists()
        
        # SECURITY CHECK: Deny access if student hasn't joined via access code
        if not has_joined:
            messages.error(request, 'Access denied. You must join this test using an access code first.')
            return redirect('dashboard')
        
        context = {
            'session': session,
            'user': request.user,
            'profile': request.user.profile,
            'has_joined': has_joined,
        }
        
        return render(request, 'accounts/test_details.html', context)
        
    except TestSession.DoesNotExist:
        messages.error(request, 'Test session not found.')
        return redirect('dashboard')


@login_required
def take_test(request, attempt_id):
    """Test taking interface with question navigation"""
    try:
        test_attempt = TestAttempt.objects.select_related(
            'student_test_attempt__test_session__test',
            'student_test_attempt__student'
        ).get(id=attempt_id)
        
        # Security check: only the student who owns this attempt can access it
        if test_attempt.student != request.user:
            messages.error(request, 'Access denied. This test attempt does not belong to you.')
            return redirect('dashboard')
        
        # v1.5.2: Server-authoritative time validation
        # Calculate actual test end time using UTC timestamps
        session = test_attempt.test_session
        test_start_time_utc = session.start_time  # Already stored in UTC
        test_duration = timezone.timedelta(minutes=session.test.time_limit_minutes)
        actual_end_time_utc = test_start_time_utc + test_duration
        current_server_time_utc = timezone.now()  # Always UTC
        
        # Server-side validation: If time has expired, auto-submit immediately
        if current_server_time_utc >= actual_end_time_utc and not test_attempt.is_submitted:
            try:
                # Call auto_submit_test function directly with server validation
                auto_result = auto_submit_test(request, test_attempt)
                if hasattr(auto_result, 'get') and auto_result.get('success'):
                    # Auto-submit succeeded, redirect to results
                    messages.info(request, 'Test time expired and was automatically submitted.')
                    return redirect('test_results')
            except Exception as e:
                # Auto-submit failed, continue to show test page
                messages.warning(request, f'Test time has expired. Please submit manually. ({str(e)})')
        
        # Check if test session is still active
        if test_attempt.test_session.status != 'active':
            messages.error(request, 'This test session is no longer active.')
            return redirect('dashboard')
        
        # Check if already submitted
        if test_attempt.is_submitted:
            messages.info(request, 'You have already submitted this test.')
            return redirect('dashboard')
        
        # Get current question
        current_question = test_attempt.current_question
        if not current_question:
            messages.error(request, 'No questions found for this test.')
            return redirect('dashboard')
        
        # Get existing answer for current question
        existing_answer = test_attempt.answers.filter(question=current_question).first()
        
        # Get answered questions count for submission modal
        answered_questions_count = test_attempt.answers.count()
        
        # v1.5.2: UTC-based time data for global compatibility
        context = {
            'test_attempt': test_attempt,
            'current_question': current_question,
            'existing_answer': existing_answer,
            'question_number': test_attempt.current_question_index + 1,
            'total_questions': test_attempt.total_questions,
            'answered_questions_count': answered_questions_count,
            'progress_percentage': test_attempt.progress_percentage,
            'test_session': test_attempt.test_session,
            'test_end_time_utc': actual_end_time_utc,  # Calculated UTC end time
            'server_time_utc': current_server_time_utc,  # Current server UTC time
            'remaining_seconds': max(0, int((actual_end_time_utc - current_server_time_utc).total_seconds())),
            'grace_period_seconds': 30,  # Industry standard grace period
        }
        
        return render(request, 'accounts/take_test.html', context)
        
    except TestAttempt.DoesNotExist:
        messages.error(request, 'Test attempt not found.')
        return redirect('dashboard')


@login_required
def navigate_question(request, attempt_id):
    """Handle question navigation (next/previous)"""
    if request.method != 'POST':
        return redirect('take_test', attempt_id=attempt_id)
    
    try:
        test_attempt = TestAttempt.objects.get(id=attempt_id)
        
        # Security check
        if test_attempt.student != request.user:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
        
        direction = request.POST.get('direction')
        
        if direction == 'next' and not test_attempt.is_last_question:
            test_attempt.current_question_index += 1
            test_attempt.save()
        elif direction == 'previous' and not test_attempt.is_first_question:
            test_attempt.current_question_index -= 1
            test_attempt.save()
        
        return redirect('take_test', attempt_id=attempt_id)
        
    except TestAttempt.DoesNotExist:
        messages.error(request, 'Test attempt not found.')
        return redirect('dashboard')


@login_required
@csrf_exempt
def save_answer(request, attempt_id):
    """AJAX endpoint to save answers and get answer count"""
    try:
        test_attempt = TestAttempt.objects.get(id=attempt_id)
        
        # Security check
        if test_attempt.student != request.user:
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        # Check if test is still active - allow saving for expired sessions since answers are continuously saved
        session_status = test_attempt.test_session.status
        
        if session_status not in ['active', 'expired']:
            return JsonResponse({'success': False, 'error': 'Test session is no longer active'})
        
        # Handle GET request - return current answered count
        if request.method == 'GET':
            answered_count = test_attempt.answers.count()
            return JsonResponse({
                'success': True,
                'answered_count': answered_count
            })
        
        # Handle POST request - save answer or log entry
        elif request.method == 'POST':
            try:
                data = json.loads(request.body)
                
                # Check if this is a log entry from frontend
                if 'log_entry' in data and data.get('log_type') == 'auto_submit_debug':
                    log_entry = data['log_entry']
                    log_level = log_entry.get('level', 'INFO')
                    log_message = log_entry.get('message', '')
                    log_data = log_entry.get('data', {})
                    
                    # Enhanced logging with comprehensive context
                    log_context = {
                        'user_id': request.user.id,
                        'username': request.user.username,
                        'attempt_id': attempt_id,
                        'session_id': log_entry.get('session'),
                        'timestamp': log_entry.get('timestamp'),
                        'attempt_id_frontend': log_entry.get('attempt_id'),
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'remote_addr': request.META.get('REMOTE_ADDR', ''),
                        'frontend_data': log_data,
                        'url': request.get_full_path(),
                        'method': request.method
                    }
                    
                    # Log to our dedicated auto-submit logger
                    logger_method = getattr(auto_submit_logger, log_level.lower(), auto_submit_logger.info)
                    logger_method(f"FRONTEND_LOG: {log_message} | Context: {json.dumps(log_context, indent=2)}")
                    
                    # Also log critical events to console for immediate visibility
                    if log_level in ['ERROR', 'WARN'] or 'auto-submit' in log_message.lower():
                        print(f"[AUTO-SUBMIT-{log_level}] {log_message} | User: {request.user.username} | Attempt: {attempt_id}")
                    
                    return JsonResponse({'success': True, 'logged': True, 'log_level': log_level})
                
                # Handle normal answer saving
                question_id = data.get('question_id')
                selected_choice = data.get('selected_choice')
                time_spent_seconds = data.get('time_spent_seconds', 0)
                
                auto_submit_logger.debug(f"Answer save request: question_id={question_id}, choice={selected_choice}, time={time_spent_seconds}, user={request.user.username}")
                print(f"DEBUG: Save answer request - question_id: {question_id}, choice: {selected_choice}, time: {time_spent_seconds}")
                
                # Validate inputs
                if not question_id or not selected_choice:
                    return JsonResponse({'success': False, 'error': 'Missing required data'})
                
                if selected_choice not in ['A', 'B', 'C', 'D']:
                    return JsonResponse({'success': False, 'error': 'Invalid choice'})
                
                # Validate time spent (should be reasonable)
                if time_spent_seconds < 0 or time_spent_seconds > 3600:  # Max 1 hour per question
                    time_spent_seconds = 0
                
                # Get the question
                question = test_attempt.test.questions.get(id=question_id)
                auto_submit_logger.debug(f"Question found: {question.title}")
                print(f"DEBUG: Found question: {question.title}")
                
                # Create or update answer
                answer, created = Answer.objects.get_or_create(
                    test_attempt=test_attempt,
                    question=question,
                    defaults={
                        'selected_choice': selected_choice,
                        'time_spent_seconds': time_spent_seconds
                    }
                )
                
                if not created:
                    answer.selected_choice = selected_choice
                    answer.time_spent_seconds = time_spent_seconds
                    answer.save()
                
                auto_submit_logger.debug(f"Answer saved: created={created}, choice={answer.selected_choice}, user={request.user.username}")
                print(f"DEBUG: Answer saved - created: {created}, choice: {answer.selected_choice}")
                
                # Refresh test attempt to get updated progress
                test_attempt.refresh_from_db()
                
                return JsonResponse({
                    'success': True,
                    'is_correct': answer.is_correct,
                    'progress_percentage': test_attempt.progress_percentage,
                    'answered_count': test_attempt.answers.count()
                })
                
            except Exception as e:
                auto_submit_logger.error(f"Error in save_answer POST: {str(e)}, user={request.user.username}, attempt={attempt_id}")
                print(f"DEBUG: Error in save_answer POST: {str(e)}")
                return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'})
        
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request method'})
        
    except TestAttempt.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Test attempt not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def submit_test(request, attempt_id):
    """Submit test attempt with instant evaluation"""
    if request.method != 'POST':
        return redirect('take_test', attempt_id=attempt_id)
    
    try:
        import json
        from smart_mcq.constants import SuccessMessages
        from django.utils import timezone
        from django.http import JsonResponse
        from django.urls import reverse
        
        # Check if this is a JSON request (auto-submission)
        is_json_request = request.content_type == 'application/json'
        
        test_attempt = TestAttempt.objects.get(id=attempt_id)
        
        # Security check
        if test_attempt.student != request.user:
            error_msg = 'Access denied.'
            if is_json_request:
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('dashboard')
        
        # Check if already submitted
        if test_attempt.is_submitted:
            info_msg = 'Test has already been submitted.'
            if is_json_request:
                return JsonResponse({'success': False, 'error': info_msg})
            messages.info(request, info_msg)
            return redirect('dashboard')
        
        # Check if this is auto-submission - if so, use dedicated function
        if is_json_request:
            try:
                data = json.loads(request.body)
                if data.get('auto_submit'):
                    auto_submit_logger.info(f"SUBMIT_TEST_ROUTING_TO_AUTO: user={request.user.username}, attempt={attempt_id}")
                    return auto_submit_test(request, test_attempt)
            except Exception as e:
                auto_submit_logger.error(f"SUBMIT_TEST_JSON_ERROR: {str(e)}, user={request.user.username}, attempt={attempt_id}")
                pass
        
        # For manual submissions, check if test session is still active
        session_status = test_attempt.test_session.status
        
        if session_status != 'active':
            error_msg = 'Test session is no longer active.'
            if is_json_request:
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('dashboard')
        
        # Calculate total time spent
        total_time_spent = int((timezone.now() - test_attempt.started_at).total_seconds())
        question_time_spent = test_attempt.answers.aggregate(total=models.Sum('time_spent_seconds'))['total'] or 0
        
        # Mark as submitted with time tracking
        test_attempt.is_submitted = True
        test_attempt.submitted_at = timezone.now()
        test_attempt.total_time_spent = total_time_spent
        test_attempt.save()
        
        # Calculate score (simple scoring: correct = 1, incorrect/blank = 0)
        total_questions = test_attempt.total_questions
        correct_answers = test_attempt.answers.filter(is_correct=True).count()
        score_percentage = round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        
        # Format time for display
        def format_time(seconds):
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            if hours > 0:
                return f"{hours}h {minutes}m {secs}s"
            elif minutes > 0:
                return f"{minutes}m {secs}s"
            else:
                return f"{secs}s"
        
        # Calculate average time per question
        avg_time_per_question = int(total_time_spent / total_questions) if total_questions > 0 else 0
        
        # Store comprehensive results in session for results page
        incorrect_answers = total_questions - correct_answers
        request.session['test_results'] = {
            'attempt_id': test_attempt.id,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'score_percentage': score_percentage,
            'test_title': test_attempt.test.title,
            'total_time_spent': total_time_spent,
            'total_time_formatted': format_time(total_time_spent),
            'question_time_spent': question_time_spent,
            'question_time_formatted': format_time(question_time_spent),
            'avg_time_per_question': avg_time_per_question,
            'avg_time_per_question_formatted': format_time(avg_time_per_question),
            'submitted_at': timezone.localtime(timezone.now()).strftime('%B %d, %Y at %I:%M %p'),
        }
        
        # Handle response based on request type
        if is_json_request:
            return JsonResponse({
                'success': True,
                'message': SuccessMessages.TEST_SUBMITTED,
                'redirect_url': reverse('test_results')
            })
        else:
            messages.success(request, SuccessMessages.TEST_SUBMITTED)
            return redirect('test_results')
        
    except TestAttempt.DoesNotExist:
        error_msg = 'Test attempt not found.'
        auto_submit_logger.error(f"SUBMIT_TEST_NOT_FOUND: attempt={attempt_id}, user={request.user.username}")
        if request.content_type == 'application/json':
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
        return redirect('dashboard')
    except Exception as e:
        error_msg = f'Error submitting test: {str(e)}'
        auto_submit_logger.error(f"SUBMIT_TEST_ERROR: {str(e)}, attempt={attempt_id}, user={request.user.username}")
        if request.content_type == 'application/json':
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
        return redirect('take_test', attempt_id=attempt_id)


def auto_submit_test(request, test_attempt):
    """
    Industry-proven server-authoritative auto-submission (v1.5.2)
    Follows Google Forms/Coursera pattern: Server validates ALL timing decisions
    """
    from smart_mcq.constants import SuccessMessages
    from django.utils import timezone
    from django.http import JsonResponse
    from django.urls import reverse
    import logging
    import json
    
    logger = logging.getLogger(__name__)
    
    # COMPREHENSIVE AUTO-SUBMIT LOGGING
    auto_submit_logger.info(f"AUTO_SUBMIT_SERVER_START: user={request.user.username}, attempt={test_attempt.id}")
    
    # Parse request data for logging
    try:
        request_data = json.loads(request.body) if request.body else {}
        auto_submit_logger.info(f"AUTO_SUBMIT_REQUEST_DATA: {json.dumps(request_data, indent=2)}")
    except json.JSONDecodeError as e:
        auto_submit_logger.error(f"AUTO_SUBMIT_JSON_ERROR: {str(e)}")
        request_data = {}
    
    # Log server environment context
    server_context = {
        'server_time_utc': timezone.now().isoformat(),
        'user_id': request.user.id,
        'username': request.user.username,
        'attempt_id': test_attempt.id,
        'test_id': test_attempt.test.id,
        'test_title': test_attempt.test.title,
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'remote_addr': request.META.get('REMOTE_ADDR', ''),
        'http_x_forwarded_for': request.META.get('HTTP_X_FORWARDED_FOR', ''),
        'content_type': request.content_type,
        'session_key': request.session.session_key,
        'request_data': request_data
    }
    auto_submit_logger.info(f"AUTO_SUBMIT_SERVER_CONTEXT: {json.dumps(server_context, indent=2)}")
    
    # Security: Double-check that test_attempt belongs to current user
    if test_attempt.student != request.user:
        auto_submit_logger.error(f"AUTO_SUBMIT_ACCESS_DENIED: user={request.user.id} attempting {test_attempt.id}")
        logger.warning(f"Auto-submit access denied for user {request.user.id} attempting {test_attempt.id}")
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    # Check if already submitted
    if test_attempt.is_submitted:
        auto_submit_logger.warn(f"AUTO_SUBMIT_ALREADY_SUBMITTED: test={test_attempt.id}, user={request.user.username}")
        logger.info(f"Auto-submit attempted on already submitted test {test_attempt.id}")
        return JsonResponse({'success': False, 'error': 'Test has already been submitted'})
    
    # INDUSTRY PATTERN: Server-authoritative time validation (v1.5.2)
    # Calculate actual test end time using UTC timestamps
    session = test_attempt.test_session
    test_start_time_utc = session.start_time  # Already stored in UTC
    test_duration = timezone.timedelta(minutes=session.test.time_limit_minutes)
    actual_end_time_utc = test_start_time_utc + test_duration
    current_server_time_utc = timezone.now()  # Always UTC
    
    # Grace period for network latency (industry standard: 30 seconds)
    grace_period = timezone.timedelta(seconds=30)
    grace_end_time = actual_end_time_utc + grace_period
    
    # Log timing calculations for debugging
    timing_context = {
        'test_start_time_utc': test_start_time_utc.isoformat(),
        'test_duration_minutes': session.test.time_limit_minutes,
        'actual_end_time_utc': actual_end_time_utc.isoformat(),
        'current_server_time_utc': current_server_time_utc.isoformat(),
        'grace_end_time': grace_end_time.isoformat(),
        'time_since_start': (current_server_time_utc - test_start_time_utc).total_seconds(),
        'time_until_end': (actual_end_time_utc - current_server_time_utc).total_seconds(),
        'grace_period_seconds': 30
    }
    auto_submit_logger.info(f"AUTO_SUBMIT_TIMING_CALC: {json.dumps(timing_context, indent=2)}")
    
    # Server-side validation: Only allow auto-submit if time has actually expired
    if current_server_time_utc < actual_end_time_utc:
        # Test time has not actually expired yet
        remaining_seconds = int((actual_end_time_utc - current_server_time_utc).total_seconds())
        auto_submit_logger.warn(f"AUTO_SUBMIT_PREMATURE_BLOCKED: test={test_attempt.id}, remaining={remaining_seconds}s, user={request.user.username}")
        logger.warning(f"Premature auto-submit blocked for test {test_attempt.id}, {remaining_seconds}s remaining")
        return JsonResponse({
            'success': False, 
            'error': 'Test time has not expired yet',
            'server_time_utc': current_server_time_utc.isoformat(),
            'test_end_time_utc': actual_end_time_utc.isoformat(),
            'remaining_seconds': remaining_seconds
        })
    
    # Allow auto-submit within grace period (for network latency)
    if current_server_time_utc > grace_end_time:
        # Beyond grace period, but still allow (answers are continuously saved)
        grace_exceeded_seconds = int((current_server_time_utc - grace_end_time).total_seconds())
        auto_submit_logger.warn(f"AUTO_SUBMIT_BEYOND_GRACE: test={test_attempt.id}, late={grace_exceeded_seconds}s, user={request.user.username}")
        logger.info(f"Auto-submit beyond grace period for test {test_attempt.id}, {grace_exceeded_seconds}s late")
    
    # Log auto-submit trigger details for monitoring
    time_since_expiry = int((current_server_time_utc - actual_end_time_utc).total_seconds())
    auto_submit_logger.info(f"AUTO_SUBMIT_TIMING_VALID: test={test_attempt.id}, time_since_expiry={time_since_expiry}s, user={request.user.username}")
    logger.info(f"Auto-submit triggered for test {test_attempt.id}, {time_since_expiry}s after expiry")
    
    # Calculate total time spent using server timestamps
    total_time_spent = int((current_server_time_utc - test_attempt.started_at).total_seconds())
    question_time_spent = test_attempt.answers.aggregate(total=models.Sum('time_spent_seconds'))['total'] or 0
    
    # Mark as submitted with UTC timestamp
    test_attempt.is_submitted = True
    test_attempt.submitted_at = current_server_time_utc
    test_attempt.total_time_spent = total_time_spent
    test_attempt.save()
    
    # Calculate score (simple scoring: correct = 1, incorrect/blank = 0)
    total_questions = test_attempt.total_questions
    correct_answers = test_attempt.answers.filter(is_correct=True).count()
    score_percentage = round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
    
    # Format time for display
    def format_time(seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    # Calculate average time per question
    avg_time_per_question = int(total_time_spent / total_questions) if total_questions > 0 else 0
    
    # Store comprehensive results in session for results page
    incorrect_answers = total_questions - correct_answers
    request.session['test_results'] = {
        'attempt_id': test_attempt.id,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'incorrect_answers': incorrect_answers,
        'score_percentage': score_percentage,
        'test_title': test_attempt.test.title,
        'total_time_spent': total_time_spent,
        'total_time_formatted': format_time(total_time_spent),
        'question_time_spent': question_time_spent,
        'question_time_formatted': format_time(question_time_spent),
        'avg_time_per_question': avg_time_per_question,
        'avg_time_per_question_formatted': format_time(avg_time_per_question),
        'submitted_at': timezone.localtime(current_server_time_utc).strftime('%B %d, %Y at %I:%M %p'),
        'auto_submit_details': {
            'triggered_at_utc': current_server_time_utc.isoformat(),
            'test_end_time_utc': actual_end_time_utc.isoformat(),
            'time_since_expiry_seconds': time_since_expiry,
            'grace_period_used': time_since_expiry <= 30
        }
    }
    
    # Log successful completion with comprehensive details
    completion_context = {
        'test_id': test_attempt.id,
        'user': request.user.username,
        'submitted_at_utc': current_server_time_utc.isoformat(),
        'time_since_expiry': time_since_expiry,
        'total_time_spent': total_time_spent,
        'score_percentage': score_percentage,
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'grace_period_used': time_since_expiry <= 30
    }
    auto_submit_logger.info(f"AUTO_SUBMIT_SUCCESS: {json.dumps(completion_context, indent=2)}")
    logger.info(f"Auto-submit completed successfully for test {test_attempt.id}")
    
    return JsonResponse({
        'success': True,
        'message': 'Test auto-submitted successfully',
        'redirect_url': reverse('test_results'),
        'server_validation': {
            'submitted_at_utc': current_server_time_utc.isoformat(),
            'time_since_expiry': time_since_expiry
        }
    })


@login_required  
def test_results(request):
    """Display test results after submission (v1.3 + v1.4.1 result release control)"""
    results = request.session.get('test_results')
    if not results:
        messages.error(request, 'No test results found.')
        return redirect('dashboard')
    
    # Get detailed answer breakdown for v1.3
    try:
        test_attempt = TestAttempt.objects.select_related(
            'student_test_attempt__test_session__test'
        ).prefetch_related(
            'answers__question__choices'
        ).get(id=results['attempt_id'])
        
        # v1.4.1: Check if student can view results based on release settings and timer
        if not test_attempt.can_view_results:
            test_session = test_attempt.test_session
            test = test_attempt.test
            
            # Check if it's due to timer not expired
            if test_session.start_time:
                test_end_time = test_session.start_time + timezone.timedelta(minutes=test.time_limit_minutes)
                if timezone.now() < test_end_time:
                    time_remaining = test_end_time - timezone.now()
                    minutes_remaining = int(time_remaining.total_seconds() / 60)
                    messages.info(request, f'Test results will be available after the exam time expires (in {minutes_remaining} minutes).')
                    return redirect('dashboard')
            
            # Otherwise it's due to release settings
            messages.info(request, 'Your test results are not yet available. Your teacher will release them when ready.')
            return redirect('dashboard')
        
        # Build detailed question review data
        question_reviews = []
        for question in test_attempt.test.questions.all():
            student_answer = test_attempt.answers.filter(question=question).first()
            correct_choice = question.choices.filter(is_correct=True).first()
            
            question_review = {
                'question': question,
                'student_answer': student_answer,
                'correct_choice': correct_choice,
                'is_answered': student_answer is not None,
                'is_correct': student_answer.is_correct if student_answer else False,
                'student_choice_text': student_answer.question.choices.filter(label=student_answer.selected_choice).first().text if student_answer else None,
                'correct_choice_text': correct_choice.text if correct_choice else None,
                'time_spent': student_answer.time_spent_seconds if student_answer else 0,
            }
            question_reviews.append(question_review)
        
    except TestAttempt.DoesNotExist:
        messages.error(request, 'Test attempt details not found.')
        return redirect('dashboard')
    
    # Clear results from session after displaying
    del request.session['test_results']
    
    context = {
        'results': results,
        'passed': results['score_percentage'] >= 60,  # 60% pass threshold
        'question_reviews': question_reviews,
        'test_attempt': test_attempt,
    }
    
    return render(request, 'accounts/test_results.html', context)


@login_required
def result_detail(request, attempt_id):
    """Display persistent test results for a specific attempt (v1.3.1 + v1.4.1 result release control)"""
    try:
        test_attempt = TestAttempt.objects.select_related(
            'student_test_attempt__test_session__test',
            'student_test_attempt__student'
        ).prefetch_related(
            'answers__question__choices'
        ).get(id=attempt_id)
        
        # Security check: only the student who owns this attempt can access it
        if test_attempt.student != request.user:
            messages.error(request, 'Access denied. You can only view your own test results.')
            return redirect('dashboard')
        
        # Check if test is submitted
        if not test_attempt.is_submitted:
            messages.error(request, 'This test has not been submitted yet.')
            return redirect('dashboard')
        
        # v1.4.1: Check if student can view results based on release settings and timer
        if not test_attempt.can_view_results:
            test_session = test_attempt.test_session
            test = test_attempt.test
            
            # Check if it's due to timer not expired
            if test_session.start_time:
                test_end_time = test_session.start_time + timezone.timedelta(minutes=test.time_limit_minutes)
                if timezone.now() < test_end_time:
                    time_remaining = test_end_time - timezone.now()
                    minutes_remaining = int(time_remaining.total_seconds() / 60)
                    messages.info(request, f'Test results will be available after the exam time expires (in {minutes_remaining} minutes).')
                    return redirect('dashboard')
            
            # Otherwise it's due to release settings
            messages.info(request, 'Your test results are not yet available. Your teacher will release them when ready.')
            return redirect('dashboard')
        
        # Build detailed question review data (same as v1.3)
        question_reviews = []
        for question in test_attempt.test.questions.all():
            student_answer = test_attempt.answers.filter(question=question).first()
            correct_choice = question.choices.filter(is_correct=True).first()
            
            question_review = {
                'question': question,
                'student_answer': student_answer,
                'correct_choice': correct_choice,
                'is_answered': student_answer is not None,
                'is_correct': student_answer.is_correct if student_answer else False,
                'student_choice_text': student_answer.question.choices.filter(label=student_answer.selected_choice).first().text if student_answer else None,
                'correct_choice_text': correct_choice.text if correct_choice else None,
                'time_spent': student_answer.time_spent_seconds if student_answer else 0,
            }
            question_reviews.append(question_review)
        
        # Calculate results data (same as submit_test view)
        total_questions = test_attempt.total_questions
        correct_answers = test_attempt.answers.filter(is_correct=True).count()
        score_percentage = round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        
        # Format time for display
        def format_time(seconds):
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            if hours > 0:
                return f"{hours}h {minutes}m {secs}s"
            elif minutes > 0:
                return f"{minutes}m {secs}s"
            else:
                return f"{secs}s"
        
        # Calculate times
        total_time_spent = test_attempt.total_time_spent
        avg_time_per_question = int(total_time_spent / total_questions) if total_questions > 0 else 0
        
        # Create results data structure
        results = {
            'attempt_id': test_attempt.id,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'incorrect_answers': total_questions - correct_answers,
            'score_percentage': score_percentage,
            'test_title': test_attempt.test.title,
            'total_time_spent': total_time_spent,
            'total_time_formatted': format_time(total_time_spent),
            'avg_time_per_question': avg_time_per_question,
            'avg_time_per_question_formatted': format_time(avg_time_per_question),
            'submitted_at': timezone.localtime(test_attempt.submitted_at).strftime('%B %d, %Y at %I:%M %p'),
        }
        
        context = {
            'results': results,
            'passed': score_percentage >= 60,  # 60% pass threshold
            'question_reviews': question_reviews,
            'test_attempt': test_attempt,
            'is_persistent_view': True,  # Flag to distinguish from post-submission view
        }
        
        return render(request, 'accounts/test_results.html', context)
        
    except TestAttempt.DoesNotExist:
        messages.error(request, 'Test results not found.')
        return redirect('dashboard')


@login_required
def teacher_test_results(request, session_id):
    """Teacher view of all student results for a test session (v1.4)"""
    try:
        # Get the test session
        test_session = TestSession.objects.select_related('test', 'created_by').get(id=session_id)
        
        # Security check - only session creator can view results
        if test_session.created_by != request.user:
            messages.error(request, 'Access denied. You can only view results for tests you created.')
            return redirect('dashboard')
        
        # Get all completed test attempts for this session
        completed_attempts = TestAttempt.objects.filter(
            student_test_attempt__test_session=test_session,
            is_submitted=True
        ).select_related(
            'student_test_attempt__student',
            'student_test_attempt__test_session__test'
        ).prefetch_related('answers')
        
        # Prepare student results data
        student_results = []
        total_scores = []
        completion_count = 0
        
        for attempt in completed_attempts:
            student = attempt.student_test_attempt.student
            total_questions = attempt.total_questions
            correct_answers = attempt.answers.filter(is_correct=True).count()
            score_percentage = round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
            
            # Calculate completion time
            completion_time = attempt.total_time_spent if attempt.total_time_spent else 0
            completion_time_formatted = format_time(completion_time)
            
            student_result = {
                'attempt_id': attempt.id,
                'student_name': f"{student.first_name} {student.last_name}" if student.first_name and student.last_name else student.username,
                'student_username': student.username,
                'score': correct_answers,
                'total_questions': total_questions,
                'score_percentage': score_percentage,
                'completion_time': completion_time,
                'completion_time_formatted': completion_time_formatted,
                'submitted_at': attempt.submitted_at,
            }
            
            student_results.append(student_result)
            total_scores.append(score_percentage)
            completion_count += 1
        
        # Calculate basic statistics
        statistics = {
            'total_students': len(student_results),
            'completion_rate': round((completion_count / len(student_results)) * 100) if student_results else 0,
            'average_score': round(sum(total_scores) / len(total_scores)) if total_scores else 0,
            'highest_score': max(total_scores) if total_scores else 0,
            'lowest_score': min(total_scores) if total_scores else 0,
        }
        
        # Handle sorting
        sort_by = request.GET.get('sort', 'name')  # Default sort by name
        if sort_by == 'score':
            student_results.sort(key=lambda x: x['score_percentage'], reverse=True)
        elif sort_by == 'completion_time':
            student_results.sort(key=lambda x: x['completion_time'])
        else:  # sort by name (default)
            student_results.sort(key=lambda x: x['student_name'].lower())
        
        # Pagination for student results
        from django.core.paginator import Paginator
        paginator = Paginator(student_results, 15)  # Show 15 students per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'test_session': test_session,
            'student_results': page_obj,
            'page_obj': page_obj,
            'statistics': statistics,
            'current_sort': sort_by,
        }
        
        return render(request, 'accounts/teacher_test_results.html', context)
        
    except TestSession.DoesNotExist:
        messages.error(request, 'Test session not found.')
        return redirect('dashboard')


@login_required
def teacher_student_detail(request, session_id, attempt_id):
    """Teacher view of individual student's detailed answer breakdown (v1.4)"""
    try:
        # Get the test session and attempt
        test_session = TestSession.objects.select_related('test', 'created_by').get(id=session_id)
        test_attempt = TestAttempt.objects.select_related(
            'student_test_attempt__student',
            'student_test_attempt__test_session__test'
        ).get(id=attempt_id)
        
        # Security checks
        if test_session.created_by != request.user:
            messages.error(request, 'Access denied. You can only view results for tests you created.')
            return redirect('dashboard')
        
        if test_attempt.student_test_attempt.test_session != test_session:
            messages.error(request, 'Test attempt does not belong to this session.')
            return redirect('teacher_test_results', session_id=session_id)
        
        # Get student information
        student = test_attempt.student_test_attempt.student
        student_name = f"{student.first_name} {student.last_name}" if student.first_name and student.last_name else student.username
        
        # Calculate basic results
        total_questions = test_attempt.total_questions
        correct_answers = test_attempt.answers.filter(is_correct=True).count()
        score_percentage = round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        
        # Get detailed question breakdown (reuse v1.3 logic)
        answers = test_attempt.answers.select_related('question').order_by('question__id')
        questions = test_attempt.test.questions.all().prefetch_related('choices').order_by('id')
        
        question_reviews = []
        for question in questions:
            # Find student's answer for this question
            student_answer = answers.filter(question=question).first()
            
            # Get question choices
            choices = []
            correct_choice = None
            for choice in question.choices.all():
                choice_data = {
                    'label': choice.label,
                    'text': choice.text,
                    'is_correct': choice.is_correct
                }
                choices.append(choice_data)
                if choice.is_correct:
                    correct_choice = choice.label
            
            question_review = {
                'question': question,
                'student_answer': student_answer,
                'choices': choices,
                'correct_answer': correct_choice,
                'is_correct': student_answer.is_correct if student_answer else False,
                'time_spent': student_answer.time_spent_seconds if student_answer else 0,
                'time_spent_formatted': format_time(student_answer.time_spent_seconds) if student_answer and student_answer.time_spent_seconds else '0s',
            }
            
            question_reviews.append(question_review)
        
        # Calculate total time spent
        total_time_spent = test_attempt.total_time_spent if test_attempt.total_time_spent else 0
        avg_time_per_question = total_time_spent // total_questions if total_questions > 0 else 0
        
        context = {
            'test_session': test_session,
            'test_attempt': test_attempt,
            'student_name': student_name,
            'student_username': student.username,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'score_percentage': score_percentage,
            'question_reviews': question_reviews,
            'total_time_spent': total_time_spent,
            'total_time_formatted': format_time(total_time_spent),
            'avg_time_per_question': avg_time_per_question,
            'avg_time_per_question_formatted': format_time(avg_time_per_question),
            'submitted_at': timezone.localtime(test_attempt.submitted_at).strftime('%B %d, %Y at %I:%M %p'),
        }
        
        return render(request, 'accounts/teacher_student_detail.html', context)
        
    except (TestSession.DoesNotExist, TestAttempt.DoesNotExist):
        messages.error(request, 'Test session or attempt not found.')
        return redirect('dashboard')


def format_time(seconds):
    """Helper function to format time in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"


# ============================================================================
# v1.4.1: Result Release Control Views
# ============================================================================

@login_required
def teacher_result_release_management(request, session_id):
    """Teacher interface for managing result releases for a test session (v1.4.1)"""
    try:
        # Get the test session
        test_session = TestSession.objects.select_related('test', 'created_by').get(id=session_id)
        
        # Security check - only session creator can manage releases
        if test_session.created_by != request.user:
            messages.error(request, 'Access denied. You can only manage releases for tests you created.')
            return redirect('dashboard')
        
        # Get all test attempts for this session (both submitted and pending)
        all_attempts = TestAttempt.objects.filter(
            student_test_attempt__test_session=test_session
        ).select_related(
            'student_test_attempt__student',
            'released_by'
        ).order_by('student_test_attempt__student__username')
        
        # Prepare release data
        release_data = []
        for attempt in all_attempts:
            student = attempt.student_test_attempt.student
            student_name = f"{student.first_name} {student.last_name}" if student.first_name and student.last_name else student.username
            
            # Calculate scores if submitted
            if attempt.is_submitted:
                total_questions = attempt.total_questions
                correct_answers = attempt.answers.filter(is_correct=True).count()
                score_percentage = round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
            else:
                total_questions = 0
                correct_answers = 0
                score_percentage = 0
            
            release_info = {
                'attempt_id': attempt.id,
                'student_name': student_name,
                'student_username': student.username,
                'is_submitted': attempt.is_submitted,
                'score': correct_answers,
                'total_questions': total_questions,
                'score_percentage': score_percentage,
                'can_view_results': attempt.can_view_results,
                'is_result_released': attempt.is_result_released,
                'result_released_at': attempt.result_released_at,
                'released_by': attempt.released_by,
                'submitted_at': attempt.submitted_at,
            }
            
            release_data.append(release_info)
        
        # Handle bulk release action
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'bulk_release':
                selected_attempts = request.POST.getlist('selected_attempts')
                released_count = 0
                
                for attempt_id in selected_attempts:
                    try:
                        attempt = TestAttempt.objects.get(
                            id=attempt_id,
                            student_test_attempt__test_session=test_session,
                            is_submitted=True
                        )
                        if not attempt.is_result_released:
                            attempt.release_result(request.user)
                            released_count += 1
                    except TestAttempt.DoesNotExist:
                        continue
                
                if released_count > 0:
                    messages.success(request, f'Successfully released results for {released_count} student(s).')
                else:
                    messages.warning(request, 'No results were released. Results may already be released or students have not submitted.')
                
                return redirect('teacher_result_release_management', session_id=session_id)
        
        context = {
            'test_session': test_session,
            'release_data': release_data,
            'total_students': len(release_data),
            'submitted_count': len([r for r in release_data if r['is_submitted']]),
            'released_count': len([r for r in release_data if r['is_result_released']]),
            'pending_release_count': len([r for r in release_data if r['is_submitted'] and not r['is_result_released']]),
        }
        
        return render(request, 'accounts/teacher_result_release_management.html', context)
        
    except TestSession.DoesNotExist:
        messages.error(request, 'Test session not found.')
        return redirect('dashboard')


@login_required
@csrf_exempt
def individual_result_release(request, session_id, attempt_id):
    """AJAX endpoint for individual result release (v1.4.1)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    try:
        # Get the test session and attempt
        test_session = TestSession.objects.select_related('created_by').get(id=session_id)
        test_attempt = TestAttempt.objects.get(
            id=attempt_id,
            student_test_attempt__test_session=test_session
        )
        
        # Security check
        if test_session.created_by != request.user:
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        # Check if attempt is submitted
        if not test_attempt.is_submitted:
            return JsonResponse({'success': False, 'error': 'Student has not submitted the test yet'})
        
        # Check if already released
        if test_attempt.is_result_released:
            return JsonResponse({'success': False, 'error': 'Results already released'})
        
        # Release the result
        test_attempt.release_result(request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Result released successfully',
            'released_at': test_attempt.result_released_at.strftime('%B %d, %Y at %I:%M %p')
        })
        
    except (TestSession.DoesNotExist, TestAttempt.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Test session or attempt not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
