# Quiz Results Logic - Django Migration Guide

## Overview

This document provides a comprehensive guide for migrating the quiz results display logic from the current React/TypeScript implementation to Django. The system processes encrypted quiz result files and provides detailed analytics on student performance, question difficulty, and learning behaviors.

## Data Structure & Input Requirements

### Input Data Source

- **File Type**: `.enc` files (AES encrypted)
- **Encryption**: AES with hardcoded password "YourStrongSecret123" using crypto-js
- **Content**: JSON data containing quiz results

### Core Data Models

#### Registration Information

```python
# Django Model Equivalent
class Registration(models.Model):
    registration_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
```

#### Quiz Session Data

```python
class QuizSession(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    percentage = models.FloatField()
    total_time = models.IntegerField()  # in seconds
    completed_at = models.DateTimeField()
```

#### Question Results (Per Question Per Student)

```python
class QuestionResult(models.Model):
    quiz_session = models.ForeignKey(QuizSession, on_delete=models.CASCADE)
    question_id = models.CharField(max_length=100)
    question = models.TextField()
    selected_answer = models.TextField()
    correct_answer = models.TextField()
    is_correct = models.BooleanField()
    time_spent = models.IntegerField()  # in seconds
    first_attempt_answer = models.TextField()
    first_attempt_correct = models.BooleanField()
    total_attempts = models.IntegerField()
    attempt_timestamp = models.DateTimeField()
    explanation = models.TextField()
```

### Flattened Table Row Structure (For Analytics)

Each row represents one question attempt by one student:

```python
class TableRow:
    registration_id: str
    name: str
    completed_at: datetime
    score: int
    total_questions: int
    percentage: float
    question_id: str
    question: str
    selected_answer: str
    correct_answer: str
    is_correct: bool
    time_spent: int  # seconds
    first_attempt_answer: str
    first_attempt_correct: bool
    total_attempts: int
    attempt_timestamp: datetime
    explanation: str
```

## Core Calculation Logic

### 1. Question Difficulty Analysis

#### Key Metrics per Question:

```python
def calculate_question_stats(question_rows):
    """
    Calculate difficulty metrics for each question
    """
    stats = {
        'question_id': question_rows[0].question_id,
        'question': question_rows[0].question,
        'total_attempts': len(question_rows),
        'correct_attempts': len([r for r in question_rows if r.first_attempt_correct]),
        'success_rate': (correct_attempts / total_attempts) * 100,
        'average_time_spent': sum(r.time_spent for r in question_rows) / len(question_rows),
        'first_attempt_success': len([r for r in question_rows if r.first_attempt_correct]),
        'first_attempt_rate': (first_attempt_success / total_attempts) * 100,
        'multiple_attempts_count': len([r for r in question_rows if r.total_attempts > 1]),
        'multiple_attempts_rate': (multiple_attempts_count / total_attempts) * 100,
        'average_attempts_per_student': sum(r.total_attempts for r in question_rows) / len(question_rows)
    }
    return stats
```

#### Difficulty Classification:

```python
def get_difficulty_level(success_rate):
    """Classify question difficulty based on first attempt success rate"""
    if success_rate >= 70:
        return "Easy"
    elif success_rate >= 50:
        return "Medium"
    elif success_rate >= 30:
        return "Hard"
    else:
        return "Very Hard"
```

#### Time Complexity Classification:

```python
def get_time_complexity(avg_time, overall_avg_time):
    """Classify time complexity relative to average"""
    ratio = avg_time / overall_avg_time
    if ratio >= 1.5:
        return "Very Long"
    elif ratio >= 1.2:
        return "Long"
    elif ratio >= 0.8:
        return "Average"
    else:
        return "Quick"
```

### 2. Learning Behavior Insights

#### Speed vs Accuracy Correlation:

