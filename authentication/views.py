from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from .models import User, KYCDocument
from .serializers import (UserSerializer, UserRegistrationSerializer, 
                        KYCDocumentSerializer, SecurityCodeSerializer)
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                phone_number=serializer.validated_data.get('phone_number', '')
            )
            # Envoyer email de vérification
            self._send_verification_email(user)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def token(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
                return Response({'error': 'Invalid credentials'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, 
                          status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def token_refresh(self, request):
        refresh_token = request.data.get('refresh')
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token),
            })
        except Exception:
            return Response({'error': 'Invalid refresh token'}, 
                          status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        token = request.data.get('token')
        try:
            user = User.objects.filter(verification_token=token).first()
            if user:
                user.email_verified = True
                user.verification_token = None
                user.save()
                return Response({'message': 'Email verified successfully'})
            return Response({'error': 'Invalid token'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, 
                          status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def set_security_code(self, request):
        user = request.user
        code = request.data.get('security_code')
        if not code:
            return Response({'error': 'Security code is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        user.set_security_code(code)
        return Response({'message': 'Security code set successfully'})

    @action(detail=False, methods=['post'])
    def upload_kyc(self, request):
        user = request.user
        documents = request.FILES.getlist('documents')
        if not documents:
            return Response({'error': 'Documents are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        for doc in documents:
            user.kyc_documents.create(document=doc)
        
        return Response({'message': 'KYC documents uploaded successfully'})

    def _send_verification_email(self, user):
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        user.verification_token = token
        user.save()
        
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        send_mail(
            'Verify your email',
            f'Please click this link to verify your email: {verification_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
