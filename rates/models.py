from django.db import models
from django.core.cache import cache
from decimal import Decimal

class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    is_crypto = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Currencies"

    def __str__(self):
        return f"{self.code} - {self.name}"

class ExchangeRate(models.Model):
    from_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='rates_from')
    to_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='rates_to')
    rate = models.DecimalField(max_digits=18, decimal_places=8)
    last_updated = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=50)  # API source
    
    class Meta:
        unique_together = ('from_currency', 'to_currency')
        indexes = [
            models.Index(fields=['from_currency', 'to_currency']),
            models.Index(fields=['last_updated']),
        ]

    def __str__(self):
        return f"{self.from_currency.code}/{self.to_currency.code}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Mettre à jour le cache
        cache_key = f"rate_{self.from_currency.code}_{self.to_currency.code}"
        cache.set(cache_key, self.rate, timeout=300)  # Cache pour 5 minutes

    @staticmethod
    def get_rate(from_currency_code, to_currency_code):
        cache_key = f"rate_{from_currency_code}_{to_currency_code}"
        rate = cache.get(cache_key)
        if rate is None:
            try:
                exchange_rate = ExchangeRate.objects.get(
                    from_currency__code=from_currency_code,
                    to_currency__code=to_currency_code
                )
                rate = exchange_rate.rate
                cache.set(cache_key, rate, timeout=300)
            except ExchangeRate.DoesNotExist:
                return None
        return rate

class RateAlert(models.Model):
    CONDITION_CHOICES = (
        ('ABOVE', 'Above'),
        ('BELOW', 'Below'),
    )
    
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    from_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='alerts_from')
    to_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='alerts_to')
    condition = models.CharField(max_length=5, choices=CONDITION_CHOICES)
    target_rate = models.DecimalField(max_digits=18, decimal_places=8)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    triggered_at = models.DateTimeField(null=True, blank=True) 