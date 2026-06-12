## 2024-06-05 - Implicit HTML Evaluation in PySide6 QTextEdit
**Vulnerability:** Unescaped user input passed to `QTextEdit.setHtml()` and `QTextEdit.append()` allows HTML Injection and Cross-Site Scripting (XSS) / UI Spoofing.
**Learning:** PySide6's `QTextEdit` component evaluates HTML implicitly. If raw user inputs (like chat messages or workspace directory paths) are embedded directly into HTML strings without escaping, malicious users or models can inject arbitrary HTML tags.
**Prevention:** Always use `html.escape()` from the Python standard library on any user-provided or dynamic text before concatenating it into an HTML string that will be rendered by `QTextEdit`.

## 2024-06-09 - Command Injection in Python subprocess with shell=True
**Vulnerability:** Command injection vulnerability identified in `ToolRegistry.aider_fix`.
**Learning:** Using `shell=True` along with string interpolation to pass user-controlled data to `subprocess.run` creates an immediate command injection flaw.
**Prevention:** Pass command arguments as a list to `subprocess.run` and ensure `shell=True` is not used.

## 2024-06-12 - Command Injection in nested Bash and SQL construction via SSH
**Vulnerability:** Command and SQL injection vulnerability in `long_term_memory` tool sending remote commands via SSH.
**Learning:** Even when using `shlex.quote()`, placing the quoted string inside double quotes (`"..."`) allows bash to interpret variables and subshells (`$()`, \`\`) if the original string was not quoted correctly, but more importantly, when injecting values into an SQL command passed to `sqlite3`, single quotes must be properly escaped for SQL (`''`) and then the *entire* SQL command should be quoted for bash using `shlex.quote()` before being executed over SSH. Combining `shlex.quote` directly into a double quoted bash string (`"INSERT ... ({safe_content})"`) is incorrect usage of `shlex.quote()` and leads to syntax errors and vulnerabilities.
**Prevention:** 1. Escape SQL string literals appropriately (e.g., replace `'` with `''`). 2. Construct the full SQL query string. 3. Use `shlex.quote(sql_query)` to safely quote the entire SQL string for bash execution. Do not construct nested shell commands using python string interpolation with double quotes around `shlex.quote()` results.
