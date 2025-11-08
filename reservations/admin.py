from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = [
        'customer_name', 'customer_email', 'reservation_date', 
        'reservation_time', 'number_of_guests', 'status', 'created_at'
    ]
    list_filter = ['status', 'reservation_date', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'customer_phone']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'reservation_date'
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Reservation Details', {
            'fields': ('reservation_date', 'reservation_time', 'number_of_guests')
        }),
        ('Additional Information', {
            'fields': ('special_requests', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )