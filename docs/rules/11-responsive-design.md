# Responsive Design Rules

These rules define the responsive design targets and constraints for CounselConnect.

## Primary Target

The primary target is a **desktop/laptop judicial workplace interface**.

The interface must be designed and optimized for desktop-class screens first. This is where Court Authorities, Police, and Lawyers will perform the majority of their work.

## Tablet Support

The interface must also support tablets.

- Layouts should adapt gracefully to tablet-width screens.
- Core functionality must remain fully usable on tablets.
- Touch targets must be appropriately sized for tablet interaction.

## Mobile Support

Mobile must remain usable for the following essential operations:

| Operation | Description |
|-----------|-------------|
| **Login** | Users must be able to authenticate on mobile devices |
| **NFC link opening** | NFC-based workflows must function on mobile |
| **Case lookup** | Users must be able to search for and view case information |
| **Key lawyer operations** | Essential lawyer tasks must be accessible |
| **Document capture** | Camera-based document capture must work where required |

## Mobile Constraints

**Do not attempt to compress complex court agenda management into an unusable mobile layout.**

Complex administrative interfaces (such as court agenda management, multi-column case dashboards, and detailed hearing scheduling) are designed for desktop use. On mobile, these interfaces should either:

1. Provide a simplified, task-focused view of the most essential information.
2. Direct users to access the full interface on a desktop or tablet.

The goal is usability, not feature parity on every screen size.
