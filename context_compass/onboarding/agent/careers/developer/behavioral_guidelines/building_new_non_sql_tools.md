Planned execution diagram (generic tools)

caller (CLI or python)
|
| tool_execute.py (CLI) or execute_command(...)
v
ToolCommandAPI.execute(...)
|
| 1) validate inputs + merge payload (inject repo_root/agent_id/work_id)
| 2) build ExecutionContext(chain_depth=0)
| 3) resolve command registry (system, then user)
| 4) parse spec.execution -> script_path + entrypoint
| 5) load hook registries (system + user) via sqlite_crud
| 6) select hooks that apply (phase/order/applies_to)
|
| --- PRE HOOKS ---
| 7) run pre hooks (ordered); if errors -> on_error hooks -> return error
|
| --- CORE COMMAND ---
| 8) import script, call entrypoint(payload, context) -> CommandResult
| if status != ok -> on_error hooks -> return error
|
| --- ACTIVATION HOOKS ---
| 9) run activation hooks (ordered)
| - may emit NextAction(s)
| - if NextAction(s): recurse execute(...) with chain_depth+1
| - guard max_chain_depth
| - if errors -> on_error hooks -> return error
|
| --- POST HOOKS ---
| 10) run post hooks (ordered); if errors -> on_error hooks -> return error
|
v
return CommandResult

Rules
- Non-SQL tools are leaf scripts; they do not call ToolCommandAPI or hook runners.
- Hooks run only when ToolCommandAPI is the entrypoint (tool_execute or execute_command).
- Direct tool execution is allowed only as a last resort and bypasses hooks.
