from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('check-auth/', views.check_auth, name='check-auth'),
]