from django.db import models
from authentication.models import User

class SupportTicket(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    )
    
    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    )
    
    CATEGORY_CHOICES = (
        ('ACCOUNT', 'Account Issues'),
        ('KYC', 'KYC Verification'),
        ('TRANSACTION', 'Transaction Issues'),
        ('WALLET', 'Wallet Issues'),
        ('SECURITY', 'Security Issues'),
        ('OTHER', 'Other'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tickets'
    )

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"

class TicketResponse(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_staff_response = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='support_attachments/', null=True, blank=True)

    class Meta:
        ordering = ['created_at']

class SupportAttachment(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='support_attachments/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255) 