```python
def calculate_speed_accuracy_correlation(student_data):
    """Calculate Pearson correlation between time spent and accuracy"""
    time_values = [s.average_time_per_question for s in student_data]
    accuracy_values = [(s.first_attempt_correct / s.total_questions) * 100 for s in student_data]

    # Pearson correlation formula
    n = len(time_values)
    sum_x = sum(time_values)
    sum_y = sum(accuracy_values)
    sum_xy = sum(x * y for x, y in zip(time_values, accuracy_values))
    sum_x2 = sum(x * x for x in time_values)
    sum_y2 = sum(y * y for y in accuracy_values)

    numerator = n * sum_xy - sum_x * sum_y
    denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5

    return numerator / denominator if denominator != 0 else 0
```

#### Fatigue Analysis:

```python
def analyze_fatigue(student_performance_sequence):
    """Analyze performance degradation over time"""
    total_questions = len(student_performance_sequence)
    midpoint = total_questions // 2

    first_half = student_performance_sequence[:midpoint]
    second_half = student_performance_sequence[midpoint:]

    first_half_accuracy = sum(1 for q in first_half if q.first_attempt_correct) / len(first_half) * 100
    second_half_accuracy = sum(1 for q in second_half if q.first_attempt_correct) / len(second_half) * 100

    fatigue_effect = first_half_accuracy - second_half_accuracy

    return {
        'first_half_accuracy': first_half_accuracy,
        'second_half_accuracy': second_half_accuracy,
        'fatigue_effect': fatigue_effect
    }
```

#### Recovery Patterns:

```python
def analyze_recovery_patterns(student_sequence):
    """Analyze how students recover from wrong answers"""
    consecutive_wrong = 0
    max_consecutive_wrong = 0
    recoveries = 0
    recovery_after_wrong = 0

    for question in student_sequence:
        if not question.first_attempt_correct:
            consecutive_wrong += 1
            max_consecutive_wrong = max(max_consecutive_wrong, consecutive_wrong)
        else:
            if consecutive_wrong > 0:
                recoveries += 1
                recovery_after_wrong += consecutive_wrong
            consecutive_wrong = 0

    return {
        'max_consecutive_wrong': max_consecutive_wrong,
        'total_recoveries': recoveries,
        'avg_recovery_time': recovery_after_wrong / recoveries if recoveries > 0 else 0
    }
```

### 3. Student Performance Analysis

#### Learning Efficiency Score (Primary Metric):

```python
def calculate_learning_efficiency(student_data):
    """
    Primary scoring metric combining first attempt accuracy and learning speed
    Formula: (first_attempt_percentage * 0.7) + (true_learning_rate * 0.3)
    """
    questions_wrong_first = [q for q in student_data if not q.first_attempt_correct]

    # Quick learners: Got it right on 2nd attempt
    learned_on_2nd_attempt = len([q for q in questions_wrong_first
                                 if q.total_attempts == 2 and q.is_correct])

    # True learning rate (2nd attempt success for initially wrong answers)
    true_learning_rate = (learned_on_2nd_attempt / len(questions_wrong_first) * 100) if questions_wrong_first else 0

    first_attempt_percentage = (sum(1 for q in student_data if q.first_attempt_correct) / len(student_data)) * 100

    learning_efficiency_score = (first_attempt_percentage * 0.7) + (true_learning_rate * 0.3)

    return {
        'first_attempt_percentage': first_attempt_percentage,
        'true_learning_rate': true_learning_rate,
        'learning_efficiency_score': learning_efficiency_score
    }
```

#### Performance Categories:

```python
def get_performance_category(efficiency_score):
    """Classify student performance based on learning efficiency"""
    if efficiency_score >= 90:
        return "Excellent"
    elif efficiency_score >= 75:
        return "Good"
    elif efficiency_score >= 60:
        return "Satisfactory"
    elif efficiency_score >= 40:
        return "Needs Improvement"
    else:
        return "Requires Support"
```

#### Random Clicking Detection:

```python
def calculate_random_clicking_rate(student_data):
    """Detect students who randomly click (3+ attempts on wrong questions)"""
    questions_wrong_first = [q for q in student_data if not q.first_attempt_correct]
    questions_many_attempts = len([q for q in questions_wrong_first if q.total_attempts > 2])

    return (questions_many_attempts / len(questions_wrong_first) * 100) if questions_wrong_first else 0
```

## Time Parsing Logic

### Time Format Handling:

