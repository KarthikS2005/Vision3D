"""
Optimization utilities for 3D model generation.
Includes caching, hash-based deduplication, and performance monitoring.
"""

import hashlib
import time
import trimesh
import numpy as np
from pathlib import Path
from django.conf import settings
from django.core.cache import cache
from .models import GenerationHistory, PerformanceMetrics


class ModelCache:
    """
    LRU-style cache manager for 3D models with hash-based lookup.
    """
    
    @staticmethod
    def get_prompt_hash(prompt: str) -> str:
        """Generate SHA256 hash of normalized prompt."""
        normalized = prompt.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    @staticmethod
    def get_cached_model(prompt: str):
        """
        Check if model exists in cache or database.
        Returns (model_path, cached: bool, generation_time: float) or None.
        """
        prompt_hash = ModelCache.get_prompt_hash(prompt)
        
        # First check Django cache (fastest)
        cache_key = f"model_{prompt_hash}"
        cached_data = cache.get(cache_key)
        if cached_data:
            # Update access count in background
            try:
                history = GenerationHistory.objects.get(prompt_hash=prompt_hash)
                history.increment_access()
            except GenerationHistory.DoesNotExist:
                pass
            return cached_data['model_path'], True, cached_data['generation_time']
        
        # Check database
        try:
            history = GenerationHistory.objects.get(prompt_hash=prompt_hash)
            history.increment_access()
            
            # Store in cache for next time
            cache_data = {
                'model_path': history.model_file,
                'generation_time': history.generation_time
            }
            cache.set(cache_key, cache_data, timeout=settings.CACHE_TIMEOUT)
            
            return history.model_file, True, history.generation_time
        except GenerationHistory.DoesNotExist:
            return None
    
    @staticmethod
    def store_model(prompt: str, model_path: str, generation_time: float):
        """Store generated model in cache and database."""
        prompt_hash = ModelCache.get_prompt_hash(prompt)
        
        # Store in database
        history, created = GenerationHistory.objects.update_or_create(
            prompt_hash=prompt_hash,
            defaults={
                'prompt': prompt,
                'model_file': model_path,
                'generation_time': generation_time,
            }
        )
        
        # Store in cache
        cache_key = f"model_{prompt_hash}"
        cache_data = {
            'model_path': model_path,
            'generation_time': generation_time
        }
        cache.set(cache_key, cache_data, timeout=settings.CACHE_TIMEOUT)


