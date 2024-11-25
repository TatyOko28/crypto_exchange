from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from .models import Wallet, WalletTransaction, WalletTransfer
from .serializers import (WalletSerializer, WalletTransactionSerializer,
                         WalletTransferSerializer, TransactionHistorySerializer)

# Create your views here.

class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):
        wallet = self.get_object()
        amount = request.data.get('amount')
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
                
            with transaction.atomic():
                wallet_transaction = WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='DEPOSIT',
                    amount=amount
                )
                wallet.deposit(amount)
                
            return Response({
                'message': 'Deposit successful',
                'transaction_id': wallet_transaction.id
            })
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        wallet = self.get_object()
        amount = request.data.get('amount')
        security_code = request.data.get('security_code')
        
        if not request.user.check_security_code(security_code):
            return Response(
                {'error': 'Invalid security code'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
                
            with transaction.atomic():
                wallet_transaction = WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='WITHDRAWAL',
                    amount=amount
                )
                wallet.withdraw(amount)
                
            return Response({
                'message': 'Withdrawal successful',
                'transaction_id': wallet_transaction.id
            })
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def transactions(self, request):
        wallet = self.get_queryset().first()
        transactions = WalletTransaction.objects.filter(wallet=wallet)
        
        # Filtrer par type si spécifié
        transaction_type = request.query_params.get('type')
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type.upper())
            
        serializer = TransactionHistorySerializer(transactions, many=True)
        return Response(serializer.data)

class WalletTransferViewSet(viewsets.ModelViewSet):
    serializer_class = WalletTransferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WalletTransfer.objects.filter(
            from_wallet__user=self.request.user
        ) | WalletTransfer.objects.filter(
            to_wallet__user=self.request.user
        )

    def perform_create(self, serializer):
        transfer = serializer.save()
        if transfer.security_code_verified:
            transfer.execute_transfer()

class WalletTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WalletTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WalletTransaction.objects.filter(
            wallet__user=self.request.user
        ).order_by('-timestamp')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context
