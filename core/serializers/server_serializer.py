from rest_framework import serializers

from core.models import Server


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = (
            'id', 'owner', 'name', 'address', 'created_at', 'updated_at'
        )
        read_only_fields = ['owner']
