from django.contrib import admin
from .models import GenerationHistory, PerformanceMetrics


@admin.register(GenerationHistory)
class GenerationHistoryAdmin(admin.ModelAdmin):
    list_display = ['prompt_preview', 'access_count', 'generation_time', 'created_at', 'last_accessed']
    list_filter = ['created_at', 'last_accessed']
    search_fields = ['prompt', 'prompt_hash']
    readonly_fields = ['prompt_hash', 'created_at', 'last_accessed']
    ordering = ['-access_count', '-created_at']
    
    def prompt_preview(self, obj):
        return obj.prompt[:50] + '...' if len(obj.prompt) > 50 else obj.prompt
    prompt_preview.short_description = 'Prompt'


@admin.register(PerformanceMetrics)
class PerformanceMetricsAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'cache_hit', 'response_time', 'generation_time', 'prompt_length']
    list_filter = ['cache_hit', 'timestamp']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        return False  # Metrics are auto-generated
