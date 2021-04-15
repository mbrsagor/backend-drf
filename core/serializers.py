from rest_framework import serializers
from .models import Server, Task


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = (
            'id', 'owner', 'name', 'address', 'created_at', 'updated_at'
        )
        read_only_fields = ['owner']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
