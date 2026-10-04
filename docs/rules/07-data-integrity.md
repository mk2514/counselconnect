# Data Integrity Rules

These rules define database transaction requirements, constraint usage, and data storage standards for CounselConnect.

## Database Transactions

Use database transactions for multi-step official operations.

### Example

When a Court Authority approves an absence:

1. Update the absence request status to "approved"
2. Create an associated audit event

Both operations must commit successfully together. If one fails, **roll back the entire transaction**. The system must never be left in a state where the absence is approved but no audit record exists, or vice versa.

### Rule

Any operation that involves multiple related database writes must be wrapped in a transaction. If any step in the transaction fails, all changes must be rolled back.

## Database Constraints

### Foreign Keys

Use foreign keys to enforce referential integrity between related tables. Every reference to another entity (e.g., a case referencing a CSR, a hearing referencing a case) must be backed by a foreign key constraint.

### Unique Constraints

Use appropriate unique constraints to prevent duplicate records where business rules require uniqueness (e.g., CSR numbers, Bar Registration IDs, FIR numbers within a jurisdiction).

### Indexes

Use indexes for commonly searched case identifiers to ensure acceptable query performance. At minimum, index:

- CSR number
- FIR number
- Case number
- Actor identifiers (Police Station Code, Bar Registration ID, JO Code)

## Data Storage Standards

### No JSON for Relational Data

Do not store important relational data only inside arbitrary JSON fields when proper tables are appropriate.

Structured, queryable data that participates in relationships, constraints, or reporting must be stored in properly designed relational tables with appropriate columns, types, and constraints.

### No localStorage as Database

Do not use browser localStorage as the authoritative database.

localStorage may be used for UI preferences, cached display state, or transient client-side data. It must never be the source of truth for case data, user records, or any official information.
