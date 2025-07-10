from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Test
from questions.models import Question


def teacher_required(view_func):
    """Decorator to ensure only teachers can access test management"""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            if request.user.profile.role != 'teacher':
                raise PermissionDenied("Only teachers can manage tests")
        except:
            raise PermissionDenied("Profile not found")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@teacher_required
def test_list(request):
    """List all tests created by the current teacher"""
    tests = Test.objects.filter(
        created_by=request.user,
        is_active=True
    )
    context = {
        'tests': tests
    }
    return render(request, 'tests/test_list.html', context)


@teacher_required
def test_create(request):
    """Create a new test with question selection"""
    if request.method == 'POST':
        # Create test
        test = Test.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            time_limit_minutes=int(request.POST['time_limit_minutes']),
            category=request.POST.get('category', ''),
            organization=request.user.profile.organization,
            created_by=request.user
        )
        
        # Add selected questions to test
        selected_questions = request.POST.getlist('questions')
        if selected_questions:
            test.questions.set(selected_questions)
        
        messages.success(request, 'Test created successfully!')
        return redirect('test_list')
    
    # Get available questions for selection
    available_questions = Question.objects.filter(
        created_by=request.user,
        is_active=True
    )
    
    context = {
        'available_questions': available_questions
    }
    return render(request, 'tests/test_form.html', context)


@teacher_required
def test_edit(request, pk):
    """Edit an existing test"""
    test = get_object_or_404(
        Test, 
        pk=pk, 
        created_by=request.user,
        is_active=True
    )
    
    if request.method == 'POST':
        # Update test
        test.title = request.POST['title']
        test.description = request.POST['description']
        test.time_limit_minutes = int(request.POST['time_limit_minutes'])
        test.category = request.POST.get('category', '')
        test.save()
        
        # Update selected questions
        selected_questions = request.POST.getlist('questions')
        test.questions.set(selected_questions)
        
        messages.success(request, 'Test updated successfully!')
        return redirect('test_list')
    
    # Get available questions for selection
    available_questions = Question.objects.filter(
        created_by=request.user,
        is_active=True
    )
    
    context = {
        'test': test,
        'available_questions': available_questions
    }
    return render(request, 'tests/test_form.html', context)


@teacher_required
def test_delete(request, pk):
    """Delete a test (soft delete)"""
    test = get_object_or_404(
        Test,
        pk=pk,
        created_by=request.user,
        is_active=True
    )
    
    if request.method == 'POST':
        test.is_active = False
        test.save()
        messages.success(request, 'Test deleted successfully!')
        return redirect('test_list')
    
    context = {'test': test}
    return render(request, 'tests/test_confirm_delete.html', context)


@teacher_required
def test_detail(request, pk):
    """View test details with questions"""
    test = get_object_or_404(
        Test,
        pk=pk,
        created_by=request.user,
        is_active=True
    )
    
    context = {
        'test': test,
        'questions': test.questions.all()
    }
    return render(request, 'tests/test_detail.html', context)
