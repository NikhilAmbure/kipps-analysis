from django.db import models


class Conversation(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title or f"conversations {self.id}"
    
    
class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=20) 
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True) # for response time cal
    
    def __str__(self):
        return f"{self.sender}: {self.text[:30]}"
    
    
class ConversationAnalysis(models.Model):
    conversation = models.OneToOneField(Conversation,on_delete=models.CASCADE, related_name="analysis")
    clarity_score = models.FloatField()
    relevance_score = models.FloatField()
    accuracy_score = models.FloatField()
    completeness_score = models.FloatField()
    sentiment = models.CharField(max_length=20)
    empathy_score = models.FloatField()
    resolution = models.BooleanField(default=False)
    escalation_needed = models.BooleanField(default=False)
    fallback_count = models.IntegerField(default=0)
    average_response_time = models.FloatField(default=0, null=True, blank=False)
    
    overall_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Analysis for conversation {self.conversation.id}"
    