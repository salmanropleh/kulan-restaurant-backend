from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_contact_message, name='contact-create'),
    path('messages/', views.ContactMessageListView.as_view(), name='contact-messages'),
    path('messages/<int:pk>/', views.ContactMessageDetailView.as_view(), name='contact-message-detail'),
    path('messages/stats/', views.message_stats, name='contact-stats'),  # Move stats under messages
]