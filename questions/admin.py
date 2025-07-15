from django.contrib import admin
from .models import Question, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0
    min_num = 4
    max_num = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'created_by', 'created_at', 'is_active']
    list_filter = ['difficulty', 'category', 'is_active']
    search_fields = ['title', 'description', 'category']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ChoiceInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).filter(is_active=True)
        if not request.user.is_superuser:
            qs = qs.filter(created_by=request.user)
        return qs


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['question', 'label', 'text', 'is_correct']
    list_filter = ['label', 'is_correct']
    search_fields = ['question__title', 'text']
