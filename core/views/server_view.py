from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.models import Server
from core.serializers import ServerSerializer
from services.validation_service import validate_server_data
from utils.custom_responses import (prepare_success_response, prepare_error_response,
                                    prepare_create_success_response)



class ServerAPIView(APIView):

    def get(self, request):
        """
        List all the server for given requested user
        :param request:
        :return:
        URL: api/server/
        """
        server = Server.objects.all()
        serializer = ServerSerializer(server, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        validate_error = validate_server_data(request.data)
        if validate_error is not None:
            return Response(prepare_error_response(validate_error), status=status.HTTP_400_BAD_REQUEST)
        serializer = ServerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(prepare_create_success_response(serializer.data), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServerRetrieveUpdateDeleteAPIView(APIView):
    """
    Server, update or delete a server instance.
    URL: api/server/<pk>/
    """

    def get_object(self, pk):
        try:
            return Server.objects.get(pk=pk)
        except Server.DoesNotExist:
            raise None

    def get(self, request, pk):
        server = self.get_object(pk)
        serializer = ServerSerializer(server)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        validate_error = validate_server_data(request.data)
        if validate_error is not None:
            return Response(prepare_error_response(validate_error), status=status.HTTP_400_BAD_REQUEST)
        server = self.get_object(pk)
        if server is not None:
            serializer = ServerSerializer(server, data=request.data)
            if serializer.is_valid():
                serializer.save(owner=request.user)
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(prepare_error_response("No data found for this ID"), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        server = self.get_object(pk)
        if server is not None:
            server.delete()
            return Response(prepare_success_response("Data deleted successfully"), status=status.HTTP_200_OK)
        return Response(prepare_error_response("Content Not found"), status=status.HTTP_400_BAD_REQUEST)

