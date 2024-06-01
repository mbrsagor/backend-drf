from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


from core.models import Schedule
from core.serializers import schedule_serializer
from services import validation_service
from utils.custom_responses import (prepare_success_response, prepare_error_response,
                                    prepare_create_success_response)


class ScheduleAPIView(APIView):
    """
    URL: api/schedule/
    """

    def get(self, request):
        schedule = Schedule.objects.all()
        serializer = schedule_serializer.ScheduleSerializer(schedule, many=True)
        return Response(serializer.data)

    def post(self, request):
        validate_error = validation_service.validate_schedule_data(request.data)
        if validate_error is not None:
            return Response(prepare_error_response(validate_error), status=status.HTTP_400_BAD_REQUEST)
        serializer = ScheduleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(prepare_create_success_response(serializer.data), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduleAPIUpdateDeleteView(APIView):
    """
    URL: api/schedule/<pk>/
    """

    def get_object(self, pk):
        try:
            return Schedule.objects.get(pk=pk)
        except Schedule.DoesNotExist:
            raise None

    # Update Schedule
    def put(self, request, pk, format=None):
        validate_error = validation_service.validate_schedule_data(request.data)
        if validate_error is not None:
            return Response(prepare_error_response(validate_error), status=status.HTTP_400_BAD_REQUEST)
        schedule = Schedule.objects.get(pk=pk).first()
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
