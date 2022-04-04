import imp

from marshmallow import ValidationError
from UserManagement.models import Users
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from django.contrib.auth.models import BaseUserManager

User = Users()

class UserLoginSerializer(serializers.Serializer):
    Mobile = serializers.CharField(max_length = 10)


class AuthUserSerializer(serializers.ModelSerializer):
    auth_token = serializers.SerializerMethodField()

    class Meta:
         model = Users
         fields = ('Mobile','auth_token','otp')
    
    def get_auth_token(self, obj):
        token = Token.objects.get_or_create(user=obj)
        print(token)
        print(token[0])
        return token[0].key



class UserRegisterSerializer(serializers.ModelSerializer):
    """
    A user serializer for registering the user
    """

    class Meta:
        model = Users
        fields = ('Mobile',)

    def validate_mobile(self, value):
        if len(value) != 10:
            raise serializers.ValidationError("mobile length error")
        return str(value)

    # def validate_otp(self, value):
    #     user = User.objects.filter(mobile=value)
    #     if user.otp == value:
    #         return value
    #     else:
    #         raise ValidationError("Invalid OTP")