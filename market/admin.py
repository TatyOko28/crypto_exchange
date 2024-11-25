from django.contrib import admin
from .models import Order, Transaction

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_type', 'cryptocurrency', 'amount', 
                   'price', 'status', 'created_at')
    list_filter = ('order_type', 'status', 'cryptocurrency')
    search_fields = ('user__email', 'cryptocurrency')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'buyer', 'seller', 'amount', 'price', 
                   'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__email', 'seller__email')
    readonly_fields = ('created_at', 'completed_at')
