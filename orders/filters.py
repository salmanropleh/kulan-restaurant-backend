# import django_filters
# from .models import Order, OrderItem

# class OrderFilter(django_filters.FilterSet):
#     customer_name = django_filters.CharFilter(lookup_expr='icontains')
#     customer_email = django_filters.CharFilter(lookup_expr='icontains')
#     status = django_filters.ChoiceFilter(choices=Order.STATUS_CHOICES)
#     order_type = django_filters.ChoiceFilter(choices=Order.ORDER_TYPE_CHOICES)
    
#     class Meta:
#         model = Order
#         fields = ['status', 'order_type']

# class OrderItemFilter(django_filters.FilterSet):
#     menu_item_name = django_filters.CharFilter(lookup_expr='icontains')
#     menu_item_category = django_filters.CharFilter(lookup_expr='icontains')
#     order__customer_name = django_filters.CharFilter(lookup_expr='icontains')
#     order__status = django_filters.ChoiceFilter(choices=Order.STATUS_CHOICES)
    
#     class Meta:
#         model = OrderItem
#         fields = ['menu_item_category', 'order__status']

import django_filters
from .models import Order, OrderItem

class OrderFilter(django_filters.FilterSet):
    customer_name = django_filters.CharFilter(lookup_expr='icontains')
    customer_email = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=Order.STATUS_CHOICES)
    order_type = django_filters.ChoiceFilter(choices=Order.ORDER_TYPE_CHOICES)
    
    class Meta:
        model = Order
        fields = ['status', 'order_type']

class OrderItemFilter(django_filters.FilterSet):
    menu_item_name = django_filters.CharFilter(field_name='cached_item_name', lookup_expr='icontains')
    menu_item_category = django_filters.CharFilter(field_name='cached_item_category', lookup_expr='icontains')
    order__customer_name = django_filters.CharFilter(lookup_expr='icontains')
    order__status = django_filters.ChoiceFilter(choices=Order.STATUS_CHOICES)
    
    class Meta:
        model = OrderItem
        fields = ['cached_item_category', 'order__status']