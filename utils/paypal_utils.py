import paypalrestsdk
from django.conf import settings

def initialize_paypal():
    paypalrestsdk.configure({
        "mode": settings.PAYPAL_MODE,  # 'sandbox' or 'live'
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_CLIENT_SECRET,
    })


