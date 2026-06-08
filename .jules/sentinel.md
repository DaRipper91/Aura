## 2024-06-05 - Implicit HTML Evaluation in PySide6 QTextEdit
**Vulnerability:** Unescaped user input passed to `QTextEdit.setHtml()` and `QTextEdit.append()` allows HTML Injection and Cross-Site Scripting (XSS) / UI Spoofing.
**Learning:** PySide6's `QTextEdit` component evaluates HTML implicitly. If raw user inputs (like chat messages or workspace directory paths) are embedded directly into HTML strings without escaping, malicious users or models can inject arbitrary HTML tags.
**Prevention:** Always use `html.escape()` from the Python standard library on any user-provided or dynamic text before concatenating it into an HTML string that will be rendered by `QTextEdit`.

## 2024-06-08 - Command Injection in Python `subprocess.run`
**Vulnerability:** Command injection vulnerability via `shell=True` and string interpolation in `subprocess.run` (found in `aider_fix` tool).
**Learning:** Using `shell=True` with `f-strings` or other forms of string concatenation allows users (or the LLM itself) to inject arbitrary shell commands by crafting malicious input strings containing shell operators (e.g., `;`, `&`, `|`, `$(...)`).
**Prevention:** Avoid `shell=True` whenever possible. Always pass arguments as a list to `subprocess.run` rather than as a single interpolated string. This lets the operating system directly pass the arguments to the executable without shell parsing.
