import datetime
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.utils import datetime_to_epoch

from .models import Server, Task

SUPERUSER_LIFETIME = datetime.timedelta(minutes=90)


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = (
            'id', 'owner', 'name', 'address', 'created_at', 'updated_at'
        )
        read_only_fields = ['owner']


class TaskSerializer(serializers.ModelSerializer):
    server = ServerSerializer(many=True)

    class Meta:
        model = Task
        fields = [
            'id', 'server', 'server_name', 'start_time', 'end_time', 'status',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        server_ids = {server['id'] for server in validated_data.pop('server_name', [])}
        tasks = super(TaskSerializer, self).create(validated_data)
        return tasks


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
