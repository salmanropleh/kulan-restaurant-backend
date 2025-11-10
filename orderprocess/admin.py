from django.contrib import admin
from .models import Cart, CartItem, CheckoutSession

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'total_items', 'subtotal', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'session_key']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['menu_item', 'cart', 'quantity', 'price', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['menu_item__name', 'cart__session_key']

@admin.register(CheckoutSession)
class CheckoutSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'expires_at', 'created_at']
    list_filter = ['created_at', 'expires_at']