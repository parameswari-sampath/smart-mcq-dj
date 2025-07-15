from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.db import transaction
import csv
import io
from questions.models import Question, Choice


def teacher_required(view_func):
    """Decorator to ensure only teachers can access bulk operations"""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            if request.user.profile.role != 'teacher':
                raise PermissionDenied("Only teachers can perform bulk operations")
        except:
            raise PermissionDenied("Profile not found")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@teacher_required
def csv_import_questions(request):
    """CSV import interface for questions"""
    if request.method == 'POST':
        if 'csv_file' not in request.FILES:
            messages.error(request, 'Please select a CSV file to upload.')
            return render(request, 'bulk_operations/csv_import.html')
        
        csv_file = request.FILES['csv_file']
        
        # Validate file type
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return render(request, 'bulk_operations/csv_import.html')
        
        # Validate file size (5MB limit)
        if csv_file.size > 5 * 1024 * 1024:
            messages.error(request, 'File size must be less than 5MB.')
            return render(request, 'bulk_operations/csv_import.html')
        
        # Parse and validate CSV
        try:
            csv_data = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_data))
            
            # Validate required columns
            required_columns = [
                'title', 'description', 'choice_a', 'choice_b', 
                'choice_c', 'choice_d', 'correct_answer', 'category', 'difficulty'
            ]
            
            if not all(col in csv_reader.fieldnames for col in required_columns):
                missing_cols = [col for col in required_columns if col not in csv_reader.fieldnames]
                messages.error(request, f'Missing required columns: {", ".join(missing_cols)}')
                return render(request, 'bulk_operations/csv_import.html')
            
            # Process and validate rows
            questions_data = []
            line_num = 2  # Start from line 2 (after header)
            
            for row in csv_reader:
                row_errors = validate_question_row(row, line_num)
                row_data = dict(row)
                row_data['line_number'] = line_num
                row_data['errors'] = row_errors
                row_data['has_errors'] = len(row_errors) > 0
                questions_data.append(row_data)
                line_num += 1
            
            # Check row count limit
            if len(questions_data) > 500:
                messages.error(request, 'Maximum 500 questions allowed per import.')
                return render(request, 'bulk_operations/csv_import.html')
            
            # Store all data (including errors) in session for validation view
            request.session['validation_data'] = questions_data
            return redirect('bulk_operations:csv_validate')
            
        except Exception as e:
            messages.error(request, f'Error reading CSV file: {str(e)}')
            return render(request, 'bulk_operations/csv_import.html')
    
    return render(request, 'bulk_operations/csv_import.html')


@teacher_required
def csv_validate(request):
    """Validate CSV data and show errors"""
    validation_data = request.session.get('validation_data')
    if not validation_data:
        messages.error(request, 'No data to validate. Please upload a CSV file first.')
        return redirect('bulk_operations:csv_import')
    
    # Count errors and valid rows
    error_count = sum(1 for row in validation_data if row['has_errors'])
    valid_count = len(validation_data) - error_count
    
    if request.method == 'POST':
        # User confirmed to proceed with only valid rows
        if error_count > 0:
            # Filter out rows with errors
            valid_rows = [row for row in validation_data if not row['has_errors']]
            request.session['import_data'] = valid_rows
        else:
            request.session['import_data'] = validation_data
            
        return redirect('bulk_operations:csv_preview')
    
    context = {
        'validation_data': validation_data,
        'total_count': len(validation_data),
        'error_count': error_count,
        'valid_count': valid_count,
        'has_errors': error_count > 0
    }
    return render(request, 'bulk_operations/csv_validate.html', context)


