# Installation

Purpose
- Provide a minimal bootstrap for Python 3.10+ and optional graph tooling.
- Create a local venv scoped to `context_compass/.venv`.

Requirements
- Python 3.10+ available on PATH.
- Internet access for `pip install` (packages: `pydantic`, `graphiti-core[kuzu]`).

Windows (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File context_compass\installation\windows\bootstrap.ps1
```

Linux/macOS (bash)
```bash
bash context_compass/installation/linux/bootstrap.sh
```

Dry run
- Windows:
  ```powershell
  powershell -ExecutionPolicy Bypass -File context_compass\installation\windows\bootstrap.ps1 -DryRun
  ```
- Linux/macOS:
  ```bash
  DRY_RUN=1 bash context_compass/installation/linux/bootstrap.sh
  ```

What the bootstrap does
1) Verifies Python 3.10+.
2) Creates a venv at `context_compass/.venv`.
3) Installs `pydantic` and `graphiti-core[kuzu]`.
4) Runs a smoke import check for `pydantic`, `kuzu`, and `graphiti_core`.

Next steps
- Use the venv interpreter for tools:
  - `context_compass/.venv/Scripts/python.exe context_compass/tools/validate.py --repo-root .` (Windows)
  - `context_compass/.venv/bin/python context_compass/tools/validate.py --repo-root .` (Linux/macOS)

Notes
- The bootstrap scripts are safe to inspect and do nothing unless executed.
- If Python is missing or too old, the scripts exit with a non-zero code and show instructions.
