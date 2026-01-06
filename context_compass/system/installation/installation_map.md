# Installation Map

Purpose
- Describe the installation surface area and build flow.
- Identify which files are inputs to the build runner.

Layout
- build runner: `installation/build_runner.py`
- build manifest: `installation/build_manifest.json`
- build scripts: `installation/build/`
- custom build scripts: `installation/custom_build/`
- bootstrap scripts: `installation/linux/bootstrap.sh`, `installation/windows/bootstrap.ps1`
- environments: `installation/environments/`
  - env installers: `installation/environments/linux/install_active_env.sh`, `installation/environments/windows/install_active_env.ps1`
  - python version pin: `installation/environments/python_version.md`
  - requirements: `installation/environments/requirements.txt`
  - active envs: `installation/environments/active_environments/`
- storage root: `storage/`
  - SQLite assets: `storage/sqlite/`
  - Kuzu assets: `storage/kuzu/`

Build flow (high level)
1) Load `installation/build_manifest.json`.
2) Resolve database paths relative to the context_compass root.
3) Ensure SQLite and Kuzu databases exist on disk.
4) Execute build steps in manifest order (build, then custom_build).

Bootstrap flow (high level)
1) Run the OS-specific bootstrap script.
2) Bootstrap installs uv (if missing) and creates the active environment.
3) Bootstrap runs the build runner to seed databases.

Notes
- Build steps must implement `run(context: BuildContext) -> None`.
- Manifest entries are the source of truth for DB paths and build steps.
