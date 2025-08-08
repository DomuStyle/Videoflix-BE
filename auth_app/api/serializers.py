from rest_framework import serializers  # imports serializers.
from django.contrib.auth.models import User  # imports user.
from django.core.exceptions import ValidationError  # imports validationerror.
from rest_framework_simplejwt.tokens import RefreshToken  # imports refresh token for manual generation.

class RegistrationSerializer(serializers.ModelSerializer):  # defines registration serializer.
    confirmed_password = serializers.CharField(write_only=True)  # adds confirmed password field.

    class Meta:  # meta class for config.
        model = User  # uses user model.
        fields = ['email', 'password', 'confirmed_password']  # fields to serialize.
        extra_kwargs = {'password': {'write_only': True}}  # makes password write-only.

    def validate(self, attrs):  # validates data.
        if attrs['password'] != attrs['confirmed_password']:  # checks password match.
            raise ValidationError("Passwords do not match")  # raises error if mismatch.
        if User.objects.filter(email=attrs['email']).exists():  # checks if email exists.
            raise ValidationError("Email already exists")  # raises error.
        return attrs  # returns validated attrs.

    def create(self, validated_data):  # creates user.
        user = User(  # creates user instance.
            username=validated_data['email'],  # uses email as username.
            email=validated_data['email'],  # sets email.
        )
        user.set_password(validated_data['password'])  # hashes and sets password.
        user.is_active = False  # ensures user is inactive.
        user.save()  # saves user, triggers signal.
        return user  # returns user.

class CookieTokenObtainPairSerializers(serializers.Serializer):  # defines login serializer.
    email = serializers.EmailField()  # email field for login.
    password = serializers.CharField(write_only=True)  # password field, write-only.

    def validate(self, attrs):  # validates input.
        email = attrs.get("email")  # gets email from request.
        password = attrs.get("password")  # gets password from request.

        try:
            user = User.objects.get(email=email)  # finds user by email.
        except User.DoesNotExist:
            raise serializers.ValidationError("Wrong email or password")  # raises error if user not found.

        if not user.check_password(password):  # checks password.
            raise serializers.ValidationError("Wrong email or password")  # raises error if password wrong.

        if not user.is_active:  # checks if user is active.
            raise serializers.ValidationError("Account not activated")  # raises error if inactive.

        refresh = RefreshToken.for_user(user)  # creates refresh token for user.
        data = {
            'refresh': str(refresh),  # refresh token as string.
            'access': str(refresh.access_token),  # access token as string.
            'user': {'id': user.id, 'username': user.username}  # user info for view response.
        }
        return data  # returns token data.