"""
URL configuration for generator app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_model, name='generate_model'),
    path('stats/', views.performance_stats, name='performance_stats'),
    path('health/', views.health_check, name='health_check'),
]
