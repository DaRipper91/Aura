## 2024-06-05 - O(N*M) Markdown Rendering Bottleneck in Stream UI
**Learning:** During LLM streaming (`handle_chunk`), `render_messages()` recalculates the full HTML for *all* past messages on every single token chunk received. Because `markdown_it` parsing is computationally heavy, this creates an O(N*M) rendering bottleneck (where N=past messages, M=tokens in current stream) that hangs the UI thread as the conversation grows.
**Action:** Always cache expensive string operations (like Markdown parsing) at the message object level in chat UIs to ensure streaming performance remains O(1) with respect to past messages.

## 2024-08-01 - O(N*M) DOM Layout Bottleneck in Stream UI
**Learning:** During fast LLM streaming, updating the `QTextEdit` HTML every single chunk causes extreme O(N*M) layout thrashing and redundant Markdown parsing, freezing the UI thread.
**Action:** Implemented a 33ms (~30 FPS) throttle for streaming UI updates and cached fully-rendered HTML blocks for past messages in `msg["_full_html"]` to bypass redundant layout and string formatting overhead.

## 2024-10-25 - Synchronous Disk I/O Bottleneck in UI Timer Loop
**Learning:** Checking for specific hardware states (like Asahi Linux via `/proc/device-tree/model`) using synchronous disk operations inside a UI timer loop (e.g., `update_telemetry` firing every 2s) causes redundant O(N) reads and unnecessary CPU usage, potentially leading to UI micro-stutters.
**Action:** Always cache hardware and environment variables at the instance level during initialization, preventing redundant synchronous disk I/O in UI loops.
