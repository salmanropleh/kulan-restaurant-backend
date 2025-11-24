from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import AnonymousUser
from .models import ContactMessage
from .serializers import ContactMessageSerializer, ContactMessageCreateSerializer

class ContactMessageListView(generics.ListAPIView):
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Show all messages to admin users, user's own messages to regular users
        if self.request.user.is_staff:
            return ContactMessage.objects.all()
        else:
            # Regular users only see their own messages
            return ContactMessage.objects.filter(email=self.request.user.email)

class ContactMessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Admin users can access all messages, regular users only their own
        if self.request.user.is_staff:
            return ContactMessage.objects.all()
        else:
            return ContactMessage.objects.filter(email=self.request.user.email)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_contact_message(request):
    serializer = ContactMessageCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Message sent successfully! We will get back to you soon.'
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def message_stats(request):
    # Admin users see all stats, regular users see only their own
    if request.user.is_staff:
        total_messages = ContactMessage.objects.count()
        unread_messages = ContactMessage.objects.filter(is_read=False).count()
        read_messages = ContactMessage.objects.filter(is_read=True).count()
    else:
        # Regular users see stats for their own messages only
        user_messages = ContactMessage.objects.filter(email=request.user.email)
        total_messages = user_messages.count()
        unread_messages = user_messages.filter(is_read=False).count()
        read_messages = user_messages.filter(is_read=True).count()
    
    return Response({
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'read_messages': read_messages
    })

# USER-SPECIFIC ENDPOINTS
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_messages(request):
    """Get messages for the current user only"""
    if request.user.is_staff:
        # Admin can see all messages
        messages = ContactMessage.objects.all()
    else:
        # Regular users see only their own messages
        messages = ContactMessage.objects.filter(email=request.user.email)
    
    serializer = ContactMessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_message_stats(request):
    """Get message stats for the current user only"""
    if request.user.is_staff:
        total_messages = ContactMessage.objects.count()
        unread_messages = ContactMessage.objects.filter(is_read=False).count()
        read_messages = ContactMessage.objects.filter(is_read=True).count()
    else:
        user_messages = ContactMessage.objects.filter(email=request.user.email)
        total_messages = user_messages.count()
        unread_messages = user_messages.filter(is_read=False).count()
        read_messages = user_messages.filter(is_read=True).count()
    
    return Response({
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'read_messages': read_messages,
        'user_type': 'admin' if request.user.is_staff else 'user'
    })