from django.urls import path
from . import views
urlpatterns = [
    path('api/text-to-speech', views.synthesize, name='synthesize'),
    path('api/metadata', views.metadata, name='metadata'),
]
