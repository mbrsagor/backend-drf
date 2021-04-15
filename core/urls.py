from django.urls import path
from .views import ServerAPIView, ServerRetrieveUpdateDeleteAPIView

urlpatterns = [
    path('server/', ServerAPIView.as_view()),
    path('server/<int:pk>/', ServerRetrieveUpdateDeleteAPIView.as_view()),
]
