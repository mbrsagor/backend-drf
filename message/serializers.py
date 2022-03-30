from rest_framework import serializers
from .models import Consult


class ConsultSerializer(serializers.ModelSerializer):

    class Meta:
        model = Consult
        fields = (
            'id', 'name', 'position', 'group', 'email',
            'phone', 'describe', 'file', 'created_at'
        )
