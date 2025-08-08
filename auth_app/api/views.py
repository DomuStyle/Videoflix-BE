from django.conf import settings
from django.core.mail import send_mail  # for email.
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode  # imports base64 decode.
from django.utils.encoding import force_str, force_bytes  # imports force_str.
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator  # imports token generator.
from django.contrib.auth.models import User  # imports user.
from rest_framework.views import APIView  # imports apiview.
from rest_framework.response import Response  # imports response.
from rest_framework import status  # imports status codes.
from .serializers import RegistrationSerializer, CookieTokenObtainPairSerializers, PasswordResetSerializer, PasswordConfirmSerializer  # imports serializers.
from rest_framework_simplejwt.views import TokenRefreshView  # imports token view.
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import UntypedToken, TokenError  # imports for token validation.
from rest_framework_simplejwt.exceptions import InvalidToken  # imports invalid token error.
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken  # imports for blacklisting.
import django_rq


class RegistrationView(APIView):  # defines registration view.
    def post(self, request):  # handles post request.
        serializer = RegistrationSerializer(data=request.data)  # initializes serializer.
        if serializer.is_valid():  # checks validity.
            user = serializer.save()  # saves user.
            return Response({  # returns success response.
                'user': {'id': user.id, 'email': user.email},  # user info.
                'token': 'activation_token'  # placeholder, actual token in email.
            }, status=status.HTTP_201_CREATED)  # 201 status.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # error response.

class ActivationView(APIView):  # defines activation view.
    def get(self, request, uidb64, token):  # handles get request.
        try:  # tries to decode uid.
            uid = force_str(urlsafe_base64_decode(uidb64))  # decodes uidb64 to id.
            user = User.objects.get(pk=uid)  # gets user by id.
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):  # catches invalid uid.
            return Response({'message': 'Activation failed'}, status=status.HTTP_400_BAD_REQUEST)  # returns 400.
        
        if default_token_generator.check_token(user, token):  # checks if token is valid.
            user.is_active = True  # activates user.
            user.save()  # saves user.
            return Response({'message': 'Account successfully activated.'}, status=status.HTTP_200_OK)  # returns success.
        return Response({'message': 'Activation failed'}, status=status.HTTP_400_BAD_REQUEST)  # returns 400 for invalid token.

