---
name: Cognitive Wellness
colors:
  surface: '#f3faff'
  surface-dim: '#cddce4'
  surface-bright: '#f3faff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#e7f6fe'
  surface-container: '#e1f0f8'
  surface-container-high: '#dbebf2'
  surface-container-highest: '#d6e5ed'
  on-surface: '#0f1d23'
  on-surface-variant: '#3f4943'
  inverse-surface: '#243238'
  inverse-on-surface: '#e4f3fb'
  outline: '#6f7a73'
  outline-variant: '#bec9c1'
  surface-tint: '#176b4d'
  primary: '#005138'
  on-primary: '#ffffff'
  primary-container: '#176b4d'
  on-primary-container: '#9ae9c3'
  inverse-primary: '#89d6b1'
  secondary: '#4f6074'
  on-secondary: '#ffffff'
  secondary-container: '#d2e4fc'
  on-secondary-container: '#55667a'
  tertiary: '#643f00'
  on-tertiary: '#ffffff'
  tertiary-container: '#845400'
  on-tertiary-container: '#ffd198'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#a4f3cc'
  primary-fixed-dim: '#89d6b1'
  on-primary-fixed: '#002114'
  on-primary-fixed-variant: '#005138'
  secondary-fixed: '#d2e4fc'
  secondary-fixed-dim: '#b6c8df'
  on-secondary-fixed: '#0a1d2e'
  on-secondary-fixed-variant: '#37485b'
  tertiary-fixed: '#ffddb6'
  tertiary-fixed-dim: '#ffb959'
  on-tertiary-fixed: '#2a1800'
  on-tertiary-fixed-variant: '#643f00'
  background: '#f3faff'
  on-background: '#0f1d23'
  surface-variant: '#d6e5ed'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 52px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 42px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 34px
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 34px
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-xl:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 20px
    fontWeight: '400'
    lineHeight: 32px
  body-lg:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  label-lg:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 22px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 15px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 18px
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-desktop: 2rem
  margin: 1.5rem
  margin-desktop: 3rem
  space-xs: 0.5rem
  space-sm: 0.75rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system establishes a restorative, dignified, and ultra-legible digital sanctuary for cognitive care, designed deliberately for older adults and their network of caregivers. The visual language blends Scandinavian clinical minimalism with domestic warmth—avoiding clinical sterility, childlike interfaces, and hyper-dense institutional dashboards.

The emotional baseline is safe, unhurried, reassuring, and mentally quiet. The UI reduces cognitive overhead by favoring predictable linear layouts, explicit labeled states, high-contrast visual cues, and generous touch points. Interactions are tactile yet gentle, providing positive reassurance at every milestone without visual noise or patronizing tones.

## Colors

The palette delivers calming clarity, high visual acuity, and effortless accessibility compliance (WCAG AAA for all text-to-background combinations).

- **Primary (`#176B4D`)**: Deep pine wellness green. Used for critical forward actions, wellness indicators, active progress bars, and high-priority controls.
- **Secondary (`#1F3042`)**: Resolute slate navy. Anchors persistent architectural framing (sidebar navigation, critical structural headers, and modal frame outlines) to instill trust and grounding.
- **Tertiary Accent (`#E9A23B`)**: Muted honey amber. Reserved exclusively for celebratory affirmations, cognitive streak achievements, and milestones. Never applied to danger or warning states.
- **Base Canvas (`#F7F8F4`)**: Warm tinted off-white canvas that reduces eye strain, glares, and retinal fatigue common with stark white backgrounds.
- **Surfaces (`#FFFFFF`)**: Crisp, immaculate container surfaces framed by soft supportive borders (`#DDE5E1`).
- **Semantic Badging & Highlights (`#E7F4ED`)**: Pale mint highlight wash paired with `#176B4D` typography for gentle status pills and active row selections.
- **Typography Tone**: Primary text is `#243238` (deep charcoal slate, avoiding harsh `#000000`), paired with `#66757D` for secondary dates, units, and timestamps.
- **Semantic Affirmation (`#238B5A`)**: Success indicators, routine completion checks, and safe cognitive benchmark indicators.

## Typography

Typography prioritizes cognitive comfort and age-related low-vision readability. **Plus Jakarta Sans** provides open counters and reassuring geometric curves for headlines and titles, while **Atkinson Hyperlegible Next**—specifically engineered for perceptual clarity—drives all body copy, navigation labels, and numeric readouts.

- Body text defaults to a spacious `18px` (`body-lg`) or `20px` (`body-xl`) in primary viewports to eradicate visual crowding.
- Line heights are generously spaced (minimum 1.5x font size) to simplify eye-tracking across lines.
- Content copy must be composed in direct, encouraging, short sentences without jargon, medical abbreviations, or ambiguous idioms.
- Uppercase styling is avoided entirely in instructional text to prevent misinterpretation and visual strain.

## Layout & Spacing

The architectural layout utilizes an asymmetrical, high-stability model:

