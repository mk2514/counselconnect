import requests

url = "http://127.0.0.1:8000/api/auth/register/police"
payload = {
    "role": "POLICE",
    "email": "test2@police.com",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!",
    "officer_name": "Test Officer 2",
    "badge_number": "12345",
    "station_code": "PS002",
    "station_name": "Test Station 2"
}
response = requests.post(url, json=payload)
print(f"Status: {response.status_code}")
print(f"Body: {response.text}")
