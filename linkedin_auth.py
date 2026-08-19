import os
import urllib.parse
from dotenv import load_dotenv
import requests

load_dotenv("backend/.env")
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/callback"

def get_auth_url():
    """Generates the URL where you will login with your NEW account."""
    # Using the standard scopes required for posting and getting profile info
    scopes = "openid profile w_member_social"
    
    url = "https://www.linkedin.com/oauth/v2/authorization?"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": scopes,
    }
    return url + urllib.parse.urlencode(params)

def get_access_token(auth_code):
    """Exchanges the auth code for a permanent Access Token."""
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=data, headers=headers)
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Copy this Access Token to your .env file:\n")
        print(f'LINKEDIN_ACCESS_TOKEN="{response.json().get("access_token")}"\n')
    else:
        print("\n❌ ERROR getting token:\n", response.text)

if __name__ == "__main__":
    print("\n🔗 STEP 1: Copy this URL and open it in an INCOGNITO WINDOW:")
    print("-" * 50)
    print(get_auth_url())
    print("-" * 50)
    print("\n🔑 STEP 2: Login with your NEW ACCOUNT and click Allow.")
    print("🌐 STEP 3: You will be redirected to a broken localhost page.")
    print("Look at the URL in your browser. It will look like this:")
    print("http://localhost:8000/callback?code=AQUQ_SOME_LONG_CODE_HERE...")
    
    code = input("\n📝 Paste that LONG CODE here and press Enter: ").strip()
    get_access_token(code)
