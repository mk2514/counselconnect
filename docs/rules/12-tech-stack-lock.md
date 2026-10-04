# Rule 12: Tech Stack Lock

This document is the **FINAL** technology specification for CounselConnect. Do not substitute technologies without explicit approval.

---

## 1. Frontend

**Use:**
- Next.js with App Router
- TypeScript with strict mode
- Tailwind CSS
- shadcn/ui (customized to match the approved judicial/government visual language)
- Lucide React icons

**Do NOT introduce:** Material UI, Bootstrap, Ant Design, Chakra UI, or any competing component framework.

shadcn/ui components must be customized to match the approved design. Do not retain default shadcn styling if it conflicts with the approved visual system (see `02-ui-design.md`).

## 2. Mobile Architecture

The application must be implemented as a **Progressive Web App (PWA)**.

The PWA must support installation on compatible Android devices and important mobile workflows:
- Registration, authentication
- NFC entry, QR scanning
- Camera document capture
- Lawyer case access, attendance, absence submissions, hearing information

Complex Court Authority operations (full agenda management) should remain optimized for desktop/tablet while failing gracefully on mobile.

**Do NOT build a separate native Android application.**

## 3. Backend

**Use:** Python, FastAPI, Pydantic, SQLAlchemy, Alembic.

FastAPI is responsible for: authentication, authorization, business logic, case workflows, document management, AI orchestration, scheduling APIs, NFC/QR resolution, audit creation.

## 4. Database

**Use:** PostgreSQL with **pgvector** enabled.

PostgreSQL is the authoritative store for structured system records. pgvector is used only for embedding/vector data (document embeddings, case-text embeddings, semantic similarity, related-document retrieval).

Do not replace relational case data with vector records.

## 5. Embeddings

**Use:** sentence-transformers.

Architecture: Document text → text chunking → sentence-transformers → embedding → pgvector.

Store metadata: source document, CSR, chunk number, model identifier, created timestamp.

Semantic similarity is an assistance/search capability. It must not determine guilt, legal precedent, judgment, or case outcome.

## 6. Redis

**Use Redis for:** Celery broker, temporary task state, short-lived caching, rate-limiting support, temporary WebAuthn challenges, temporary NFC authentication challenges, temporary processing state.

Redis must NOT become the authoritative case database.

## 7. Background Processing

**Use:** Celery + Redis. **Do NOT use ARQ.**

Use Celery for expensive/asynchronous operations: OCR, document processing, OpenCV preprocessing, embedding generation, AI extraction, AI summarization, document classification, speech transcription, long-running processing tasks.

Do not perform expensive AI/OCR processing synchronously inside FastAPI requests.

Architecture: FastAPI → create database job → enqueue Celery task → worker executes → worker updates job result → frontend polls/subscribes for state.

Explicit states: `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`, `REVIEWED`. Do not fake processing completion using frontend timers.

## 8. File Storage

**Use:** MinIO.

PostgreSQL stores file metadata. MinIO stores actual file objects.

Metadata: document ID, CSR, object-storage key, original filename, sanitized filename, MIME type, file size, SHA-256 digest, uploader, upload timestamp, processing status.

Do not store large PDFs/images directly as PostgreSQL relational fields unless justified.

## 9. Document Integrity

**Use:** SHA-256 for integrity verification. Do NOT describe SHA-256 as encryption.

## 10. Encryption

Where application-layer AES encryption is required, use **AES-256-GCM**. Do not implement custom cryptography.

Encryption keys must: never be committed to Git, never be stored beside encrypted files, be provided through secure environment/secret configuration.

## 11. OCR

Primary pipeline: **OpenCV → PaddleOCR**. Fallback: Tesseract.

OpenCV may perform: deskew, rotation correction, contrast adjustment, denoising, cropping, perspective correction, preprocessing.

OCR results are candidate information. OCR output must NOT automatically become authoritative judicial data. Required flow: OCR → extraction → human verification → official record update.

## 12. Local LLM

**Use:** Ollama + Qwen-family model.

Used for: structured extraction assistance, summarization, document classification assistance, explanations, absence/withdrawal-document summaries, judgment metadata extraction, case organization assistance.

AI proposes or assists. Authorized humans decide.

