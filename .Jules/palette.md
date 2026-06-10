## 2024-06-05 - Explicit Focus States Needed for PySide6 Stylesheets
**Learning:** When applying custom stylesheets to PySide6 components (like overriding background or border colors on `QLineEdit`, `QPushButton`, and `QComboBox`), the default OS-level focus indicators are removed. This severely harms keyboard accessibility.
**Action:** Always include explicit `:focus` pseudo-class rules in custom Qt stylesheets to ensure keyboard navigation remains visible and accessible.
## 2026-06-10 - Explicit Disabled States Needed for PySide6 Stylesheets
**Learning:** When applying custom stylesheets to PySide6 components, the default OS-level visual cues for inactive (disabled) elements are overridden. Without explicit styles, disabled inputs and buttons look identical to active ones, degrading accessibility and user intuition.
**Action:** Always define explicit `:disabled` pseudo-class rules alongside `:focus` and `:hover` states in custom Qt stylesheets to maintain clear visual feedback.
