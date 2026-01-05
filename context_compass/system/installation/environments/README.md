Use this directory to create and store the active Python environment for context_compass.

- The installation bootstrap calls the OS-specific scripts in this folder.
- Environments live under `active_environments/`.
- The Python version is pinned in `python_version.md`.
- Dependencies install from `requirements.txt`.

If you need to create the environment manually, run:
- Linux/macOS: `bash context_compass/system/installation/environments/linux/install_active_env.sh`
- Windows: `powershell -ExecutionPolicy Bypass -File context_compass\system\installation\environments\windows\install_active_env.ps1`

What the installers do
- Read `python_version.md` for the target runtime.
- Use `uv` (installed via curl/wget if missing) to install Python and create a venv.
- Create `active_environments/context_compass_py<version>` if it does not exist.
- Install `requirements.txt` into the active environment.

Notes
- Network access is required for `uv` installs and dependency downloads.
- Re-running the installer is safe; it will reuse the existing env path when present.
