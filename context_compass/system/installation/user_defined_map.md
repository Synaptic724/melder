# User-Defined Behavior Map

Purpose
- Document where user-defined behaviors can plug into installation.
- Keep extension points explicit and reviewable.

User-defined build steps
- Directory: `installation/custom_build/`
- Manifest phase: `custom_build`
- Contract: each script implements `run(context: BuildContext) -> None`.

User-defined database surfaces
- SQLite registry: `storage/sqlite/user_defined.tables.json`
- SQLite DB file: `storage/sqlite/user_defined.db`
- Kuzu registry: `storage/kuzu/user_defined.tables.json`
- Kuzu DB path: `storage/kuzu/user_defined.kuzu`

Notes
- Update `installation/build_manifest.json` when adding user-defined build steps.
- User-defined DBs are created by the build runner when listed in the manifest.
