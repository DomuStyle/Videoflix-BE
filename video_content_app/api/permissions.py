"""Custom permission classes for the Django REST Framework API.

This module defines a custom permission to enforce JWT-based authentication.
"""

from rest_framework.permissions import IsAuthenticated


class IsJWTAuthenticated(IsAuthenticated):
    """Custom permission to enforce JWT-based authentication."""
    message = 'JWT authentication required.'  # Custom error message for unauthorized requests