from django.contrib import admin
from .models import Currency, ExchangeRate, RateAlert

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_crypto', 'is_active')
    list_filter = ('is_crypto', 'is_active')
    search_fields = ('code', 'name')

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('from_currency', 'to_currency', 'rate', 'last_updated', 'source')
    list_filter = ('source', 'last_updated')
    search_fields = ('from_currency__code', 'to_currency__code')
    date_hierarchy = 'last_updated'

@admin.register(RateAlert)
class RateAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'from_currency', 'to_currency', 'condition', 
                   'target_rate', 'is_active', 'triggered_at')
    list_filter = ('condition', 'is_active')
    search_fields = ('user__email', 'from_currency__code', 'to_currency__code')
    date_hierarchy = 'created_at' 