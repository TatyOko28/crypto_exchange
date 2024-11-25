from rest_framework import serializers
from .models import Order, Transaction

class OrderSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user_email', 'order_type', 'cryptocurrency', 
                 'amount', 'price', 'status', 'created_at', 'updated_at']
        read_only_fields = ['status', 'created_at', 'updated_at']
    
    def validate(self, data):
        user = self.context['request'].user
        if not user.is_verified or not user.kyc_verified:
            raise serializers.ValidationError(
                "User must be verified and complete KYC to place orders"
            )
        return data

class TransactionSerializer(serializers.ModelSerializer):
    buyer_email = serializers.EmailField(source='buyer.email', read_only=True)
    seller_email = serializers.EmailField(source='seller.email', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'order', 'buyer_email', 'seller_email', 'amount', 
                 'price', 'status', 'created_at', 'completed_at']
        read_only_fields = ['status', 'created_at', 'completed_at']

class SecurityCodeConfirmationSerializer(serializers.Serializer):
    security_code = serializers.CharField(write_only=True)
    
    def validate_security_code(self, value):
        if len(value) != 6:
            raise serializers.ValidationError("Security code must be 6 digits")
        return value 