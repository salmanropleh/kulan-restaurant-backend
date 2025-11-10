from django.db import models
import uuid
from django.contrib.sessions.models import Session

class Cart(models.Model):
    """Shopping cart model - can be session-based or user-based"""
    session_key = models.CharField(max_length=40, unique=True, null=True, blank=True)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Session Cart ({self.session_key})"
    
    @property
    def total_items(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    """Individual items in the cart"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey('menu.MenuItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    # Customizations
    extras = models.JSONField(default=list, blank=True)  # Extra toppings
    spice_level = models.CharField(max_length=50, blank=True, null=True)
    special_notes = models.TextField(blank=True, null=True)
    
    # Cached price at time of adding to cart
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cart', 'menu_item', 'extras', 'spice_level']
    
    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"
    
    @property
    def total_price(self):
        return self.price * self.quantity
    
    def save(self, *args, **kwargs):
        # Auto-set price from menu item if not set
        if not self.price and self.menu_item:
            self.price = self.menu_item.price
        super().save(*args, **kwargs)

class CheckoutSession(models.Model):
    """Temporary checkout session data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    customer_data = models.JSONField()  # Store form data temporarily
    shipping_option = models.JSONField()  # Delivery/pickup choice
    payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"Checkout Session {self.id}"