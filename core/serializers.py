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
    server_name = ServerSerializer(many=True)

    class Meta:
        model = Task
        fields = [
            'id', 'task_name', 'server_name', 'start_time', 'end_time', 'status',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        server_ids = {server['id'] for server in validated_data.pop('server_name', [])}
        tasks = super(TaskSerializer, self).create(validated_data)
        return tasks
