import requests

def fetch_external_api_data():
    url = "https://api.example.com/data"  # Replace with the API endpoint
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",  # Add authentication if needed
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()  # Assuming the API returns JSON data
    else:
        response.raise_for_status()

