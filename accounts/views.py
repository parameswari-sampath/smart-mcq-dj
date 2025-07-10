from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse
from .models import Profile, Organization


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
            return render(request, 'accounts/student_dashboard.html', context)
            
    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found. Please contact administrator.')
        return redirect('login')
