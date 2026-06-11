## 2024-06-05 - Explicit Focus States Needed for PySide6 Stylesheets
**Learning:** When applying custom stylesheets to PySide6 components (like overriding background or border colors on `QLineEdit`, `QPushButton`, and `QComboBox`), the default OS-level focus indicators are removed. This severely harms keyboard accessibility.
**Action:** Always include explicit `:focus` pseudo-class rules in custom Qt stylesheets to ensure keyboard navigation remains visible and accessible.
## 2026-06-10 - Explicit Disabled States Needed for PySide6 Stylesheets
**Learning:** When applying custom stylesheets to PySide6 components, the default OS-level visual cues for inactive (disabled) elements are overridden. Without explicit styles, disabled inputs and buttons look identical to active ones, degrading accessibility and user intuition.
**Action:** Always define explicit `:disabled` pseudo-class rules alongside `:focus` and `:hover` states in custom Qt stylesheets to maintain clear visual feedback.
## 2024-08-01 - Explicit Checked States Needed for Toggleable Buttons in PySide6
**Learning:** When using toggleable buttons (`QPushButton` with `setCheckable(True)`) and applying a custom stylesheet in PySide6, the default OS-level checked styling is lost. This results in the button looking identical whether it is pressed or not, causing confusion about the active state.
**Action:** Always include an explicit `:checked` pseudo-class rule for `QPushButton` alongside normal, hover, focus, and disabled states in custom QSS to ensure users have clear visual feedback of the active panel or state.
