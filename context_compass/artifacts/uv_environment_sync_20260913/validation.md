# Owner environment sync validation

Task: tickets/tasks/2026-09-13_sync_owner_uv_environment_task.md.
Completed validation: 2026-09-13T20:48:32Z.

- Target: .venv_new, existing uv-managed CPython 3.14.7 free-threaded Windows x64.
- uv version: 0.12.13; existing repository uv.lock used unchanged.
- Command: uv sync --locked --all-groups --inexact --python .venv_new/Scripts/python.exe --no-python-downloads.
- UV_PROJECT_ENVIRONMENT explicitly targeted .venv_new; cache stayed inside this artifact directory.
- Twelve tools upgraded; editable Melder 0.2.40 installed from the current checkout.
- Every one of the forty pre-existing package names remains installed; no extra package removed.
- Repeating the same selection with --offline --check reports no changes.
- uv pip check reports all 41 installed package names compatible.
- Melder imports from src/melder/__init__.py, with Py_GIL_DISABLED=1 and GIL off.
- Melder metadata has no runtime Requires-Dist entries.
- pyproject.toml, uv.lock and .venv_new/pyvenv.cfg hashes match the before snapshot.
- pytest 9.1.1, Ruff 0.16.6, build 1.6.0 and mypy 2.3.1 launch successfully.
- Full tests were not run; validation here checks the installation and environment contract.

The first download attempt failed under the network sandbox. The network-enabled retry prepared all
packages, then Windows blocked replacing ruff.exe while this project's `ruff.exe server` was running.
Only that server (verified PID/path/arguments) was stopped; the cached retry completed and the
post-install checks above passed. The unrelated CommandOps Ruff server was left running.
This project's Ruff server had not restarted at final inspection; restart its editor integration.

Evidence: before.json, dry-run.log, sync.log, sync-network.log, sync-complete.log, after.json,
verification.json. importlib reports duplicate Melder metadata through its editable source path;
the package-name comparison and uv pip check count 41 distinct installed packages.
