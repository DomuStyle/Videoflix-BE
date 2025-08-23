from rest_framework_simplejwt.authentication import JWTAuthentication  # imports base jwt auth.
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed  # imports exceptions.
from django.utils.translation import gettext_lazy as _  # for translations.

class CookieJWTAuthentication(JWTAuthentication):  # custom jwt auth for cookies/headers.
    def authenticate(self, request):  # overrides authenticate method.
        header = self.get_header(request)  # gets authorization header (default).

        if header is None:  # if no header.
            raw_token = request.COOKIES.get('access_token')  # checks cookie for access_token.
            if raw_token is None:  # if no cookie either.
                return None  # no authentication.
        else:
            raw_token = self.get_raw_token(header)  # extracts from header if present.

        if raw_token is None:  # if no token found.
            return None  # no authentication.

        validated_token = self.get_validated_token(raw_token)  # validates token.

        return self.get_user(validated_token), validated_token  # returns user and token.