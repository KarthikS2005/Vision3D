from django.db import models
from django.utils import timezone


class GenerationHistory(models.Model):
    """
    Model to track 3D model generation history and enable caching.
    """
    prompt = models.TextField(help_text="Text prompt used for generation")
    prompt_hash = models.CharField(max_length=64, unique=True, db_index=True, 
                                   help_text="SHA256 hash of the prompt for fast lookup")
    model_file = models.CharField(max_length=255, help_text="Path to generated GLB file")
    generation_time = models.FloatField(help_text="Time taken to generate in seconds")
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    access_count = models.IntegerField(default=1, help_text="Number of times this model was accessed")
    last_accessed = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Generation History'
        verbose_name_plural = 'Generation Histories'
        indexes = [
            models.Index(fields=['prompt_hash']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['-access_count']),
        ]
    
    def __str__(self):
        return f"{self.prompt[:50]}... ({self.access_count} accesses)"
    
    def increment_access(self):
        """Increment access count and update last accessed time."""
        self.access_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['access_count', 'last_accessed'])


class PerformanceMetrics(models.Model):
    """
    Model to track performance metrics for optimization analysis.
    """
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    cache_hit = models.BooleanField(default=False)
    response_time = models.FloatField(help_text="Total response time in seconds")
    generation_time = models.FloatField(null=True, blank=True, 
                                       help_text="Model generation time if not cached")
    prompt_length = models.IntegerField()
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Performance Metric'
        verbose_name_plural = 'Performance Metrics'
    
    def __str__(self):
        cache_status = "HIT" if self.cache_hit else "MISS"
        return f"{cache_status} - {self.response_time:.2f}s at {self.timestamp}"
