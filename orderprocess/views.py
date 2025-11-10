from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .models import Cart, CartItem, CheckoutSession
from .serializers import (
    CartSerializer, CartItemSerializer, CheckoutSessionSerializer,
    AddToCartSerializer, CheckoutDataSerializer
)
from orders.models import Order, OrderItem
from menu.models import MenuItem

# ===== CART ENDPOINTS =====
@api_view(['GET'])
@permission_classes([AllowAny])
def get_cart(request):
    """Get or create cart for current session/user"""
    cart = get_or_create_cart(request)
    serializer = CartSerializer(cart)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_to_cart(request):
    """Add item to cart"""
    serializer = AddToCartSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        cart = get_or_create_cart(request)
        menu_item = MenuItem.objects.get(id=serializer.validated_data['menu_item_id'])
        
        # Check if item with same customization exists
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            menu_item=menu_item,
            extras=serializer.validated_data.get('extras', []),
            spice_level=serializer.validated_data.get('spice_level', ''),
            defaults={
                'quantity': serializer.validated_data['quantity'],
                'price': menu_item.price,
                'special_notes': serializer.validated_data.get('special_notes', '')
            }
        )
        
        if not created:
            cart_item.quantity += serializer.validated_data['quantity']
            cart_item.save()
        
        cart_serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'message': 'Item added to cart',
            'cart': cart_serializer.data
        })
        
    except MenuItem.DoesNotExist:
        return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    try:
        cart = get_or_create_cart(request)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        new_quantity = request.data.get('quantity', 1)
        
        if new_quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = new_quantity
            cart_item.save()
        
        cart_serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'cart': cart_serializer.data
        })
        
    except CartItem.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def remove_cart_item(request, item_id):
    """Remove item from cart"""
    try:
        cart = get_or_create_cart(request)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        cart_item.delete()
        
        cart_serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'message': 'Item removed from cart',
            'cart': cart_serializer.data
        })
        
    except CartItem.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def clear_cart(request):
    """Clear entire cart"""
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    
    cart_serializer = CartSerializer(cart)
    return Response({
        'success': True,
        'message': 'Cart cleared',
        'cart': cart_serializer.data
    })

# ===== CHECKOUT ENDPOINTS =====
@api_view(['POST'])
@permission_classes([AllowAny])
def create_checkout_session(request):
    """Create checkout session from cart"""
    cart = get_or_create_cart(request)
    
    if cart.items.count() == 0:
        return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = CheckoutDataSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Create or update checkout session
    checkout_session, created = CheckoutSession.objects.get_or_create(
        cart=cart,
        defaults={
            'customer_data': serializer.validated_data,
            'shipping_option': {
                'type': serializer.validated_data['delivery_type'],
                'fee': 2.99 if serializer.validated_data['delivery_type'] == 'delivery' else 0
            },
            'expires_at': timezone.now() + timedelta(hours=1)
        }
    )
    
    if not created:
        checkout_session.customer_data = serializer.validated_data
        checkout_session.shipping_option = {
            'type': serializer.validated_data['delivery_type'],
            'fee': 2.99 if serializer.validated_data['delivery_type'] == 'delivery' else 0
        }
        checkout_session.expires_at = timezone.now() + timedelta(hours=1)
        checkout_session.save()
    
    session_serializer = CheckoutSessionSerializer(checkout_session)
    return Response(session_serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def process_order(request):
    """Process order from checkout session"""
    try:
        cart = get_or_create_cart(request)
        checkout_session = CheckoutSession.objects.get(cart=cart)
        
        if checkout_session.expires_at < timezone.now():
            return Response({'error': 'Checkout session expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Create order in orders app
            customer_data = checkout_session.customer_data
            
            order = Order.objects.create(
                first_name=customer_data['first_name'],
                last_name=customer_data['last_name'],
                email=customer_data['email'],
                phone=customer_data['phone'],
                address=customer_data.get('address'),
                city=customer_data.get('city'),
                zip_code=customer_data.get('zip_code'),
                delivery_type=customer_data['delivery_type'],
                payment_method=customer_data['payment_method'],
                special_instructions=customer_data.get('special_instructions', ''),
                subtotal=cart.subtotal,
                delivery_fee=checkout_session.shipping_option['fee'],
                tax_amount=cart.subtotal * 0.08,  # 8% tax
                grand_total=cart.subtotal + checkout_session.shipping_option['fee'] + (cart.subtotal * 0.08),
                status='pending'
            )
            
            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    menu_item=cart_item.menu_item,
                    quantity=cart_item.quantity,
                    price_at_time=cart_item.price,
                    item_name=cart_item.menu_item.name,
                    item_price=cart_item.price,
                    extras=cart_item.extras,
                    spice_level=cart_item.spice_level,
                    special_notes=cart_item.special_notes
                )
            
            # Clear cart and checkout session
            cart.items.all().delete()
            checkout_session.delete()
            
            return Response({
                'success': True,
                'order_id': order.id,
                'order_number': f"#{order.id.hex[:8].upper()}",
                'grand_total': order.grand_total,
                'estimated_delivery': '25-35 minutes'
            })
            
    except CheckoutSession.DoesNotExist:
        return Response({'error': 'No active checkout session'}, status=status.HTTP_400_BAD_REQUEST)

# ===== ORDER CONFIRMATION ENDPOINTS =====
@api_view(['GET'])
@permission_classes([AllowAny])
def get_order_confirmation(request, order_id):
    """Get order details for confirmation page"""
    try:
        order = Order.objects.get(id=order_id)
        from orders.serializers import OrderDetailSerializer
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

# ===== HELPER FUNCTIONS =====
def get_or_create_cart(request):
    """Get or create cart for current session/user"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    
    return cart