# Reset Map

Purpose
- Define what reset_system removes and what it preserves.
- Keep reset behavior deterministic and safe to rerun.

Reset targets (removed)
- SQLite DB files listed in `installation/build_manifest.json`.
- SQLite sidecar files for those DBs:
  - `*.db-wal` (WAL log)
  - `*.db-shm` (shared memory file)
  - `*.db-journal` (rollback journal)
- Kuzu DB paths listed in `installation/build_manifest.json`.
  - Kuzu paths may be files or directories.
- Active environments under `installation/environments/active_environments/`.

Preserved assets (not removed)
- `installation/build_manifest.json`
- `installation/build/` and `installation/custom_build/` scripts
- `storage/sqlite/*.tables.json` and `storage/kuzu/*.tables.json`
- `storage/sqlite/*.seed.json` (registry and config seeds)
- Documentation and README files

Reset entrypoint
- `installation/reset_system.py`
- Default is dry-run; pass `--apply` to delete files.
