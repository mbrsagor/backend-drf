from rest_framework import views, status, generics
from rest_framework.response import Response

from worker.serializers import complete_job_serializer
from django.db.models import Sum, F, ExpressionWrapper, fields
from worker.models import CompleteJob, WorkerProfile, AddTask, Tracker

from utils.enum_utils import TaskStatus
from utils import responses, messages, custom_pagination


# Create complete job
class CompleteJobCreateApiView(views.APIView):
    """
    Name: Create Complete Job
    Desc: Create a new complete job
    URL: /worker/complete-job/
    Method: POST
    """

    def post(self, request, *args, **kwargs):
        # Get task id
        task_id = request.data.get("task")
        try:
            worker_profile = WorkerProfile.objects.get(worker=request.user)
            serializer = complete_job_serializer.CompleteJobSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(worker=worker_profile)

                # Update task status
                task = AddTask.objects.get(id=task_id)
                task.status = 4 # Completed
                task.save()

                # Calculate reward point based on priority
                trackers = Tracker.objects.filter(task=task, worker=worker_profile)
                
                # Calculate total tracked time in seconds
                total_tracked_seconds = trackers.aggregate(
                    total_time=Sum(
                        ExpressionWrapper(
                            F('end_time') - F('start_time'), 
                            output_field=fields.BigIntegerField()
                        )
                    )
                )['total_time'] or 0

                # duration is in milliseconds (BigInteger), convert to minutes
                estimated_minutes = (task.duration / 1000) / 60
                tracked_minutes = total_tracked_seconds / 60
                
                points_to_add = 0
                
                # Condition: Tracked Time is greater than Estimated Hour = 0 bonus (Just estimated points)
                if tracked_minutes > estimated_minutes:
                    pass
                
                # Condition: Tracked Time is equal to Estimated Hour = 2x bonus
                elif tracked_minutes == estimated_minutes:
                    points_to_add = estimated_minutes * 2
                    profile = request.user.profile
                    profile.points += int(points_to_add)
                    profile.save()

                # Condition: Tracked Time is less than Estimated Hour = Extra bonus
                else:
                    save_tracked_minutes = estimated_minutes - tracked_minutes
                    save_points = save_tracked_minutes * 2
                    tracked_points = tracked_minutes * 2
                    points_to_add = save_points + tracked_points
                    # save points
                    profile = request.user.profile
                    profile.points += int(points_to_add)
                    profile.save()

                if points_to_add > 0:
                    profile = request.user.profile
                    profile.points += int(points_to_add)
                    profile.save()

                return Response(
                    responses.prepare_success_response(messages.COMPLETE_JOB_MSG),
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                responses.prepare_error_response(serializer.errors),
                status=status.HTTP_400_BAD_REQUEST,
            )
        except WorkerProfile.DoesNotExist:
            return Response(
                responses.prepare_error_response(messages.NOT_FOUND),
                status=status.HTTP_404_NOT_FOUND,
            )


class CompleteJobListApiView(generics.ListAPIView):
    """
    Name: List Complete Job
    Desc: List all complete job
    URL: /worker/complete-job-list/
    Method: GET
    params: page, page_size
    """

    queryset = CompleteJob.objects.all()
    serializer_class = complete_job_serializer.CompleteJobListSerializer
    pagination_class = custom_pagination.CustomPagination

    def get_queryset(self):
        return self.queryset.filter(
            worker=self.request.user.worker_profile
        )
