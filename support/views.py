from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import SupportTicket
from .serializers import SupportTicketSerializer
from django.core.mail import send_mail

class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        ticket = serializer.save(user=self.request.user)
        # Remplacer notify par une notification simple
        if hasattr(ticket, 'user') and ticket.user.email:
            send_mail(
                'Support Ticket Created',
                f'Your ticket #{ticket.id} has been created.',
                'noreply@cryptoexchange.com',
                [ticket.user.email],
                fail_silently=True,
            ) 