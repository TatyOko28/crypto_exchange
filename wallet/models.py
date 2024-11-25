from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from authentication.models import User
from decimal import Decimal

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    currency = models.CharField(max_length=10)
    balance = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_transaction_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'currency']

    def __str__(self):
        return f"{self.user.username}'s {self.currency} Wallet"

    def deposit(self, amount):
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        self.balance += Decimal(str(amount))
        self.save()

    def withdraw(self, amount):
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        if self.balance < amount:
            raise ValidationError("Insufficient funds")
        self.balance -= Decimal(str(amount))
        self.save()

class WalletTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('TRANSFER', 'Transfer'),
        ('TRADE', 'Trade'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    reference = models.CharField(max_length=100, blank=True)  # Pour lier à un ordre ou une transaction
    fee = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['wallet', 'status']),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} {self.wallet.currency}"

class WalletTransfer(models.Model):
    from_wallet = models.ForeignKey(Wallet, related_name='transfers_sent', on_delete=models.CASCADE)
    to_wallet = models.ForeignKey(Wallet, related_name='transfers_received', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    fee = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    status = models.CharField(max_length=10, choices=WalletTransaction.STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    security_code_verified = models.BooleanField(default=False)

    def execute_transfer(self):
        if self.from_wallet.balance < (self.amount + self.fee):
            raise ValidationError("Insufficient funds")
        
        self.from_wallet.withdraw(self.amount + self.fee)
        self.to_wallet.deposit(self.amount)
        self.status = 'COMPLETED'
        self.save()
