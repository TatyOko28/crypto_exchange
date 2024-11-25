from rest_framework import serializers
from .models import User, KYCDocument

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone_number', 'is_verified', 
                 'email_verified', 'kyc_verified')
        read_only_fields = ('is_verified', 'email_verified', 'kyc_verified')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password', 'phone_number')

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data

class KYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCDocument
        fields = ('id', 'document_type', 'document_file', 'document_number', 
                 'status', 'verification_date', 'rejection_reason')
        read_only_fields = ('status', 'verification_date', 'rejection_reason')

class SecurityCodeSerializer(serializers.Serializer):
    current_code = serializers.CharField(required=False)
    new_code = serializers.CharField(min_length=6, max_length=6)
    confirm_code = serializers.CharField(min_length=6, max_length=6)

    def validate(self, data):
        if data['new_code'] != data['confirm_code']:
            raise serializers.ValidationError("Security codes don't match")
        return data 