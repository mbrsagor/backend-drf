import datetime
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.utils import datetime_to_epoch

from django.contrib.auth.models import User



SUPERUSER_LIFETIME = datetime.timedelta(minutes=90)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    :param
    Here, `TokenObtainPairSerializer` overwrite
    like get use `id`, `username`, 'email', `first_name`, `last_name`, etc
    but by default `TokenObtainPairSerializer` get `user_id`, and `token`
    """

    @classmethod
    def get_token(cls, user):
        token = super(CustomTokenObtainPairSerializer, cls).get_token(user)
        token['user_id'] = user.id
        token['name'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_active'] = user.is_active
        if user:
            token.payload['exp'] = datetime_to_epoch(token.current_time + SUPERUSER_LIFETIME)
            return token


# User registration pass JWT token
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    tokens = serializers.SerializerMethodField()

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )

        return user

    class Meta:
        model = User
        fields = [
            'id', 'tokens', 'username', 'email', 'first_name', 'last_name', 'password'
        ]

    # When user registration automatically `refresh` and `access token return`
    """
    :param access_token:
     :return:
    """

    def get_tokens(self, user):
        tokens = RefreshToken.for_user(user)
        refresh = str(tokens)
        access = str(tokens.access_token)
        data = {
            "refresh": refresh,
            "access": access
        }
        return data

# Todo: user can change his/her password after Sign In 
class PasswordChangeSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['old_password', 'new_password', 'confirm_password']

    def validate(self, attrs):
        # Check if new_password and confirm_password match
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New password and confirm password must match."})
        return attrs

    def validate_old_password(self, value):
        # Check if the old password is correct
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct.")
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
