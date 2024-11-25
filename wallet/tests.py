from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from decimal import Decimal
from authentication.models import User
from .models import Wallet, WalletTransaction, WalletTransfer

class WalletTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.wallet = Wallet.objects.create(
            user=self.user,
            currency='BTC',
            balance=Decimal('1.0')
        )
        self.client.force_authenticate(user=self.user)

    def test_get_wallet_balance(self):
        """Test la récupération du solde du portefeuille"""
        url = reverse('wallet-detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['balance']), self.wallet.balance)

    def test_deposit(self):
        """Test le dépôt de fonds"""
        url = reverse('wallet-deposit', args=[self.wallet.id])
        data = {'amount': '0.5'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('1.5'))

    def test_withdraw(self):
        """Test le retrait de fonds"""
        self.user.set_security_code('123456')
        url = reverse('wallet-withdraw', args=[self.wallet.id])
        data = {
            'amount': '0.5',
            'security_code': '123456'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('0.5'))

    def test_transaction_history(self):
        # Créer quelques transactions
        WalletTransaction.objects.create(
            wallet=self.wallet,
            transaction_type='DEPOSIT',
            amount=Decimal('0.5'),
            status='COMPLETED'
        )
        
        url = reverse('wallet-transactions')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class WalletTransferTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
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

    def test_transfer(self):
        transfer = WalletTransfer.objects.create(
            from_wallet=self.wallet1,
            to_wallet=self.wallet2,
            amount=Decimal('0.5'),
            security_code_verified=True
        )
        
        transfer.execute_transfer()
        
        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()
        
        self.assertEqual(self.wallet1.balance, Decimal('0.5'))
        self.assertEqual(self.wallet2.balance, Decimal('0.5'))
