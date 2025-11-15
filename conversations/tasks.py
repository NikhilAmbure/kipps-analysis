from celery import shared_task
from .models import Conversation, ConversationAnalysis
from .analysis_logic import analyze_conversations


@shared_task
def daily_analyse():
    conversations = Conversation.objects.all()

    for convo in conversations:
        if not hasattr(convo, "analysis"):  # avoiding duplicate analysis
            result = analyze_conversations(convo)
            ConversationAnalysis.objects.create(
                conversation=convo,
                **result
            )

    return "Daily analysis completed"
