# crud

Purpose
- Workspace facades for registry-backed SQLite CRUD execution.
- Workspace entrypoints for inspecting CRUD action registry entries.

Scripts
- sql_crud_execute.py -> context_compass/system/ai_restricted/database_management/sqlite_crud_command.py
- sql_command_registry_describe.py -> context_compass/system/ai_restricted/database_management/sql_command_registry_describe.py

Usage
- Execute a CRUD action:
  `python context_compass/workspace/tools/sql/crud/sql_crud_execute.py --repo-root . --agent-id <agent_id> --work-id <work_id> --operation read --scope user --table-name <table> --action <action> --actor-id <agent_id>`
- Inspect CRUD registry entries:
  `python context_compass/workspace/tools/sql/crud/sql_command_registry_describe.py --repo-root . --agent-id <agent_id> --work-id <work_id> --scope all`

Notes
- CRUD operations must use explicit action names (no implied defaults).
- These scripts delegate to ai_restricted implementations.