```python
def parse_time_to_seconds(time_value):
    """
    Convert various time formats to seconds
    Handles: MM:SS format, numeric strings, and direct numbers
    """
    if isinstance(time_value, (int, float)):
        return float(time_value)

    if isinstance(time_value, str):
        # Handle MM:SS format
        if ':' in time_value:
            parts = time_value.split(':')
            if len(parts) == 2:
                minutes = int(parts[0]) or 0
                seconds = int(parts[1]) or 0
                return minutes * 60 + seconds

        # Handle numeric string
        try:
            return float(time_value)
        except ValueError:
            return 0

    return 0
```

## Summary Statistics Calculations

### Overall Analytics:

```python
def calculate_summary_stats(all_data):
    """Calculate system-wide statistics"""
    # Question-level summaries
    challenging_questions = len([q for q in question_stats if q.success_rate < 40])
    avg_time_all_questions = sum(q.average_time_spent for q in question_stats) / len(question_stats)
    avg_first_attempt_rate = sum(q.first_attempt_rate for q in question_stats) / len(question_stats)
    avg_multiple_attempts_rate = sum(q.multiple_attempts_rate for q in question_stats) / len(question_stats)

    # Student-level summaries
    avg_learning_efficiency = sum(s.learning_efficiency_score for s in student_stats) / len(student_stats)
    students_needing_support = len([s for s in student_stats if s.performance_category in ["Requires Support", "Needs Improvement"]])

    return {
        'challenging_questions': challenging_questions,
        'avg_time_all_questions': avg_time_all_questions,
        'avg_first_attempt_rate': avg_first_attempt_rate,
        'avg_multiple_attempts_rate': avg_multiple_attempts_rate,
        'avg_learning_efficiency': avg_learning_efficiency,
        'students_needing_support': students_needing_support
    }
```

## Export Functionality

### Excel Export Structure:

The system exports a flattened table with these columns:

- RegistrationID, Name, CompletedAt
- Score, TotalQuestions, Percentage
- QuestionID, Question, SelectedAnswer, CorrectAnswer, IsCorrect
- TimeSpent, FirstAttemptAnswer, FirstAttemptCorrect
- TotalAttempts, AttemptTimestamp, Explanation

### Key Implementation Notes:

1. **Encryption Handling**: Django will need crypto functionality to decrypt .enc files
2. **Time Parsing**: Flexible parsing for MM:SS format and numeric values
3. **Primary Metrics**: Learning Efficiency Score is the key metric, not final score (which is always 40/40)
4. **Data Grouping**: Analytics require grouping by student and by question
5. **Performance Focus**: First attempt success rate is more meaningful than final success rate
6. **Learning Detection**: 2nd attempt success indicates genuine learning vs 3+ attempts indicating guessing

## Django Implementation Recommendations

1. **Models**: Create the models above to store processed data
2. **File Processing**: Create a management command or API endpoint to process .enc files
3. **Analytics Views**: Create separate views/serializers for each analysis type
4. **Caching**: Consider caching calculated statistics for performance
5. **Export**: Use libraries like openpyxl for Excel export functionality
6. **Frontend**: API endpoints should return data in similar structure for frontend consumption

This migration preserves all the complex analytics logic while adapting it to Django's architecture.

# Next.js to Django Migration Guide - Parvam Quiz Platform

## Overview

This document provides a comprehensive guide for migrating the Parvam Quiz Platform from Next.js/React to Django. The current application is a secure online quiz platform with advanced tracking and security features.

## Current Architecture Analysis

### Frontend Structure (Next.js/React)

The application follows a modular architecture with the following structure:

