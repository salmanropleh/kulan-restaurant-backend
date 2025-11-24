from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Keep both username and email, but make email unique
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.email if self.email else self.username

    @property
    def full_name(self):
        """Return full name for frontend compatibility"""
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        db_table = 'custom_user'