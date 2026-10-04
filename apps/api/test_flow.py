import httpx
import asyncio

async def test_flow():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # 1. Register (new user)
        r = await client.post("/api/auth/register/police", json={
            "station_code": "ps_e2e_" + str(int(asyncio.get_event_loop().time())),
            "officer_name": "E2E Officer",
            "station_name": "E2E Station",
            "jurisdiction": "E2E City",
            "password": "Password@123",
            "confirm_password": "Password@123"
        })
        print(f"1. Register: {r.status_code} -> {r.text[:200]}")
        cookies = r.cookies
        
        if r.status_code != 201:
            print("FAILED at register")
            return

        # 2. Create draft case
        r2 = await client.post("/api/police/cases/draft", json={}, cookies=cookies)
        print(f"2. Draft Case: {r2.status_code} -> {r2.text[:200]}")
        
        if r2.status_code != 201:
            print("FAILED at draft case")
            return
            
        draft = r2.json()
        case_id = draft["id"]
        print(f"   Case ID: {case_id}")

        # 3. Upload FIR (create a dummy PDF-like file)
        dummy_pdf = b"%PDF-1.4 dummy content for testing purposes " + str(asyncio.get_event_loop().time()).encode()
        files = {"file": ("test_fir.pdf", dummy_pdf, "application/pdf")}
        r3 = await client.post(f"/api/police/cases/{case_id}/documents/fir", files=files, cookies=cookies)
        print(f"3. Upload FIR: {r3.status_code} -> {r3.text[:300]}")
        
        if r3.status_code not in (201, 202):
            print("FAILED at FIR upload")
            return
        
        job = r3.json()
        job_id = job["id"]
        print(f"   Job ID: {job_id}, Status: {job['status']}")

        # 4. Poll for AI job completion
        for i in range(15):
            await asyncio.sleep(1)
            r4 = await client.get(f"/api/ai/jobs/{job_id}", cookies=cookies)
            status_data = r4.json()
            print(f"4. Poll #{i+1}: status={status_data['status']}")
            if status_data["status"] in ("COMPLETED", "FAILED"):
                if status_data.get("outputs"):
                    print(f"   AI Output: {status_data['outputs'][0]['content'][:300]}")
                else:
                    print(f"   Error: {status_data.get('error_message')}")
                break

        print("\n=== FULL FLOW TEST COMPLETE ===")

asyncio.run(test_flow())
