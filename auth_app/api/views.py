"""API views for user authentication and password management.

This module defines views for user registration, account activation, login, logout,
token refresh, and password reset functionality, integrating with Django REST
Framework and Simple JWT for token-based authentication.
"""

from django.conf import settings
from django.core.mail import send_mail 
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode 
from django.utils.encoding import force_str, force_bytes 
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from django.contrib.auth.models import User  
from rest_framework.views import APIView  
from rest_framework.response import Response  
from rest_framework import status  
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView 
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import UntypedToken, TokenError  
from rest_framework_simplejwt.exceptions import InvalidToken  
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken 
from .serializers import RegistrationSerializer, CookieTokenObtainPairSerializers, PasswordResetSerializer, PasswordConfirmSerializer  
import django_rq


class RegistrationView(APIView):
    """Handle user registration via email and password."""
    authentication_classes = []  
    permission_classes = [AllowAny] 

    def post(self, request): 
        """Process registration requests and create inactive users.

        Args:
            request: The HTTP request object containing user data.

        Returns:
            Response: Success response with user info or error details.
        """
        serializer = RegistrationSerializer(data=request.data) 
        if serializer.is_valid():  
            user = serializer.save()  
            return Response({  
                'user': {'id': user.id, 'email': user.email}, 
                'token': 'activation_token'  # Placeholder for activation token sent via email
            }, status=status.HTTP_201_CREATED)  
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivationView(APIView):
    """Handle account activation via emailed token."""

    def get(self, request, uidb64, token):
        """Activate a user account using a base64-encoded UID and token.

        Args:
            request: The HTTP request object.
            uidb64 (str): Base64-encoded user ID.
            token (str): Activation token.

        Returns:
            Response: Success or error message based on activation result.
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'message': 'Activation failed'}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Account successfully activated.'}, status=status.HTTP_200_OK)  
        return Response({'message': 'Activation failed'}, status=status.HTTP_400_BAD_REQUEST) 


class CookieTokenObtainPairView(APIView):
    """Handle user login with cookie-based JWT tokens."""
    authentication_classes = [] 
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Process login requests and set JWT tokens in cookies.

        Args:
            request: The HTTP request object containing email and password.
            *args: Variable positional arguments.
            **kwargs: Variable keyword arguments.

        Returns:
            Response: Success response with user info and tokens set in cookies.
        """
        serializer = CookieTokenObtainPairSerializers(data=request.data)  
        serializer.is_valid(raise_exception=True) 
        
        response = Response({  
            "detail": "Login successful",  
            "user": serializer.validated_data['user'] 
        })
        # Set access and refresh tokens in HTTP-only cookies
        refresh = serializer.validated_data["refresh"]  
        access = serializer.validated_data["access"]  

        response.set_cookie(
            key="access_token",
            value=serializer.validated_data['access'],
            httponly=True,
            secure=False if settings.DEBUG else True,
            samesite="None",
            # path='/' 
        )
        response.set_cookie(
            key="refresh_token",
            value=serializer.validated_data['refresh'],
            httponly=True,
            secure=False if settings.DEBUG else True,
            samesite="None",
            #path='/'  
        )
        return response


class LogoutView(APIView):
    """Handle user logout by blacklisting refresh tokens."""

    def post(self, request):
        """Process logout requests and clear token cookies.

        Args:
            request: The HTTP request object containing the refresh token cookie.

        Returns:
            Response: Success or error message based on logout result.
        """
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token is None:  
            return Response({"detail": "Refresh token missing."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = UntypedToken(refresh_token)
        except (InvalidToken, TokenError): 
            return Response({'detail': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)

        # Blacklist the refresh token if it exists
        outstanding_token = OutstandingToken.objects.filter(user_id=token['user_id'], token=refresh_token).first()
        if outstanding_token:
            BlacklistedToken.objects.get_or_create(token=outstanding_token)

        response = Response({'detail': 'Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid.'})
        response.delete_cookie('access_token') 
        response.delete_cookie('refresh_token') 
        return response


class TokenRefreshViewCustom(TokenRefreshView):
    """Handle token refresh using refresh token from cookies."""

    def post(self, request):
        """Generate a new access token from a refresh token.

        Args:
            request: The HTTP request object containing the refresh token cookie.

        Returns:
            Response: Success response with new access token or error details.
        """
        refresh_token = request.COOKIES.get('refresh_token')  
        if not refresh_token: 
            return Response({"detail": "Refresh token missing."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except (InvalidToken, TokenError):
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)

        access_token = serializer.validated_data['access']

        response = Response({  
            "detail": "Token refreshed",  
            "access": access_token  
        })
        # Set new access token in HTTP-only cookie
        response.set_cookie(  
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False if settings.DEBUG else True, 
            samesite="None"  
        )
        return response


def send_reset_email_task(instance):
    """Queue a password reset email task for a user.

    Args:
        instance: The User instance to send the reset email for.
    """
    uid = urlsafe_base64_encode(force_bytes(instance.pk))  
    token = PasswordResetTokenGenerator().make_token(instance) 
    frontend_url = 'http://localhost:5500'
    reset_link = f"{frontend_url}/pages/auth/confirm_password.html?uid={uid}&token={token}"
    send_mail(
        'Reset Your Password', 
        f'Click here to reset your password: {reset_link}',
        settings.DEFAULT_FROM_EMAIL, 
        [instance.email],
    )


class PasswordResetView(APIView):
    """Handle password reset requests by sending reset emails."""

    def post(self, request):
        """Process password reset requests and queue email tasks.

        Args:
            request: The HTTP request object containing the email.

        Returns:
            Response: Success message or error details.
        """
        serializer = PasswordResetSerializer(data=request.data) 
        if serializer.is_valid():  
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)  
            except User.DoesNotExist:
                user = None  

            # Always simulate sending email, even for non-existent users
            if user:
                if getattr(settings, 'TESTING', False): 
                    send_reset_email_task(user)
                else:
                    django_rq.enqueue(send_reset_email_task, user)
            else:
                # Simulate email for non-existent users to prevent enumeration
                if getattr(settings, 'TESTING', False):
                    send_mail('Reset Your Password', 'If an account exists, a reset link has been sent.', 
                    settings.DEFAULT_FROM_EMAIL, [email])
                else:
                    django_rq.enqueue(send_mail, 'Reset Your Password', 'If an account exists, a reset link has been sent.', 
                    settings.DEFAULT_FROM_EMAIL, [email])

            return Response({'detail': 'An email has been sent to reset your password.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordConfirmView(APIView):
    """Handle password reset confirmation with new password."""
    authentication_classes = []
    permission_classes = [AllowAny] 

    def post(self, request, uidb64, token): 
        """Set a new password using a reset token.

        Args:
            request: The HTTP request object containing new password data.
            uidb64 (str): Base64-encoded user ID.
            token (str): Password reset token.

        Returns:
            Response: Success or error message based on reset result.
        """
        serializer = PasswordConfirmSerializer(data=request.data) 
        if not serializer.is_valid():  
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

        try:  
            uid = force_str(urlsafe_base64_decode(uidb64))  
            user = User.objects.get(pk=uid) 
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):  
            return Response({'detail': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)

        if PasswordResetTokenGenerator().check_token(user, token):  
            user.set_password(serializer.validated_data['new_password'])  
            user.save() 
            return Response({'detail': 'Your Password has been successfully reset.'}, status=status.HTTP_200_OK) 
        return Response({'detail': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)