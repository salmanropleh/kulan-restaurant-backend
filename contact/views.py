# from rest_framework import generics, permissions, status
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from .models import ContactMessage
# from .serializers import ContactMessageSerializer, ContactMessageCreateSerializer

# class ContactMessageListView(generics.ListAPIView):
#     queryset = ContactMessage.objects.all()
#     serializer_class = ContactMessageSerializer
#     permission_classes = [permissions.IsAdminUser]

# class ContactMessageDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = ContactMessage.objects.all()
#     serializer_class = ContactMessageSerializer
#     permission_classes = [permissions.IsAdminUser]

# @api_view(['POST'])
# @permission_classes([permissions.AllowAny])
# def create_contact_message(request):
#     serializer = ContactMessageCreateSerializer(data=request.data)
    
#     if serializer.is_valid():
#         serializer.save()
#         return Response({
#             'success': True,
#             'message': 'Message sent successfully! We will get back to you soon.'
#         }, status=status.HTTP_201_CREATED)
    
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET'])
# @permission_classes([permissions.IsAdminUser])
# def message_stats(request):
#     total_messages = ContactMessage.objects.count()
#     unread_messages = ContactMessage.objects.filter(is_read=False).count()
#     read_messages = ContactMessage.objects.filter(is_read=True).count()
    
#     return Response({
#         'total_messages': total_messages,
#         'unread_messages': unread_messages,
#         'read_messages': read_messages
#     })


from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import ContactMessage
from .serializers import ContactMessageSerializer, ContactMessageCreateSerializer

class ContactMessageListView(generics.ListAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]  # Changed to AllowAny

class ContactMessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]  # Changed to AllowAny

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
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Changed to AllowAny
def message_stats(request):
    total_messages = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    read_messages = ContactMessage.objects.filter(is_read=True).count()
    
    return Response({
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'read_messages': read_messages
    })