from rest_framework import serializers
from .models import Currency, ExchangeRate, RateAlert

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['code', 'name', 'is_crypto']

class ExchangeRateSerializer(serializers.ModelSerializer):
    from_currency = CurrencySerializer(read_only=True)
    to_currency = CurrencySerializer(read_only=True)
    
    class Meta:
        model = ExchangeRate
        fields = ['from_currency', 'to_currency', 'rate', 'last_updated']

class RateAlertSerializer(serializers.ModelSerializer):
    from_currency = serializers.SlugRelatedField(slug_field='code', queryset=Currency.objects.all())
    to_currency = serializers.SlugRelatedField(slug_field='code', queryset=Currency.objects.all())
    
    class Meta:
        model = RateAlert
        fields = ['id', 'from_currency', 'to_currency', 'condition', 
                 'target_rate', 'is_active', 'created_at']
        read_only_fields = ['created_at'] 