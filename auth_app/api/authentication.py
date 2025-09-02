from rest_framework_simplejwt.authentication import JWTAuthentication  # imports base jwt auth.
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed  # imports exceptions.
from django.utils.translation import gettext_lazy as _  # for translations.


import logging  # ADDITION: Import for logging.

logger = logging.getLogger(__name__)  # ADDITION: Logger instance.

class CookieJWTAuthentication(JWTAuthentication):  # Unchanged.
    def authenticate(self, request):  # Unchanged structure.
        header = self.get_header(request)  # Unchanged.

        if header is None:  # Unchanged.
            raw_token = request.COOKIES.get('access_token')  # Unchanged.
            if raw_token is None:  # Unchanged.
                logger.warning("No access_token cookie found in request")  # ADDITION: Log if no cookie (helps debug if not sent).
                return None  # Unchanged.
        else:
            raw_token = self.get_raw_token(header)  # Unchanged.

        if raw_token is None:  # Unchanged.
            logger.warning("No raw token found in header or cookie")  # ADDITION: Log if no token at all.
            return None  # Unchanged.

        try:  # ADDITION: Wrap validation in try-except for logging errors.
            validated_token = self.get_validated_token(raw_token)  # Unchanged.
            user, token = self.get_user(validated_token), validated_token  # Slight change: Get user here.
            logger.info(f"Token validated for user: {user.username if user else 'None'}")  # ADDITION: Log successful validation.
            return user, token  # Unchanged.
        except (InvalidToken, AuthenticationFailed) as e:  # ADDITION: Catch and log exceptions (e.g., expired/invalid token).
            logger.error(f"Token validation failed: {str(e)}")  # Log error.
            return None  # Return None on failure.