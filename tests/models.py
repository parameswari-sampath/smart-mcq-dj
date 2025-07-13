from django.db import models
from django.contrib.auth.models import User
from accounts.models import Organization
from questions.models import Question
from smart_mcq.constants import ResultReleaseModes, AnswerVisibilityLevels, TestTypes


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
    
    # v1.4.1: Result Release Control fields
    result_release_mode = models.CharField(
        max_length=20,
        choices=ResultReleaseModes.RELEASE_MODE_CHOICES,
        default=ResultReleaseModes.DEFAULT_MODE,
        help_text="Controls when results are released to students"
    )
    answer_visibility_level = models.CharField(
        max_length=20,
        choices=AnswerVisibilityLevels.VISIBILITY_CHOICES,
        default=AnswerVisibilityLevels.DEFAULT_LEVEL,
        help_text="Controls what students see in their results"
    )
    is_practice_test = models.BooleanField(
        default=True,
        help_text="Practice tests auto-release, assessments require manual review"
    )
    scheduled_release_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When to automatically release results (for scheduled mode)"
    )

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
