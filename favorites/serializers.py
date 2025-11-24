from rest_framework import serializers
from .models import Favorite
from menu.serializers import MenuItemSerializer

class FavoriteSerializer(serializers.ModelSerializer):
    menu_item_details = MenuItemSerializer(source='menu_item', read_only=True)
    
    class Meta:
        model = Favorite
        fields = [
            'id', 'menu_item', 'menu_item_details', 
            'created_at', 'last_ordered', 'order_count'
        ]
        read_only_fields = ['id', 'created_at']

class CreateFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['menu_item']

class FavoriteItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    image = serializers.CharField()
    type = serializers.CharField(source='category.name')
    lastOrdered = serializers.SerializerMethodField()
    prep_time = serializers.CharField(required=False)
    serves = serializers.CharField(required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    popular = serializers.BooleanField(required=False)
    
    def get_lastOrdered(self, obj):
        return "Recently"  # You can customize this based on your data