## 13. Speech-to-Text

**Use:** faster-whisper.

Architecture: Audio → faster-whisper → draft transcript → authorized human review → verified proceeding record.

An unreviewed transcript must never automatically become official proceeding text.

## 14. Scheduling

**Use:** Google OR-Tools for constraint-based scheduling/recommendation.

Required flow: OR-Tools recommends → Court Authority reviews → Court Authority confirms → official hearing update.

OR-Tools must NOT independently confirm final hearing schedules.

## 15. Case Prioritization

**Use:** Deterministic Explainable Rule Engine. Do NOT ask the LLM to determine case priority.

Architecture: Verified database facts → deterministic rule engine → priority result → optional LLM explanation → Court Authority view.

## 16. QR

Use server-side QR generation (Python QR library) and a browser/PWA scanner.

QR must contain an opaque secure case-access reference or a secure HTTPS resolver URL. QR must NOT contain sensitive case details directly. QR is NOT an authentication bypass.

## 17. NFC

**Use:** NDEF HTTPS NFC card + Web NFC API where supported.

The NFC card contains an opaque HTTPS URL (e.g., `https://app.example.in/nfc/c/{opaque-random-token}`).

It must NOT contain: password, raw Bar Registration ID, JWT, access token, refresh token, personal case data, reusable account credential.

NFC flow: Tap NFC card → HTTPS URL opens → server validates card token → identify registered lawyer → verify card active → verify registered device → WebAuthn/passkey verification → authenticated session → Lawyer dashboard.

## 18. Passkeys and Biometrics

**Use:** WebAuthn / Passkeys. Device biometrics are provided through the device authenticator. The backend must verify the WebAuthn assertion.

Support: credential registration, challenge generation, challenge expiry, assertion verification, credential counter handling, credential revocation.

## 19. Authentication

**Use:** Secure HttpOnly cookie-based authentication. A short-lived JWT MAY be used internally inside the secure cookie architecture.

Do NOT store authentication JWTs in localStorage. Cookies must use: HttpOnly, Secure (in production), appropriate SameSite.

## 20. Password Security

**Use:** Argon2id. Never store plaintext passwords, encrypt passwords for later recovery, log passwords, place passwords on NFC, or include passwords in browser-visible storage.

## 21. Authorization

**Use:** RBAC + case-level authorization. Roles: `POLICE`, `LAWYER`, `COURT_AUTHORITY`. Do NOT create `CLIENT` as an authenticated application role.

Authorization must be enforced by FastAPI. Frontend hiding alone is never sufficient.

## 22. Audit System

Use append-oriented/append-only audit history. Historical audit events must not be editable through ordinary application APIs. See `08-audit.md` for auditable actions.

## 23. Reverse Proxy

**Use:** Nginx for reverse proxying, HTTPS termination, request routing, upload limits, production security headers.

Preferred routing: `app.example.in/` → Next.js, `app.example.in/api/` → FastAPI.

## 24. Deployment

**Use:** Docker + Docker Compose. Services: Next.js, FastAPI, PostgreSQL, Redis, Celery worker, MinIO, Ollama, Nginx.

Prefer a stable demonstration architecture over unnecessary microservice complexity.

## 25. CI

**Use:** GitHub Actions. Run: frontend lint, frontend typecheck, backend lint, backend tests, frontend tests (where available), production build. A failing CI check must not be silently ignored.

## 26. Development Environment

Tools: Antigravity, VS Code, Git, GitHub, Docker.

Never regenerate the entire project simply because a new layer is requested.

---

## Technology Resolution Rules

When any existing prompt contains an ambiguous technology option, interpret it according to this locked stack:

| Ambiguous Reference | Resolves To |
|---|---|
| "Celery / ARQ" | Celery + Redis |
| "JWT / secure session" | Secure HttpOnly cookie architecture, optionally with short-lived JWT internally |
| "Web NFC" | NDEF HTTPS NFC card + Web NFC where supported |
| "AES-256" | AES-256-GCM where application-layer AES is implemented |
| "Object storage" | MinIO |
| "Scheduling engine" | Google OR-Tools |
| "Priority calculation" | Deterministic Explainable Rule Engine |

Do not modify product workflows or business requirements while applying this amendment.
