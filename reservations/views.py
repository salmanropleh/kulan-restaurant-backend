# reservations/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count
from django.utils import timezone
from rest_framework.views import APIView
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
    
    # CHANGE BACK TO AllowAny (like your orders view)
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Show ALL reservations to everyone (like your orders view)"""
        queryset = super().get_queryset()
        return queryset
    
    def perform_create(self, serializer):
        """Automatically assign the current user's email to new reservations if logged in"""
        if self.request.user.is_authenticated:
            # Update customer_email to match logged-in user's email
            serializer.save(customer_email=self.request.user.email)
        else:
            serializer.save()
    
    def create(self, request, *args, **kwargs):
        """Create a new reservation (default status: pending)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set status to pending for new reservations
        reservation = serializer.save(status='pending')
        
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
    
    # ADD THIS ACTION: Get current user's reservations specifically
    @action(detail=False, methods=['get'])
    def my_reservations(self, request):
        """Alternative endpoint specifically for user's reservations"""
        if request.user.is_authenticated:
            # Filter by user email for authenticated users
            reservations = Reservation.objects.filter(customer_email=request.user.email)
        else:
            # Return empty for unauthenticated users
            reservations = Reservation.objects.none()
            
        page = self.paginate_queryset(reservations)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(reservations, many=True)
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

# Update the stats view to show all data
class ReservationStatsView(APIView):
    # CHANGE BACK TO AllowAny
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        today = timezone.now().date()
        
        # Show all reservations (like your orders stats)
        all_reservations = Reservation.objects.all()
        
        stats = {
            'total_reservations': all_reservations.count(),
            'today_reservations': all_reservations.filter(reservation_date=today).count(),
            'pending_reservations': all_reservations.filter(status='pending').count(),
            'upcoming_reservations': all_reservations.filter(
                Q(reservation_date__gt=today) |
                Q(reservation_date=today, reservation_time__gte=timezone.now().time()),
                status__in=['pending', 'confirmed']
            ).count(),
            'status_distribution': all_reservations.values('status').annotate(
                count=Count('id')
            )
        }
        
        return Response(stats)