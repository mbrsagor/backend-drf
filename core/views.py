from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from .models import Server, Task
from .serializers import ServerSerializer


class ServerAPIView(APIView):
    pass
