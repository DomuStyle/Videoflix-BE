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