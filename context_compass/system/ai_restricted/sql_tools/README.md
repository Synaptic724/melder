# sql_tools

Purpose
- Host explicit, script-driven CRUD operations for relational SQLite tables.
- Keep command inputs/outputs JSON while storing data in relational columns.

Structure
- One folder per table or domain:
  - sql_tools/<table_name>/<operation>/<action>.py
  - operations: create, read, update, delete
  - action: script name within the operation folder (required)

Resolution rules
- The sqlite_crud router resolves scripts deterministically via db_action_registry.

Contract
- Each script exposes: run(payload: dict, ctx: ExecutionContext) -> CommandResult
- Scripts validate inputs, execute a transaction, and return JSON output.
- Scripts must record created_by/updated_by using the actor_id.
- Scripts are deterministic and do not print to stdout.

Notes
- These scripts are invoked by a router command, not directly by agents.
- JSON is not stored in SQLite; scripts map inputs to relational columns.
