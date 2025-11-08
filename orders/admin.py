# from django.contrib import admin
# from .models import Order, OrderItem

# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     extra = 0
#     readonly_fields = ['total_price']

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = [
#         'id_short', 'customer_name', 'order_type', 'status', 
#         'total_amount', 'items_count', 'created_at'
#     ]
#     list_filter = ['status', 'order_type', 'created_at']
#     search_fields = ['customer_name', 'customer_email', 'customer_phone']
#     readonly_fields = ['created_at', 'updated_at']
#     inlines = [OrderItemInline]
    
#     def id_short(self, obj):
#         return f"#{obj.id.hex[:8]}"
#     id_short.short_description = 'Order ID'
    
#     def items_count(self, obj):
#         return obj.items.count()
#     items_count.short_description = 'Items'

# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ['menu_item_name', 'order_short', 'quantity', 'price', 'total_price']
#     list_filter = ['menu_item_category', 'order__status']
#     search_fields = ['menu_item_name', 'order__customer_name']
    
#     def order_short(self, obj):
#         return f"#{obj.order.id.hex[:8]}"
#     order_short.short_description = 'Order'



# from django.contrib import admin
# from .models import Order, OrderItem

# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     extra = 0
#     readonly_fields = ['total_price', 'cached_item_name', 'cached_item_category']
#     fields = ['menu_item', 'quantity', 'price_at_time', 'total_price', 'cached_item_name']

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = [
#         'id_short', 'customer_name', 'order_type', 'status', 
#         'total_amount', 'items_count', 'created_at'
#     ]
#     list_filter = ['status', 'order_type', 'created_at']
#     search_fields = ['customer_name', 'customer_email', 'customer_phone']
#     readonly_fields = ['created_at', 'updated_at', 'total_amount']
#     inlines = [OrderItemInline]
    
#     def id_short(self, obj):
#         return f"#{obj.id.hex[:8]}"
#     id_short.short_description = 'Order ID'
    
#     def items_count(self, obj):
#         return obj.items.count()
#     items_count.short_description = 'Items'

# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ['cached_item_name', 'order_short', 'quantity', 'price_at_time', 'total_price']
#     list_filter = ['cached_item_category', 'order__status']
#     search_fields = ['cached_item_name', 'order__customer_name', 'menu_item__name']
    
#     def order_short(self, obj):
#         return f"#{obj.order.id.hex[:8]}"
#     order_short.short_description = 'Order'

from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # ⬅️ CHANGE THIS: Show 1 form by default
    min_num = 1  # ⬅️ ADD THIS: Require at least 1 item
    fields = ['menu_item', 'quantity', 'price_at_time', 'total_price_display']
    readonly_fields = ['total_price_display']  # ⬅️ REMOVE status_badge and actions_display from inline
    
    def total_price_display(self, obj):
        return f"${obj.total_price}" if obj.total_price else "$0.00"
    total_price_display.short_description = 'TOTAL'
    
    # ⬅️ ADD THIS: Show prices in dropdown
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['menu_item'].label_from_instance = lambda obj: f"{obj.name} - ${obj.price}"
        return formset

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id_display', 'customer_name', 'order_type', 'status_badge', 
        'total_amount_display', 'items_count', 'created_at'
    ]
    list_filter = ['status', 'order_type', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'customer_phone']
    readonly_fields = ['created_at', 'updated_at', 'total_amount']
    inlines = [OrderItemInline]
    
    # ⬅️ ADD THIS: Include the JavaScript file
    class Media:
        js = ('admin/js/order_price_auto.js',)
    
    # ⬅️ ADD THIS: Better form organization
    fieldsets = [
        ('CUSTOMER INFORMATION', {
            'fields': [
                'customer_name', 
                'customer_email', 
                'customer_phone', 
                'delivery_address'
            ]
        }),
        ('ORDER DETAILS', {
            'fields': [
                'order_type', 
                'status',
                'total_amount'
            ]
        }),
        ('TIMESTAMPS', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def order_id_display(self, obj):
        return f"#{obj.id.hex[:8].upper()}"
    order_id_display.short_description = 'ORDER ID'
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'ITEMS'
    
    def total_amount_display(self, obj):
        return f"${obj.total_amount}" if obj.total_amount else "$0.00"
    total_amount_display.short_description = 'TOTAL'
    
    def status_badge(self, obj):
        status_colors = {
            'pending': 'gray',
            'confirmed': 'blue',
            'preparing': 'orange',
            'ready': 'green', 
            'delivered': 'purple',
            'completed': 'darkgreen',
            'cancelled': 'red'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 15px; font-weight: bold;">⬆ {}</span>',
            color, obj.status.title()
        )
    status_badge.short_description = 'STATUS'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'order_item_display', 'order_customer', 'category_display', 
        'quantity_display', 'unit_price_display', 'total_price_display',
        'status_badge', 'actions_display'
    ]
    list_filter = ['cached_item_category', 'order__status']
    search_fields = [
        'cached_item_name', 'cached_item_category', 
        'order__customer_name', 'order__id'
    ]
    
    # ⬅️ REMOVE this line since you don't have the template:
    # change_list_template = 'admin/orders/orderitem/change_list.html'
    
    def order_item_display(self, obj):
        item_name = obj.cached_item_name or obj.menu_item.name if obj.menu_item else "Unknown Item"
        order_short = f"#{obj.order.id.hex[:8].upper()}" if obj.order else "No Order"
        customer_name = obj.order.customer_name if obj.order else "Unknown Customer"
        return format_html(
            '<strong>{}</strong><br><small>Order {} - {}</small>',
            item_name, order_short, customer_name
        )
    order_item_display.short_description = 'ORDER & ITEM'
    
    def order_customer(self, obj):
        return obj.order.customer_name if obj.order else "Unknown"
    order_customer.short_description = 'CUSTOMER'
    
    def category_display(self, obj):
        category = obj.cached_item_category or (obj.menu_item.category.name if obj.menu_item and obj.menu_item.category else "Unknown")
        return format_html('<strong>{}</strong>', category)
    category_display.short_description = 'CATEGORY'
    
    def quantity_display(self, obj):
        return format_html('<strong>{}</strong>', obj.quantity)
    quantity_display.short_description = 'QTY'
    
    def unit_price_display(self, obj):
        return f"${obj.price_at_time}" if obj.price_at_time else "$0.00"
    unit_price_display.short_description = 'UNIT PRICE'
    
    def total_price_display(self, obj):
        return f"<strong>${obj.total_price}</strong>" if obj.total_price else "<strong>$0.00</strong>"
    total_price_display.short_description = 'TOTAL'
    total_price_display.allow_tags = True
    
    def status_badge(self, obj):
        if not obj.order:
            return "No Status"
            
        status_colors = {
            'pending': 'gray',
            'confirmed': 'blue',
            'preparing': 'orange',
            'ready': 'green',
            'delivered': 'purple', 
            'completed': 'darkgreen',
            'cancelled': 'red'
        }
        color = status_colors.get(obj.order.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 15px; font-weight: bold;">⬆ {}</span>',
            color, obj.order.status.title()
        )
    status_badge.short_description = 'STATUS'
    
    def actions_display(self, obj):
        return format_html('⬇ ⬇ ⬇')
    actions_display.short_description = 'ACTIONS'