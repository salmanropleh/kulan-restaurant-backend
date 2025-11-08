from rest_framework import serializers
from .models import Reservation
from django.utils import timezone

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            'id', 'customer_name', 'customer_email', 'customer_phone',
            'reservation_date', 'reservation_time', 'number_of_guests',
            'special_requests', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_reservation_date(self, value):
        """Ensure reservation date is not in the past"""
        if value < timezone.now().date():
            raise serializers.ValidationError("Reservation date cannot be in the past.")
        return value
    
    def validate_number_of_guests(self, value):
        """Ensure number of guests is reasonable"""
        if value < 1:
            raise serializers.ValidationError("Number of guests must be at least 1.")
        if value > 20:
            raise serializers.ValidationError("For groups larger than 20, please call us directly.")
        return value