from rest_framework import serializers
from .models import SupportTicket, TicketResponse, SupportAttachment

class SupportAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportAttachment
        fields = ['id', 'file', 'file_name', 'uploaded_at']
        read_only_fields = ['uploaded_at']

class TicketResponseSerializer(serializers.ModelSerializer):
    responder_name = serializers.CharField(source='responder.username', read_only=True)
    
    class Meta:
        model = TicketResponse
        fields = ['id', 'message', 'responder_name', 'is_staff_response', 
                 'created_at', 'attachment']
        read_only_fields = ['is_staff_response', 'created_at']

class SupportTicketSerializer(serializers.ModelSerializer):
    responses = TicketResponseSerializer(many=True, read_only=True)
    attachments = SupportAttachmentSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = SupportTicket
        fields = ['id', 'subject', 'message', 'category', 'priority', 
                 'status', 'created_at', 'updated_at', 'resolved_at', 
                 'responses', 'attachments', 'user_email']
        read_only_fields = ['status', 'created_at', 'updated_at', 'resolved_at'] 