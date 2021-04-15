from django.urls import path
from .views import ServerAPIView

urlpatterns = [
    path('server/', ServerAPIView.as_view()),
]
