from rest_framework.permissions import IsAuthenticated  # imports authenticated permission.

class IsJWTAuthenticated(IsAuthenticated):  # custom permission for jwt.
    message = 'JWT authentication required.'  # custom message for 401.