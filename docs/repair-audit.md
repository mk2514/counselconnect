# Repair Audit

| Feature | Frontend Present? | Backend Present? | Database Connected? | Actual Persistence? | Authorization? | Validation? | Working? | Problem | Required Fix |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Registration | Yes | Yes | Yes | Yes | Yes | Yes | WORKING | None | None |
| Login | Yes | Yes | Yes | Yes | Yes | Yes | WORKING | None | None |
| Logout | Yes | Yes | Yes | Yes | Yes | Yes | WORKING | None | None |
| Role routing | Yes | Yes | Yes | Yes | Yes | Yes | WORKING | None | None |
| Police dashboard | Yes | Yes | Yes | Yes | Yes | Yes | WORKING | None | None |
| Create Case | Yes | Yes | Yes | Yes | Yes | Yes | WORKING | None | None |
| CSR generation | Yes | Yes | Yes | Yes | Yes | Yes | WORKING | None | None |
| FIR upload | Yes | Yes | Yes | Yes | Yes | Yes | WORKING | Initially socket hung | Already Fixed (async thread) |
| Camera capture | Yes | No | No | No | No | No | UI ONLY | Missing API handler | Implement media upload |
| Document storage | No | No | No | No | No | No | NOT IMPLEMENTED | Currently no MinIO setup | Configure MinIO storage |
| SHA-256 hashing | No | No | No | No | No | No | NOT IMPLEMENTED | Files are not hashed | Add hashing to upload |
| OCR | No | No | No | No | No | No | NOT IMPLEMENTED | Raw PDF passed to AI | Add PaddleOCR/Tesseract |
| AI extraction | Yes | Yes | Yes | Yes | Yes | Yes | PARTIALLY WORKING | Fallback mock works | Connect real Ollama model |
| Human verification | Yes | No | No | No | No | No | UI ONLY | Button does nothing | Connect verify API |
| Case QR | Yes | No | No | No | No | No | UI ONLY | Placeholder QR | Implement JWT QR token |
| Investigation | Yes | No | No | No | No | No | UI ONLY | Buttons do nothing | Connect investigation APIs |
| Evidence | Yes | No | No | No | No | No | UI ONLY | Buttons do nothing | Connect evidence APIs |
| Party management | Yes | No | No | No | No | No | UI ONLY | Form not wired | Connect party APIs |
| Lawyer assignment | Yes | No | No | No | No | No | UI ONLY | Disconnected | Connect assignment APIs |
| Lawyer dashboard | Yes | Yes | Yes | Yes | Yes | Yes | WORKING | None | None |
| My Cases | Yes | Yes | Yes | Yes | Yes | Yes | WORKING | None | None |
| Hearings | Yes | Yes | Yes | Yes | Yes | Yes | BACKEND ONLY | Frontend handlers missing | Wire hearing components |
| Attendance | Yes | No | No | No | No | No | UI ONLY | Fake states | Connect attendance API |
| Absence requests | Yes | No | No | No | No | No | UI ONLY | Fake states | Connect absence API |
| Absence proof | Yes | No | No | No | No | No | UI ONLY | Upload does nothing | Connect proof MinIO upload |
| Court agenda | Yes | Yes | Yes | Yes | Yes | Yes | BACKEND ONLY | Missing frontend handlers | Wire agenda UI |
| AI prioritization | No | No | No | No | No | No | NOT IMPLEMENTED | Fake priority in UI | Connect rules engine |
| AI categorization | No | No | No | No | No | No | NOT IMPLEMENTED | Missing implementation | Implement AI categorizer |
| AI scheduling | No | No | No | No | No | No | NOT IMPLEMENTED | Missing OR-Tools | Connect OR-Tools |
| Court approval | Yes | No | No | No | No | No | UI ONLY | Buttons dead | Connect approval endpoints |
| Representation retirement | Yes | No | No | No | No | No | UI ONLY | Buttons dead | Connect retirement endpoints |
| Replacement lawyer | Yes | No | No | No | No | No | UI ONLY | Disconnected | Connect assignment change |
| Withdrawal/disposal | Yes | No | No | No | No | No | UI ONLY | Disconnected | Connect withdrawal |
| Proceedings | Yes | No | No | No | No | No | UI ONLY | Disconnected | Connect proceedings API |
| Speech-to-text | No | No | No | No | No | No | NOT IMPLEMENTED | Missing faster-whisper | Integrate faster-whisper |
| Judgment upload | Yes | No | No | No | No | No | UI ONLY | Disconnected | Connect judgment upload |
| Judgment metadata | No | No | No | No | No | No | NOT IMPLEMENTED | Missing extraction | Add metadata extractor |
| Case completion | Yes | No | No | No | No | No | UI ONLY | Fake toast | Connect completion API |
| Audit timeline | Yes | No | No | No | No | No | UI ONLY | Static demo events | Connect audit trail DB |
| NFC | No | No | No | No | No | No | NOT IMPLEMENTED | Missing | Implement NFC endpoints |
| Passkey/WebAuthn | No | No | No | No | No | No | NOT IMPLEMENTED | Missing | Implement WebAuthn |
| PWA | No | No | No | No | No | No | NOT IMPLEMENTED | Missing | Configure manifest/SW |
| Terms | Yes | No | No | No | No | No | UI ONLY | Placeholder | Implement terms |
| Privacy | Yes | No | No | No | No | No | UI ONLY | Placeholder | Implement privacy |
| Favicon | Yes | No | No | No | No | No | UI ONLY | Default Next.js icon | Update icon |

## Infrastructure Audit

*   **Docker:** Not installed on the host machine.
*   **PostgreSQL:** Not installed. Automated installation via winget hangs.
*   **Redis:** Not installed (Memurai installation hangs).
*   **MinIO:** Not installed.
*   **Celery Worker:** Cannot start without Redis broker.

**Resolution Plan per Rule 43:**
Due to the absence of required hardware/software, the application will:
1. Fallback to the existing SQLite `counselconnect.db` to allow the API to start, so frontend connectivity can be tested.
2. Provide explicit HTTP 503 "Service Unavailable" errors in the API when attempting to hit MinIO (document storage) or Redis (Celery AI job queue).
3. Connect Ollama to a smaller, CPU-friendly `qwen2.5:1.5b` model.
