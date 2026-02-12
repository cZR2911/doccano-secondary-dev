import requests
import sys

BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/v1/auth/login/"
ME_URL = f"{BASE_URL}/v1/me"

def test_login(username, password):
    print(f"Testing login for user: {username}")
    session = requests.Session()
    
    # 1. Login
    payload = {
        "username": username,
        "password": password
    }
    try:
        # Note: requests automatically handles CSRF if session cookie is set?
        # But for the first request, we don't have cookies.
        # dj-rest-auth login is usually exempt or we need to get CSRF token first.
        # Let's try simple POST first.
        
        response = session.post(LOGIN_URL, json=payload)
        print(f"Login Status Code: {response.status_code}")
        print(f"Login Response: {response.text[:200]}")
        print(f"Cookies: {session.cookies.get_dict()}")
        
        if response.status_code == 200:
            print("Login successful. Checking /me endpoint...")
            # Extract CSRF token if needed (for safe methods like GET usually not needed)
            headers = {}
            csrftoken = session.cookies.get('csrftoken')
            if csrftoken:
                headers['X-CSRFToken'] = csrftoken
                
            me_response = session.get(ME_URL, headers=headers)
            print(f"Me Status Code: {me_response.status_code}")
            print(f"Me Response: {me_response.text[:200]}")
        else:
            print("Login failed.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login("admin", "password")
