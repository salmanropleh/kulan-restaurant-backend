from django.contrib import admin
from .models import PasswordResetToken

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at', 'used', 'is_valid']
    list_filter = ['used', 'created_at']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['token', 'created_at']