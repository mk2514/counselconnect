# UI Design Rules

These rules define the approved visual direction, color palette, typography, iconography, and explicit prohibitions for the CounselConnect interface.

## Approved Visual Direction

The interface must follow this visual direction:

- Light theme
- Official judicial/government interface
- Light or white sidebar
- Warm white/light grey backgrounds
- Restrained terracotta accent
- Subtle light terracotta gradient only where appropriate
- Structured enterprise/government dashboard
- Professional typography
- Strong information hierarchy
- Compact but readable layout

**Do not introduce a new visual direction without user approval.**

## Color Palette

### Core Colors

| Token | Hex | Usage |
|-------|-----|-------|
| Background | `#F7F6F3` | Page background |
| Surface | `#FFFFFF` | Cards, panels, content areas |
| Sidebar | `#FCFBF8` | Sidebar background |
| Primary text | `#1F2428` | Headings, body text |
| Secondary text | `#667085` | Labels, descriptions, muted text |
| Border | `#E4E1DC` | Dividers, card borders, input borders |

### Terracotta Palette

Terracotta is an **accent color**, not the entire interface. Use it sparingly for primary actions, active states, and key highlights.

| Token | Hex | Usage |
|-------|-----|-------|
| Terracotta primary | `#B85C3A` | Primary buttons, active nav items, key links |
| Terracotta dark | `#8E432B` | Hover states, pressed states |
| Terracotta soft | `#E8B49F` | Subtle highlights, secondary accents |
| Terracotta background | `#F6E7E0` | Light background fills, badges, tags |

### Subtle Gradient

Use sparingly and only where appropriate:

```css
background: linear-gradient(135deg, #F4DDD3 0%, #E8B49F 100%);
```

### Status Colors

Use dedicated status colors. Do not misuse terracotta as an error color.

| Status | Color | Usage |
|--------|-------|-------|
| Completed/Approved | Green | Success states, approved actions |
| Pending/Review | Amber | Awaiting action, in-review states |
| Rejected/Critical error | Red | Rejected items, error states |
| Information/Current process | Blue or neutral | Informational messages, active processes |

## Typography

- Use professional typography.
- Establish strong information hierarchy through font weight, size, and spacing.
- Maintain compact but readable layouts.

## Iconography

- Use professional iconography from **one consistent icon library** throughout the application.
- Do not mix icon libraries.
- Do not use emoji icons.

## Border Radius

- Use approximately **6px to 10px** border radius.
- Primary buttons should be **rectangular with modest rounding**.
- Do not use pill-shaped buttons throughout the interface.

## Prohibitions

The following are explicitly prohibited:

### Visual Effects
- Purple gradients
- Neon gradients
- Random gradients
- Glassmorphism
- Unnecessary glowing effects
- Excessive scroll animations
- Parallax effects
- Cursor animations

### Layout
- Oversized startup hero sections
- Giant rounded cards
- Excessive card nesting

### Content
- Vague marketing hero text
- Fake counters
- Fake metrics
- Fake testimonials
- Fake reviews
- Fake organizations
- Fake usage statistics
- Generic AI marketing copy
- Em dashes in website copy

### Media
- AI-generated artwork
- Generic AI illustrations
- "Made with AI" labels

### Buttons
- Pill-shaped buttons throughout the interface (modest rounding is acceptable)
