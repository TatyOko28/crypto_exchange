from django.contrib import admin
from .models import Wallet, WalletTransaction, WalletTransfer

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency', 'balance', 'is_active', 'last_transaction_at')
    list_filter = ('currency', 'is_active')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'last_transaction_at')

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'status', 'timestamp')
    list_filter = ('transaction_type', 'status', 'timestamp')
    search_fields = ('wallet__user__email', 'reference')
    readonly_fields = ('timestamp', 'completed_at')

@admin.register(WalletTransfer)
class WalletTransferAdmin(admin.ModelAdmin):
    list_display = ('from_wallet', 'to_wallet', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('from_wallet__user__email', 'to_wallet__user__email')
    readonly_fields = ('created_at', 'completed_at')
