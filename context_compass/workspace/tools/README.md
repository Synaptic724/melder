# workspace/tools

Purpose
- Workspace-owned facades for context_compass tooling.
- Keep workspace scripts thin; delegate to system implementations.
- Provide a stable, agent-facing surface that does not duplicate logic.

Layout
- general/: ToolCommandAPI entrypoints and registry inspectors.
- sql/crud/: SQLite CRUD command facades and CRUD registry inspectors.
- sql/query/: SQLite query command facades and query registry inspectors.

Notes
- These scripts are facades only; do not add business logic here.
- Certification and work_mode enforcement happens in the system tools.
- CLI signatures mirror the underlying system scripts so help output stays consistent.
- If a command is missing, add it to the system tool and create a new facade here.

Facade map (workspace -> system)
- `general/command_registry_generate.py` -> `context_compass/system/ai_restricted/system_management/command_registry_generate.py`
- `general/command_registry_describe.py` -> `context_compass/system/ai_restricted/system_management/command_registry_describe.py`
- `general/command_registry_path.py` -> `context_compass/system/ai_restricted/system_management/command_registry_path.py`
- `general/tool_execute.py` -> `context_compass/system/ai_restricted/system_management/tool_execute.py`
- `general/tool_registry_describe.py` -> `context_compass/system/ai_restricted/system_management/tool_registry_describe.py`
- `sql/crud/sql_crud_execute.py` -> `context_compass/system/ai_restricted/database_management/sqlite_crud_command.py`
- `sql/crud/sql_command_registry_describe.py` -> `context_compass/system/ai_restricted/database_management/sql_command_registry_describe.py`
- `sql/query/sql_query_execute.py` -> `context_compass/system/ai_restricted/database_management/sqlite_query_command.py`
- `sql/query/sql_query_command_registry_describe.py` -> `context_compass/system/ai_restricted/database_management/sql_query_command_registry_describe.py`

Examples
- Registry generation:
  `python context_compass/workspace/tools/general/command_registry_generate.py --repo-root . --agent-id <agent_id> --work-id <work_id>`
- Registry description (path-safe):
  `python context_compass/workspace/tools/general/command_registry_describe.py --repo-root . --agent-id <agent_id> --actor-id <actor_id> --scope user`
- Registry path lookup:
  `python context_compass/workspace/tools/general/command_registry_path.py --repo-root . --agent-id <agent_id> --actor-id <actor_id> --scope system --command-name <name> --work-id <work_id>`
- ToolCommandAPI execution:
  `python context_compass/workspace/tools/general/tool_execute.py --command-name <name> --payload-json '{}' --repo-root . --agent-id <agent_id> --work-id <work_id>`
- Tool registry inspection (full details):
  `python context_compass/workspace/tools/general/tool_registry_describe.py --repo-root . --agent-id <agent_id> --work-id <work_id> --scope both`
- SQL CRUD execution:
  `python context_compass/workspace/tools/sql/crud/sql_crud_execute.py --repo-root . --agent-id <agent_id> --work-id <work_id> --operation read --scope user --table-name <table> --action <action> --actor-id <agent_id>`
- SQL CRUD registry inspection:
  `python context_compass/workspace/tools/sql/crud/sql_command_registry_describe.py --repo-root . --agent-id <agent_id> --work-id <work_id> --scope all`
- SQL query execution:
  `python context_compass/workspace/tools/sql/query/sql_query_execute.py --repo-root . --agent-id <agent_id> --work-id <work_id> --scope user --query-name <name> --actor-id <agent_id>`
- SQL query registry inspection:
  `python context_compass/workspace/tools/sql/query/sql_query_command_registry_describe.py --repo-root . --agent-id <agent_id> --work-id <work_id> --scope all`
