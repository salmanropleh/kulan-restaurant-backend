from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FavoriteViewSet

router = DefaultRouter()
router.register(r'favorites', FavoriteViewSet, basename='favorites')

app_name = 'favorites'

urlpatterns = [
    path('', include(router.urls)),
]