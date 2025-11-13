from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db.models import Count
from .models import MenuCategory, MenuItem, ExtraTopping
from .serializers import MenuCategorySerializer, MenuItemSerializer, ExtraToppingSerializer

# Full CRUD for Menu Categories
class MenuCategoryViewSet(viewsets.ModelViewSet):
    queryset = MenuCategory.objects.annotate(item_count=Count('items'))  # Keep this annotation
    serializer_class = MenuCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'item_count']
    ordering = ['name']

# Full CRUD for Menu Items
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.select_related('category')
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['category', 'popular']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'popular']
    ordering = ['name']

    # Custom action to get items by category
    @action(detail=False, methods=['get'])
    def by_category(self, request, category_id=None):
        items = MenuItem.objects.filter(category_id=category_id)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

# Full CRUD for Extra Toppings
class ExtraToppingViewSet(viewsets.ModelViewSet):
    queryset = ExtraTopping.objects.all()
    serializer_class = ExtraToppingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Keep your existing function-based views for specific endpoints
@api_view(['GET'])
def featured_items(request):
    featured = MenuItem.objects.filter(popular=True)[:6]
    serializer = MenuItemSerializer(featured, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def popular_items(request):
    popular = MenuItem.objects.filter(popular=True)
    serializer = MenuItemSerializer(popular, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def menu_by_category(request, category_id):
    try:
        category = MenuCategory.objects.get(id=category_id)
        items = MenuItem.objects.filter(category=category)
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data)
    except MenuCategory.DoesNotExist:
        return Response({"error": "Category not found"}, status=404)