```
app/
├── test/page.tsx                    # Main test page route
├── analytics/page.tsx               # Analytics dashboard
├── decrypt/page.tsx                 # Result decryption page
└── layout.tsx                       # Root layout

modules/
├── quiz/                            # Core quiz functionality
│   ├── components/
│   │   ├── Quiz.tsx                 # Main quiz component
│   │   ├── TestContainer.tsx        # Test wrapper component
│   │   ├── QuestionCard.tsx         # Individual question display
│   │   ├── QuizResults.tsx          # Results display
│   │   ├── QuizHeader.tsx           # Quiz progress header
│   │   ├── LoadingScreen.tsx        # Pre-test loading
│   │   ├── AnswerResultModal.tsx    # Answer feedback modal
│   │   └── ConfirmationModal.tsx    # Confirmation dialogs
│   ├── hooks/
│   │   ├── useQuizFlow.ts          # Test phase management
│   │   ├── useQuizState.ts         # Quiz state management
│   │   ├── useQuizTimer.ts         # Timer functionality
│   │   ├── useQuizShuffle.ts       # Question/option shuffling
│   │   └── useQuizPersistence.ts   # Local storage persistence
│   └── types/quiz.ts               # TypeScript interfaces
├── security/                        # Security enforcement
│   ├── components/
│   │   ├── SecurityManager.tsx     # Main security component
│   │   └── SecurityWarning.tsx     # Violation warnings
│   └── hooks/
│       ├── useSecurityMonitoring.ts
│       ├── useFullscreenSecurity.ts
│       ├── useKeyboardSecurity.ts
│       └── useTabSwitchSecurity.ts
├── registration/
│   └── components/
│       └── RegistrationForm.tsx    # User registration
└── shared/
    ├── utils/downloadHelper.ts     # Encrypted result downloads
    └── hooks/useRegistration.ts    # Registration logic
```

## Key Features to Migrate

### 1. Test Flow Management (`app/test/page.tsx`)

**Current Implementation:**

- Main coordinator component managing test phases
- Integrates registration, security, quiz, and results
- Phase-based state management: `registration` → `loading` → `testing` → `completed` → `security-violation`

**Django Migration:**

```python
# views.py
class QuizFlowView(TemplateView):
    template_name = 'quiz/test.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['phase'] = self.request.session.get('quiz_phase', 'registration')
        context['security_config'] = settings.QUIZ_SECURITY_CONFIG
        return context

# urls.py
urlpatterns = [
    path('test/', QuizFlowView.as_view(), name='quiz_test'),
    path('api/phase/', PhaseUpdateAPIView.as_view(), name='phase_update'),
]
```

### 2. Registration System (`modules/registration/`)

**Current Implementation:**

- Local form validation with real-time error feedback
- Generates unique registration IDs with timestamps
- Stores data in component state

**Django Migration:**

```python
# models.py
class Registration(models.Model):
    registration_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40)

# forms.py
class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['registration_id', 'name', 'email']

    def clean_registration_id(self):
        reg_id = self.cleaned_data['registration_id']
        if len(reg_id) < 3:
            raise ValidationError("Registration ID must be at least 3 characters")
        return reg_id

# views.py
class RegistrationAPIView(APIView):
    def post(self, request):
        form = RegistrationForm(request.data)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.session_key = request.session.session_key
            registration.save()
            request.session['registration_id'] = registration.id
            request.session['quiz_phase'] = 'loading'
            return Response({'success': True})
        return Response({'errors': form.errors})
```

### 3. Quiz Engine (`modules/quiz/components/Quiz.tsx`)

**Current Implementation:**

- Advanced first-click tracking system
- Question/option shuffling for each attempt
- Comprehensive timing mechanisms
- Local storage persistence
- Detailed result tracking with attempt analytics

**Django Migration:**

