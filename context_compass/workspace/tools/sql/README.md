# sql

Purpose
- Provide workspace-owned facades for SQLite tooling.
- Separate single-table CRUD operations from multi-table query workflows.

Directories
- crud/: registry-backed CRUD execution and CRUD registry inspection.
- query/: registry-backed query execution and query registry inspection.

Notes
- Use CRUD for single-table create/read/update/delete operations.
- Use query for multi-table or complex SQL that does not map to a single table.
- These scripts are facades; keep logic in ai_restricted tools.
