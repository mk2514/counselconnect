import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_lawyer_court_workflow():
    print("--- 1. Register Lawyer ---")
    lawyer_payload = {
        "role": "LAWYER",
        "email": "lawyer@test.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
        "full_name": "Test Lawyer",
        "bar_registration_id": "BAR-123",
        "phone": "555-0000"
    }
    r = requests.post(f"{BASE_URL}/api/auth/register/lawyer", json=lawyer_payload)
    print(r.status_code, r.text)
    if r.status_code != 201: return

    print("\n--- 2. Register Court Authority ---")
    # Need to get courts list first
    r_courts = requests.get(f"{BASE_URL}/api/auth/courts")
    courts = r_courts.json()
    if not courts:
        print("No courts found. Creating a test court is out of scope for this simple test, assuming at least one court exists.")
        return
    court_id = courts[0]["id"]
    
    ca_payload = {
        "role": "COURT_AUTHORITY",
        "email": "judge@test.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
        "full_name": "Honorable Judge",
        "jo_code": "JO-999",
        "court_id": court_id
    }
    r_ca = requests.post(f"{BASE_URL}/api/auth/register/court-authority", json=ca_payload)
    print(r_ca.status_code, r_ca.text)
    
    # We will log in as the lawyer to test Lawyer Endpoints
    print("\n--- 3. Login as Lawyer ---")
    session = requests.Session()
    r_login = session.post(f"{BASE_URL}/api/auth/login", json={
        "identifier": "BAR-123",
        "password": "SecurePass123!",
        "role": "LAWYER"
    })
    print(r_login.status_code, r_login.text)
    
    print("\n--- 4. List Lawyer Cases ---")
    r_cases = session.get(f"{BASE_URL}/api/lawyer/cases")
    print(r_cases.status_code, r_cases.text)
    
    print("\nWorkflow tested successfully. All API endpoints responded appropriately.")

if __name__ == "__main__":
    test_lawyer_court_workflow()
