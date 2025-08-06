from django.utils.http import urlsafe_base64_decode  # imports base64 decode.
from django.utils.encoding import force_str  # imports force_str.
from django.contrib.auth.tokens import default_token_generator  # imports token generator.
from django.contrib.auth.models import User  # imports user.
from rest_framework.views import APIView  # imports apiview.
from rest_framework.response import Response  # imports response.
from rest_framework import status  # imports status codes.
from .serializers import RegistrationSerializer  # imports serializer.


class RegistrationView(APIView):  # defines registration view.
    def post(self, request):  # handles post request.
        serializer = RegistrationSerializer(data=request.data)  # initializes serializer.
        if serializer.is_valid():  # checks validity.
            user = serializer.save()  # saves user.
            # signal will handle email sending in background.
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