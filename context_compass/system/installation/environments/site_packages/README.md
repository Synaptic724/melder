# site-packages integration

Purpose
- Document how the active environment gains access to the repo root for imports.

What the installers do
- After the venv is created and dependencies are installed, the OS-specific installers write
  `context_compass_repo.pth` into the venv's site-packages directory.
- The file contains a single line: the repo root (parent of `context_compass/`).
- Python automatically reads `.pth` files at startup, so `import context_compass` works even
  when scripts are executed by file path instead of `-m`.

Where the `.pth` lives
- The file is written into the active venv's site-packages directory (not this repo).
- To discover the exact location, use the venv python:
    - `python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])"`

Verify
- With the venv python, list the file:
    - Linux/macOS: `ls <site-packages>/context_compass_repo.pth`
    - Windows: `dir <site-packages>\context_compass_repo.pth`
- The file should contain the repo root path on a single line.

Notes
- The `.pth` file is venv-scoped and does not affect system Python installs.
- Re-running the installer is safe; it overwrites the `.pth` with the current repo root.
