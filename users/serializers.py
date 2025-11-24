from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        min_length=6,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 'phone_number']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Check if email already exists
        if CustomUser.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
            
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        # Ensure new users are not staff/superuser by default
        validated_data['is_staff'] = False
        validated_data['is_superuser'] = False
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
            if not user.is_active:
                raise serializers.ValidationError('Account is disabled')
            attrs['user'] = user
        return attrs

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'phone_number', 'profile_picture', 
            'date_joined', 'is_staff', 'is_superuser', 'is_active'
        ]
        read_only_fields = ['id', 'date_joined', 'is_staff', 'is_superuser', 'is_active']

class UserAdminSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=6)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'phone_number', 'profile_picture', 'password',
            'date_joined', 'last_login', 'is_staff', 'is_superuser', 'is_active'
        ]
        read_only_fields = ['date_joined', 'last_login']
    
    def create(self, validated_data):
        # Extract password
        password = validated_data.pop('password', None)
        
        # Create user
        user = CustomUser.objects.create(**validated_data)
        
        # Set password if provided
        if password:
            user.set_password(password)
            user.save()
        
        return user
    
    def update(self, instance, validated_data):
        # Handle password separately if provided
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance