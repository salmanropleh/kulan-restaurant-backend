from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReservationViewSet, ReservationStatsView

router = DefaultRouter()
router.register(r'reservations', ReservationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', ReservationStatsView.as_view(), name='reservation-stats'),
]