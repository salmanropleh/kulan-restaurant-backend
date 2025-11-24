# favorites/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Favorite
from .serializers import FavoriteSerializer, CreateFavoriteSerializer
from menu.models import MenuItem


class FavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return appropriate queryset based on user role and action.
        Regular users see only their favorites, admins see all for admin_list.
        """
        if self.request.user.is_staff and self.action == 'admin_list':
            # Admins can see all favorites for admin_list action
            return Favorite.objects.all().select_related('user', 'menu_item', 'menu_item__category')
        # Regular users only see their own favorites
        return Favorite.objects.filter(user=self.request.user).select_related('menu_item', 'menu_item__category')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return CreateFavoriteSerializer
        return FavoriteSerializer
    
    def perform_create(self, serializer):
        """Automatically set the current user when creating a favorite."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_favorites(self, request):
        """Get current user's favorites with menu item details."""
        favorites = self.get_queryset()
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Toggle favorite status for a menu item."""
        menu_item_id = request.data.get('menu_item_id')
        
        if not menu_item_id:
            return Response(
                {'error': 'menu_item_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            menu_item = MenuItem.objects.get(id=menu_item_id)
        except MenuItem.DoesNotExist:
            return Response(
                {'error': 'Menu item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        favorite = Favorite.objects.filter(
            user=request.user, 
            menu_item=menu_item
        ).first()
        
        if favorite:
            # Remove from favorites
            favorite.delete()
            return Response({
                'status': 'removed',
                'message': 'Item removed from favorites'
            })
        else:
            # Add to favorites
            favorite = Favorite.objects.create(
                user=request.user,
                menu_item=menu_item
            )
            serializer = FavoriteSerializer(favorite)
            return Response({
                'status': 'added',
                'message': 'Item added to favorites',
                'favorite': serializer.data
            })
    
    @action(detail=False, methods=['get'])
    def favorites_list(self, request):
        """Get simplified favorites list for frontend."""
        favorites = self.get_queryset()
        
        # Transform to match frontend expected format
        favorites_data = []
        for favorite in favorites:
            menu_item = favorite.menu_item
            favorites_data.append({
                'id': menu_item.id,
                'name': menu_item.name,
                'description': menu_item.description,
                'price': str(menu_item.price),
                'image': menu_item.image.url if menu_item.image else '',
                'type': menu_item.category.name if menu_item.category else 'Uncategorized',
                'lastOrdered': 'Recently',  # You can implement actual tracking
                'prep_time': getattr(menu_item, 'prep_time', ''),
                'serves': getattr(menu_item, 'serves', ''),
                'tags': getattr(menu_item, 'tags', []),
                'popular': getattr(menu_item, 'popular', False)
            })
        
        return Response(favorites_data)
    
    @action(detail=False, methods=['post'])
    def bulk_add(self, request):
        """Add multiple items to favorites (for migration from localStorage)."""
        menu_item_ids = request.data.get('menu_item_ids', [])
        
        if not menu_item_ids:
            return Response(
                {'error': 'menu_item_ids is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_count = 0
        with transaction.atomic():
            for menu_item_id in menu_item_ids:
                try:
                    menu_item = MenuItem.objects.get(id=menu_item_id)
                    favorite, created = Favorite.objects.get_or_create(
                        user=request.user,
                        menu_item=menu_item
                    )
                    if created:
                        created_count += 1
                except MenuItem.DoesNotExist:
                    continue
        
        return Response({
            'message': f'Added {created_count} items to favorites',
            'added_count': created_count
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def admin_list(self, request):
        """Admin endpoint to get ALL favorites."""
        favorites = Favorite.objects.all().select_related('user', 'menu_item', 'menu_item__category')
        
        # Transform data for admin view
        favorites_data = []
        for favorite in favorites:
            favorites_data.append({
                'id': favorite.id,
                'user': {
                    'id': favorite.user.id,
                    'username': favorite.user.username,
                    'email': favorite.user.email,
                },
                'menu_item': {
                    'id': favorite.menu_item.id,
                    'name': favorite.menu_item.name,
                    'category': {
                        'name': favorite.menu_item.category.name if favorite.menu_item.category else 'Uncategorized'
                    } if favorite.menu_item.category else None
                },
                'created_at': favorite.created_at.isoformat() if favorite.created_at else None,
            })
        
        return Response(favorites_data)