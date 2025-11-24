from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetToken
from .serializers import ForgotPasswordSerializer, ResetPasswordSerializer

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Create reset token
        reset_token = PasswordResetToken.objects.create(user=user)
        
        # FIXED: Use correct frontend URL with port 5173
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{reset_token.token}/"
        
        # TODO: Implement actual email sending
        print(f"Password reset link for {email}: {reset_link}")
        
        return Response({
            "message": "If an account with this email exists, a reset link has been sent.",
            "reset_link": reset_link  # Remove in production
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    
    if serializer.is_valid():
        reset_token = serializer.validated_data['reset_token']
        new_password = serializer.validated_data['new_password']
        
        # Update user password
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        reset_token.mark_used()
        
        return Response({
            "message": "Password has been reset successfully. You can now login with your new password."
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def validate_reset_token(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token, used=False)
        if reset_token.is_valid():
            return Response({
                "valid": True,
                "email": reset_token.user.email
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "valid": False,
                "error": "This reset link has expired."
            }, status=status.HTTP_400_BAD_REQUEST)
    except PasswordResetToken.DoesNotExist:
        return Response({
            "valid": False,
            "error": "Invalid reset link."
        }, status=status.HTTP_400_BAD_REQUEST)