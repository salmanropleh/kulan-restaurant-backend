from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Keep both username and email, but make email unique
    email = models.EmailField(unique=True)
    
    # USERNAME_FIELD remains 'username' (default)
    # But we can use email for authentication if needed
    
    def __str__(self):
        return self.email if self.email else self.username

    class Meta:
        db_table = 'custom_user'