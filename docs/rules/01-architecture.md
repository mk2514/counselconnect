# Architecture Rules

These rules define the foundational architecture of CounselConnect, including platform actors, the CSR lifecycle model, and AI usage boundaries.

## Platform Actors

The application connects three types of users:

| Actor | Description |
|-------|-------------|
| **Police** | Files FIRs, manages investigation, submits evidence |
| **Lawyer** | Represents clients/parties, attends hearings, submits documents |
| **Court Authority** | Administers cases, schedules hearings, issues orders and judgments |

### Client/Party Rule

- The client or party is **not** a separate application user.
- The client/party exists **inside a case record** and is represented through an authorized lawyer.
- Do not create a separate user account, login, or role for clients/parties.

## Central Architectural Rule

### ONE CSR = ONE CONTINUOUS DIGITAL CASE LIFECYCLE

The Case Status Record (CSR) is the central organizing entity. Every piece of data in the system connects to and remains associated with a single CSR throughout the entire lifecycle of a case.

### Entities Connected to the CSR

The following entities must all remain connected to the same CSR:

| Entity | Entity |
|--------|--------|
| FIR | Case details |
| Complainants | Accused persons |
| Witnesses | Investigating officer |
| Investigation | Evidence |
| Documents | Lawyer assignments |
| Hearings | Attendance |
| Absence requests | Absence proof |
| Court agenda | Proceedings |
| Rescheduling | Representation changes |
| Withdrawal/disposal requests | Final orders |
| Judgment | Audit history |

### CSR Invariants

These invariants must never be violated:

1. **Changing lawyers must not create a new CSR.** Lawyer reassignment is a modification within the existing CSR.
2. **Rescheduling must not create a new CSR.** A rescheduled hearing is an update to the existing CSR timeline.
3. **Withdrawal/disposal must not delete historical records.** All historical data remains permanently connected to the CSR.

## AI Control Model

The platform is not permitted to let AI make official judicial decisions.

### AI MAY

AI is permitted to perform the following assistive tasks:

- Perform OCR
- Extract document text
- Extract metadata
- Identify names and dates
- Organize documents
- Summarize documents
- Categorize cases
- Calculate administrative priority
- Explain prioritization factors
- Recommend scheduling options
- Transcribe speech
- Identify possible conflicts
- Summarize absence supporting documents
- Summarize withdrawal documents
- Extract judgment metadata

### AI MUST NOT Independently

AI is prohibited from independently performing any of the following:

- Determine guilt
- Convict
- Acquit
- Issue judgments
- Issue final orders
- Approve absences
- Reject absences
- Officially assign lawyers
- Approve lawyer retirement
- Reject lawyer retirement
- Select replacement lawyers
- Punish lawyers
- Approve withdrawal
- Reject withdrawal
- Permanently close cases
- Confirm final hearing dates
- Override Court Authority decisions

### Required Control Flow

All consequential state changes must follow this sequence:

```
AI proposes
    → Human reviews
        → Authorized human confirms
            → Official database state changes
```

**Never allow AI-generated JSON alone to write consequential official state changes.**

Every consequential action requires explicit human confirmation by an authorized user before the official database state is modified.
