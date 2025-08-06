from rest_framework import serializers  # imports serializers.
from django.contrib.auth.models import User  # imports user.
from django.core.exceptions import ValidationError  # imports validationerror.

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
        user.is_active = False  # ensures user is inactive (critical fix!).
        user.save()  # saves user, triggers signal.
        return user  # returns user.