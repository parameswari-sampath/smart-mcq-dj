from django.db import models
from django.contrib.auth.models import User
from accounts.models import Organization


class Question(models.Model):
    """Question model for MCQ tests"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    title = models.CharField(max_length=500)
    description = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    image = models.ImageField(upload_to='questions/', blank=True, null=True)
    
    # Multi-tenant and tracking fields
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title[:100]
    
    class Meta:
        ordering = ['-created_at']


class Choice(models.Model):
    """Answer choices for questions (A, B, C, D)"""
    CHOICE_LABELS = [
        ('A', 'A'),
        ('B', 'B'), 
        ('C', 'C'),
        ('D', 'D'),
    ]
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    label = models.CharField(max_length=1, choices=CHOICE_LABELS)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.question.title[:50]} - {self.label}: {self.text[:50]}"
    
    class Meta:
        ordering = ['label']
        unique_together = ['question', 'label']
