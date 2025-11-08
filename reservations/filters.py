import django_filters
from .models import Reservation

class ReservationFilter(django_filters.FilterSet):
    customer_name = django_filters.CharFilter(lookup_expr='icontains')
    customer_email = django_filters.CharFilter(lookup_expr='icontains')
    reservation_date = django_filters.DateFilter()
    reservation_date_from = django_filters.DateFilter(field_name='reservation_date', lookup_expr='gte')
    reservation_date_to = django_filters.DateFilter(field_name='reservation_date', lookup_expr='lte')
    status = django_filters.ChoiceFilter(choices=Reservation.STATUS_CHOICES)
    
    class Meta:
        model = Reservation
        fields = [
            'customer_name', 'customer_email', 'reservation_date',
            'status', 'number_of_guests'
        ]