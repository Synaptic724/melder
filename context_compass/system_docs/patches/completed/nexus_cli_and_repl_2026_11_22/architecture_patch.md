# architecture_patch

## Metadata
- Patch ID: nexus_cli_and_repl_2026_11_22
- Status: implemented at 0.2.8314-0.2.8315; merged into src_components, src_architecture, tests_components and the
  source graph
- Owner: Mark (accountable); melder_0 (synaptic_python_developer) authors and implements
- Ticket: https://github.com/Synaptic724/melder/issues/339 (story; parent epic #337, tasks 6 and 7)
- Created: 2026-11-22T14:40:00Z
- Updated: 2026-11-22T16:19:07Z

## Patch Scope and Non-Goals
- Objective: a room's command surface becomes a command line an agent can use without a harness written around
  it - a catalog, per-command help, a by-name entry point that refuses a bad call plainly, and tool definitions -
  all generated from the commands' signatures and docstrings; and the codegen REPL reports where room code failed.
  Decided by the owner on 2026-11-22 (#337 and #339 Decision Logs), with test_melder_0's guidance (#339 Notes).
- Non-goals: no change to what a room allows or to any command's gates; no rendering of live objects as text; no
  envelope around successful answers; no argument type checking beyond binding; `runtime_error` unchanged; the
  `ValueError` an empty `code` raises is unchanged; tracebacks inside materialized modules are not located.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Room command surface (`CommandSystem`, `StaticCommandSystem`, `CapabilityCommandSystem`, `CodegenCommandSystem`) | modify | `run_command`, `describe_commands`, `describe_command`, `tool_definitions`; each room's command list read through one internal method; `frame_name` optional on the three codegen commands | none |
| Command catalog (new kernel class `CommandCatalog`) | add | reads a command's signature and docstring once per call, without evaluating annotations: summaries, help, refusal text and JSON Schemas | none |
| Codegen engine (`CodegenSystem`, `CodegenCompiler`, `CodegenExecutor`, `CodegenExecutionResult`) | modify | run ids on every execute payload; the failing room-code line, its text and its run; the room keeps every run's source | none |
| Research commands (`CodegenCommandSystem.research_heads`) | docstring | its tip is the newest recorded version, not the active one | none |

## Interface and Boundary Deltas
- `CommandSystem.run_command(command_name, arguments=None)`: runs a command in the room's command list by name with
  keyword arguments. Refuses a name outside the list (`reason: command_not_supported`, with `supported_commands`)
  and arguments that do not bind (`reason: command_arguments_invalid`, with `missing_arguments` and
  `unknown_arguments`); otherwise returns exactly what the command returns. Not itself in the command list.
- `CommandSystem.describe_commands()`: one entry per supported command - `command`, `signature`, `summary` (the
  docstring's first line). `describe_command(command_name)`: `accepted: True`, `command`, `signature`, `arguments`
  (each `name`, `type`, `required`, and `default` when not required) and `doc` (the full docstring); an unknown name
  gets the refusal. Both are in every room's command list.
- `CommandSystem.tool_definitions()`: one `{name, description, input_schema}` per supported command. The
  description is the docstring's text before `Args:`; each property's description is its `Args:` entry, else its
  annotation text. Not itself in the command list.
- One refusal shape: `accepted: False`, `command`, `reason`, `message`, plus the keys named above.
- `validate_codegen`, `execute_codegen`, `materialize_codegen`: `frame_name: Optional[str] = None`; an omitted name
  resolves to the room's default runtime frame (its only assigned frame) through the helper the room's other
  commands use, which raises when the room has none.
- Execute payloads gain `run_id` (always) and, on a runtime failure in room code, `runtime_error_line`,
  `runtime_error_run_id` and `runtime_error_line_text` (when the room kept that run's source).

## Cross-Component Invariants
- `run_command` adds no reach: it dispatches only a name in the room's own command list, and that command runs its
  own gates. A `getattr` dispatch reaching `cleanup` or private methods is what it refuses.
- The catalog, help, refusals and schemas are derived from the live signatures and docstrings every call; nothing is
  hand-maintained, so they cannot drift. Annotations are read as text or forward references, never evaluated.
- A run's source is kept by the room's `CodegenSystem` from the moment the run is accepted until the room is
  removed; validation-refused runs keep nothing.

## Migration and Rollout Order
1. Failing-first pins on 0.2.8313: the new commands absent; a bad by-name call raising `TypeError`; `frame_name`
   required; no run ids or failure locations; the two docstrings.
2. The catalog class and the command surface (0.2.8314).
3. The codegen engine's run ids, failure locations and kept sources, and the two docstrings (0.2.8315).
4. Docs, system docs, graph descriptors, release note; the rebuild last.

## Rollback Strategy
- Rollback trigger: a command reachable through `run_command` that a direct call could not reach, or a payload
  consumer broken by the new keys.
- Rollback steps: remove the four methods and the catalog class; restore `frame_name` as required; drop the payload
  keys and the kept sources.
- Post-rollback verification: the failing-first pins return to their 0.2.8313 expectations.

## Validation Expectations and Evidence Plan
- Unit: the catalog's signature text, argument rows, docstring sections, JSON Schema mapping and refusal messages.
- Component or integration: in a `safe`-profile codegen room, every acceptance criterion of #339; in static and
  capability rooms, the command lists and a `run_command` round trip.
- Suites: the command-system and codegen suites, then the full suite, with the GIL off.

## Ticket Coverage Map
- Epic: https://github.com/Synaptic724/melder/issues/337 (tasks 6 and 7)
- Story: https://github.com/Synaptic724/melder/issues/339
- Tasks: the story's checklist

## Unknowns and Decision Requests
- UNKNOWN: none blocking.
- DECISION_REQUEST: none open; the design and the tool-description text were decided on 2026-11-22.

## Context / Handoff Summary
- What changed: implemented as specified at 0.2.8314 (the command line: `run_command`, the two describe commands,
  `tool_definitions`, the `frame_name` default and `CommandCatalog`) and 0.2.8315 (run ids, failure locations, kept
  run sources and the docstring corrections - `research_heads` corrected in the capability room as well as the
  codegen room, recorded in #339's Notes); the deltas are merged into the canonical system docs and the graph.
- What remains: the agent loop re-runs on a wheel of this landing.
- Next entrypoints: component_patch_room_command_surface.md, component_patch_codegen_execution.md.
