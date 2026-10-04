import httpx
import asyncio

async def test_dashboards():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        print("\n--- 1. POLICE DASHBOARD TEST ---")
        # 1. Register Police
        ts = str(int(asyncio.get_event_loop().time()))
        r = await client.post("/api/auth/register/police", json={
            "station_code": f"ps_e2e_{ts}",
            "officer_name": "E2E Officer",
            "station_name": "E2E Station",
            "jurisdiction": "E2E City",
            "password": "Password@123",
            "confirm_password": "Password@123"
        })
        print(f"Register Police: {r.status_code}")
        police_cookies = r.cookies
        
        r2 = await client.post("/api/police/cases/draft", json={}, cookies=police_cookies)
        print(f"Create Draft Case: {r2.status_code}")
        case_id = r2.json().get("id")
        
        dummy_pdf = b"%PDF-1.4 dummy content"
        files = {"file": ("test_fir.pdf", dummy_pdf, "application/pdf")}
        r3 = await client.post(f"/api/police/cases/{case_id}/documents/fir", files=files, cookies=police_cookies)
        print(f"Upload FIR (Police): {r3.status_code}")

        print("\n--- 2. LAWYER DASHBOARD TEST ---")
        r = await client.post("/api/auth/register/lawyer", json={
            "bar_registration_id": f"BAR_{ts}",
            "full_name": "E2E Lawyer",
            "specialization": "Criminal",
            "jurisdiction": "E2E Court",
            "phone": "9999999999",
            "password": "Password@123",
            "confirm_password": "Password@123"
        })
        print(f"Register Lawyer: {r.status_code} {r.text}")
        lawyer_cookies = r.cookies
        
        r2 = await client.get("/api/lawyer/cases", cookies=lawyer_cookies)
        print(f"List Lawyer Cases: {r2.status_code} {r2.text}")
        
        print("\n--- 3. COURT DASHBOARD TEST ---")
        # Needs to get courts first to find a valid court_id for registration
        r_courts = await client.get("/api/auth/courts")
        courts = r_courts.json()
        court_id = courts[0]["id"] if courts else None
        print(f"Found Court ID: {court_id}")
        
        r = await client.post("/api/auth/register/court-authority", json={
            "court_id": court_id,
            "full_name": "E2E Judge",
            "jo_code": f"JO_{ts}",
            "role_title": "JUDGE",
            "password": "Password@123",
            "confirm_password": "Password@123"
        })
        print(f"Register Court Authority: {r.status_code} {r.text}")
        court_cookies = r.cookies
        
        r2 = await client.get("/api/court/cases", cookies=court_cookies)
        print(f"List Court Cases: {r2.status_code} {r2.text}")
        
        r3 = await client.get("/api/court/agenda/today", cookies=court_cookies)
        print(f"Get Court Agenda: {r3.status_code} {r3.text}")
        
        print("\n=== ALL DASHBOARDS FUNCTIONALITY TESTS COMPLETE ===")

asyncio.run(test_dashboards())
