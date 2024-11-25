from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from .models import Order, Transaction
from .serializers import (OrderSerializer, TransactionSerializer, 
                         SecurityCodeConfirmationSerializer)
#from notifications.signals import notify

# Create your views here.

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les ordres actifs"""
        queryset = Order.objects.filter(status='ACTIVE')
        order_type = self.request.query_params.get('type', None)
        if order_type:
            queryset = queryset.filter(order_type=order_type.upper())
        return queryset
    
    def perform_create(self, serializer):
        """Créer un nouvel ordre"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['put'])
    def execute(self, request, pk=None):
        """Exécuter une transaction"""
        order = self.get_object()
        if order.status != 'ACTIVE':
            return Response(
                {'error': 'Order is not active'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Créer la transaction
            transaction_obj = Transaction.objects.create(
                order=order,
                buyer=request.user if order.order_type == 'SELL' else order.user,
                seller=order.user if order.order_type == 'SELL' else request.user,
                amount=order.amount,
                price=order.price
            )
            
            # Mettre à jour le statut de l'ordre
            order.status = 'PENDING'
            order.save()

            return Response({
                'status': 'transaction initiated',
                'transaction_id': transaction_obj.id
            })

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Obtenir les transactions de l'utilisateur"""
        return Transaction.objects.filter(
            buyer=self.request.user
        ) | Transaction.objects.filter(
            seller=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        transaction = self.get_object()
        serializer = SecurityCodeConfirmationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                transaction.validate_security_codes(
                    request.user,
                    serializer.validated_data['security_code']
                )
                
                # Notifier l'autre partie
                other_user = (transaction.seller if request.user == transaction.buyer 
                            else transaction.buyer)
                notify.send(
                    sender=request.user,
                    recipient=other_user,
                    verb='confirmed transaction',
                    action_object=transaction,
                    description=f'Transaction #{transaction.id} has been confirmed'
                )
                
                return Response({'status': 'confirmation successful'})
            except ValidationError as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
