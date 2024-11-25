from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Currency, ExchangeRate, RateAlert
from .serializers import (CurrencySerializer, ExchangeRateSerializer, 
                         RateAlertSerializer)
from .tasks import broadcast_rates

class ExchangeRateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ExchangeRate.objects.select_related(
            'from_currency', 'to_currency'
        ).all()
        
        from_currency = self.request.query_params.get('from', None)
        to_currency = self.request.query_params.get('to', None)
        
        if from_currency:
            queryset = queryset.filter(from_currency__code=from_currency.upper())
        if to_currency:
            queryset = queryset.filter(to_currency__code=to_currency.upper())
            
        return queryset

    @action(detail=False)
    def latest(self, request):
        """Obtenir les derniers taux de change"""
        rates = self.get_queryset()
        serializer = self.get_serializer(rates, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def convert(self, request):
        """Convertir un montant entre deux devises"""
        from_currency = request.query_params.get('from')
        to_currency = request.query_params.get('to')
        amount = request.query_params.get('amount')
        
        if not all([from_currency, to_currency, amount]):
            return Response(
                {'error': 'Missing parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            amount = float(amount)
            rate = ExchangeRate.get_rate(from_currency.upper(), to_currency.upper())
            
            if rate is None:
                return Response(
                    {'error': 'Rate not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            converted_amount = amount * float(rate)
            return Response({
                'from': from_currency.upper(),
                'to': to_currency.upper(),
                'amount': amount,
                'rate': float(rate),
                'result': converted_amount
            })
        except ValueError:
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )

class RateAlertViewSet(viewsets.ModelViewSet):
    serializer_class = RateAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RateAlert.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 