from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import CustomUser
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)
    confirm_password = serializers.CharField(write_only = True)
    id = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'addres', 'password', 'confirm_password']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError({'msg': 'Parollar mos emas', 'status': status.HTTP_400_BAD_REQUEST})

    def validate_username(self, username):
        if CustomUser.objects.filter(username=username):
            raise ValidationError({'msg': "Bu Username band", 'status': status.HTTP_400_BAD_REQUEST})
        return username

    def validate_email(self, email):
        if CustomUser.objects.filter(email=email):
            raise ValidationError("BU Email band.")
        return email

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["status"] = status.HTTP_201_CREATED
        data["msg"] = "SignUp successful"

        return data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            raise ValidationError({'msg': "Username yoki parol noto'g'ri", 'status': status.HTTP_400_BAD_REQUEST})

        attrs['user'] = user

        return attrs
    def to_representation(self, instance):
        user = instance.get('user')


        refresh = RefreshToken.for_user(user)
        return {
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ["id","first_name","last_name","username","email","addres",]


    