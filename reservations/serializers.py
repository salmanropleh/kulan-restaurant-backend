# reservations\serializers.py
from rest_framework import serializers
from .models import Reservation
from django.utils import timezone
from datetime import datetime, time

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            'id', 'customer_name', 'customer_email', 'customer_phone',
            'reservation_date', 'reservation_time', 'number_of_guests',
            'special_requests', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']
    
    def validate_reservation_date(self, value):
        """Ensure reservation date is not in the past"""
        if value < timezone.now().date():
            raise serializers.ValidationError("Reservation date cannot be in the past.")
        return value
    
    def validate_reservation_time(self, value):
        """Ensure reservation time is valid"""
        # Check if it's a valid time format
        if not isinstance(value, time):
            try:
                time.fromisoformat(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError("Invalid time format.")
        return value
    
    def validate(self, data):
        """Additional validation combining date and time"""
        reservation_date = data.get('reservation_date')
        reservation_time = data.get('reservation_time')
        
        if reservation_date and reservation_time:
            # If reservation is for today, check if time has passed
            if reservation_date == timezone.now().date():
                current_time = timezone.now().time()
                if reservation_time < current_time:
                    raise serializers.ValidationError({
                        'reservation_time': 'Reservation time cannot be in the past for today.'
                    })
        
        return data
    
    def validate_number_of_guests(self, value):
        """Ensure number of guests is reasonable"""
        if value < 1:
            raise serializers.ValidationError("Number of guests must be at least 1.")
        if value > 20:
            raise serializers.ValidationError("For groups larger than 20, please call us directly.")
        return value