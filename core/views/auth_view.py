from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import views, status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.models import User

from utils import responses, messages, mixin
from core.serializers import auth_serializer


class CompanySignUpAPIView(views.APIView):
    """
    Name: Company Sign Up API.
    Desc: Create a company sign up endpoint.
    URL:/api/v1/auth/company-signup/
    Method: POST
    :param
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            serializer = auth_serializer.CompanySignUpSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                # Send OTP
                otp = mixin.generate_otp()
                user.otp = otp
                user.is_active = False
                user.save()
                mixin.send_otp(user.email, user.otp)
                return Response(responses.prepare_success_response(messages.SIGNUP_SUCCESS),
                                status=status.HTTP_201_CREATED)
            error_list = [serializer.errors[error][0] for error in serializer.errors]
            error = ' '.join(error_list)
            return Response(responses.prepare_error_response(error), status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(responses.prepare_error_response(str(ex)), status=status.HTTP_200_OK)


class GuestSignUpAPIView(views.APIView):
    """
    Name: Guest & general user SignUp API.
    Desc: Create a guest & general users sign up endpoint.
    URL:/api/v1/auth/signup/
    Method: POST
    :param
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            serializer = auth_serializer.GuestSignUpSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                otp = mixin.generate_otp()
                user.otp = otp
                user.is_active = False
                user.save()
                mixin.send_otp(user.email, user.otp)
                return Response(responses.prepare_success_response(messages.SIGNUP_SUCCESS),
                                status=status.HTTP_201_CREATED)
            return Response(responses.prepare_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response(responses.prepare_error_response(str(ex)), status=status.HTTP_400_BAD_REQUEST)


class GuardSignUpAPIView(views.APIView):
    """
    Name: Guard user SignUp API.
    Desc: Create a guard user sign up endpoint.
    URL:/api/v1/auth/signup-guard/
    Method: POST
    :param
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            serializer = auth_serializer.GuestSignUpSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                mixin.send_mail_to_access(request.data.get('email'), request.data.get('password'))
                serializer.save()
                return Response(responses.prepare_success_response(messages.GUARD_SIGNUP),
                                status=status.HTTP_201_CREATED)
            return Response(responses.prepare_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response(responses.prepare_error_response(str(ex)), status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailOtpAPIView(views.APIView):
    """
    Name: Verify email OTP API
    Method: POST
    URL: /api/v1/user/verify-otp/
    :param
    email,
    otp
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = request.data
        email = data['email']
        otp = data['otp']
        try:
            user = User.objects.get(email=email, otp=otp)
            if user:
                user.is_active = True
                user.save()
                return Response(responses.prepare_success_response(messages.OTP_VERIFY), status=status.HTTP_201_CREATED)
            return Response(responses.prepare_error_response(messages.NOT_FOUND), status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response(responses.prepare_error_response(messages.OTP_NOT_MATCH), status=status.HTTP_404_NOT_FOUND)


class VerifyEmailOtpForCompanyAPIView(views.APIView):
    """
    Name: Verify email OTP API
    Method: POST
    URL: /api/v1/user/verify-otp-company/
    :param
    email,
    otp
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = request.data
        email = data['email']
        otp = data['otp']
        try:
            user = User.objects.get(email=email, otp=otp)
            if user:
                return Response(responses.prepare_success_response(messages.OTP_VERIFY_COMPANY), status=status.HTTP_201_CREATED)
            return Response(responses.prepare_error_response(messages.NOT_FOUND), status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response(responses.prepare_error_response(messages.OTP_NOT_MATCH), status=status.HTTP_404_NOT_FOUND)


class SignInAPIView(ObtainAuthToken):
    """
    Name: SignIn API
    Desc: Signin API endpoint.
    URL:/api/v1/auth/signin/
    Method: POST
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            token, created = Token.objects.get_or_create(user=serializer.validated_data['user'])
            user = serializer.validated_data['user']
            device_token = request.data['device_token']
            try:
                user.device_token = device_token
                user.save()
            except Exception as ex:
                return Response(responses.prepare_error_response(str(ex)), status=status.HTTP_200_OK)
            return Response(
                responses.signin_success_response(user.id, user.fullname, user.email, user.role, user.role_name,
                                                  user.device_token, token.key),
                status=status.HTTP_200_OK)
        else:
            return Response(responses.prepare_error_response(messages.SIGNIN_FAILED), status=status.HTTP_200_OK)


class SignOutAPIView(views.APIView):
    """
    Name: Signout API
    Desc: Signout API endpoint.
    Method: GET
    URL: /api/v1/auth/signout/
    :param
    token
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        if request.user.auth_token:
            try:
                device_token = ""
                user = User.objects.get(email=self.request.user.email)
                user.device_token = device_token
                user.save()
                request.user.auth_token.delete()
                return Response(responses.prepare_success_response(messages.SIGN_OUT_SUCCESS),
                                status=status.HTTP_200_OK)
            except Exception as ex:
                return Response(responses.prepare_error_response(str(ex)), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(responses.prepare_error_response(messages.EXPIRED), status=status.HTTP_200_OK)


class PasswordRestOtpAPIView(views.APIView):
    """
    Name: Send OTP email for password change.
    Desc: When user will forget password send 6 digit OTP the email address.
    URL: /api/v1/user/password-reset/
    Method: POST
    :param: email
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = self.request.data
        email = data['email']
        try:
            user = User.objects.get(email=email)
            if User.objects.filter(email=email).exists():
                mixin.send_otp(user.email, user.otp)
                return Response(responses.prepare_success_response(messages.OTP_SUCCESS), status=status.HTTP_200_OK)
            return Response(responses.prepare_error_response(messages.OTP_NOT_MATCH), status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response(responses.prepare_error_response(messages.NOT_FOUND), status=status.HTTP_404_NOT_FOUND)


class PasswordChangeConfirm(views.APIView):
    """
    Name: Password Reset confirm with OTP
    URL: /api/v1/user/password-change-confirm/
    Method: POST
    @:param:
    OTP
    Email
    New Password
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        new_password = None
        data = self.request.data

        try:
            user = User.objects.get(email=data['email'])
            if user.is_active:
                # Check if otp is valid
                if data['otp'] == user.otp:
                    if new_password != '':
                        # Change Password
                        user.set_password(data['new_password'])
                        user.save()  # Here user otp will also be changed on save automatically
                        return Response(responses.prepare_success_response(messages.PASSWORD_CHANGE),
                                        status=status.HTTP_201_CREATED)
                    return Response(responses.prepare_error_response(messages.PASSWORD_MSG),
                                    status=status.HTTP_400_BAD_REQUEST)
            return Response(responses.prepare_error_response(messages.OTP_NOT_MATCH),
                            status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(responses.prepare_error_response(messages.NOT_FOUND), status=status.HTTP_404_NOT_FOUND)
