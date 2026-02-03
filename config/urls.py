"""
URL configuration for Django text-to-speech starter.
"""
from django.urls import path, include

urlpatterns = [
    path('', include('starter.urls')),
]