class ModelGenerator:
    """
    Optimized 3D model generator with various geometric primitives.
    """
    
    @staticmethod
    def generate_from_prompt(prompt: str) -> tuple[str, float]:
        """
        Generate a 3D model based on text prompt.
        Returns (model_path, generation_time).
        
        This is a simplified implementation. In production, you would integrate
        with actual AI models like Shap-E, Point-E, or other text-to-3D systems.
        """
        start_time = time.time()
        
        # Create generated directory if it doesn't exist
        generated_dir = Path(settings.MEDIA_ROOT)
        generated_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        prompt_hash = ModelCache.get_prompt_hash(prompt)
        filename = f"model_{prompt_hash[:12]}.glb"
        filepath = generated_dir / filename
        
        # Generate 3D mesh based on prompt keywords
        mesh = ModelGenerator._create_mesh_from_prompt(prompt)
        
        # Export to GLB format
        mesh.export(str(filepath))
        
        generation_time = time.time() - start_time
        
        return str(filename), generation_time
    
    @staticmethod
    def _create_mesh_from_prompt(prompt: str) -> trimesh.Trimesh:
        """
        Create a 3D mesh based on prompt analysis.
        This is a simplified version - in production, use actual AI models.
        """
        prompt_lower = prompt.lower()
        
        # Determine shape based on keywords
        if any(word in prompt_lower for word in ['cube', 'box', 'block']):
            mesh = trimesh.creation.box(extents=[2, 2, 2])
        elif any(word in prompt_lower for word in ['sphere', 'ball', 'globe']):
            mesh = trimesh.creation.icosphere(subdivisions=3, radius=1.0)
        elif any(word in prompt_lower for word in ['cylinder', 'tube', 'pipe']):
            mesh = trimesh.creation.cylinder(radius=0.5, height=2.0)
        elif any(word in prompt_lower for word in ['cone', 'pyramid']):
            mesh = trimesh.creation.cone(radius=1.0, height=2.0)
        elif any(word in prompt_lower for word in ['torus', 'donut', 'ring']):
            mesh = trimesh.creation.torus(major_radius=1.0, minor_radius=0.3)
        elif any(word in prompt_lower for word in ['dragon', 'creature', 'animal']):
            # Create a more complex shape for creatures
            mesh = ModelGenerator._create_dragon_like_mesh()
        else:
            # Default to a stylized shape
            mesh = trimesh.creation.icosphere(subdivisions=2, radius=1.0)
        
        # Apply color based on prompt
        color = ModelGenerator._extract_color_from_prompt(prompt_lower)
        mesh.visual.vertex_colors = color
        
        return mesh
    
    @staticmethod
    def _create_dragon_like_mesh() -> trimesh.Trimesh:
        """Create a dragon-like mesh using multiple primitives."""
        # Body
        body = trimesh.creation.capsule(height=2.0, radius=0.5)
        
        # Head
        head = trimesh.creation.icosphere(subdivisions=2, radius=0.6)
        head.apply_translation([0, 0, 1.5])
        
        # Tail
        tail = trimesh.creation.cone(radius=0.3, height=1.5)
        tail.apply_translation([0, 0, -1.5])
        
        # Combine meshes
        combined = trimesh.util.concatenate([body, head, tail])
        return combined
    
    @staticmethod
    def _extract_color_from_prompt(prompt: str) -> list:
        """Extract color from prompt or return default."""
        color_map = {
            'red': [255, 0, 0, 255],
            'blue': [0, 0, 255, 255],
            'green': [0, 255, 0, 255],
            'yellow': [255, 255, 0, 255],
            'purple': [128, 0, 128, 255],
            'orange': [255, 165, 0, 255],
            'pink': [255, 192, 203, 255],
            'white': [255, 255, 255, 255],
            'black': [0, 0, 0, 255],
            'gray': [128, 128, 128, 255],
            'gold': [255, 215, 0, 255],
            'silver': [192, 192, 192, 255],
        }
        
        for color_name, color_value in color_map.items():
            if color_name in prompt:
                return color_value
        
        # Default color (light blue)
        return [100, 150, 255, 255]


class PerformanceMonitor:
    """
    Monitor and log performance metrics for optimization analysis.
    """
    
    @staticmethod
    def log_request(cache_hit: bool, response_time: float, 
                   generation_time: float = None, prompt_length: int = 0):
        """Log performance metrics for a request."""
        PerformanceMetrics.objects.create(
            cache_hit=cache_hit,
            response_time=response_time,
            generation_time=generation_time,
            prompt_length=prompt_length
        )
    
    @staticmethod
    def get_cache_hit_rate(days: int = 7) -> float:
        """Calculate cache hit rate for the last N days."""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff = timezone.now() - timedelta(days=days)
        metrics = PerformanceMetrics.objects.filter(timestamp__gte=cutoff)
        
        total = metrics.count()
        if total == 0:
            return 0.0
        
        hits = metrics.filter(cache_hit=True).count()
        return (hits / total) * 100
    
    @staticmethod
    def get_average_response_time(days: int = 7) -> dict:
        """Get average response times for cached vs non-cached requests."""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Avg
        
        cutoff = timezone.now() - timedelta(days=days)
        metrics = PerformanceMetrics.objects.filter(timestamp__gte=cutoff)
        
        cached = metrics.filter(cache_hit=True).aggregate(Avg('response_time'))
        non_cached = metrics.filter(cache_hit=False).aggregate(Avg('response_time'))
        
        return {
            'cached_avg': cached['response_time__avg'] or 0,
            'non_cached_avg': non_cached['response_time__avg'] or 0,
        }
