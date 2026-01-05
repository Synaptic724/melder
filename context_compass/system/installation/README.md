# Installation

Purpose
- Provide a single bootstrap that installs the active Python environment and seeds system databases.
- Use uv to install the pinned Python version and dependencies.

Requirements
- Internet access for uv + dependency installs.
- The pinned Python version lives in `installation/environments/python_version.md`.

Windows (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File context_compass\system\installation\windows\bootstrap.ps1
```

Linux/macOS (bash)
```bash
bash context_compass/system/installation/linux/bootstrap.sh
```

Dry run
- Windows:
  ```powershell
  powershell -ExecutionPolicy Bypass -File context_compass\system\installation\windows\bootstrap.ps1 -DryRun
  ```
- Linux/macOS:
  ```bash
  DRY_RUN=1 bash context_compass/system/installation/linux/bootstrap.sh
  ```

What the bootstrap does
1) Installs uv (if missing).
2) Reads `installation/environments/python_version.md`.
3) Creates the active environment under `installation/environments/active_environments/`.
4) Installs dependencies from `installation/environments/requirements.txt`.
5) Runs the build runner to seed SQLite/Kuzu databases.

Active environment path
- `context_compass/system/installation/environments/active_environments/context_compass_py<version>`
- Example (Python 3.13.11):
  `context_compass/system/installation/environments/active_environments/context_compass_py3_13_11`

Build runner (DB init + build scripts)
- Initializes SQLite and Kuzu database files defined in `context_compass/system/installation/build_manifest.json`.
- Executes build scripts in the order listed in the manifest.
- Build scripts live in:
  - `context_compass/system/installation/build`
  - `context_compass/system/installation/custom_build`
- Each build script must implement `run(context: BuildContext) -> None`.

Usage (manual, if needed)
```bash
python context_compass/system/installation/build_runner.py
python context_compass/system/installation/build_runner.py --manifest path/to/build_manifest.json
```

Reset system (remove DB artifacts)
- Removes database artifacts declared in the build manifest.
- Removes active environments under `installation/environments/active_environments/`.
- Default is dry-run; pass `--apply` to delete files.
```bash
python context_compass/system/installation/reset_system.py
python context_compass/system/installation/reset_system.py --apply
```

Installation maps
- `context_compass/system/installation/installation_map.md`
- `context_compass/system/installation/reset_map.md`
- `context_compass/system/installation/user_defined_map.md`

Next steps
- Use the active environment interpreter for tools:
  - `context_compass/system/installation/environments/active_environments/context_compass_py<version>/Scripts/python.exe context_compass/system/ai_restricted/system_management/validate.py --repo-root .` (Windows)
  - `context_compass/system/installation/environments/active_environments/context_compass_py<version>/bin/python context_compass/system/ai_restricted/system_management/validate.py --repo-root .` (Linux/macOS)

Notes
- The bootstrap scripts are safe to inspect and do nothing unless executed.
- Manifest paths are resolved relative to the `context_compass` directory.