class CookieTokenObtainPairView(APIView):  # defines login view.
    def post(self, request, *args, **kwargs):  # handles post request.
        serializer = CookieTokenObtainPairSerializers(data=request.data)  # initializes serializer.
        serializer.is_valid(raise_exception=True)  # validates, raises 400 on error.
        
        response = Response({  # creates response.
            "detail": "Login successful",  # matches test expectation.
            "user": serializer.validated_data['user']  # uses user info from serializer.
        })
        refresh = serializer.validated_data["refresh"]  # gets refresh token.
        access = serializer.validated_data["access"]  # gets access token.

        response.set_cookie(  # sets access token cookie.
            key="access_token",
            value=str(access),
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        response.set_cookie(  # sets refresh token cookie.
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        return response  # returns response.

class LogoutView(APIView):  # defines logout view.
    def post(self, request):  # handles post request.
        refresh_token = request.COOKIES.get('refresh_token')  # gets refresh token from cookie.
        if refresh_token is None:  # checks if missing.
            return Response({"detail": "Refresh token missing."}, status=status.HTTP_400_BAD_REQUEST)  # returns 400.

        try:
            token = UntypedToken(refresh_token)  # validates token.
        except (InvalidToken, TokenError):  # catches invalid token.
            return Response({'detail': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)  # returns 400.

        # blacklist the refresh token
        outstanding_token = OutstandingToken.objects.filter(user_id=token['user_id'], token=refresh_token).first()
        if outstanding_token:
            BlacklistedToken.objects.get_or_create(token=outstanding_token)  # blacklists it.

        response = Response({'detail': 'Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid.'})  # success response.
        response.delete_cookie('access_token')  # deletes access token cookie.
        response.delete_cookie('refresh_token')  # deletes refresh token cookie.
        return response  # returns response.
    
class TokenRefreshViewCustom(TokenRefreshView):  # defines custom refresh view.
    def post(self, request):  # handles post request.
        refresh_token = request.COOKIES.get('refresh_token')  # gets refresh token from cookie.
        if not refresh_token:  # checks if missing.
            return Response({"detail": "Refresh token missing."}, status=status.HTTP_400_BAD_REQUEST)  # returns 400.

        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})  # initializes serializer with refresh.

        try:
            serializer.is_valid(raise_exception=True)  # validates token, raises on error.
        except (InvalidToken, TokenError):  # catches invalid or malformed token.
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)  # returns 401.

        access_token = serializer.validated_data['access']  # gets new access token.

        response = Response({  # creates response.
            "detail": "Token refreshed",  # detail message.
            "access": access_token  # new access token.
        })
        response.set_cookie(  # sets new access token cookie.
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        return response  # returns response.
    
def send_reset_email_task(instance):  # top-level task for RQ.
    uid = urlsafe_base64_encode(force_bytes(instance.pk))  # encodes user id.
    token = PasswordResetTokenGenerator().make_token(instance)  # generates reset token.
    reset_link = f"http://your-frontend-ip/pages/auth/reset.html?uidb64={uid}&token={token}"  # frontend link (adapt if needed).
    send_mail(
        'Reset Your Password',  # subject.
        f'Click here to reset your password: {reset_link}',  # body.
        settings.DEFAULT_FROM_EMAIL,  # from email.
        [instance.email],  # to email.
    )

class PasswordResetView(APIView):  # defines password reset view.
    def post(self, request):  # handles post request.
        serializer = PasswordResetSerializer(data=request.data)  # initializes serializer.
        if serializer.is_valid():  # checks validity.
            email = serializer.validated_data['email']  # gets email.
            try:
                user = User.objects.get(email=email)  # finds user if exists.
            except User.DoesNotExist:
                user = None  # no user, but still "send" email per doc.

            # always "send" email, even if no user (queue task or simulate)
            if user:
                if getattr(settings, 'TESTING', False):  # sync in tests.
                    send_reset_email_task(user)  # runs directly.
                else:
                    django_rq.enqueue(send_reset_email_task, user)  # queues with RQ.
            else:
                # for non-existent, simulate send (queue dummy or empty task, but since doc says "always send", send to the email anyway)
                if getattr(settings, 'TESTING', False):
                    send_mail('Reset Your Password', 'If an account exists, a reset link has been sent.', settings.DEFAULT_FROM_EMAIL, [email])
                else:
                    django_rq.enqueue(send_mail, 'Reset Your Password', 'If an account exists, a reset link has been sent.', settings.DEFAULT_FROM_EMAIL, [email])

            return Response({'detail': 'An email has been sent to reset your password.'}, status=status.HTTP_200_OK)  # returns 200.

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # returns 400 for invalid email.
    
class PasswordConfirmView(APIView):  # defines password confirm view.
    def post(self, request, uidb64, token):  # handles post request with params.
        serializer = PasswordConfirmSerializer(data=request.data)  # initializes serializer.
        if not serializer.is_valid():  # checks validity.
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # returns 400 for mismatch/invalid.

        try:  # tries to decode uid.
            uid = force_str(urlsafe_base64_decode(uidb64))  # decodes uidb64 to id.
            user = User.objects.get(pk=uid)  # gets user by id.
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):  # catches invalid uid.
            return Response({'detail': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)  # returns 400.

        if PasswordResetTokenGenerator().check_token(user, token):  # checks if token is valid.
            user.set_password(serializer.validated_data['new_password'])  # sets new password.
            user.save()  # saves user.
            return Response({'detail': 'Your Password has been successfully reset.'}, status=status.HTTP_200_OK)  # returns 200.
        return Response({'detail': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)  # returns 400 for invalid token.