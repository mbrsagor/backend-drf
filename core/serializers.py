from rest_framework import serializers
from .models import Server, Task


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = (
            'id', 'owner', 'name', 'address'
        )
        read_only_fields = ['owner']