@teacher_required
def csv_preview(request):
    """Preview CSV data before import"""
    import_data = request.session.get('import_data')
    if not import_data:
        messages.error(request, 'No data to preview. Please upload a CSV file first.')
        return redirect('bulk_operations:csv_import')
    
    if request.method == 'POST':
        # Confirm import
        try:
            with transaction.atomic():
                created_count = 0
                rejected_count = 0
                total_count = len(import_data)
                
                for row_data in import_data:
                    # Check for duplicates (user-based, not organization-based)
                    existing = Question.objects.filter(
                        title=row_data['title'],
                        created_by=request.user,
                        is_active=True
                    ).exists()
                    
                    if existing:
                        rejected_count += 1
                        continue  # Skip duplicate
                    
                    # Create question
                    question = Question.objects.create(
                        title=row_data['title'],
                        description=row_data['description'],
                        category=row_data['category'],
                        difficulty=row_data['difficulty'],
                        organization=request.user.profile.organization,
                        created_by=request.user
                    )
                    
                    # Create choices
                    choices_data = [
                        ('A', row_data['choice_a'], row_data['correct_answer'].upper() == 'A'),
                        ('B', row_data['choice_b'], row_data['correct_answer'].upper() == 'B'),
                        ('C', row_data['choice_c'], row_data['correct_answer'].upper() == 'C'),
                        ('D', row_data['choice_d'], row_data['correct_answer'].upper() == 'D'),
                    ]
                    
                    for label, text, is_correct in choices_data:
                        Choice.objects.create(
                            question=question,
                            label=label,
                            text=text,
                            is_correct=is_correct
                        )
                    
                    created_count += 1
                
                # Clear session data
                del request.session['import_data']
                
                # Create detailed success message
                success_msg = f'Import completed: {created_count} questions imported'
                if rejected_count > 0:
                    success_msg += f', {rejected_count} duplicates rejected'
                success_msg += f' (Total processed: {total_count})'
                
                messages.success(request, success_msg)
                return redirect('questions:question_list')
                
        except Exception as e:
            messages.error(request, f'Error importing questions: {str(e)}')
            return render(request, 'bulk_operations/csv_preview.html', {'questions': import_data})
    
    context = {
        'questions': import_data,
        'total_count': len(import_data)
    }
    return render(request, 'bulk_operations/csv_preview.html', context)


@teacher_required
def csv_template_download(request):
    """Download CSV template with sample data"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="question_import_template.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'title', 'description', 'choice_a', 'choice_b', 
        'choice_c', 'choice_d', 'correct_answer', 'category', 'difficulty'
    ])
    
    # Write sample data
    sample_questions = [
        [
            'What is the capital of France?',
            'Choose the correct capital city of France.',
            'London',
            'Paris',
            'Berlin',
            'Madrid',
            'B',
            'Geography',
            'easy'
        ],
        [
            'Which programming language is known for web development?',
            'Select the language primarily used for web development.',
            'Python',
            'JavaScript',
            'C++',
            'Java',
            'B',
            'Programming',
            'medium'
        ],
        [
            'What is 2 + 2?',
            'Basic arithmetic calculation.',
            '3',
            '4',
            '5',
            '6',
            'B',
            'Mathematics',
            'easy'
        ]
    ]
    
    for question in sample_questions:
        writer.writerow(question)
    
    return response


def validate_question_row(row, line_num):
    """Validate a single question row"""
    errors = []
    
    # Check required fields
    required_fields = ['title', 'description', 'choice_a', 'choice_b', 'choice_c', 'choice_d', 'correct_answer']
    for field in required_fields:
        if not row.get(field, '').strip():
            errors.append(f"Line {line_num}: Missing {field}")
    
    # Validate correct_answer
    correct_answer = row.get('correct_answer', '').strip().upper()
    if correct_answer not in ['A', 'B', 'C', 'D']:
        errors.append(f"Line {line_num}: correct_answer must be A, B, C, or D")
    
    # Validate difficulty
    difficulty = row.get('difficulty', '').strip().lower()
    if difficulty and difficulty not in ['easy', 'medium', 'hard']:
        errors.append(f"Line {line_num}: difficulty must be easy, medium, or hard")
    
    # Validate title length
    title = row.get('title', '').strip()
    if len(title) > 500:
        errors.append(f"Line {line_num}: title too long (max 500 characters)")
    
    return errors