## 2024-06-05 - Explicit Focus States Needed for PySide6 Stylesheets
**Learning:** When applying custom stylesheets to PySide6 components (like overriding background or border colors on `QLineEdit`, `QPushButton`, and `QComboBox`), the default OS-level focus indicators are removed. This severely harms keyboard accessibility.
**Action:** Always include explicit `:focus` pseudo-class rules in custom Qt stylesheets to ensure keyboard navigation remains visible and accessible.
