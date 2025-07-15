from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
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
    """List all tests created by the current teacher with pagination"""
    tests = Test.objects.filter(
        created_by=request.user,
        is_active=True
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(tests, 10)  # Show 10 tests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tests': page_obj,
        'page_obj': page_obj
    }
    return render(request, 'tests/test_list.html', context)


@teacher_required
def test_create(request):
    """Create a new test with question selection"""
    if request.method == 'POST':
        # Handle scheduled release time
        scheduled_release_time = None
        if request.POST.get('result_release_mode') == 'scheduled':
            scheduled_release_time = request.POST.get('scheduled_release_time')
        
        # Create test with v1.4.1 result release control fields
        test = Test.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            time_limit_minutes=int(request.POST['time_limit_minutes']),
            category=request.POST.get('category', ''),
            created_by=request.user,
            # v1.4.1 Result Release Control fields
            is_practice_test=request.POST.get('is_practice_test', 'True') == 'True',
            result_release_mode=request.POST.get('result_release_mode', 'immediate'),
            answer_visibility_level=request.POST.get('answer_visibility_level', 'with_answers'),
            scheduled_release_time=scheduled_release_time
        )
        
        # Add selected questions to test
        selected_questions = request.POST.getlist('questions')
        if selected_questions:
            test.questions.set(selected_questions)
        
        messages.success(request, f'{"Practice" if test.is_practice_test else "Assessment"} test created successfully with {test.get_result_release_mode_display().lower()} release mode!')
        return redirect('tests:test_list')
    
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
        # Handle scheduled release time
        scheduled_release_time = None
        if request.POST.get('result_release_mode') == 'scheduled':
            scheduled_release_time = request.POST.get('scheduled_release_time')
        
        # Update test with v1.4.1 result release control fields
        test.title = request.POST['title']
        test.description = request.POST['description']
        test.time_limit_minutes = int(request.POST['time_limit_minutes'])
        test.category = request.POST.get('category', '')
        # v1.4.1 Result Release Control fields
        test.is_practice_test = request.POST.get('is_practice_test', 'True') == 'True'
        test.result_release_mode = request.POST.get('result_release_mode', 'immediate')
        test.answer_visibility_level = request.POST.get('answer_visibility_level', 'with_answers')
        test.scheduled_release_time = scheduled_release_time
        test.save()
        
        # Update selected questions
        selected_questions = request.POST.getlist('questions')
        test.questions.set(selected_questions)
        
        messages.success(request, f'{"Practice" if test.is_practice_test else "Assessment"} test updated successfully with {test.get_result_release_mode_display().lower()} release mode!')
        return redirect('tests:test_list')
    
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
        return redirect('tests:test_list')
    
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
