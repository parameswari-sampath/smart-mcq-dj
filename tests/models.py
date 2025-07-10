from django.db import models
from django.contrib.auth.models import User
from accounts.models import Organization
from questions.models import Question


class Test(models.Model):
    """Test model for assembling questions into tests"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    time_limit_minutes = models.PositiveIntegerField(default=60)
    category = models.CharField(max_length=100, blank=True)
    questions = models.ManyToManyField(Question, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_question_count(self):
        """Return the number of questions in this test"""
        return self.questions.count()

    def get_total_marks(self):
        """Return total marks for this test (1 mark per question)"""
        return self.get_question_count()
