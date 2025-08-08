from django.urls import path  # imports path.
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegistrationView, ActivationView, CookieTokenObtainPairView, LogoutView, TokenRefreshViewCustom, PasswordResetView # imports view.

urlpatterns = [  # url patterns list.
    path('login/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),  # logout url.
    path('token/refresh/', TokenRefreshViewCustom.as_view(), name='token_refresh'),
    path('register/', RegistrationView.as_view(), name='register'),  # registration url.
    path('activate/<str:uidb64>/<str:token>/', ActivationView.as_view(), name='activate'),  # activation url.
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),  # reset url.
]