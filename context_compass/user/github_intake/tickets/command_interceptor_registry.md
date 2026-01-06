# Ticket: Command Interceptor System (Pre/Activation/Post Hooks) + Script Runner + SQLite Registry

## Summary
Design and implement a command interceptor system that wraps tool execution with **pre-hooks**, **activation hooks**, and **post-hooks**. Commands must expose a **common programmatic interface** (`kwargs in → kwargs out`) and be executed through a **single in-process runner**. Hook and command metadata live in a **SQLite registry**, enabling deterministic discovery, ordering, validation, auditability, and user-extensible behaviors.

## Motivation
- We want cross-cutting behaviors (logging, audit, policy, mailbox warnings, memory updates) without changing every tool.
- We need a deterministic, inspectable execution pipeline with stable ordering.
- Commands should be invocable without reading implementation code: **interface + schema are the contract**.
- Users should be able to chain additional scripts by authoring activation hooks that emit the next actions.

## Goals
- Define a stable **command interface** (programmatic entrypoint) for all tools.
- Provide a deterministic **hook pipeline**:
  - **Pre-hooks**: validate/enrich/gate.
  - **Activation hooks**: transform outputs into next actions.
  - **Post-hooks**: audit/notify/emit memories.
- Store **command registry + hook registry** in SQLite.
- Provide **runner** that:
  - Loads a command module dynamically.
  - Enforces schema contracts.
  - Executes hook chain with deterministic ordering.
- Support user-extensible hooks without bypassing safety or policy.

## Non-Goals
- No daemonized server.
- No interactive stdin REPL (commands are run-to-completion; prompts are turn-based).
- No permanent override of core command behavior by hooks (additive only).

## Core Concepts

### 1) Command Interface
Each command module must expose a programmatic entrypoint:
```
def run(payload: dict, ctx: ExecutionContext) -> CommandResult
```

Contract:
- **Inputs**: `payload` is a JSON-serializable kwargs dict.
- **Outputs**: `CommandResult` is JSON-serializable and must include:
  - `status`: "ok" | "error" | "pending_input"
  - `output`: dict (core output, immutable by hooks)
  - `metadata`: dict (hook-writable)
  - `artifacts`: list (paths/ids for large outputs)
  - `errors`: list of structured errors (if any)
  - `queries`: optional list of structured prompts for pause/resume

CLI `main()` remains a thin adapter that parses args → builds payload → calls `run()`.

### 2) Hook Phases
- **Pre-hook**: runs before core command.
  - Validate inputs, enforce policy, enrich context.
  - May block execution with a typed error.
- **Activation hook**: runs after core command output.
  - Reads `output` + `metadata`, emits `next_actions` to chain additional commands.
  - Does not mutate core output.
- **Post-hook**: runs after chain completion or after each command (configurable).
  - Audit logs, memory writes, notifications, telemetry.

### 3) Deterministic Ordering
Hooks are ordered by:
```
(phase_order, order, hook_id)
```
- `phase_order`: pre=10, activation=20, post=30
- `order`: integer (default 100)
- `hook_id`: stable tiebreaker

### 4) Chain Execution
- The runner executes a command, then activation hooks can emit `next_actions`.
- Each `next_action` specifies `command_name` + `payload`.
- The runner resolves and executes each next action via the same pipeline.
- **Guardrails**:
  - Max chain depth (configurable).
  - Cycle detection by `(command_name, payload_hash)` or explicit chain_id.
  - Activation hooks cannot directly import or execute commands; they must emit `next_actions`.

### 5) Pause/Resume (Input Requests)
If a hook or command needs user/agent input:
- Return `status="pending_input"` + `queries=[{id, prompt, schema, defaults}]`.
- Runner persists queries to SQLite and halts the chain.
- A `chain_resume` command can submit the answer and continue.

## SQLite Registry (Proposed Schema)
Minimal tables (names are illustrative):

### commands
- `command_id` (pk)
- `name` (unique, stable)
- `module_path`
- `entrypoint` (e.g., "run")
- `inputs_schema_json`
- `outputs_schema_json`
- `side_effects_json` (files, db, network)
- `tags` (csv or JSON)
- `enabled` (bool)

### hooks
- `hook_id` (pk)
- `name` (unique)
- `phase` ("pre"|"activation"|"post")
- `module_path`
- `entrypoint` (e.g., "run_hook")
- `order` (int)
- `enabled` (bool)
- `applies_to` (JSON: command names, tags, capabilities)
- `requires` / `provides` (optional dependency hints)

### hook_bindings (optional)
- `binding_id` (pk)
- `hook_id`
- `command_id`
- `priority` (override order for specific command)

### chain_runs
- `chain_id` (pk)
- `root_command`
- `started_at`
- `finished_at`
- `status`
- `error_summary`

### command_runs
- `run_id` (pk)
- `chain_id`
- `command_name`
- `payload_json`
- `result_json`
- `started_at`
- `finished_at`
- `status`

### hook_runs
- `hook_run_id` (pk)
- `run_id`
- `hook_id`
- `phase`
- `input_json`
- `output_json`
- `status`
- `started_at`
- `finished_at`

### interaction_requests
- `request_id` (pk)
- `chain_id`
- `origin_command`
- `origin_hook`
- `prompt`
- `schema_json`
- `default_json`
- `status` ("pending"|"answered"|"expired")
- `created_at`
- `answered_at`
- `answer_json`

## Script Runner Responsibilities
- Load registry (commands + hooks) from SQLite.
- Resolve applicable hooks for a command deterministically.
- Validate `payload` against command input schema.
- Call command `run(payload, ctx)` and validate outputs.
- Execute hooks in phase order and merge allowed metadata.
- Enforce additive-only rules (hooks cannot mutate core output).
- Persist `command_runs`, `hook_runs`, and `chain_runs`.

## Required Interfaces
### ExecutionContext (example fields)
- `command_name`, `chain_id`, `correlation_id`
- `agent_id`, `work_id`
- `annotations` (hook-writable)
- `db` (registry connection handle)

### Hook Interface
```
def run_hook(ctx: ExecutionContext, payload: dict, result: CommandResult) -> HookResult
```

`HookResult` may include:
- `metadata_patch` (dict)
- `next_actions` (activation only)
- `errors` (typed, for policy gating)

## Validation & Determinism
Provide a validator that:
- Verifies command/hook schemas are valid JSON schema.
- Ensures hook ordering is deterministic.
- Ensures hooks reference real commands/tags.
- Checks that around/activation hooks never skip core execution.
- Optionally runs smoke tests with minimal inputs.

## Acceptance Criteria
- All commands expose a `run()` entrypoint with schema-defined inputs/outputs.
- Hooks are discovered from SQLite and run in deterministic phase order.
- Activation hooks can chain additional commands via `next_actions`.
- Runner enforces additive-only behavior; core output is immutable.
- Hook and command runs are audited in SQLite.
- Validator reports configuration errors clearly and blocks unsafe pipelines.
- A pause/resume flow exists for pending input requests.

## Open Questions
- Should post-hooks run after each command or only once at chain end?
- Should activation hooks be allowed to modify next command payload directly, or only emit `next_actions`?
- What is the default max chain depth and timeout policy?
- Where should user-provided hooks live (repo scripts + registry metadata)?
- Do we need per-agent enable/disable flags for hooks?