- **Desktop Shell**: Anchored by a fixed 280px left sidebar in deep navy (`#1F3042`). Navigation items stay in an uncollapsed, un-truncated vertical state with a clear active pill indicator. The bottom houses a dedicated "Switch View" panel (Caregiver / Participant toggle).
- **Main Canvas**: A fluid workspace backed by `#F7F8F4` featuring an intentional maximum content cap of 1440px to ensure line-lengths do not span excessively wide.
- **Rhythm & Safe Areas**: Spacing strictly adheres to an 8px grid. Touch target envelopes never dip below a 48px by 48px box (extending to 56px for primary assessment cards and key inputs).
- **Responsive Adaptation**:
  - *Desktop (≥1024px)*: Persistent 280px sidebar, multi-column card layout with 32px gaps.
  - *Tablet (768px - 1023px)*: Sidebar collapses to an off-canvas drawer; main workspace switches to a 2-column or 1-column layout with 24px margins.
  - *Mobile (<768px)*: Full-width stacked linear hierarchy; bottom navigation dock for top 3 daily actions, cards occupy full width with 16px lateral padding.

## Elevation & Depth

Visual hierarchy uses clean containment borders coupled with soft, daylight ambient diffusion. Deep, dramatic drop shadows and glossy glassmorphic layers are deliberately excluded to prevent disorientation or blur-related visual distortions for senior users.

- **Base Cards & Surfaces**: Constructed with a crisp 1px perimeter border (`#DDE5E1`) and a calm ambient elevation: `box-shadow: 0 2px 8px -2px rgba(31, 48, 66, 0.05), 0 1px 3px 0 rgba(31, 48, 66, 0.03)`.
- **Active / Hover State**: When hovering or focusing interactive cards, the elevation raises gently with an accent border: `box-shadow: 0 8px 24px -4px rgba(23, 107, 77, 0.08)`, border changes to `#176B4D`.
- **Modals & Overlays**: Modals sit above a 40% `#1F3042` darkened veil (`backdrop-filter: blur(2px)`) to keep participants grounded without jarring context switching.

## Shapes

The design system standardizes on organic, approachable geometry:

- **Main Cards & Panels**: Fixed at `16px` (`rounded-lg` under Level 2), creating friendly, non-aggressive modular compartments.
- **Buttons & Control Inputs**: `12px` to `16px` radius, providing a pill-adjacent softness that clearly telegraphs tactile affordance.
- **Badges & Status Tags**: Full rounded pills (`9999px`) to distinguish meta information from clickable cards.
- **Checkboxes & Radios**: Checkboxes use `8px` corner rounding for comfortable internal checking; radio controls remain standard circular targets.

## Components

### Buttons
- **Primary**: Background `#176B4D`, text `#FFFFFF`, minimum height 52px (desktop/tablet) and 48px (mobile). Padding: 16px 28px. Font: `label-lg` (Atkinson Hyperlegible Next, 16px SemiBold). Pressed state: `#0F4C35`.
- **Secondary**: Surface `#FFFFFF`, border `2px solid #1F3042`, text `#1F3042`. Focus ring: 3px solid `#E7F4ED` with an outer 2px `#176B4D` focus indicator.
- **Ghost/Tertiary**: Text `#176B4D`, transparent background, with an explicit focus state and underline on hover.

### Chips & Badges
- **Active Status Badge**: Background `#E7F4ED`, text `#176B4D`, border `1px solid rgba(23, 107, 77, 0.2)`. Padding: 6px 14px. Border-radius: `9999px`.
- **Streak & Milestone Chip**: Background `#FFF8EB`, text `#8A5810`, border `1px solid #F5D399`. Accompanied by a clear 18px glyph icon.

### Selection Controls (Checkboxes & Radios)
- Minimum target dimension: 28px physical box centered within a 48px interactive target area.
- Checkbox: `2px solid #66757D` in default state. Selected state fills with `#176B4D` displaying a bold 3px white checkmark icon.
- Radio Button: Outer ring `#176B4D`, inner selected disc 14px solid `#176B4D`.

### Form Fields & Inputs
- Height: 52px.
- Background: `#FFFFFF`. Border: `2px solid #DDE5E1`. Roundedness: 12px.
- Label: Prominently displayed above the input (`label-md`, `#1F3042`), never reliance on placeholder text alone.
- Focused state: Border changes to `#176B4D` with `0 0 0 3px #E7F4ED` halo. Helper copy rendered in `#66757D`.

### Cards & Modules
- Background `#FFFFFF`, border `1px solid #DDE5E1`, padding 24px (mobile) to 32px (desktop).
- Header row features clean icon/title groupings with explicit separation before main interactive content.

### Cognitive Exercise Tiles (Platform Specific)
- Designed with high color differentiation, prominent pictorial cues, and immediate auditory/haptic visual confirmations upon selection.

### Caregiver / Participant View Switcher
- Persistent segmented pill switch positioned at the bottom of the 280px sidebar. Clear label indicating the active perspective with high visual contrast.