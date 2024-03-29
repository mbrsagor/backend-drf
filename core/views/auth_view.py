from rest_framework_simplejwt.views import TokenObtainPairView
from core.serializers.auth_serializer import CustomTokenObtainPairSerializer



class JWTLoginView(TokenObtainPairView):
    """
    The veiw basically custom uer signIn endpoint.
    Here, customization JET auth.
    """
    serializer_class = CustomTokenObtainPairSerializer
