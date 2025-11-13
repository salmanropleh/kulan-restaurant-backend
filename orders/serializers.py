# from rest_framework import serializers
# from .models import Order, OrderItem

# class OrderItemSerializer(serializers.ModelSerializer):
#     total_price = serializers.ReadOnlyField()
#     menu_item = serializers.SerializerMethodField()
    
#     class Meta:
#         model = OrderItem
#         fields = [
#             'id', 'menu_item_name', 'menu_item_description', 'menu_item_image',
#             'menu_item_category', 'price', 'quantity', 'total_price', 'menu_item'
#         ]
#         read_only_fields = ['id', 'created_at']
    
#     def get_menu_item(self, obj):
#         """Format menu item data to match frontend structure"""
#         return {
#             'id': obj.id.hex[:8],
#             'name': obj.menu_item_name,
#             'image': obj.menu_item_image,
#             'category': {
#                 'name': obj.menu_item_category
#             }
#         }

# class OrderListSerializer(serializers.ModelSerializer):
#     items_count = serializers.SerializerMethodField()
#     order_items_list = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Order
#         fields = [
#             'id', 'customer_name', 'customer_email', 'customer_phone',
#             'delivery_address', 'order_type', 'status', 'total_amount',
#             'created_at', 'items_count', 'order_items_list'
#         ]
    
#     def get_items_count(self, obj):
#         return obj.items.count()
    
#     def get_order_items_list(self, obj):
#         """Get first few items for the list view"""
#         items = obj.items.all()[:3]  # Limit for list view
#         return OrderItemSerializer(items, many=True).data

# class OrderDetailSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True, read_only=True)
#     order_items_list = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Order
#         fields = [
#             'id', 'customer_name', 'customer_email', 'customer_phone',
#             'delivery_address', 'order_type', 'status', 'total_amount',
#             'created_at', 'updated_at', 'items', 'order_items_list'
#         ]
    
#     def get_order_items_list(self, obj):
#         return OrderItemSerializer(obj.items.all(), many=True).data

# class OrderCreateSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True)
    
#     class Meta:
#         model = Order
#         fields = [
#             'customer_name', 'customer_email', 'customer_phone',
#             'delivery_address', 'order_type', 'items'
#         ]
    
#     def create(self, validated_data):
#         items_data = validated_data.pop('items')
#         order = Order.objects.create(**validated_data)
        
#         # Create order items
#         for item_data in items_data:
#             OrderItem.objects.create(order=order, **item_data)
        
#         # Calculate total
#         order.calculate_total()
        
#         return order

# class OrderItemDetailSerializer(serializers.ModelSerializer):
#     order = serializers.SerializerMethodField()
#     menu_item = serializers.SerializerMethodField()
    
#     class Meta:
#         model = OrderItem
#         fields = [
#             'id', 'order', 'menu_item_name', 'menu_item_description',
#             'menu_item_image', 'menu_item_category', 'price', 'quantity',
#             'total_price', 'created_at', 'menu_item'
#         ]
    
#     def get_order(self, obj):
#         return {
#             'id': obj.order.id.hex[:8],
#             'customer_name': obj.order.customer_name,
#             'total_amount': obj.order.total_amount,
#             'status': obj.order.status
#         }
    
#     def get_menu_item(self, obj):
#         return {
#             'id': obj.id.hex[:8],
#             'name': obj.menu_item_name,
#             'image': obj.menu_item_image,
#             'category': {
#                 'name': obj.menu_item_category
#             }
#         }
from rest_framework import serializers
from .models import Order, OrderItem
from menu.serializers import MenuItemSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField()
    menu_item_details = serializers.SerializerMethodField()
    custom_spice_level_display = serializers.CharField(source='get_custom_spice_level_display', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'menu_item', 'quantity', 'price_at_time', 
            'total_price', 'cached_item_name', 'cached_item_category',
            'menu_item_details', 'created_at',
            'custom_spice_level', 'custom_spice_level_display', 'spice_notes'
        ]
        read_only_fields = ['id', 'created_at', 'cached_item_name', 'cached_item_category']
    
    def get_menu_item_details(self, obj):
        """Get detailed menu item information with absolute image URL"""
        if obj.menu_item:
            # Use MenuItemSerializer to get full details including proper image URL
            from menu.serializers import MenuItemSerializer
            return MenuItemSerializer(obj.menu_item, context=self.context).data
        
        # Fallback for cached data
        return {
            'name': obj.cached_item_name,
            'category': {'name': obj.cached_item_category},
            'image': None
        }

class OrderListSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()
    order_items_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'customer_email', 'customer_phone',
            'delivery_address', 'order_type', 'status', 'total_amount',
            'created_at', 'items_count', 'order_items_preview'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()
    
    def get_order_items_preview(self, obj):
        """Get first few items for the list view with proper image URLs"""
        items = obj.items.all()[:3]
        return OrderItemSerializer(items, many=True, context=self.context).data

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'customer_email', 'customer_phone',
            'delivery_address', 'order_type', 'status', 'total_amount',
            'created_at', 'updated_at', 'items', 'items_count'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'customer_name', 'customer_email', 'customer_phone',
            'delivery_address', 'order_type', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        # Create order items with proper menu_item relationship
        for item_data in items_data:
            # Extract menu_item from the data
            menu_item = item_data.pop('menu_item')
            OrderItem.objects.create(
                order=order, 
                menu_item=menu_item,
                **item_data
            )
        
        # Calculate total
        order.calculate_total()
        
        return order

class OrderItemDetailSerializer(serializers.ModelSerializer):
    order_info = serializers.SerializerMethodField()
    menu_item_details = serializers.SerializerMethodField()
    custom_spice_level_display = serializers.CharField(source='get_custom_spice_level_display', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'order_info', 'menu_item', 'cached_item_name', 
            'cached_item_category', 'quantity', 'price_at_time',
            'total_price', 'created_at', 'menu_item_details',
            'custom_spice_level', 'custom_spice_level_display', 'spice_notes'
        ]
    
    def get_order_info(self, obj):
        return {
            'id': obj.order.id.hex[:8] if obj.order else None,
            'customer_name': obj.order.customer_name if obj.order else 'Unknown',
            'total_amount': float(obj.order.total_amount) if obj.order and obj.order.total_amount else 0.0,
            'status': obj.order.status if obj.order else 'unknown'
        }
    
    def get_menu_item_details(self, obj):
        if obj.menu_item:
            # Use MenuItemSerializer to get full details including proper image URL
            from menu.serializers import MenuItemSerializer
            return MenuItemSerializer(obj.menu_item, context=self.context).data
        
        # Fallback for cached data
        return {
            'name': obj.cached_item_name,
            'category': {'name': obj.cached_item_category},
            'image': None
        }