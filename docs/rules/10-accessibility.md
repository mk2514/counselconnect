# Accessibility Rules

These rules define accessibility requirements for the CounselConnect interface.

## Form Fields

Every field must have a label.

- Use `<label>` elements with `for` attributes pointing to the corresponding input.
- Do not use placeholder text as a substitute for labels.
- Labels must be visible and persistent, not hidden or removed on focus.

## Keyboard Navigation

Keyboard navigation must function throughout the application.

- All interactive elements must be reachable via the Tab key.
- Interactive elements must be operable via keyboard (Enter, Space, arrow keys as appropriate).
- Tab order must follow a logical reading order.
- Custom interactive components must have appropriate `tabindex` values.

## Focus State

Focus state must be visible.

- Every focusable element must display a clearly visible focus indicator.
- Do not remove the default browser focus outline without providing a custom alternative that is equally visible.
- Focus indicators must have sufficient contrast against the background.

## Dialog Focus Management

Dialogs must trap focus properly.

- When a dialog opens, focus must move to the dialog.
- Tab navigation must cycle within the dialog while it is open.
- When a dialog closes, focus must return to the element that triggered it.
- Pressing Escape must close the dialog (where appropriate).

## Color Independence

Important controls must not rely only on color.

- Status indicators must include text labels, icons, or patterns in addition to color.
- Error states must not be communicated solely through a red border or color change.
- Interactive elements must be identifiable without relying on color alone.

## Tables

Tables require usable headings.

- Use `<th>` elements for header cells.
- Use `scope` attributes (`col` or `row`) on header cells.
- Complex tables should use `<caption>` elements for context.
- Data tables must not be used for layout purposes.

## Status Indicators

Status indicators require text labels.

- Every status badge, icon, or color indicator must include a visible text label or accessible label (`aria-label`) that describes the status.
- Do not communicate status through color or icons alone.

## Priority

Do not sacrifice accessibility for visual styling.

Accessibility requirements take precedence over visual design preferences. If a visual design choice conflicts with an accessibility requirement, the accessible implementation must be used.
