from django.db import models
from django.contrib.auth import get_user_model
from menu.models import MenuItem

User = get_user_model()

class Favorite(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='favorites'
    )
    menu_item = models.ForeignKey(
        MenuItem, 
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Additional fields for tracking
    last_ordered = models.DateTimeField(null=True, blank=True)
    order_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'menu_item']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.menu_item.name}"