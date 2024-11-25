from celery import shared_task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import requests
import logging
from .models import Currency, ExchangeRate, RateAlert


logger = logging.getLogger(__name__)

@shared_task
def update_exchange_rates():
    """Mise à jour des taux de change depuis différentes APIs"""
    try:
        # Mise à jour des cryptomonnaies
        update_crypto_rates()
        # Mise à jour des devises traditionnelles
        update_fiat_rates()
        # Vérifier les alertes
        check_rate_alerts()
    except Exception as e:
        logger.error(f"Error updating exchange rates: {str(e)}")

def update_crypto_rates():
    """Mise à jour des taux crypto depuis CoinGecko"""
    crypto_currencies = Currency.objects.filter(is_crypto=True, is_active=True)
    
    for crypto in crypto_currencies:
        try:
            response = requests.get(
                f"https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids": crypto.code.lower(),
                    "vs_currencies": "usd,eur"
                }
            )
            data = response.json()
            
            # Mettre à jour les taux
            for fiat, rate in data[crypto.code.lower()].items():
                fiat_currency = Currency.objects.get(code=fiat.upper())
                ExchangeRate.objects.update_or_create(
                    from_currency=crypto,
                    to_currency=fiat_currency,
                    defaults={'rate': rate, 'source': 'coingecko'}
                )
        except Exception as e:
            logger.error(f"Error updating {crypto.code} rates: {str(e)}")

def update_fiat_rates():
    """Mise à jour des taux de change fiat depuis Exchange Rates API"""
    try:
        response = requests.get(
            "https://api.exchangeratesapi.io/latest",
            params={"base": "USD"}
        )
        data = response.json()
        
        usd = Currency.objects.get(code='USD')
        for currency_code, rate in data['rates'].items():
            try:
                currency = Currency.objects.get(code=currency_code)
                ExchangeRate.objects.update_or_create(
                    from_currency=usd,
                    to_currency=currency,
                    defaults={'rate': rate, 'source': 'exchangerates'}
                )
            except Currency.DoesNotExist:
                continue
    except Exception as e:
        logger.error(f"Error updating fiat rates: {str(e)}")

@shared_task
def check_rate_alerts():
    """Vérifier les alertes de taux et notifier les utilisateurs"""
    alerts = RateAlert.objects.filter(is_active=True, triggered_at__isnull=True)
    
    for alert in alerts:
        current_rate = ExchangeRate.get_rate(
            alert.from_currency.code,
            alert.to_currency.code
        )
        
        if current_rate is None:
            continue
            
        should_trigger = (
            (alert.condition == 'ABOVE' and current_rate >= alert.target_rate) or
            (alert.condition == 'BELOW' and current_rate <= alert.target_rate)
        )
        
        if should_trigger:
            alert.triggered_at = timezone.now()
            alert.is_active = False
            alert.save()
            
            # Notifier l'utilisateur
            notify.send(
                sender=alert,
                recipient=alert.user,
                verb='rate_alert_triggered',
                description=f"Rate alert triggered for {alert.from_currency.code}/{alert.to_currency.code}"
            )

@shared_task
def broadcast_rates():
    """Diffuser les taux de change via WebSocket"""
    channel_layer = get_channel_layer()
    rates = ExchangeRate.objects.select_related('from_currency', 'to_currency').all()
    
    rates_data = {
        f"{rate.from_currency.code}/{rate.to_currency.code}": float(rate.rate)
        for rate in rates
    }
    
    async_to_sync(channel_layer.group_send)(
        "rates",
        {
            "type": "rates.update",
            "data": rates_data
        }
    ) 