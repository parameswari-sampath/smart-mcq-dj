from django.contrib import admin
from .models import TestSession, StudentTestAttempt, TestAttempt, Answer


@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ('test', 'access_code', 'start_time', 'end_time', 'status', 'created_by', 'is_active')
    list_filter = ('is_active', 'start_time', 'created_by')
    search_fields = ('test__title', 'access_code', 'created_by__username')
    readonly_fields = ('access_code', 'created_at', 'updated_at', 'end_time')
    ordering = ('-start_time',)
    
    fieldsets = (
        (None, {
            'fields': ('test', 'access_code', 'start_time', 'created_by', 'is_active')
        }),
        ('Calculated Fields', {
            'fields': ('end_time',),
            'description': 'End time is automatically calculated based on start time + test duration'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filter by created_by for non-superusers
        return qs.filter(created_by=request.user)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "test" and not request.user.is_superuser:
            # Only show tests created by the current user
            kwargs["queryset"] = db_field.related_model.objects.filter(created_by=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(StudentTestAttempt)
class StudentTestAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'test_session', 'joined_at', 'is_completed']
    list_filter = ['joined_at', 'is_completed']
    search_fields = ['student__username', 'test_session__test__title', 'test_session__access_code']
    readonly_fields = ['joined_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # For teachers, show attempts for their test sessions
        return qs.filter(test_session__created_by=request.user)


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'test_session', 'current_question_index', 'progress_percentage', 'started_at', 'is_submitted']
    list_filter = ['is_submitted', 'started_at']
    search_fields = ['student_test_attempt__student__username', 'student_test_attempt__test_session__test__title']
    readonly_fields = ['started_at', 'submitted_at', 'progress_percentage']
    
    def student(self, obj):
        return obj.student.username
    
    def test_session(self, obj):
        return obj.test_session.test.title
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # For teachers, show attempts for their test sessions
        return qs.filter(student_test_attempt__test_session__created_by=request.user)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['student', 'question_title', 'selected_choice', 'is_correct', 'answered_at']
    list_filter = ['is_correct', 'selected_choice', 'answered_at']
    search_fields = ['test_attempt__student_test_attempt__student__username', 'question__title']
    readonly_fields = ['is_correct', 'answered_at']
    
    def student(self, obj):
        return obj.test_attempt.student.username
    
    def question_title(self, obj):
        return obj.question.title
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # For teachers, show answers for their test sessions
        return qs.filter(test_attempt__student_test_attempt__test_session__created_by=request.user)
