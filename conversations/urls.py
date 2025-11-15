from django.urls import path
from .views import (
    UploadConversationView,
    AnalyseConversationView,
    ConversationAnalysisListView
)

urlpatterns = [
    path("conversations/", UploadConversationView.as_view()),
    path("analyse/<int:conversation_id>/", AnalyseConversationView.as_view()),
    path("reports/", ConversationAnalysisListView.as_view()),
]