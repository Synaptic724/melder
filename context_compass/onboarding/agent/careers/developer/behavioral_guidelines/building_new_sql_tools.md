Here’s the direct sqlite_crud path (no CLI wrapper), based strictly on the code:

caller code
|
| 1) build SqliteCrudRequest(...)
v
sqlite_crud.execute_request(repo_root, request)
|
| 2) validate: scope/operation/action/table/actor_id
| 3) resolve DB path + open engine/session
| 4) ensure registry tables exist
| 5) confirm table + action registered
| 6) resolve sql_tools/<table>/<operation>/<action>.py path
v
sqlite_crud._run_script(script_path, repo_root, request)
|
| 7) import module, call run(payload, ctx)
v
sql_tools/<table>/<operation>/<action>.py::run(payload, ctx)
|
| 8) returns CommandResult (ok or error)
v
sqlite_crud.execute_request(...)
|
| 9a) if ok: build SqliteCrudResponse + write db_operation_log
| 9b) if error: convert to SqliteCrudError + write db_operation_log
v
return SqliteCrudResponse (ok) or raise SqliteCrudError (error)

Notes
- SQL CRUD/query tools are DB-only; they never execute hooks.
- Do not route SQL tools through ToolCommandAPI or tool_execute.
- SQL tools should not call ToolCommandAPI or any hook runners.
- sqlite_query follows the same script-based path and also bypasses hooks.
