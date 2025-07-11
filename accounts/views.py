from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db import models
from .models import Profile, Organization
from test_sessions.models import TestSession, StudentTestAttempt, TestAttempt, Answer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


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
        
        # Get or create default organization
        organization, _ = Organization.objects.get_or_create(
            name='Default Organization',
            defaults={'is_active': True}
        )
        
        # Create profile
        profile = Profile.objects.create(
            user=user,
            organization=organization,
            role=role,
            is_active=True
        )
        
        # Add user to appropriate group
        group_name = 'Students' if role == 'student' else 'Teachers'
        group = Group.objects.get(name=group_name)
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
            return render(request, 'accounts/teacher_dashboard.html', context)
        else:
            # For students, get test sessions for dashboard
            # Note: In MVP, students see all sessions since there's no enrollment system yet
            current_time = timezone.now()
            
            # Get all active test sessions
            all_sessions = TestSession.objects.filter(is_active=True).select_related('test', 'created_by')
            
            # Get student's test attempts
            student_attempts = StudentTestAttempt.objects.filter(student=request.user).select_related('test_session')
            joined_session_ids = set(attempt.test_session.id for attempt in student_attempts)
            
            # Categorize sessions by status
            upcoming_sessions = []
            ongoing_sessions = []
            completed_sessions = []  # For now, empty since we don't track student attempts yet
            
            for session in all_sessions:
                # Add joined status to session object
                session.has_joined = session.id in joined_session_ids
                
                
                if session.status == 'upcoming':
                    upcoming_sessions.append(session)
                elif session.status == 'active':
                    ongoing_sessions.append(session)
                # expired sessions are not shown in student dashboard
            
            context.update({
                'upcoming_sessions': upcoming_sessions,
                'ongoing_sessions': ongoing_sessions,
                'completed_sessions': completed_sessions,
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
    """Display test session details for students"""
    try:
        session = TestSession.objects.select_related('test', 'created_by').get(
            id=session_id, 
            is_active=True
        )
        
        # Check if student has already joined this test
        has_joined = StudentTestAttempt.objects.filter(
            student=request.user,
            test_session=session
        ).exists()
        
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
        
        context = {
            'test_attempt': test_attempt,
            'current_question': current_question,
            'existing_answer': existing_answer,
            'question_number': test_attempt.current_question_index + 1,
            'total_questions': test_attempt.total_questions,
            'answered_questions_count': answered_questions_count,
            'progress_percentage': test_attempt.progress_percentage,
            'test_session': test_attempt.test_session,
            'test_end_time': test_attempt.test_session.end_time,
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
        
        # Check if test is still active
        if test_attempt.test_session.status != 'active':
            return JsonResponse({'success': False, 'error': 'Test session is no longer active'})
        
        # Handle GET request - return current answered count
        if request.method == 'GET':
            answered_count = test_attempt.answers.count()
            return JsonResponse({
                'success': True,
                'answered_count': answered_count
            })
        
        # Handle POST request - save answer
        elif request.method == 'POST':
            try:
                data = json.loads(request.body)
                question_id = data.get('question_id')
                selected_choice = data.get('selected_choice')
                time_spent_seconds = data.get('time_spent_seconds', 0)
                
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
        from smart_mcq.constants import SuccessMessages
        from django.utils import timezone
        
        test_attempt = TestAttempt.objects.get(id=attempt_id)
        
        # Security check
        if test_attempt.student != request.user:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
        
        # Check if already submitted
        if test_attempt.is_submitted:
            messages.info(request, 'Test has already been submitted.')
            return redirect('dashboard')
        
        # Check if test session is still active
        if test_attempt.test_session.status != 'active':
            messages.error(request, 'Test session is no longer active.')
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
        
        messages.success(request, SuccessMessages.TEST_SUBMITTED)
        return redirect('test_results')
        
    except TestAttempt.DoesNotExist:
        messages.error(request, 'Test attempt not found.')
        return redirect('dashboard')
    except Exception as e:
        messages.error(request, f'Error submitting test: {str(e)}')
        return redirect('take_test', attempt_id=attempt_id)


@login_required  
def test_results(request):
    """Display test results after submission"""
    results = request.session.get('test_results')
    if not results:
        messages.error(request, 'No test results found.')
        return redirect('dashboard')
    
    # Clear results from session after displaying
    del request.session['test_results']
    
    context = {
        'results': results,
        'passed': results['score_percentage'] >= 60,  # 60% pass threshold
    }
    
    return render(request, 'accounts/test_results.html', context)
