# component_patch_room_command_surface

## Metadata
- Patch ID: nexus_cli_and_repl_2026_11_22
- Component: RiftSpace Workstation And Command Surface - `CommandSystem` and its static, capability and codegen
  subclasses - plus the new kernel class `CommandCatalog`
- Status: implemented at 0.2.8314-0.2.8315; merged into src_components, src_architecture, tests_components and the
  source graph
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-22T14:40:00Z
- Updated: 2026-11-22T16:19:07Z

## Component Purpose and Boundary
- Current boundary: a room exposes its commands as methods and their names through
  `list_supported_command_methods()`. A caller that runs commands by name does `getattr(room, name)(**kwargs)`:
  a missing argument raises Python's `TypeError` in the caller, and any attribute - `cleanup`, a private method -
  is reachable. The three codegen commands require `frame_name`; the room's other commands default it.
- Target boundary: the room also answers `describe_commands()`, `describe_command(name)`, `run_command(name,
  arguments)` and `tool_definitions()`, all derived from the commands' live signatures and docstrings.

## Before/After Behavior Summary
- Before: `getattr(room, "validate_codegen")(frame_name="lab")` raises `TypeError ... missing 1 required positional
  argument: 'code'`.
- After: `room.run_command("validate_codegen", {"frame_name": "lab"})` answers `{"accepted": False, "command":
  "validate_codegen", "reason": "command_arguments_invalid", "message": ..., "missing_arguments": ("code",),
  "unknown_arguments": ()}`; `room.run_command("cleanup", {})` answers `reason: command_not_supported` with
  `supported_commands`; `room.run_command("execute_codegen", {"code": "result = 1"})` returns exactly what
  `room.execute_codegen("result = 1")` returns, the frame being the room's default.
- Unchanged: every direct call; every command's gates, locks, hooks, memory records and errors;
  `list_supported_command_methods()` keeps its order and gains `describe_commands` and `describe_command` at its end.

## Interface Deltas
- Inputs: `run_command(command_name: str, arguments: Optional[Mapping[str, object]] = None) -> object`;
  `describe_command(command_name: str) -> Dict[str, object]`; `describe_commands() -> Tuple[Dict[str, object],
  ...]`; `tool_definitions() -> Tuple[Dict[str, object], ...]`. `frame_name: Optional[str] = None` on
  `validate_codegen`, `execute_codegen` and `materialize_codegen`.
- Outputs: the refusal shape (`accepted: False`, `command`, `reason`, `message`, then `missing_arguments` and
  `unknown_arguments`, or `supported_commands`); `describe_commands` entries (`command`, `signature`, `summary`);
  `describe_command` (`accepted: True`, `command`, `signature`, `arguments`, `doc`); tool definitions (`name`,
  `description`, `input_schema`).
- Error semantics: `arguments` that is not a mapping with string keys raises `TypeError` (a caller bug, not an
  agent's call); everything a dispatched command raises propagates unchanged - `run_command` never catches it.

## State and Lifecycle Deltas
- Owned state changes: none. `CommandCatalog` holds no state; each subclass's command list moves into an override
  of the internal `_list_supported_command_methods_tuple()`, which its public method returns inside its gate.
- Lifecycle/cleanup changes: none; the four methods `check_cleaned()` first.

## Failure Mode Deltas
- Removed failure modes: a by-name call with a bad argument surfacing as a raw `TypeError`; a by-name dispatch
  reaching a method outside the room's command list; an agent finding no help but a list of names.
- New failure mode: an omitted `frame_name` in a room with no single assigned frame raises the room's existing
  "Rift has no default runtime frame." `ValueError`.

## Dependency and Ordering Constraints
1. `run_command` checks the name against the room's list, then binds, then dispatches; it takes no lock and no
   RiftGate ticket of its own, so the dispatched command's own admission is the only one.
2. The help commands enter a command action like `list_supported_command_methods()` does; `run_command` and
   `tool_definitions` serve the caller and are not in the command list.

## Validation Expectations
- A missing, an unknown and a both-missing-and-unknown call each refused with the right names; a name outside the
  list refused with the list; a binding call's value identical to the direct call's.
- `describe_commands()` covers exactly `list_supported_command_methods()`; `describe_command` rows match the
  signature; unknown names refused.
- Every tool definition's schema: `required` equals the parameters without defaults; `frame_name` optional on the
  codegen commands; `additionalProperties` false unless the command takes `**kwargs`.
- Static and capability rooms: their lists end with the two help commands and `run_command` round-trips one command.
