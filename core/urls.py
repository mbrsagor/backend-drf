from django.urls import path
from . import views

urlpatterns = [
    path('user/login/', views.JWTLoginView.as_view()),
    path('server/', views.ServerAPIView.as_view()),
    path('server/<pk>/', views.ServerRetrieveUpdateDeleteAPIView.as_view()),
    path('task/', views.TaskAPIView.as_view()),
    path('schedule/', views.ScheduleAPIView.as_view()),
    path('schedule/update/<pk>/', views.ScheduleAPIUpdateDeleteView.as_view()),
    path('schedule/delete/<pk>/', views.ScheduleAPIUpdateDeleteView.as_view()),
]
