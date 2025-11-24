from django.contrib import admin
from .models import Favorite

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'menu_item', 'created_at')
    list_filter = ('created_at', 'menu_item__category')
    search_fields = ('user__email', 'user__username', 'menu_item__name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'menu_item', 'menu_item__category')