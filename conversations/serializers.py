from rest_framework import serializers
from .models import Conversation, Message, ConversationAnalysis


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'timestamp']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'messages']


class ConversationAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationAnalysis
        fields = '__all__'


# uploading a JSON conversation
class ConversationUploadSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    messages = serializers.ListField()

    def create(self, validated_data):
        title = validated_data.get("title", "Untitled Conversation")
        messages_data = validated_data["messages"]

        conversation = Conversation.objects.create(title=title)

        for msg in messages_data:
            Message.objects.create(
                conversation=conversation,
                sender=msg.get("sender"),
                text=msg.get("message")
            )

        return conversation
        