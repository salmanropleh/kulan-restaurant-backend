from rest_framework import serializers
from .models import MenuCategory, MenuItem, ExtraTopping

class ExtraToppingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraTopping
        fields = ['name', 'price']

class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    extra_toppings = ExtraToppingSerializer(many=True, read_only=True)
    spice_level_display = serializers.CharField(source='get_spice_level_display', read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'detailed_description', 'price', 
            'image', 'popular', 'prep_time', 'serves', 'ingredients', 
            'calories', 'protein', 'carbs', 'fat', 'rating', 'tags',
            'category', 'category_name', 'extra_toppings',
            'spice_level', 'spice_level_display', 'customizable_spice'
        ]

class MenuCategorySerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()  # Change to SerializerMethodField

    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'description', 'items', 'item_count', 'created_at', 'updated_at']

    def get_item_count(self, obj):
        # This will use the annotated item_count if available, otherwise count manually
        if hasattr(obj, 'item_count'):
            return obj.item_count
        return obj.items.count()