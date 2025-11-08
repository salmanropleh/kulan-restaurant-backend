from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    number_of_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-reservation_date', '-reservation_time']
        indexes = [
            models.Index(fields=['reservation_date', 'reservation_time']),
            models.Index(fields=['status']),
            models.Index(fields=['customer_email']),
        ]
    
    def __str__(self):
        return f"{self.customer_name} - {self.reservation_date} {self.reservation_time}"
    
    def is_past_due(self):
        """Check if reservation date/time has passed"""
        reservation_datetime = timezone.make_aware(
            timezone.datetime.combine(self.reservation_date, self.reservation_time)
        )
        return timezone.now() > reservation_datetime