from django.urls import path
from . import views

urlpatterns = [
    path('auth/login/', views.JWTLoginView.as_view()),
    path('server/', views.ServerAPIView.as_view()),
    path('server/<int:pk>/', views.ServerRetrieveUpdateDeleteAPIView.as_view()),
    path('task/', views.TaskAPIView.as_view()),
    path('schedule/', views.ScheduleAPIView.as_view()),
    path('schedule/update/<int:pk>/', views.ScheduleAPIUpdateDeleteView.as_view()),
    path('schedule/delete/<int:pk>/', views.ScheduleAPIUpdateDeleteView.as_view()),
]
