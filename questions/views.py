from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
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
    """List all questions for the teacher's organization"""
    questions = Question.objects.filter(
        organization=request.user.profile.organization,
        is_active=True
    )
    context = {
        'questions': questions
    }
    return render(request, 'questions/question_list.html', context)


@teacher_required
def question_create(request):
    """Create a new question with 4 choices"""
    if request.method == 'POST':
        # Create question
        question = Question.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            category=request.POST.get('category', ''),
            difficulty=request.POST['difficulty'],
            organization=request.user.profile.organization,
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
        return redirect('question_list')
    
    return render(request, 'questions/question_form.html')


@teacher_required
def question_edit(request, pk):
    """Edit an existing question"""
    question = get_object_or_404(
        Question, 
        pk=pk, 
        organization=request.user.profile.organization,
        is_active=True
    )
    
    if request.method == 'POST':
        # Update question
        question.title = request.POST['title']
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
        return redirect('question_list')
    
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
        organization=request.user.profile.organization,
        is_active=True
    )
    
    if request.method == 'POST':
        question.is_active = False
        question.save()
        messages.success(request, 'Question deleted successfully!')
        return redirect('question_list')
    
    context = {'question': question}
    return render(request, 'questions/question_confirm_delete.html', context)
