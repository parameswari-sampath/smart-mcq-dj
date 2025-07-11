import secrets
import string
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from tests.models import Test


def generate_access_code():
    """Generate a unique 6-digit alphanumeric access code"""
    while True:
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        if not TestSession.objects.filter(access_code=code, is_active=True).exists():
            return code


class TestSession(models.Model):
    """Test session model for scheduling tests with access codes"""
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='sessions')
    access_code = models.CharField(max_length=6, default=generate_access_code, unique=True)
    start_time = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.test.title} - {self.access_code}"

    @property
    def end_time(self):
        """Calculate end time based on start time + test duration"""
        return self.start_time + timedelta(minutes=self.test.time_limit_minutes)

    @property
    def is_expired(self):
        """Check if the session has expired"""
        return timezone.now() > self.end_time

    @property
    def is_active_session(self):
        """Check if session is currently active (started but not expired)"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    @property
    def is_upcoming(self):
        """Check if session is scheduled for the future"""
        return timezone.now() < self.start_time

    @property
    def status(self):
        """Get current session status"""
        if not self.is_active:
            return 'cancelled'
        elif self.is_expired:
            return 'expired'
        elif self.is_active_session:
            return 'active'
        elif self.is_upcoming:
            return 'upcoming'
        else:
            return 'unknown'

    def save(self, *args, **kwargs):
        # Ensure access code is unique
        if not self.access_code:
            self.access_code = generate_access_code()
        super().save(*args, **kwargs)


class StudentTestAttempt(models.Model):
    """Track student attempts to join test sessions"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    test_session = models.ForeignKey(TestSession, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['student', 'test_session']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.test_session.test.title}"


class TestAttempt(models.Model):
    """Track detailed test attempt progress and state"""
    student_test_attempt = models.OneToOneField(StudentTestAttempt, on_delete=models.CASCADE, related_name='attempt_detail')
    current_question_index = models.IntegerField(default=0)  # 0-based index
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_submitted = models.BooleanField(default=False)
    total_time_spent = models.IntegerField(default=0)  # in seconds
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.student_test_attempt.student.username} - {self.student_test_attempt.test_session.test.title} - Attempt"
    
    @property
    def student(self):
        return self.student_test_attempt.student
    
    @property
    def test_session(self):
        return self.student_test_attempt.test_session
    
    @property
    def test(self):
        return self.test_session.test
    
    @property
    def questions(self):
        return self.test.questions.all()
    
    @property
    def total_questions(self):
        return self.questions.count()
    
    @property
    def current_question(self):
        questions = list(self.questions)
        if 0 <= self.current_question_index < len(questions):
            return questions[self.current_question_index]
        return None
    
    @property
    def progress_percentage(self):
        if self.total_questions == 0:
            return 0
        answered_count = self.answers.count()
        return round((answered_count / self.total_questions) * 100)
    
    @property
    def is_last_question(self):
        return self.current_question_index >= self.total_questions - 1
    
    @property
    def is_first_question(self):
        return self.current_question_index <= 0


class Answer(models.Model):
    """Store individual question answers for test attempts"""
    test_attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('questions.Question', on_delete=models.CASCADE)
    selected_choice = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now=True)
    time_spent_seconds = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['test_attempt', 'question']
        ordering = ['answered_at']
    
    def __str__(self):
        return f"{self.test_attempt.student.username} - Q{self.question.id} - {self.selected_choice}"
    
    def save(self, *args, **kwargs):
        # Automatically determine if answer is correct
        correct_choice = self.question.choices.filter(is_correct=True).first()
        if correct_choice:
            self.is_correct = (self.selected_choice == correct_choice.label)
        super().save(*args, **kwargs)
