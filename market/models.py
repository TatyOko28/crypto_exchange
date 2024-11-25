from django.db import models
from django.core.exceptions import ValidationError
from authentication.models import User
from wallet.models import Wallet
from django.utils import timezone

class Order(models.Model):
    ORDER_TYPES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )
    
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('FAILED', 'Failed'),
    )
    
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    order_type = models.CharField(max_length=4, choices=ORDER_TYPES)
    cryptocurrency = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    price = models.DecimalField(max_digits=18, decimal_places=8)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    security_code_verified = models.BooleanField(default=False)
    
    def clean(self):
        if self.order_type == 'SELL':
            wallet = Wallet.objects.filter(user=self.user, currency=self.cryptocurrency).first()
            if not wallet or wallet.balance < self.amount:
                raise ValidationError('Insufficient balance for sell order')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('INITIATED', 'Initiated'),
        ('BUYER_CONFIRMED', 'Buyer Confirmed'),
        ('SELLER_CONFIRMED', 'Seller Confirmed'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('DISPUTED', 'Disputed'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, related_name='buying_transactions', on_delete=models.CASCADE)
    seller = models.ForeignKey(User, related_name='selling_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    price = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='INITIATED')
    buyer_security_confirmed = models.BooleanField(default=False)
    seller_security_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def validate_security_codes(self, user, security_code):
        if not user.check_security_code(security_code):
            raise ValidationError('Invalid security code')
        
        if user == self.buyer:
            self.buyer_security_confirmed = True
        elif user == self.seller:
            self.seller_security_confirmed = True
        
        if self.buyer_security_confirmed and self.seller_security_confirmed:
            self.execute_transaction()
    
    def execute_transaction(self):
        from wallet.models import WalletTransaction
        try:
            # Créer les transactions de portefeuille
            WalletTransaction.objects.create(
                wallet=self.seller.wallet,
                transaction_type='DEBIT',
                amount=self.amount,
                reference=f'Transaction #{self.id}'
            )
            WalletTransaction.objects.create(
                wallet=self.buyer.wallet,
                transaction_type='CREDIT',
                amount=self.amount,
                reference=f'Transaction #{self.id}'
            )
            self.status = 'COMPLETED'
            self.completed_at = timezone.now()
            self.save()
        except Exception as e:
            self.status = 'FAILED'
            self.save()
            raise e
