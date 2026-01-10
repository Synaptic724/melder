# query

Purpose
- Workspace facades for registry-backed SQLite query execution.
- Workspace entrypoints for inspecting query registry entries.

Scripts
- sql_query_execute.py -> context_compass/system/ai_restricted/database_management/sqlite_query_command.py
- sql_query_command_registry_describe.py -> context_compass/system/ai_restricted/database_management/sql_query_command_registry_describe.py

Usage
- Execute a registered query:
  `python context_compass/workspace/tools/sql/query/sql_query_execute.py --repo-root . --agent-id <agent_id> --work-id <work_id> --scope user --query-name <name> --actor-id <agent_id>`
- Inspect query registry entries:
  `python context_compass/workspace/tools/sql/query/sql_query_command_registry_describe.py --repo-root . --agent-id <agent_id> --work-id <work_id> --scope all`

Notes
- Use query tools for multi-table or composite operations.
- These scripts delegate to ai_restricted implementations.
