from django.urls import path
from .views.query_view import VoiceQueryView

urlpatterns = [
    path('query/', VoiceQueryView.as_view(), name='voice_query'),
]
