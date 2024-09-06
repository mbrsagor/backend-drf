import random
import string
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template

# When user will create device token will automatically create random 10 digit string
letters = string.ascii_lowercase
random_device_token = ''.join(random.choice(letters) for i in range(10))


def generate_otp(length=4):
    otp_chars = "0123456789"
    otp = ''.join(random.choice(otp_chars) for _ in range(length))
    return otp


def send_otp(email, otp):
    template_name = 'email/email_otp.html'
    subject = 'Verification OTP'
    message = f'Your OTP for email verification is: {otp}. Please use this OTP to verify your email.'
    context = {'email': email, 'otp': otp}
    template = get_template(template_name).render(context)
    from_email = settings.EMAIL_HOST_USER
    to_email = [email]
    send_mail(subject, message, from_email, to_email, html_message=template, fail_silently=False)


def send_mail_to_access(email, password):
    template_name = 'email/guard_access_email.html'
    subject = 'You are assigned as a guard. Please signin with below credentials'
    message = 'Here is your credentials.'
    to_email = [email]
    context = {'email': email, 'password': password}
    template = get_template(template_name).render(context)
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_email, to_email, html_message=template, fail_silently=False)
