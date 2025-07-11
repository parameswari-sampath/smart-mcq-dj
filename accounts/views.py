from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .models import Profile, Organization
from test_sessions.models import TestSession, StudentTestAttempt


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
                StudentTestAttempt.objects.create(
                    student=request.user,
                    test_session=session
                )
                # TODO: In v1.0, this will redirect to the test taking interface
                messages.success(request, f'Successfully joined test: {session.test.title}! (Test interface will be available in v1.0)')
                return redirect('dashboard')
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
