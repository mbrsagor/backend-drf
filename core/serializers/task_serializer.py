from rest_framework import serializers
from django.contrib.auth.models import User

from core.models import Task
from core.serializers.server_serializer import ServerSerializer


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
