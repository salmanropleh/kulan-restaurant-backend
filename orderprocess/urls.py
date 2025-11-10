from django.urls import path
from . import views

app_name = 'orderprocess'

urlpatterns = [
    # Cart endpoints
    path('cart/', views.get_cart, name='get-cart'),
    path('cart/add/', views.add_to_cart, name='add-to-cart'),
    path('cart/update/<uuid:item_id>/', views.update_cart_item, name='update-cart-item'),
    path('cart/remove/<uuid:item_id>/', views.remove_cart_item, name='remove-cart-item'),
    path('cart/clear/', views.clear_cart, name='clear-cart'),
    
    # Checkout endpoints
    path('checkout/create-session/', views.create_checkout_session, name='create-checkout-session'),
    path('checkout/process-order/', views.process_order, name='process-order'),
    
    # Order confirmation
    path('confirmation/<uuid:order_id>/', views.get_order_confirmation, name='order-confirmation'),
]