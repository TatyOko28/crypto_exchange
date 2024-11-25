from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, null=True, blank=True)
    security_code = models.CharField(max_length=6, blank=True)
    email_verified = models.BooleanField(default=False)
    kyc_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked = models.BooleanField(default=False)
    
    def set_security_code(self, code):
        """Définir le code de sécurité de l'utilisateur"""
        if len(code) != 6 or not code.isdigit():
            raise ValueError("Le code de sécurité doit être composé de 6 chiffres")
        self.security_code = code
        self.save()

    def check_security_code(self, code):
        """Vérifier le code de sécurité"""
        return self.security_code == code

class KYCDocument(models.Model):
    DOCUMENT_TYPES = (
        ('PASSPORT', 'Passport'),
        ('ID_CARD', 'Identity Card'),
        ('DRIVING_LICENSE', 'Driving License'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kyc_documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='kyc_documents/')
    document_number = models.CharField(max_length=50)
    is_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    verification_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
