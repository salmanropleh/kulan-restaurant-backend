from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    
    def is_valid(self):
        # Token expires after 1 hour
        return not self.used and (timezone.now() - self.created_at) < timedelta(hours=1)
    
    def mark_used(self):
        self.used = True
        self.save()
    
    class Meta:
        db_table = 'password_reset_tokens'