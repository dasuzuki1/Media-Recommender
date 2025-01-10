import pip._vendor.requests as requests
import os
from dotenv import load_dotenv

def get_access_token(auth_code):
    url = "https://anilist.co/api/v2/oauth/token"
    load_dotenv()
    payload = {
        "grant_type": "authorization_code",
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "redirect_uri": os.getenv("REDIRECT_URI"),
        "code": auth_code
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        token_data = response.json()
        print("Access Token:", token_data["access_token"])
        return token_data["access_token"]
    else:
        print("Failed to get access token:", response.status_code, response.text)
        return None

# Example usage:
authorization_code = "AUTH_CODE_RECEIVED_FROM_CALLBACK"
access_token = get_access_token(authorization_code)
