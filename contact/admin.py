from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'subject', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['created_at']
    
    fieldsets = [
        ('Contact Information', {
            'fields': ['name', 'email', 'phone']
        }),
        ('Message Details', {
            'fields': ['subject', 'message', 'is_read', 'created_at']
        }),
    ]