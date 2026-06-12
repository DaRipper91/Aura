# Repository Guidelines

## Project Structure & Module Organization
- `python/` contains the packaged Aura app: `aura/` for UI code, `aura_core/` for engine logic, `main.py` for the GUI entry point, and `aura_cli.py` for the CLI entry point.
- `main.go` is the Go desktop/TUI implementation; `go.mod` and `go.sum` define its Go dependencies.
- `README.md` documents the current product shape. Assets live under `python/aura/ui/` and project data lives in `models/`, `ollama/`, and `memory/`.
- Test and scratch files are at the repo root (`test_*.py`, `test_file.txt`); keep new tests close to the code they exercise when practical.

## Build, Test, and Development Commands
- `python3 -m pip install -e .` installs Aura in editable mode and refreshes the `aura` and `aura-gui` launchers.
- `aura` starts the CLI experience.
- `aura-gui` starts the Qt desktop UI.
- `python3 -m py_compile python/aura/ui/window.py python/aura_core/engine.py python/main.py` catches syntax errors quickly.
- `go run main.go` launches the Go TUI when you want to work on the Go path.

## Coding Style & Naming Conventions
- Use ASCII unless an existing file already uses Unicode styling.
- Prefer 4-space indentation in Python and idiomatic Go formatting (`gofmt` before committing Go changes).
- Keep names descriptive and consistent with existing modules: `aura_core`, `OllamaClient`, `AuraWindow`, `run_cli`.
- Avoid broad refactors; this repo mixes launcher, UI, and engine code, so changes should stay targeted.

## Testing Guidelines
- There is no formal automated test suite yet; use focused runtime checks and syntax checks.
- Name new tests with `test_*.py` if you add Python coverage.
- For UI changes, verify the launcher path and the desktop entry, not just imports.

## Commit & Pull Request Guidelines
- Commit messages in this repo follow short conventional prefixes such as `feat:`, `fix:`, and `chore:` followed by a concise imperative summary.
- Pull requests should explain the user-visible impact, note any launcher/runtime changes, and include screenshots for UI work.
- Call out any Ollama/model assumptions, because launch behavior depends on local runtime state.

## Security & Configuration Tips
- Do not commit local runtime state such as `.aura_session.json`, `~/.ollama`, or downloaded model blobs.
- If Ollama runs in a read-only home environment, set `AURA_OLLAMA_HOME` or `OLLAMA_MODELS` to a writable path before launching.
