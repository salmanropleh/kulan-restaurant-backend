# from django.db import models
# import uuid
# from django.db.models import Sum  # Add this import

# class Order(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('confirmed', 'Confirmed'),
#         ('preparing', 'Preparing'),
#         ('ready', 'Ready'),
#         ('delivered', 'Delivered'),
#         ('completed', 'Completed'),
#         ('cancelled', 'Cancelled'),
#     ]
    
#     ORDER_TYPE_CHOICES = [
#         ('delivery', 'Delivery'),
#         ('pickup', 'Pickup'),
#     ]
    
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     customer_name = models.CharField(max_length=255)
#     customer_email = models.EmailField()
#     customer_phone = models.CharField(max_length=20, blank=True)
#     delivery_address = models.TextField(blank=True, null=True)
    
#     order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='delivery')
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         ordering = ['-created_at']
#         indexes = [
#             models.Index(fields=['status']),
#             models.Index(fields=['order_type']),
#             models.Index(fields=['created_at']),
#         ]
    
#     def __str__(self):
#         return f"Order #{self.id.hex[:8]} - {self.customer_name}"
    
#     def calculate_total(self):
#         """Calculate total amount from order items"""
#         # More accurate calculation using aggregation
#         total_result = self.items.aggregate(
#             total=Sum(models.F('price') * models.F('quantity'))
#         )['total'] or 0
#         self.total_amount = total_result
#         self.save()
#         return total_result
    
#     def calculate_total_simple(self):
#         """Calculate total amount from order items (simpler version)"""
#         total = sum(item.total_price for item in self.items.all())
#         self.total_amount = total
#         self.save()
#         return total

# class OrderItem(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    
#     # Menu item details (in a real app, you'd have a MenuItem model)
#     menu_item_name = models.CharField(max_length=255)
#     menu_item_description = models.TextField(blank=True)
#     menu_item_image = models.URLField(blank=True, null=True)
#     menu_item_category = models.CharField(max_length=100, blank=True)
    
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     quantity = models.PositiveIntegerField(default=1)
    
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['created_at']
    
#     def __str__(self):
#         return f"{self.quantity}x {self.menu_item_name} - Order #{self.order.id.hex[:8]}"
    
#     @property
#     def total_price(self):
#         return self.price * self.quantity 



from django.db import models
import uuid
from django.db.models import Sum

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    ORDER_TYPE_CHOICES = [
        ('delivery', 'Delivery'),
        ('pickup', 'Pickup'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    delivery_address = models.TextField(blank=True, null=True)
    
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='delivery')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['order_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Order #{self.id.hex[:8]} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        # Save first to get ID if new order
        is_new = not self.id
        super().save(*args, **kwargs)
        
        # Calculate total after saving (so order items are available)
        if is_new:
            self.calculate_total()
    
    def calculate_total(self):
        """Calculate total amount from order items"""
        total = sum(item.total_price for item in self.items.all())
        self.total_amount = total
        # Use update to avoid recursion
        Order.objects.filter(id=self.id).update(total_amount=total)
        return total

class OrderItem(models.Model):
    CUSTOM_SPICE_CHOICES = [
        ('milder', 'Milder than default'),
        ('default', 'As prepared'),
        ('spicier', 'Spicier than default'),
        ('extra_spicy', 'Extra Spicy'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    
    menu_item = models.ForeignKey('menu.MenuItem', on_delete=models.PROTECT, related_name='order_items', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Spice customization
    custom_spice_level = models.CharField(
        max_length=20,
        choices=CUSTOM_SPICE_CHOICES,
        default='default'
    )
    spice_notes = models.TextField(blank=True)
    
    # Cached data
    cached_item_name = models.CharField(max_length=255, blank=True)
    cached_item_category = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        if self.menu_item:
            return f"{self.quantity}x {self.menu_item.name} - Order #{self.order.id.hex[:8]}"
        return f"{self.quantity}x Item - Order #{self.order.id.hex[:8]}"
    
    def save(self, *args, **kwargs):
        # Auto-populate cached fields and price when saving
        if self.menu_item:
            self.cached_item_name = self.menu_item.name
            self.cached_item_category = self.menu_item.category.name
            if not self.price_at_time or self.price_at_time == 0:
                self.price_at_time = self.menu_item.price
        super().save(*args, **kwargs)
        
        # Update order total after saving
        if self.order:
            self.order.calculate_total()
    
    @property
    def total_price(self):
        """Calculate total price for this order item"""
        if self.price_at_time is not None and self.quantity is not None:
            return self.price_at_time * self.quantity
        return 0
    