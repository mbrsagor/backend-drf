from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Server, Task, Schedule
from .serializers import ServerSerializer, TaskSerializer, CustomTokenObtainPairSerializer, ScheduleSerializer
from services.validation_service import validate_schedule_data
from utils.custom_responses import (prepare_success_response, prepare_error_response,
                                           prepare_create_success_response)


class ServerAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        """
        List all the server for given requested user
        :param request:
        :return:
        """
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
    permission_classes = [IsAuthenticated, ]
    """
       Server, update or delete a server instance.
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
        server = self.get_object(pk)
        serializer = ServerSerializer(server, data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        server = self.get_object(pk)
        server.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskAPIView(APIView):

    def get(self, request):
        task = Task.objects.all()
        task_serializer = TaskSerializer(task, many=True)
        return Response(task_serializer.data)

    def post(self, request):
        task_serializer = TaskSerializer(data=request.data)
        if task_serializer.is_valid():
            task_serializer.save()
            return Response(task_serializer.data, status=status.HTTP_201_CREATED)
        return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduleAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        schedule = Schedule.objects.all()
        serializer = ScheduleSerializer(schedule, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ScheduleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduleAPIUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get_object(self, pk):
        try:
            return Schedule.objects.get(pk=pk)
        except Schedule.DoesNotExist:
            raise None

    # Update Schedule
    def put(self, request, pk, format=None):
        validate_error = validate_schedule_data(request.data)
        if validate_error is not None:
            return Response(prepare_error_response(validate_error), status=status.HTTP_400_BAD_REQUEST)
        schedule = Schedule.objects.get(pk=id).first()
        if schedule is not None:
            serializer = ScheduleSerializer(schedule, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(prepare_create_success_response(serializer.data), status=status.HTTP_201_CREATED)
            return Response(prepare_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(prepare_error_response("No data found for this ID"), status=status.HTTP_400_BAD_REQUEST)

    # Delete Schedule
    def delete(self, request, pk):
        schedule = self.get_object(pk)
        if schedule is not None:
            schedule.delete()
            return Response(prepare_success_response("Data deleted successfully"), status=status.HTTP_200_OK)
        else:
            return Response(prepare_error_response("Content Not found"), status=status.HTTP_400_BAD_REQUEST)


class JWTLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
