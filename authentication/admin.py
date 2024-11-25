from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, KYCDocument

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_verified', 'email_verified', 
                   'kyc_verified', 'date_joined')
    list_filter = ('is_verified', 'email_verified', 'kyc_verified', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Verification', {'fields': ('is_verified', 'email_verified', 
                                   'kyc_verified', 'security_code')}),
    )

class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'status', 'is_verified', 
                   'verification_date')
    list_filter = ('document_type', 'status', 'is_verified')
    search_fields = ('user__username', 'user__email', 'document_number')

admin.site.register(User, CustomUserAdmin)
admin.site.register(KYCDocument, KYCDocumentAdmin)
