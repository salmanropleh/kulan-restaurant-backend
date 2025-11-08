# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.filters import SearchFilter, OrderingFilter
# from django.db.models import Count, Q, Sum  # Added Sum import
# from django.utils import timezone
# from datetime import timedelta

# from .models import Order, OrderItem
# from .serializers import (
#     OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer,
#     OrderItemDetailSerializer, OrderItemSerializer
# )
# from .filters import OrderFilter, OrderItemFilter

# class OrderViewSet(viewsets.ModelViewSet):
#     queryset = Order.objects.prefetch_related('items').all()
#     filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
#     filterset_class = OrderFilter
#     search_fields = ['customer_name', 'customer_email', 'customer_phone']
#     ordering_fields = ['created_at', 'total_amount', 'status']
#     ordering = ['-created_at']
    
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return OrderCreateSerializer
#         elif self.action == 'retrieve':
#             return OrderDetailSerializer
#         return OrderListSerializer
    
#     def get_queryset(self):
#         queryset = super().get_queryset()
        
#         # Optimize for different actions
#         if self.action == 'list':
#             queryset = queryset.prefetch_related('items')[:10]  # Limit for performance
        
#         return queryset
    
#     @action(detail=True, methods=['post'])
#     def update_status(self, request, pk=None):
#         """Update order status"""
#         order = self.get_object()
#         new_status = request.data.get('status')
        
#         if new_status not in dict(Order.STATUS_CHOICES):
#             return Response(
#                 {'error': 'Invalid status'}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         order.status = new_status
#         order.save()
        
#         serializer = self.get_serializer(order)
#         return Response(serializer.data)
    
#     @action(detail=False, methods=['get'])
#     def stats(self, request):
#         """Get order statistics for dashboard"""
#         today = timezone.now().date()
#         week_ago = today - timedelta(days=7)
        
#         stats = {
#             'total_orders': Order.objects.count(),
#             'today_orders': Order.objects.filter(created_at__date=today).count(),
#             'pending_orders': Order.objects.filter(status='pending').count(),
#             'preparing_orders': Order.objects.filter(status='preparing').count(),
#             'ready_orders': Order.objects.filter(status='ready').count(),
#             'revenue_today': Order.objects.filter(
#                 created_at__date=today
#             ).aggregate(total_revenue=Sum('total_amount'))['total_revenue'] or 0,
#             'status_distribution': list(Order.objects.values('status').annotate(
#                 count=Count('id')
#             )),
#             'type_distribution': list(Order.objects.values('order_type').annotate(
#                 count=Count('id')
#             )),
#         }
        
#         return Response(stats)

# class OrderItemViewSet(viewsets.ModelViewSet):
#     queryset = OrderItem.objects.select_related('order').all()
#     serializer_class = OrderItemDetailSerializer
#     filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
#     filterset_class = OrderItemFilter
#     search_fields = [
#         'menu_item_name', 'menu_item_category', 
#         'order__customer_name', 'order__id'
#     ]
#     ordering_fields = ['created_at', 'price', 'quantity']
#     ordering = ['-created_at']
    
#     def get_queryset(self):
#         queryset = super().get_queryset()
        
#         # Filter by order ID if provided
#         order_id = self.request.query_params.get('order_id')
#         if order_id:
#             queryset = queryset.filter(order_id=order_id)
        
#         return queryset
    
#     @action(detail=False, methods=['get'])
#     def grouped_by_order(self, request):
#         """Get order items grouped by order (for OrderItems dashboard)"""
#         orders = Order.objects.prefetch_related('items').all()
        
#         # Apply filters
#         status_filter = request.query_params.get('status')
#         search_term = request.query_params.get('search', '')
        
#         if status_filter:
#             orders = orders.filter(status=status_filter)
        
#         if search_term:
#             orders = orders.filter(
#                 Q(customer_name__icontains=search_term) |
#                 Q(id__icontains=search_term) |
#                 Q(items__menu_item_name__icontains=search_term) |
#                 Q(items__menu_item_category__icontains=search_term)
#             ).distinct()
        
#         # Group items by order
#         grouped_data = []
#         for order in orders:
#             if order.items.exists():  # Only include orders with items
#                 grouped_data.append({
#                     'order': {
#                         'id': order.id.hex[:8],
#                         'customer_name': order.customer_name,
#                         'total_amount': order.total_amount,
#                         'status': order.status
#                     },
#                     'items': OrderItemSerializer(order.items.all(), many=True).data
#                 })
        
#         return Response(grouped_data)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta

from .models import Order, OrderItem
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer,
    OrderItemDetailSerializer, OrderItemSerializer
)
from .filters import OrderFilter, OrderItemFilter

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items', 'items__menu_item').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ['customer_name', 'customer_email', 'customer_phone']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.action == 'list':
            queryset = queryset.prefetch_related('items__menu_item')[:10]
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update order status"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get order statistics for dashboard"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        stats = {
            'total_orders': Order.objects.count(),
            'today_orders': Order.objects.filter(created_at__date=today).count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'preparing_orders': Order.objects.filter(status='preparing').count(),
            'ready_orders': Order.objects.filter(status='ready').count(),
            'revenue_today': Order.objects.filter(
                created_at__date=today
            ).aggregate(total_revenue=Sum('total_amount'))['total_revenue'] or 0,
            'status_distribution': list(Order.objects.values('status').annotate(
                count=Count('id')
            )),
            'type_distribution': list(Order.objects.values('order_type').annotate(
                count=Count('id')
            )),
        }
        
        return Response(stats)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related('order', 'menu_item').all()
    serializer_class = OrderItemDetailSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OrderItemFilter
    search_fields = [
        'cached_item_name', 'cached_item_category', 
        'order__customer_name', 'menu_item__name'
    ]
    ordering_fields = ['created_at', 'price_at_time', 'quantity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def grouped_by_order(self, request):
        """Get order items grouped by order"""
        orders = Order.objects.prefetch_related('items__menu_item').all()
        
        status_filter = request.query_params.get('status')
        search_term = request.query_params.get('search', '')
        
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        if search_term:
            orders = orders.filter(
                Q(customer_name__icontains=search_term) |
                Q(id__icontains=search_term) |
                Q(items__cached_item_name__icontains=search_term) |
                Q(items__menu_item__name__icontains=search_term)
            ).distinct()
        
        grouped_data = []
        for order in orders:
            if order.items.exists():
                grouped_data.append({
                    'order': {
                        'id': order.id.hex[:8],
                        'customer_name': order.customer_name,
                        'total_amount': order.total_amount,
                        'status': order.status
                    },
                    'items': OrderItemSerializer(order.items.all(), many=True).data
                })
        
        return Response(grouped_data)