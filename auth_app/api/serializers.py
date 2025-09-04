"""User authentication serializers for the Django REST Framework API.

This module defines serializers for user registration, login, and password reset
functionality, leveraging Django's User model and Simple JWT for token-based
authentication.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with email and password validation."""
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        """Configuration for the RegistrationSerializer."""
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        """Validate that passwords match and email is unique.

        Args:
            attrs (dict): The input data to validate.

        Returns:
            dict: Validated attributes.

        Raises:
            ValidationError: If passwords don't match or email already exists.
        """
        if attrs['password'] != attrs['confirmed_password']:
            raise ValidationError("Passwords do not match")
        
        if User.objects.filter(email=attrs['email']).exists():
            raise ValidationError("Email already exists")
        
        return attrs

    def create(self, validated_data):
        """Create a new user with the provided email and password.

        Args:
            validated_data (dict): Validated data containing email and password.

        Returns:
            User: The created user instance.
        """
        user = User(
            username=validated_data['email'],  # Use email as username
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.is_active = False  # Require activation before login
        user.save()
        return user


class CookieTokenObtainPairSerializers(serializers.Serializer):
    """Serializer for user login with email and password."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate user credentials and generate JWT tokens.

        Args:
            attrs (dict): Input data containing email and password.

        Returns:
            dict: Token data and user information.

        Raises:
            ValidationError: If credentials are invalid or account is inactive.
        """
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Wrong email or password")

        if not user.check_password(password):
            raise serializers.ValidationError("Wrong email or password")

        if not user.is_active:
            raise serializers.ValidationError("Account not activated")

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {'id': user.id, 'username': user.username}
        }


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for initiating a password reset via email."""
    email = serializers.EmailField(required=True)


class PasswordConfirmSerializer(serializers.Serializer):
    """Serializer for confirming and setting a new password."""
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        """Validate that the new password and confirmation match.

        Args:
            attrs (dict): Input data containing new and confirm passwords.

        Returns:
            dict: Validated attributes.

        Raises:
            ValidationError: If passwords do not match.
        """
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs