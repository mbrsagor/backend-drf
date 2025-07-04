from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status, permissions, views
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from user.models import User, OTPVerification
from user.serializers import auth_serializer
from utils import responses, messages, plain_error_helper, mixin



class SendOTPView(views.APIView):
    """
    Name: Send SignUp OTP API.
    Desc: This API endpoint will use for user send OTP.
    URL:/api/v1/auth/send-otp/
    Method: POST
    :param
    email
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            email = data['email']

            # Email is already verified
            if OTPVerification.objects.filter(is_verified=True).first():
                return Response(responses.prepare_success_response(messages.EMAIL_ALREADY_EXISTS),
                                status=status.HTTP_200_OK)
            # Check if the user already exists
            if User.objects.filter(email=email).exists():
                return Response(responses.prepare_error_response(messages.EMAIL_ALREADY_EXISTS),
                                status=status.HTTP_200_OK)
            # Here, start generate OTP via the phone number
            otp = mixin.generate_otp()
            OTPVerification.objects.create(email=email, otp=otp)
            # Sent OTP via mail
            mixin.send_otp_mail_to_access(email, otp)
            return Response(responses.prepare_send_otp_success_response(email, otp), status=status.HTTP_200_OK)
        except Exception as ex:
            msg = plain_error_helper.get_plain_error_message(ex)
            return Response(responses.prepare_error_response(msg), status=status.HTTP_200_OK)


class OTPResendAPIView(views.APIView):
    """
    Name: Resend OTP API.
    Desc: This API endpoint will use for user resend OTP.
    URL:/api/v1/auth/otp-resend/
    Method: POST
    :param
    phone
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            email = data['email']
            otp_verification = OTPVerification.objects.filter(email=email).exists()
            if otp_verification:
                # Delete existing OTP verification
                old_otp = OTPVerification.objects.filter(email=email)
                old_otp.delete()
                # Here, start generate OTP via the phone number
                otp = mixin.generate_otp()
                OTPVerification.objects.create(email=email, otp=otp)
                # Sent OTP via mail
                mixin.send_otp_mail_to_access(email, otp)
                return Response(responses.prepare_send_otp_success_response(email, otp), status=status.HTTP_200_OK)
            else:
                return Response(responses.prepare_error_response("OTP sent failed"), status=status.HTTP_200_OK)
        except Exception as ex:
            msg = plain_error_helper.get_plain_error_message(ex)
            return Response(responses.prepare_error_response(msg), status=status.HTTP_200_OK)


class OTPVerifyAPIView(views.APIView):
    """
    Name: Verify Sign Up OTP API
    Desc: This API use for all otp verification.
    Method: POST
    URL: /api/v1/user/verify-otp/
    :param
    email,
    otp
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = request.data
        otp = data['otp']
        email = data['email']
        # Check if OTP matches
        try:
            otp_verify = OTPVerification.objects.filter(email=email, otp=otp).first()
            if otp_verify:
                otp_verify.is_verified = True
                otp_verify.save()
                # otp_verify.delete()
                return Response(responses.prepare_success_response(messages.OTP_VERIFY), status=status.HTTP_201_CREATED)
            return Response(responses.prepare_error_response(messages.OTP_NOT_MATCH), status=status.HTTP_200_OK)
        except Exception as ex:
            msg = plain_error_helper.get_plain_error_message(ex)
            return Response(responses.prepare_error_response(msg), status=status.HTTP_200_OK)


class SignUpAPIView(views.APIView):
    """
    Name: General user SignUp API.
    Desc: Create a general & other users sign up endpoint.
    URL:/api/v1/auth/signup/
    Method: POST
    :param
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        try:
            serializer = auth_serializer.SignUpSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                # when user created then OTP will be deleted from OTP verify table
                otp_verify = OTPVerification.objects.filter(email=email).first()
                otp_verify.delete()
                return Response(responses.prepare_success_response(messages.SIGNUP_SUCCESS),
                                status=status.HTTP_201_CREATED)
            return Response(responses.prepare_error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            msg = plain_error_helper.get_plain_error_message(ex)
            return Response(responses.prepare_error_response(msg), status=status.HTTP_400_BAD_REQUEST)
