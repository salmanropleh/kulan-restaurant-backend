from rest_framework import serializers
from .models import Cart, CartItem, CheckoutSession
from menu.serializers import MenuItemSerializer

class CartItemSerializer(serializers.ModelSerializer):
    menu_item_details = MenuItemSerializer(source='menu_item', read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'menu_item', 'menu_item_details', 'quantity', 
            'price', 'total_price', 'extras', 'spice_level', 
            'special_notes', 'created_at'
        ]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'session_key', 'user', 'items', 
            'total_items', 'subtotal', 'created_at', 'updated_at'
        ]

class CheckoutSessionSerializer(serializers.ModelSerializer):
    cart_details = CartSerializer(source='cart', read_only=True)
    
    class Meta:
        model = CheckoutSession
        fields = [
            'id', 'cart', 'cart_details', 'customer_data', 
            'shipping_option', 'payment_intent_id', 'created_at', 'expires_at'
        ]

class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    menu_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)
    extras = serializers.ListField(child=serializers.CharField(), required=False)
    spice_level = serializers.CharField(required=False, allow_blank=True)
    special_notes = serializers.CharField(required=False, allow_blank=True)

class CheckoutDataSerializer(serializers.Serializer):
    """Serializer for checkout form data"""
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    zip_code = serializers.CharField(required=False, allow_blank=True)
    delivery_type = serializers.ChoiceField(choices=[('delivery', 'Delivery'), ('pickup', 'Pickup')])
    payment_method = serializers.ChoiceField(choices=[('card', 'Card'), ('cash', 'Cash')])
    special_instructions = serializers.CharField(required=False, allow_blank=True)