import requests
from oauth2client.service_account import ServiceAccountCredentials

fsm_scope = 'https://www.googleapis.com/auth/firebase.messaging'
fcm_url = "https://fcm.googleapis.com/v1/projects/e-pass-1fe10/messages:send"


def _get_access_token():
    """Retrieve a valid access token that can be used to authorize requests.
    :return: Access token.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'utils/service-account.json', fsm_scope)
    access_token_info = credentials.get_access_token()
    return access_token_info.access_token


headers = {
    'Authorization': 'Bearer ' + _get_access_token(),
    'Content-Type': 'application/json; UTF-8',
}


def send_notification(title, message, device_token):
    body = {
        "message": {
            "token": "/topics/all" if device_token == "all" else device_token,
            "notification": {
                "title": title,
                "body": message
            }
        }
    }
    response = requests.post(fcm_url, json=body, headers=headers)
    # print(response.json())
    return response
