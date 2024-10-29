import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings

url = "https://api.bulksms.com/v1/messages"

# Send sms from bulksms.com using their API
def send_sms(sender, message):
    # Define your credentials
    username = "username"
    password = "password"
    data = {
        "from": settings.SENDER_NUMBER,
        "to": sender,
        "body": message,
    }
    response = requests.post(url, data=data, auth=HTTPBasicAuth(username, password))
    if response.status_code == 201:
        return True
    else:
        return False

