from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Server
from .serializers import ServerSerializer


class ServerAPIView(APIView):
    def get(self, request):
        server = Server.objects.all()
        serializer = ServerSerializer(server, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ServerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServerRetrieveUpdateDeleteAPIView(APIView):
    """
       Server, update or delete a snippet instance.
    """
    pass
