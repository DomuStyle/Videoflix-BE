"""Custom JWT authentication for handling token-based authentication via cookies.

This module extends the Django REST Framework Simple JWT authentication to support
token extraction from cookies, with added logging for debugging and monitoring.
"""

import logging
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed

logger = logging.getLogger(__name__)


class CookieJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication class to extract tokens from cookies or headers."""
    
    def authenticate(self, request):
        """Authenticate a user by validating a JWT token from headers or cookies.

        Args:
            request: The HTTP request object containing headers or cookies.

        Returns:
            tuple: A tuple of (user, validated_token) if authentication succeeds,
                   or None if no valid token is found or validation fails.
        """
        header = self.get_header(request)

        if header is None:
            # Check for access token in cookies if no Authorization header
            raw_token = request.COOKIES.get('access_token')
            if raw_token is None:
                logger.warning("No access token found in cookies")
                return None
        else:
            # Extract raw token from Authorization header
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            logger.warning("No token found in header or cookies")
            return None

        try:
            # Validate token and retrieve associated user
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            logger.info(f"Successfully authenticated user: {user.username}")
            return user, validated_token
        except (InvalidToken, AuthenticationFailed) as e:
            # Log token validation errors (e.g., expired or invalid token)
            logger.error(f"Token validation failed: {str(e)}")
            return None