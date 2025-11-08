from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.MenuCategoryViewSet)
router.register(r'items', views.MenuItemViewSet)
router.register(r'toppings', views.ExtraToppingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Specific category endpoints (keep these for your frontend)
    path('category/breakfast/', views.menu_by_category, {'category_id': 'breakfast'}, name='breakfast-items'),
    path('category/lunch/', views.menu_by_category, {'category_id': 'lunch'}, name='lunch-items'),
    path('category/dinner/', views.menu_by_category, {'category_id': 'dinner'}, name='dinner-items'),
    path('category/afternoon-tea/', views.menu_by_category, {'category_id': 'afternoon'}, name='afternoon-items'),
    path('category/desserts/', views.menu_by_category, {'category_id': 'desserts'}, name='desserts-items'),
    path('category/kulan-specialties/', views.menu_by_category, {'category_id': 'specials'}, name='specials-items'),
    path('category/beverages/', views.menu_by_category, {'category_id': 'beverages'}, name='beverages-items'),
    
    # Other endpoints
    path('popular/', views.popular_items, name='popular-items'),
    path('featured/', views.featured_items, name='featured-items'),
    path('category/<str:category_id>/', views.menu_by_category, name='menu-by-category'),
]