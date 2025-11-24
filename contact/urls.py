from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_contact_message, name='contact-create'),
    path('messages/', views.ContactMessageListView.as_view(), name='contact-messages'),
    path('messages/<int:pk>/', views.ContactMessageDetailView.as_view(), name='contact-message-detail'),
    path('stats/', views.message_stats, name='contact-stats'),
    
    # USER-SPECIFIC ENDPOINTS
    path('user/messages/', views.user_messages, name='user-messages'),
    path('user/stats/', views.user_message_stats, name='user-stats'),
]