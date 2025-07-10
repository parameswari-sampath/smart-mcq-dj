from django.contrib import admin
from .models import Test


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'get_question_count', 'time_limit_minutes', 'organization', 'created_by', 'created_at', 'is_active']
    list_filter = ['category', 'time_limit_minutes', 'organization', 'is_active']
    search_fields = ['title', 'description', 'category']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['questions']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).filter(is_active=True)
        if not request.user.is_superuser:
            qs = qs.filter(created_by=request.user)
        return qs
