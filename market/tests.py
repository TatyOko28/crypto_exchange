from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from decimal import Decimal
from authentication.models import User
from wallet.models import Wallet
from .models import Order, Transaction

class MarketTests(APITestCase):
    def setUp(self):
        # Créer deux utilisateurs pour les tests
        self.user1 = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='pass123'
        )
        
        # Créer des portefeuilles
        self.wallet1 = Wallet.objects.create(
            user=self.user1,
            currency='BTC',
            balance=Decimal('1.0')
        )
        self.wallet2 = Wallet.objects.create(
            user=self.user2,
            currency='BTC',
            balance=Decimal('0.0')
        )

    def test_create_order(self):
        """Test la création d'un ordre"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('order-list')
        data = {
            'type': 'SELL',
            'amount': '0.5',
            'price': '20000',
            'currency': 'BTC'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_execute_order(self):
        """Test l'exécution d'un ordre"""
        order = Order.objects.create(
            user=self.user1,
            order_type='SELL',
            amount=Decimal('0.5'),
            price=Decimal('20000'),
            cryptocurrency='BTC'
        )
        
        # Exécuter l'ordre
        self.client.force_authenticate(user=self.user2)
        url = reverse('order-execute', args=[order.id])
        data = {'security_code': '123456'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
