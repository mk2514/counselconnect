# Interaction Matrix

| Page | Control | Visible to role | Expected result | Frontend handler | API endpoint | Backend service | Database effect | Audit event | Loading state | Success state | Error state | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Login | Submit | All | Login session created | handleLogin() | POST /api/auth/login | auth_service | Session created | None | Yes | Yes | Yes | WORKING |
| Register | Submit | All | Account created | handleRegister() | POST /api/auth/register | auth_service | User insert | USER_REGISTERED | Yes | Yes | Yes | WORKING |
| Police > Dashboard | Create Case | POLICE | CSR generated | handleCreateCase() | POST /api/police/cases/draft | police_service | cases insert | CASE_CREATED | Yes | Yes | Yes | WORKING |
| Police > FIR Upload | Upload FIR | POLICE | Upload starts | handleUpload() | POST /api/police/cases/{id}/documents/fir | police_service | documents insert | FIR_UPLOADED | Yes | Yes | Yes | WORKING |
| Police > FIR Verify | Confirm | POLICE | Real data updated | verifyAiData() | PUT /api/police/cases/{id}/fir-data | police_service | cases update | FIR_VERIFIED | No | No | No | UI ONLY |
| Police > Evidence | Add Evidence | POLICE | Evidence added | handleAddEvidence()| POST /api/police/cases/{id}/evidence| police_service | evidence insert | EVIDENCE_ADDED | No | No | No | UI ONLY |
| Police > Parties | Add Party | POLICE | Party added | handleAddParty() | POST /api/police/cases/{id}/parties | police_service | parties insert | PARTY_ADDED | No | No | No | UI ONLY |
| Lawyer > Dashboard | View Case | LAWYER | Case opened | navigate() | GET /api/lawyer/cases/{id} | lawyer_service | None | None | No | No | No | WORKING |
| Lawyer > Case | Mark Absent | LAWYER | Absence workflow | handleAbsent() | POST /api/lawyer/cases/{id}/absence | lawyer_service | absence insert | ABSENCE_REQUESTED | No | No | No | UI ONLY |
| Lawyer > Case | Withdraw | LAWYER | Withdrawal workflow | handleWithdraw() | POST /api/lawyer/cases/{id}/withdrawal | lawyer_service | withdraw insert | WITHDRAW_REQUESTED | No | No | No | UI ONLY |
| Court > Agenda | Approve Absence | COURT | Absence approved | handleApprove() | POST /api/court/absence/{id}/approve | court_service | absence update | ABSENCE_APPROVED | No | No | No | UI ONLY |
| Court > Hearing | Submit Judgment | COURT | Judgment uploaded | uploadJudgment() | POST /api/court/cases/{id}/judgment | court_service | judgment insert | JUDGMENT_ISSUED | No | No | No | UI ONLY |

*(Note: This matrix will be incrementally expanded during Phase 3 when I perform the complete UI control audit. This initial version highlights the known state of critical paths.)*
