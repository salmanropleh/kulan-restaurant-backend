from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Reservation
from .serializers import ReservationSerializer
from .filters import ReservationFilter

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ReservationFilter
    search_fields = ['customer_name', 'customer_email', 'customer_phone', 'special_requests']
    ordering_fields = ['reservation_date', 'reservation_time', 'created_at']
    ordering = ['-reservation_date', '-reservation_time']
    
    def create(self, request, *args, **kwargs):
        """Create a new reservation (default status: pending)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set status to pending for new reservations
        reservation = serializer.save(status='pending')
        
        # In a real application, you would send confirmation email here
        # send_reservation_confirmation_email(reservation)
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a pending reservation"""
        reservation = self.get_object()
        if reservation.status != 'pending':
            return Response(
                {'error': 'Only pending reservations can be confirmed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'confirmed'
        reservation.save()
        
        # In a real application, send confirmation notification
        # send_reservation_confirmed_email(reservation)
        
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a reservation"""
        reservation = self.get_object()
        if reservation.status in ['completed', 'cancelled']:
            return Response(
                {'error': 'Cannot cancel a completed or already cancelled reservation.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'cancelled'
        reservation.save()
        
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming reservations"""
        from django.utils import timezone
        from django.db.models import Q
        
        upcoming_reservations = self.get_queryset().filter(
            Q(reservation_date__gt=timezone.now().date()) |
            Q(reservation_date=timezone.now().date(), 
              reservation_time__gte=timezone.now().time())
        ).exclude(status='cancelled')
        
        page = self.paginate_queryset(upcoming_reservations)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(upcoming_reservations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def availability(self, request):
        """Check availability for a specific date and time"""
        date = request.query_params.get('date')
        time = request.query_params.get('time')
        
        if not date or not time:
            return Response(
                {'error': 'Both date and time parameters are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if there are existing reservations for the same date and time
        existing_reservations = Reservation.objects.filter(
            reservation_date=date,
            reservation_time=time,
            status__in=['pending', 'confirmed']
        )
        
        total_guests = sum(reservation.number_of_guests for reservation in existing_reservations)
        
        # Assuming restaurant capacity - adjust as needed
        restaurant_capacity = 50
        available_seats = restaurant_capacity - total_guests
        
        return Response({
            'date': date,
            'time': time,
            'available_seats': available_seats,
            'is_available': available_seats > 0,
            'existing_reservations': existing_reservations.count()
        })

# Additional view for dashboard statistics
from rest_framework.views import APIView
from django.db.models import Count, Q
from django.utils import timezone

class ReservationStatsView(APIView):
    def get(self, request):
        today = timezone.now().date()
        
        stats = {
            'total_reservations': Reservation.objects.count(),
            'today_reservations': Reservation.objects.filter(reservation_date=today).count(),
            'pending_reservations': Reservation.objects.filter(status='pending').count(),
            'upcoming_reservations': Reservation.objects.filter(
                Q(reservation_date__gt=today) |
                Q(reservation_date=today, reservation_time__gte=timezone.now().time()),
                status__in=['pending', 'confirmed']
            ).count(),
            'status_distribution': Reservation.objects.values('status').annotate(
                count=Count('id')
            )
        }
        
        return Response(stats)