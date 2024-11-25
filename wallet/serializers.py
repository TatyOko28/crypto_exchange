from rest_framework import serializers
from .models import Wallet, WalletTransaction, WalletTransfer

class WalletSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Wallet
        fields = ['id', 'user_email', 'currency', 'balance', 'is_active', 
                 'created_at', 'last_transaction_at']
        read_only_fields = ['balance', 'created_at', 'last_transaction_at']

class WalletTransactionSerializer(serializers.ModelSerializer):
    wallet_currency = serializers.CharField(source='wallet.currency', read_only=True)
    
    class Meta:
        model = WalletTransaction
        fields = ['id', 'wallet', 'wallet_currency', 'transaction_type', 
                 'amount', 'status', 'reference', 'fee', 'timestamp', 
                 'completed_at', 'notes']
        read_only_fields = ['status', 'timestamp', 'completed_at']

class WalletTransferSerializer(serializers.ModelSerializer):
    from_currency = serializers.CharField(source='from_wallet.currency', read_only=True)
    to_currency = serializers.CharField(source='to_wallet.currency', read_only=True)
    
    class Meta:
        model = WalletTransfer
        fields = ['id', 'from_wallet', 'to_wallet', 'from_currency', 
                 'to_currency', 'amount', 'fee', 'status', 'created_at', 
                 'completed_at']
        read_only_fields = ['status', 'created_at', 'completed_at']

class TransactionHistorySerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(source='get_transaction_type_display')
    
    class Meta:
        model = WalletTransaction
        fields = ['id', 'transaction_type', 'transaction_type_display', 
                 'amount', 'status', 'timestamp'] 