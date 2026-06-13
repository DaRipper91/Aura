## 2024-06-05 - Explicit Focus States Needed for PySide6 Stylesheets
**Learning:** When applying custom stylesheets to PySide6 components (like overriding background or border colors on `QLineEdit`, `QPushButton`, and `QComboBox`), the default OS-level focus indicators are removed. This severely harms keyboard accessibility.
**Action:** Always include explicit `:focus` pseudo-class rules in custom Qt stylesheets to ensure keyboard navigation remains visible and accessible.
## 2026-06-10 - Explicit Disabled States Needed for PySide6 Stylesheets
**Learning:** When applying custom stylesheets to PySide6 components, the default OS-level visual cues for inactive (disabled) elements are overridden. Without explicit styles, disabled inputs and buttons look identical to active ones, degrading accessibility and user intuition.
**Action:** Always define explicit `:disabled` pseudo-class rules alongside `:focus` and `:hover` states in custom Qt stylesheets to maintain clear visual feedback.
## 2026-06-11 - Explicit Checked States Needed for PySide6 Stylesheets
**Learning:** In PySide6 Qt Style Sheets, toggleable components like `QPushButton` (using `setCheckable(True)`) require an explicitly defined `:checked` pseudo-class rule to provide visual feedback for their active state when custom stylesheets override default OS cues.
**Action:** Always include explicit `:checked` pseudo-class rules in custom Qt stylesheets for checkable components to ensure active states are visually communicated to the user.
