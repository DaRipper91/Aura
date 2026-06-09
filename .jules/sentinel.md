## 2024-06-05 - Implicit HTML Evaluation in PySide6 QTextEdit
**Vulnerability:** Unescaped user input passed to `QTextEdit.setHtml()` and `QTextEdit.append()` allows HTML Injection and Cross-Site Scripting (XSS) / UI Spoofing.
**Learning:** PySide6's `QTextEdit` component evaluates HTML implicitly. If raw user inputs (like chat messages or workspace directory paths) are embedded directly into HTML strings without escaping, malicious users or models can inject arbitrary HTML tags.
**Prevention:** Always use `html.escape()` from the Python standard library on any user-provided or dynamic text before concatenating it into an HTML string that will be rendered by `QTextEdit`.

## 2024-06-09 - Command Injection in Python subprocess with shell=True
**Vulnerability:** Command injection vulnerability identified in `ToolRegistry.aider_fix`.
**Learning:** Using `shell=True` along with string interpolation to pass user-controlled data to `subprocess.run` creates an immediate command injection flaw.
**Prevention:** Pass command arguments as a list to `subprocess.run` and ensure `shell=True` is not used.
