from django.contrib import admin
from .models import SupportTicket, TicketResponse, SupportAttachment

class TicketResponseInline(admin.TabularInline):
    model = TicketResponse
    extra = 0
    readonly_fields = ['created_at']

class SupportAttachmentInline(admin.TabularInline):
    model = SupportAttachment
    extra = 0
    readonly_fields = ['uploaded_at']

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'category', 'priority', 
                   'status', 'created_at', 'assigned_to')
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('subject', 'user__email', 'message')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TicketResponseInline, SupportAttachmentInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle création
            obj.assigned_to = request.user
        super().save_model(request, obj, form, change)

@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'responder', 'is_staff_response', 'created_at')
    list_filter = ('is_staff_response', 'created_at')
    search_fields = ('ticket__subject', 'message', 'responder__email') 