from django.urls import path
from . import views
urlpatterns = [
    path('tts/synthesize', views.synthesize, name='synthesize'),
    path('api/metadata', views.metadata, name='metadata'),
]
