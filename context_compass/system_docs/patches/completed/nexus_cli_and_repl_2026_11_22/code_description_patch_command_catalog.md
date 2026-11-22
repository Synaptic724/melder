# code_description_patch_command_catalog

## Metadata
- Patch ID: nexus_cli_and_repl_2026_11_22
- Component: `CommandCatalog` (new, `src/melder/nexus/rift/command_system/command_catalog.py`) and the four command
  surface methods that use it
- Status: implemented at 0.2.8314-0.2.8315; merged into src_components, src_architecture, tests_components and the
  source graph
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-22T14:40:00Z
- Updated: 2026-11-22T16:19:07Z

## Control Flow Commitments
- Signatures are read with `inspect.signature(method, annotation_format=annotationlib.Format.FORWARDREF)`, so an
  annotation naming a typing-only import is never evaluated; the signature text uses
  `annotationlib.Format.STRING`, so it reads as the source spells it (`Optional[str]`).
- `run_command`: `check_cleaned()`; reject a non-mapping or a non-string key with `TypeError`; refuse a name not in
  `self._list_supported_command_methods_tuple()`; read the bound method with `getattr(self, name)` (a dynamic name
  from the room's own list); compute missing arguments (keyword-passable parameters without defaults that were not
  given) and unknown arguments (names no parameter takes, none when the command has `**kwargs`); refuse when either
  is non-empty; otherwise `return method(**arguments)`. `*args` cannot be passed and is never reported missing.
- Docstrings are read with `inspect.getdoc`. The summary is its first line. The description is its text before the
  first line that is exactly `Args:`, `Returns:`, `Raises:` or `Yields:`, stripped. An `Args:` entry is a line one
  level inside `Args:` shaped `name:` or `name: text` (optionally `name (Type): text`), plus the deeper lines under
  it, joined with single spaces; a parameter with no entry is described by its annotation text.
- JSON Schema per parameter, from the forward-reference annotation: `str` string, `int` integer, `float` number,
  `bool` boolean, `None` null; `Optional[X]` with a `None` default is `X` and not required, otherwise `anyOf` with
  null; `Union` is `anyOf`; `Literal` is `enum`; `list`, `tuple`, `set`, `frozenset`, `Sequence` and their typing
  forms are arrays (with `items` for one element type); `dict` and `Mapping` are objects; anything else - `object`,
  `Any`, a class, an unresolved forward reference - is the empty schema, with the annotation text in its
  description. A JSON-representable default (`str`, `int`, `float`, `bool`, `None`) is recorded as `default`.
- `input_schema` is `{"type": "object", "properties": ..., "required": [...], "additionalProperties": <bool>}`, true
  only when the command takes `**kwargs`; `*args` is omitted.

## Edge and Error Semantics
- `run_command` never catches what the command raises, including its own `TypeError`s; only the bind is checked.
- An argument given by name for a positional-only parameter is unknown and that parameter is missing (no room
  command declares one today).
- A refusal's `message` names the command, the problem and the command's signature, so the fix is in the text.

## Invariants and Idempotency
- Pure reads of live methods: the same command answers the same help and schema until its code changes.
- `describe_commands()` covers exactly the room's command list, in its order.

## Explicit Non-Goals
- No type checking of argument values; no rendering of return values; no caching of signatures (the per-call cost
  is small beside an agent's tool call, and a cache would need invalidation when a room's methods change).
