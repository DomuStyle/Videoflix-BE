# from rest_framework.permissions import BasePermission  # imports base permission.

# class HasRefreshToken(BasePermission):  # custom permission for refresh token.
#     def has_permission(self, request, view):  # checks permission.
#         return 'refresh_token' in request.COOKIES  # true if refresh token cookie exists.