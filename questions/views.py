from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from .models import Question, Choice


def teacher_required(view_func):
    """Decorator to ensure only teachers can access question management"""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            if request.user.profile.role != 'teacher':
                raise PermissionDenied("Only teachers can manage questions")
        except:
            raise PermissionDenied("Profile not found")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@teacher_required
def question_list(request):
    """List all questions created by the current teacher with pagination"""
    questions = Question.objects.filter(
        created_by=request.user,
        is_active=True
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(questions, 10)  # Show 10 questions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'questions': page_obj,
        'page_obj': page_obj
    }
    return render(request, 'questions/question_list.html', context)


@teacher_required
def question_create(request):
    """Create a new question with 4 choices"""
    if request.method == 'POST':
        # Check for duplicate questions (teacher-specific)
        title = request.POST['title'].strip()
        existing_question = Question.objects.filter(
            title=title,
            created_by=request.user,
            is_active=True
        ).exists()
        
        if existing_question:
            messages.error(request, f'A question with the title "{title}" already exists in your question bank.')
            return render(request, 'questions/question_form.html', {
                'form_data': request.POST,
                'error': True
            })
        
        # Create question
        question = Question.objects.create(
            title=title,
            description=request.POST['description'],
            category=request.POST.get('category', ''),
            difficulty=request.POST['difficulty'],
            created_by=request.user
        )
        
        # Handle image upload
        if 'image' in request.FILES:
            question.image = request.FILES['image']
            question.save()
        
        # Create 4 choices
        choices_data = [
            ('A', request.POST['choice_a'], request.POST.get('correct') == 'A'),
            ('B', request.POST['choice_b'], request.POST.get('correct') == 'B'),
            ('C', request.POST['choice_c'], request.POST.get('correct') == 'C'),
            ('D', request.POST['choice_d'], request.POST.get('correct') == 'D'),
        ]
        
        for label, text, is_correct in choices_data:
            Choice.objects.create(
                question=question,
                label=label,
                text=text,
                is_correct=is_correct
            )
        
        messages.success(request, 'Question created successfully!')
        return redirect('questions:question_list')
    
    return render(request, 'questions/question_form.html', {
        'question': None,
        'choices': []
    })


@teacher_required
def question_detail(request, pk):
    """View question details"""
    question = get_object_or_404(
        Question, 
        pk=pk, 
        created_by=request.user,
        is_active=True
    )
    
    context = {
        'question': question,
        'choices': question.choices.all().order_by('label')
    }
    return render(request, 'questions/question_detail.html', context)


@teacher_required
def question_edit(request, pk):
    """Edit an existing question"""
    question = get_object_or_404(
        Question, 
        pk=pk, 
        created_by=request.user,
        is_active=True
    )
    
    if request.method == 'POST':
        # Check for duplicate questions (teacher-specific, excluding current question)
        title = request.POST['title'].strip()
        existing_question = Question.objects.filter(
            title=title,
            created_by=request.user,
            is_active=True
        ).exclude(pk=question.pk).exists()
        
        if existing_question:
            messages.error(request, f'A question with the title "{title}" already exists in your question bank.')
            context = {
                'question': question,
                'choices': question.choices.all().order_by('label'),
                'form_data': request.POST,
                'error': True
            }
            return render(request, 'questions/question_form.html', context)
        
        # Update question
        question.title = title
        question.description = request.POST['description']
        question.category = request.POST.get('category', '')
        question.difficulty = request.POST['difficulty']
        
        # Handle image upload
        if 'image' in request.FILES:
            question.image = request.FILES['image']
        
        question.save()
        
        # Update choices
        choices = question.choices.all().order_by('label')
        choice_updates = [
            ('A', request.POST['choice_a'], request.POST.get('correct') == 'A'),
            ('B', request.POST['choice_b'], request.POST.get('correct') == 'B'),
            ('C', request.POST['choice_c'], request.POST.get('correct') == 'C'),
            ('D', request.POST['choice_d'], request.POST.get('correct') == 'D'),
        ]
        
        for choice, (label, text, is_correct) in zip(choices, choice_updates):
            choice.text = text
            choice.is_correct = is_correct
            choice.save()
        
        messages.success(request, 'Question updated successfully!')
        return redirect('questions:question_list')
    
    context = {
        'question': question,
        'choices': question.choices.all().order_by('label')
    }
    return render(request, 'questions/question_form.html', context)


@teacher_required
def question_delete(request, pk):
    """Delete a question (soft delete)"""
    question = get_object_or_404(
        Question,
        pk=pk,
        created_by=request.user,
        is_active=True
    )
    
    if request.method == 'POST':
        question.is_active = False
        question.save()
        messages.success(request, 'Question deleted successfully!')
        return redirect('questions:question_list')
    
    context = {'question': question}
    return render(request, 'questions/question_confirm_delete.html', context)
