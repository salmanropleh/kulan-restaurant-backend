from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 'phone_number']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    # Allow login with either username or email
    username_or_email = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')
        
        if username_or_email and password:
            # Try to authenticate with username first, then email
            user = authenticate(username=username_or_email, password=password)
            if not user:
                # Try with email
                try:
                    user_obj = CustomUser.objects.get(email=username_or_email)
                    user = authenticate(username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    user = None
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            attrs['user'] = user
        return attrs

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'profile_picture', 'date_joined']
        read_only_fields = ['id', 'date_joined']