```python
# models.py
class Question(models.Model):
    question_id = models.IntegerField(unique=True)
    question_text = models.TextField()
    explanation = models.TextField()

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField()

class QuizSession(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    shuffled_questions = models.JSONField()  # Store question order
    current_question = models.IntegerField(default=0)
    quiz_start_time = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

class QuestionAttempt(models.Model):
    quiz_session = models.ForeignKey(QuizSession, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    # First-click tracking (key feature)
    first_attempt_answer = models.IntegerField()
    first_attempt_text = models.TextField()
    first_attempt_correct = models.BooleanField()
    first_attempt_timestamp = models.DateTimeField()

    # Final answer tracking
    selected_answer = models.IntegerField()
    selected_answer_text = models.TextField()
    is_correct = models.BooleanField()
    total_attempts = models.IntegerField(default=1)
    time_spent = models.DurationField()

# views.py
class QuizAPIView(APIView):
    def post(self, request):
        action = request.data.get('action')

        if action == 'submit_answer':
            # Handle first-click tracking logic
            return self.handle_answer_submission(request)
        elif action == 'next_question':
            return self.handle_next_question(request)
        elif action == 'try_again':
            return self.handle_try_again(request)

    def handle_answer_submission(self, request):
        session = QuizSession.objects.get(registration__session_key=request.session.session_key)

        # Capture first-click data (critical feature)
        if not QuestionAttempt.objects.filter(
            quiz_session=session,
            question_id=request.data['question_id']
        ).exists():
            QuestionAttempt.objects.create(
                quiz_session=session,
                question_id=request.data['question_id'],
                first_attempt_answer=request.data['answer_index'],
                first_attempt_text=request.data['answer_text'],
                first_attempt_correct=request.data['is_correct'],
                first_attempt_timestamp=timezone.now()
            )
```

### 4. Security System (`modules/security/`)

**Current Implementation:**

- Fullscreen enforcement with exit detection
- Keyboard shortcut blocking (F12, Ctrl+Shift+I, etc.)
- Tab switch detection and penalties
- Mouse cursor monitoring
- Window focus tracking
- Comprehensive violation logging

**Django Migration:**

```python
# models.py
class SecurityConfiguration(models.Model):
    enabled = models.BooleanField(default=True)
    fullscreen = models.BooleanField(default=False)
    keyboard = models.BooleanField(default=True)
    tab_switch = models.BooleanField(default=False)
    cursor = models.BooleanField(default=False)
    focus = models.BooleanField(default=False)
    logging = models.BooleanField(default=False)

class SecurityViolation(models.Model):
    VIOLATION_TYPES = [
        ('fullscreen_exit', 'Fullscreen Exit'),
        ('tab_switch', 'Tab Switch'),
        ('keyboard_shortcut', 'Keyboard Shortcut'),
        ('focus_loss', 'Focus Loss'),
        ('cursor_violation', 'Cursor Violation'),
    ]

    quiz_session = models.ForeignKey(QuizSession, on_delete=models.CASCADE)
    violation_type = models.CharField(max_length=20, choices=VIOLATION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField()
    action_taken = models.CharField(max_length=50)  # 'warning', 'restart', 'terminate'

# static/js/security.js - Frontend JavaScript
class SecurityManager {
    constructor(config) {
        this.config = config;
        this.violations = [];
        this.initializeSecurityFeatures();
    }

    initializeSecurityFeatures() {
        if (this.config.fullscreen) {
            this.enforceFullscreen();
        }
        if (this.config.keyboard) {
            this.blockKeyboardShortcuts();
        }
        if (this.config.tab_switch) {
            this.detectTabSwitching();
        }
    }

    enforceFullscreen() {
        document.addEventListener('fullscreenchange', () => {
            if (!document.fullscreenElement) {
                this.reportViolation('fullscreen_exit');
            }
        });
    }

    reportViolation(type, details = {}) {
        fetch('/api/security/violation/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                violation_type: type,
                details: details,
                timestamp: new Date().toISOString()
            })
        });
    }
}
```

### 5. Timer System (`modules/quiz/hooks/useQuizTimer.ts`)

**Current Implementation:**

- Overall quiz timing
- Per-question timing
- Countdown timers for wrong answers
- Formatted time display

**Django Migration:**

```python
# models.py
class QuizTiming(models.Model):
    quiz_session = models.ForeignKey(QuizSession, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

# views.py - WebSocket for real-time timing
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class QuizTimerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # Start timing session

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['action'] == 'question_start':
            await self.start_question_timer(data['question_id'])
        elif data['action'] == 'question_end':
            await self.end_question_timer(data['question_id'])
```

### 6. Result System (`modules/quiz/components/QuizResults.tsx`)

**Current Implementation:**

- Encrypted result downloads using CryptoJS
- Comprehensive analytics including first-click data
- Performance categorization
- Detailed question-by-question breakdown

**Django Migration:**

