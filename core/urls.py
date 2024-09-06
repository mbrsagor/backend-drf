from django.urls import path
from core.views import auth_view, server_view, task_view, schedule_view

urlpatterns = [
    path("user/login/", auth_view.SignInAPIView.as_view()),
    path("server/", server_view.ServerAPIView.as_view()),
    path("server/<pk>/", server_view.ServerRetrieveUpdateDeleteAPIView.as_view()),
    path("task/", task_view.TaskAPIView.as_view()),
    path("schedule/", schedule_view.ScheduleAPIView.as_view()),
    path("schedule/update/<pk>/", schedule_view.ScheduleAPIUpdateDeleteView.as_view()),
    path("schedule/delete/<pk>/", schedule_view.ScheduleAPIUpdateDeleteView.as_view()),
]
