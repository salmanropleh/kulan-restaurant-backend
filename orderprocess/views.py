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
import logging

logger = logging.getLogger(__name__)

# ===== CART ENDPOINTS =====
@api_view(['GET'])
@permission_classes([AllowAny])
def get_cart(request):
    """Get or create cart for current session/user"""
    try:
        cart = get_or_create_cart(request)
        serializer = CartSerializer(cart)
        logger.info(f"Cart retrieved: {cart.id}, session: {request.session.session_key}, items: {cart.items.count()}")
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error getting cart: {str(e)}")
        return Response({'error': 'Failed to get cart'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        
        # FIXED: More flexible item matching
        extras = serializer.validated_data.get('extras', [])
        spice_level = serializer.validated_data.get('spice_level', '')
        special_notes = serializer.validated_data.get('special_notes', '')
        
        # Try to find existing cart item with same customizations
        existing_items = CartItem.objects.filter(
            cart=cart,
            menu_item=menu_item,
            spice_level=spice_level,
            special_notes=special_notes
        )
        
        # Check if any existing item has the same extras (order doesn't matter)
        cart_item = None
        for item in existing_items:
            if sorted(item.extras) == sorted(extras):
                cart_item = item
                break
        
        if cart_item:
            # Update existing item
            cart_item.quantity += serializer.validated_data['quantity']
            cart_item.save()
            logger.info(f"Updated existing cart item: {cart_item.id}, new quantity: {cart_item.quantity}")
        else:
            # Create new item
            cart_item = CartItem.objects.create(
                cart=cart,
                menu_item=menu_item,
                quantity=serializer.validated_data['quantity'],
                price=menu_item.price,
                extras=extras,
                spice_level=spice_level,
                special_notes=special_notes
            )
            logger.info(f"Created new cart item: {cart_item.id} for cart: {cart.id}")
        
        cart_serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'message': 'Item added to cart',
            'cart': cart_serializer.data
        })
        
    except MenuItem.DoesNotExist:
        logger.error(f"Menu item not found: {serializer.validated_data['menu_item_id']}")
        return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            logger.info(f"Deleted cart item: {item_id}")
        else:
            cart_item.quantity = new_quantity
            cart_item.save()
            logger.info(f"Updated cart item: {item_id}, quantity: {new_quantity}")
        
        cart_serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'cart': cart_serializer.data
        })
        
    except CartItem.DoesNotExist:
        logger.error(f"Cart item not found: {item_id}")
        return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def remove_cart_item(request, item_id):
    """Remove item from cart"""
    try:
        cart = get_or_create_cart(request)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        cart_item.delete()
        
        logger.info(f"Removed cart item: {item_id}")
        cart_serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'message': 'Item removed from cart',
            'cart': cart_serializer.data
        })
        
    except CartItem.DoesNotExist:
        logger.error(f"Cart item not found for removal: {item_id}")
        return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def clear_cart(request):
    """Clear entire cart"""
    try:
        cart = get_or_create_cart(request)
        items_count = cart.items.count()
        cart.items.all().delete()
        
        logger.info(f"Cleared cart: {cart.id}, removed {items_count} items")
        cart_serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'message': 'Cart cleared',
            'cart': cart_serializer.data
        })
    except Exception as e:
        logger.error(f"Error clearing cart: {str(e)}")
        return Response({'error': 'Failed to clear cart'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    """Process order from checkout session - FIXED to use correct Order model structure"""
    try:
        cart = get_or_create_cart(request)
        checkout_session = CheckoutSession.objects.get(cart=cart)
        
        if checkout_session.expires_at < timezone.now():
            return Response({'error': 'Checkout session expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Create order using the CORRECT model structure from orders app
            customer_data = checkout_session.customer_data
            
            # Combine first and last name for customer_name field
            customer_name = f"{customer_data['first_name']} {customer_data['last_name']}"
            
            # Build delivery address
            delivery_address = ""
            if customer_data['delivery_type'] == 'delivery':
                address_parts = []
                if customer_data.get('address'):
                    address_parts.append(customer_data['address'])
                if customer_data.get('city'):
                    address_parts.append(customer_data['city'])
                if customer_data.get('zip_code'):
                    address_parts.append(customer_data['zip_code'])
                delivery_address = ', '.join(address_parts)
            
            order = Order.objects.create(
                # Use the correct field names from your orders.Order model
                customer_name=customer_name,
                customer_email=customer_data['email'],
                customer_phone=customer_data['phone'],
                delivery_address=delivery_address,
                order_type=customer_data['delivery_type'],  # 'delivery' or 'pickup'
                status='pending',  # Use the correct status choices from orders app
                total_amount=0  # Will be calculated from order items
            )
            
            # Create order items using the CORRECT model structure
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    menu_item=cart_item.menu_item,
                    quantity=cart_item.quantity,
                    price_at_time=cart_item.price,
                    # Add cached fields for display
                    cached_item_name=cart_item.menu_item.name,
                    cached_item_category=cart_item.menu_item.category.name if cart_item.menu_item.category else "Uncategorized",
                    # Store customizations if needed
                    custom_spice_level=cart_item.spice_level or 'default',
                    spice_notes=cart_item.special_notes or ''
                )
            
            # Calculate total and save
            order.calculate_total()
            
            # Clear cart and checkout session
            cart.items.all().delete()
            checkout_session.delete()
            
            return Response({
                'success': True,
                'order_id': order.id,
                'order_number': f"#{order.id.hex[:8].upper()}",
                'grand_total': float(order.total_amount),
                'estimated_delivery': '25-35 minutes'
            })
            
    except CheckoutSession.DoesNotExist:
        return Response({'error': 'No active checkout session'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error processing order: {str(e)}")
        return Response({'error': 'Failed to process order'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    """Get or create cart for current session/user with session handling"""
    # Ensure session exists
    if not request.session.session_key:
        request.session.create()
        logger.info(f"Created new session: {request.session.session_key}")
    
    session_key = request.session.session_key
    
    if request.user.is_authenticated:
        # For authenticated users, try to get user cart or migrate session cart
        try:
            user_cart, created = Cart.objects.get_or_create(user=request.user)
            if not created and session_key:
                # Migrate session cart items to user cart if needed
                session_carts = Cart.objects.filter(session_key=session_key)
                for session_cart in session_carts:
                    for item in session_cart.items.all():
                        # Check if item already exists in user cart
                        existing_item = user_cart.items.filter(
                            menu_item=item.menu_item,
                            extras=item.extras,
                            spice_level=item.spice_level,
                            special_notes=item.special_notes
                        ).first()
                        
                        if existing_item:
                            existing_item.quantity += item.quantity
                            existing_item.save()
                        else:
                            item.cart = user_cart
                            item.save()
                    
                    # Delete the session cart after migration
                    if session_cart.id != user_cart.id:
                        session_cart.delete()
            
            logger.info(f"Using user cart: {user_cart.id} for user: {request.user.username}")
            return user_cart
            
        except Exception as e:
            logger.error(f"Error with user cart, falling back to session: {str(e)}")
            # Fallback to session cart
            cart, created = Cart.objects.get_or_create(session_key=session_key)
            if created:
                logger.info(f"Created fallback session cart: {cart.id}")
            return cart
    else:
        # For anonymous users, use session-based cart
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        if created:
            logger.info(f"Created session cart: {cart.id} for session: {session_key}")
        else:
            logger.info(f"Retrieved existing session cart: {cart.id} for session: {session_key}")
        return cart