```python
# models.py
class QuizResult(models.Model):
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    percentage = models.FloatField()
    total_time = models.DurationField()
    completed_at = models.DateTimeField(auto_now_add=True)

# views.py
from cryptography.fernet import Fernet
import json
from django.http import HttpResponse

class DownloadResultsView(View):
    def get(self, request, registration_id):
        # Generate comprehensive results with first-click analytics
        result = self.generate_detailed_results(registration_id)

        # Encrypt results
        key = settings.ENCRYPTION_KEY
        f = Fernet(key)
        encrypted_data = f.encrypt(json.dumps(result).encode())

        response = HttpResponse(encrypted_data, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="quiz_result_{registration_id}_{timezone.now().date()}.enc"'
        return response

    def generate_detailed_results(self, registration_id):
        # Include first-click analytics, timing data, security violations
        attempts = QuestionAttempt.objects.filter(
            quiz_session__registration__registration_id=registration_id
        ).select_related('question')

        detailed_results = []
        for attempt in attempts:
            detailed_results.append({
                'questionId': attempt.question.question_id,
                'question': attempt.question.question_text,
                'selectedAnswer': attempt.selected_answer_text,
                'correctAnswer': attempt.question.get_correct_answer(),
                'isCorrect': attempt.is_correct,
                'timeSpent': str(attempt.time_spent),
                'explanation': attempt.question.explanation,
                # First-click analytics (key feature)
                'firstAttemptAnswer': attempt.first_attempt_text,
                'firstAttemptCorrect': attempt.first_attempt_correct,
                'totalAttempts': attempt.total_attempts,
                'attemptTimestamp': attempt.first_attempt_timestamp.isoformat(),
            })

        return detailed_results
```

## Data Flow Analysis

### Current Data Flow (Next.js)

1. **Registration**: Local state → Registration hook → Phase transition
2. **Quiz State**: Multiple hooks managing state (useQuizState, useQuizTimer, etc.)
3. **Security**: Real-time monitoring with immediate violations
4. **Persistence**: LocalStorage for quiz state, encrypted downloads for results
5. **No Backend**: All data processing happens client-side

### Proposed Django Data Flow

1. **Registration**: Form → Django Model → Session storage
2. **Quiz State**: Database-backed with real-time updates via WebSockets
3. **Security**: Client-side monitoring → Server-side logging → Policy enforcement
4. **Persistence**: Database storage with encrypted export capability
5. **API Endpoints**: RESTful API for all interactions

## Required Django Apps Structure

```
quiz_project/
├── quiz/                    # Core quiz functionality
│   ├── models.py           # Question, QuizSession, QuestionAttempt
│   ├── views.py            # Quiz flow, API endpoints
│   ├── serializers.py      # DRF serializers
│   └── templates/quiz/
├── registration/            # User registration
│   ├── models.py           # Registration model
│   ├── forms.py            # Registration forms
│   └── views.py            # Registration logic
├── security/                # Security monitoring
│   ├── models.py           # SecurityViolation, SecurityConfiguration
│   ├── views.py            # Violation logging
│   └── middleware.py       # Security enforcement
├── analytics/               # Quiz analytics (existing analytics page)
│   ├── models.py           # Analytics data models
│   └── views.py            # Analytics views
└── core/                    # Shared utilities
    ├── utils.py            # Encryption, timing utilities
    └── decorators.py       # Security decorators
```

## Key Migration Challenges & Solutions

### 1. First-Click Tracking System

**Challenge**: Complex client-side state management for tracking true user knowledge vs. final answers.

**Solution**:

- Use AJAX calls to immediately capture first-click data
- Implement database triggers to ensure data integrity
- Maintain separation between first attempt and final answer tracking

### 2. Real-time Security Monitoring

**Challenge**: JavaScript-based security enforcement needs server-side coordination.

**Solution**:

- Keep client-side monitoring for immediate feedback
- Implement server-side violation logging and policy enforcement
- Use WebSockets for real-time security state synchronization

### 3. Local Storage Persistence

**Challenge**: Current system uses localStorage for quiz state persistence.

**Solution**:

- Migrate to database-backed session storage
- Implement auto-save functionality with periodic database updates
- Add recovery mechanisms for interrupted sessions

### 4. Complex State Management

