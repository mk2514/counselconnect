# CounselConnect

Judicial Case Management Platform connecting Police, Lawyers, and Court Authorities through a unified digital case lifecycle.

## Overview

CounselConnect manages the complete lifecycle of judicial cases through a single, continuous Case Status Record (CSR). Every entity in the system -- from FIR filing through final judgment -- remains connected to the same CSR throughout the case lifecycle.

### Platform Actors

| Role | Identity | Scope |
|------|----------|-------|
| Police | Police Station Code | FIR filing, investigation, evidence management |
| Lawyer | Bar Registration ID | Case representation, hearing attendance, document submission |
| Court Authority | JO Code | Case administration, hearings, orders, judgments |

The client or party is not a separate application user. Clients exist inside case records and are represented through authorized lawyers.

## Local AI document processing

FIR extraction and case summaries use the Ollama service configured by
`OLLAMA_BASE_URL` and `OLLAMA_MODEL`. For the default scanned-document flow,
install the vision model with `ollama pull llama3.2-vision`. AI results remain
candidates: the Police user reviews and submits case details before they become
official data. If Ollama is unavailable, processing is marked failed and the
case can still be completed manually.

## Project Rules

All development on this project must follow the mandatory rules documented in [RULES.md](RULES.md).

The full rule set is organized under [`docs/rules/`](docs/rules/):

| Document | Scope |
|----------|-------|
| [Architecture](docs/rules/01-architecture.md) | CSR lifecycle, roles, AI boundaries |
| [UI Design](docs/rules/02-ui-design.md) | Visual direction, palette, prohibitions |
| [Functionality](docs/rules/03-functionality.md) | Button behavior, state management |
| [Form Validation](docs/rules/04-form-validation.md) | Frontend and backend validation |
| [Authentication](docs/rules/05-authentication.md) | Registration, login, identity types |
| [Role Security](docs/rules/06-role-security.md) | Authorization, endpoint protection |
| [Data Integrity](docs/rules/07-data-integrity.md) | Transactions, constraints, storage |
| [Audit](docs/rules/08-audit.md) | Audit events, append-only records |
| [Security](docs/rules/09-security.md) | Passwords, uploads, secrets, CSRF |
| [Accessibility](docs/rules/10-accessibility.md) | Labels, keyboard, focus, color |
| [Responsive Design](docs/rules/11-responsive-design.md) | Desktop-first, tablet, mobile |

## License

Proprietary. All rights reserved.
