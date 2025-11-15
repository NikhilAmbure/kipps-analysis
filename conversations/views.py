from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    ConversationUploadSerializer,
    ConversationSerializer,
    ConversationAnalysisSerializer
)
from .models import *
from .analysis_logic import analyze_conversations 


class UploadConversationView(APIView):
    
    def post(self, request):
        serializer = ConversationUploadSerializer(data=request.data)
        if serializer.is_valid():
            conversation = serializer.save()
            return Response(
                {"message": "Conversation uploaded", "conversation_id": conversation.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AnalyseConversationView(APIView):
    def post(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found"}, status=404)

        # Avoiding duplicate analysis
        if hasattr(conversation, "analysis"):
            return Response({"message": "Already analysed"}, status=400)

        # Performing analysis using logic function
        result = analyze_conversations(conversation)

        
        analysis = ConversationAnalysis.objects.create(
            conversation=conversation,
            **result
        )

        return Response(ConversationAnalysisSerializer(analysis).data, status=201)



class ConversationAnalysisListView(ListAPIView):
    queryset = ConversationAnalysis.objects.all()
    serializer_class = ConversationAnalysisSerializer