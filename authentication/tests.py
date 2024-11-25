from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core import mail
from .models import User, KYCDocument
import tempfile
from PIL import Image
import io
import json

class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.valid_payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'phone_number': '+1234567890'
        }

    def test_valid_registration(self):
        response = self.client.post(self.register_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.valid_payload['email']).exists())
        self.assertEqual(len(mail.outbox), 1)  # Vérifie qu'un email a été envoyé

    def test_invalid_password_confirmation(self):
        payload = self.valid_payload.copy()
        payload['confirm_password'] = 'WrongPass123!'
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email(self):
        # Créer un utilisateur
        User.objects.create_user(
            username='existing',
            email=self.valid_payload['email'],
            password='ExistingPass123!'
        )
        response = self.client.post(self.register_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class EmailVerificationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.verify_email_url = reverse('verify-email')

    def test_valid_verification(self):
        # Simuler l'envoi du token
        self.user.verification_token = 'valid-token'
        self.user.save()
        
        response = self.client.post(self.verify_email_url, {'token': 'valid-token'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Rafraîchir l'utilisateur depuis la base de données
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)

    def test_invalid_token(self):
        response = self.client.post(self.verify_email_url, {'token': 'invalid-token'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class KYCDocumentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.client.force_authenticate(user=self.user)
        self.upload_kyc_url = reverse('upload-kyc')

    def create_test_image(self):
        # Créer une image temporaire pour les tests
        image = Image.new('RGB', (100, 100), color='red')
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        return image_io

    def test_kyc_document_upload(self):
        image = self.create_test_image()
        payload = {
            'document_type': 'PASSPORT',
            'document_file': image,
            'document_number': 'ABC123'
        }
        response = self.client.post(self.upload_kyc_url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(KYCDocument.objects.filter(user=self.user).exists())

class SecurityCodeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.client.force_authenticate(user=self.user)
        self.security_code_url = reverse('security-code')

    def test_set_initial_security_code(self):
        payload = {
            'new_code': '123456',
            'confirm_code': '123456'
        }
        response = self.client.put(self.security_code_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Rafraîchir l'utilisateur
        self.user.refresh_from_db()
        self.assertTrue(self.user.security_code)

    def test_change_security_code(self):
        # D'abord définir un code
        self.user.set_security_code('123456')
        self.user.save()

        payload = {
            'current_code': '123456',
            'new_code': '654321',
            'confirm_code': '654321'
        }
        response = self.client.put(self.security_code_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_current_code(self):
        self.user.set_security_code('123456')
        self.user.save()

        payload = {
            'current_code': 'wrong-code',
            'new_code': '654321',
            'confirm_code': '654321'
        }
        response = self.client.put(self.security_code_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserModelTests(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.assertFalse(user.is_verified)
        self.assertFalse(user.email_verified)
        self.assertFalse(user.kyc_verified)
        self.assertEqual(user.failed_login_attempts, 0)
        self.assertFalse(user.account_locked)

    def test_failed_login_attempts(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        user.failed_login_attempts = 3
        user.save()
        self.assertTrue(user.account_locked)

class AuthenticationTests(APITestCase):
    def setUp(self):
        # Créer un utilisateur de test
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'username': 'testuser'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.user.is_verified = True
        self.user.save()

    def test_user_registration(self):
        """Test l'enregistrement d'un nouvel utilisateur"""
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'username': 'newuser'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_user_login(self):
        """Test la connexion d'un utilisateur"""
        url = reverse('token')
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_verify_email(self):
        """Test la vérification d'email"""
        url = reverse('verify-email')
        self.user.verification_token = 'test-token'
        self.user.save()
        
        data = {'token': 'test-token'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que l'email est marqué comme vérifié
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)

    def test_set_security_code(self):
        """Test la configuration du code de sécurité"""
        self.client.force_authenticate(user=self.user)
        url = reverse('set-security-code')
        data = {'security_code': '123456'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
