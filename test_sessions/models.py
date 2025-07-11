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
