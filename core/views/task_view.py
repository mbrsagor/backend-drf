from rest_framework import status
from rest_framework.views import APIView
from django.views import View
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from core.models import Task
from core.serializers.task_serializer import TaskSerializer
from services.validation_service import validate_task_data
from utils.custom_responses import (prepare_success_response, prepare_error_response,
                                    prepare_create_success_response)



class CreateManufacturerView(View):
    def get(self, request, *args, **kwargs):
        name = request.GET.get('name', None)
        is_active = request.GET.get('is_active', None)

        obj = Manufacturer.objects.create(name=name, is_active=is_active)
        manufacturer = {'id': obj.id, 'name': obj.name, 'is_active': obj.is_active}
        data = {'manufacturer': manufacturer}
        return JsonResponse(data)



class TaskAPIView(APIView):

    """
    Task create and listview API
    URL: api/task/
    """

    def get(self, request):
        task = Task.objects.all()
        task_serializer = TaskSerializer(task, many=True)
        return Response(task_serializer.data)

    def post(self, request):
        validate_error = validate_task_data(request.data)
        if validate_error is not None:
            return Response(prepare_error_response(validate_error), status=status.HTTP_400_BAD_REQUEST)
        task_serializer = TaskSerializer(data=request.data)
        if task_serializer.is_valid():
            task_serializer.save()
            return Response(task_serializer.data, status=status.HTTP_201_CREATED)
        return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
