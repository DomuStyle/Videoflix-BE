"""URL configuration for the authentication API endpoints.

This module defines URL patterns for user authentication, including login, logout,
registration, account activation, token refresh, and password reset functionality.
"""

from django.urls import path
from .views import (
    RegistrationView,
    ActivationView,
    CookieTokenObtainPairView,
    LogoutView,
    TokenRefreshViewCustom,
    PasswordResetView,
    PasswordConfirmView,
)


urlpatterns = [
    path('login/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshViewCustom.as_view(), name='token_refresh'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('activate/<str:uidb64>/<str:token>/', ActivationView.as_view(), name='activate'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_confirm/<str:uidb64>/<str:token>/', PasswordConfirmView.as_view(), name='password_confirm'),
]