**Challenge**: Multiple React hooks managing interconnected state.

**Solution**:

- Use Django sessions for server-side state management
- Implement Redux-like pattern with Django channels for real-time updates
- Create centralized state management API endpoints

## Migration Steps

### Phase 1: Backend Foundation

1. Set up Django project with required apps
2. Create all database models
3. Implement basic API endpoints
4. Set up authentication and session management

### Phase 2: Core Functionality

1. Migrate registration system
2. Implement quiz engine with first-click tracking
3. Add timing and scoring systems
4. Create result generation and encryption

### Phase 3: Security Integration

1. Implement security monitoring APIs
2. Add violation logging and enforcement
3. Create security configuration management
4. Test security policies

### Phase 4: Frontend Integration

1. Create Django templates
2. Implement JavaScript for client-side interactions
3. Add WebSocket connections for real-time features
4. Integrate security monitoring

### Phase 5: Analytics and Reporting

1. Migrate analytics dashboard
2. Implement comprehensive reporting
3. Add data export capabilities
4. Create admin interfaces

## Database Schema

```sql
-- Core Tables
CREATE TABLE registrations (
    id SERIAL PRIMARY KEY,
    registration_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(254),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_key VARCHAR(40)
);

CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    question_id INTEGER UNIQUE NOT NULL,
    question_text TEXT NOT NULL,
    explanation TEXT
);

CREATE TABLE question_options (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES questions(id),
    option_text TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    explanation TEXT
);

CREATE TABLE quiz_sessions (
    id SERIAL PRIMARY KEY,
    registration_id INTEGER REFERENCES registrations(id),
    shuffled_questions JSONB,
    current_question INTEGER DEFAULT 0,
    quiz_start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed BOOLEAN DEFAULT FALSE
);

-- Critical: First-click tracking table
CREATE TABLE question_attempts (
    id SERIAL PRIMARY KEY,
    quiz_session_id INTEGER REFERENCES quiz_sessions(id),
    question_id INTEGER REFERENCES questions(id),

    -- First-click analytics (key feature)
    first_attempt_answer INTEGER NOT NULL,
    first_attempt_text TEXT NOT NULL,
    first_attempt_correct BOOLEAN NOT NULL,
    first_attempt_timestamp TIMESTAMP NOT NULL,

    -- Final answer data
    selected_answer INTEGER,
    selected_answer_text TEXT,
    is_correct BOOLEAN,
    total_attempts INTEGER DEFAULT 1,
    time_spent INTERVAL
);

CREATE TABLE security_violations (
    id SERIAL PRIMARY KEY,
    quiz_session_id INTEGER REFERENCES quiz_sessions(id),
    violation_type VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB,
    action_taken VARCHAR(50)
);
```

## Configuration Files

### settings.py

```python
# Quiz-specific settings
QUIZ_SECURITY_CONFIG = {
    'enabled': True,
    'fullscreen': False,
    'keyboard': True,
    'tab_switch': False,
    'cursor': False,
    'focus': False,
    'logging': False,
}

ENCRYPTION_KEY = env('QUIZ_ENCRYPTION_KEY')  # For result encryption
QUIZ_SESSION_TIMEOUT = 3600  # 1 hour

# WebSocket settings for real-time features
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

## Critical Features to Preserve

1. **First-Click Tracking**: Essential for measuring true student knowledge
2. **Question/Option Shuffling**: Prevents answer pattern memorization
3. **Comprehensive Timing**: Question-level and overall timing analytics
4. **Security Monitoring**: Multi-layered security enforcement
5. **Encrypted Results**: Secure result storage and transmission
6. **Session Persistence**: Recovery from interruptions
7. **Real-time Feedback**: Immediate answer validation and progression

## Testing Strategy

1. **Unit Tests**: Test all models, views, and utilities
2. **Integration Tests**: Test complete quiz flow
3. **Security Tests**: Verify security enforcement
4. **Performance Tests**: Ensure real-time capabilities
5. **Migration Tests**: Verify data integrity during migration

This migration guide preserves all critical functionality while providing a robust, scalable Django backend that can handle the complex requirements of the secure quiz platform.
