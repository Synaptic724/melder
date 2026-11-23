# Melder 0.2.8316

**Unreleased**

## Codegen validation accepts every way Python binds a name

Room code that binds a name through an exception handler, a match pattern or a type parameter was refused by codegen
validation, although it is valid Python: `except ValueError as e:` followed by `str(e)` was refused with "Name 'e' is
not available in the codegen namespace.", and so were `case n:`, `case [first, *rest]:`, `case {'a': v, **rest}:`,
`case int() as n:` and `def first[T](items: list[T]) -> T:` (GitHub issue #337). Name resolution counted only
assignment-style bindings, definitions, parameters and imports. It now counts every binding form - `except ... as` and
`except* ... as`, the match captures and PEP 695 type parameters included - so such code validates and runs. A name
that nothing in the code binds is still refused with the same message.

## `execute_codegen` returns what room code printed

What room code printed went to the stdout of the process running Melder, where the agent that sent the code never saw
it. A codegen room now captures it: `execute_codegen`'s payload carries it under a new `output` key, also when the code
raised (beside `runtime_error`), and nothing reaches the host's stdout.

```python
payload = command.execute_codegen("print('rows:', 3)\nresult = {'answer': 42}\n", frame_name="ops")
# {'accepted': True, 'frame_name': 'ops', 'result': {'answer': 42}, 'output': 'rows: 3\n'}
```

Two new room settings control it, fixed when the room is created:
`RiftConfiguration.with_codegen_output_capture(enabled)` (on by default) and `with_codegen_output_limit(characters)`
(65,536 by default). Text past the limit is dropped and `output` ends with one line, "[output truncated: N more
characters not kept]". A limit below 1 is refused with ValueError, a bool or a non-int with TypeError.
`print(..., file=x)` still writes to `x`, and a materialized module's `print` is unchanged. `execute_codegen`'s
docstring - the room's own help - now says that assigning `result` returns a value and names every payload key (GitHub
issue #337).

**Breaking change:** in a codegen room, room code's `print` no longer reaches the host process's stdout by default.
To keep the old behaviour, create the room from a configuration with `.with_codegen_output_capture(False)`.

## A room's commands can be listed, explained and run by name

A room offered its commands as methods and their names through `list_supported_command_methods()`, and nothing more.
A caller that ran them by name - as an agent's tool layer does - used `getattr(room, name)(**arguments)`: a missing
argument raised Python's `TypeError` in the caller, and any attribute of the room, `cleanup` included, was reachable
(GitHub issue #339). Every room - static, capability and codegen - now answers four more calls, all read from its
commands' own signatures and docstrings, so they cannot drift from the code:

- `describe_commands()`: each command with its signature and the first line of its docstring.
- `describe_command(name)`: one command's arguments (name, type, required, default) and its whole docstring.
- `run_command(name, arguments)`: runs a command of the room's list with keyword arguments and returns exactly what
  the command returns. A name outside the list, or arguments that do not fit the command's signature, are answered
  instead of raised; what the command itself raises still propagates.
- `tool_definitions()`: one `{name, description, input_schema}` per command, ready to offer each command as its own
  tool. The description is the docstring's text before `Args:`, each argument is described by its `Args:` entry,
  and the JSON Schema comes from the signature.

```python
command.run_command("validate_codegen", {})
# {'accepted': False, 'command': 'validate_codegen', 'reason': 'command_arguments_invalid',
#  'message': "Command 'validate_codegen' cannot run with these arguments: missing required argument 'code'.
#              Call it as validate_codegen(code: str, *, frame_name: Optional[str] = None) -> Dict[str, object].",
#  'missing_arguments': ('code',), 'unknown_arguments': ()}
```

`describe_commands` and `describe_command` are appended to every room's `list_supported_command_methods()`;
`run_command` and `tool_definitions` serve the caller and are not in it. A command run by name passes the same checks,
locks and hooks as a direct call. `validate_codegen`, `execute_codegen` and `materialize_codegen` no longer require
`frame_name`: when it is omitted they use the room's only assigned frame, as the room's other commands already did,
and a room assigned no frame or several raises the existing "Rift has no default runtime frame." `ValueError`.

## `execute_codegen` says where room code failed

A runtime failure reported only its type and message, so a failing bare `assert` came back as `"AssertionError: "`
with no line (GitHub issue #339). Every execute payload now carries `run_id`, the id of that run. A run that raised
also carries `runtime_error_line`, `runtime_error_run_id` and `runtime_error_line_text`: the innermost line of room
code on the failing path, the run whose code it is, and that line's text.

```python
command.execute_codegen("x = 1\nassert x == 2\n")
# {'accepted': False, 'frame_name': 'ops', 'run_id': '...', 'reason': 'codegen_execution_runtime_failed',
#  'runtime_error': 'AssertionError: ', 'runtime_error_line': 2, 'runtime_error_run_id': '...',
#  'runtime_error_line_text': 'assert x == 2'}
```

A failure inside a function an earlier run left on the room's workstation names that earlier run and the line of its
code; a failure inside melder or library code names the room line that called it. To quote such lines, a codegen room
keeps the source of every run that passed validation until the room is removed. `runtime_error` itself is unchanged.
`execute_codegen`'s docstring now says that each run starts from a fresh namespace and that state kept between runs
goes on the workstation (`workstation.bind_object(name, obj)`, then `workstation.get(name)`), and `research_heads`
says that each lane's tip is the newest version recorded there, not the active one: after a notch back,
`research_residency(spell_id)` names the active version.

## A late bind its commit refuses is undone

A bind after `conjure` - a late bind - is compiled when its bind window commits. When that commit refused it, for
example with HIDDEN_PROVIDER, the spell stayed registered: the caller was told the bind failed, and binding it again
raised "Spell ID collision detected" (GitHub issue #330). Now the refused window is undone before the error
propagates. Every spell the window bound leaves the Book and every registry - an existing object leaves its store slot
and is not disposed, and a managed pool the bind created is discarded - the spells compiled against them are flagged
for revalidation, and the error keeps its type and text and gains a note naming what was undone. Binding again meets
the same refusal until its cause is fixed, then binds.

```python
world = book.conjure(dynamic=True, name="world")
try:
    book.bind(spell=Host, existence="many")   # Host asks for a class bound only under a spellframe
except SpellbookValidationError as error:
    print(error.__notes__)
# ["The refused bind window was undone: 'Host' (spell_id ...) left every registry. Bind again once the refusal's
#   cause is fixed."]
world.meld(Host)                              # KeyError: "[MELD] No spell found for frame='host', ..."
```

A bind window is one transaction: in `with book.transaction("bind"):`, one refused spell undoes every spell the window
bound, a version staged with `bind_inactive` included. The commit also refuses a staged spell the binding thread
already compiled broken inside its window, which used to commit broken.

**Breaking change:** while a late bind's window is open, a meld on another thread that reaches one of its spells -
melding it, or melding a consumer whose plan would resolve it - raises `MeldExecutionError` "'<Name>' (spell_id <id>)
is being late-bound by another thread: its bind has not committed yet, so nothing is built from it until the bind
resolves. Meld again once that bind finishes; ...". Retry the meld once the bind finishes; there is no wait. The thread
that holds the window melds what it binds as before.

**Breaking change:** a consumer refused at its late bind is no longer registered, so a meld of it raises
`KeyError` ("No spell found ...") instead of repeating the refusal. Fix the cause - ask for the class where it is bound,
or bind the class bare - and bind the consumer again. A consumer bound before its class arrived under a spellframe is
still registered and refused at its meld, with or without an override.

Unchanged: binds before `conjure`, which compile at `conjure`; a late bind that commits; a window whose body raises,
which keeps what it bound; and every meld while no late bind is open in the frame, which pays one map read.

## Packaging and documentation

The codegen profile docstrings and `docs/expert/codegen.md` now state what a profile enforces on room code: its
capability rules - imports, the denied builtins, reflection, dunder access and nested codegen. Its frame, conduit and
spell rules, among them `safe`'s denial of linking, lesser conduits, transfers, spell creation, method calls and
attribute writes, are published to agents as the frame's `allowed_commands` but are not yet enforced on room code,
which can call any method of a live object it holds, such as the conduit `command.get_conduit_by_name` returns (GitHub
issue #338). The same page now lists what `execute_codegen` returns and the room settings above, including `run_id`,
the failure location and keeping state between runs on the workstation, and `docs/expert/agent-rooms.md` gains a
section on learning and running a room's commands by name (GitHub issue #339).

Two new kernel classes: `CodegenOutputCapture` (`melder.nexus.rift.codegen_system.namespace.codegen_output_capture`)
is room code's `print` in a capturing room, and `CommandCatalog` (`melder.nexus.rift.command_system.command_catalog`)
reads a room command's signature and docstring for the command line. The internal-bind guard manifest holds 637
entries (635 at 0.2.8310): neither class can be bound. The docstrings of `RiftConfiguration`,
`CodegenNameResolutionStrategy`, `CodegenNamespaceBuilder`, `CodegenBuiltinsStrategy`, `CodegenNamespace`,
`CodegenSystem`, `CodegenCompiler`, `CodegenExecutor`, `CodegenExecutionResult`, `CommandSystem` and its static,
capability and codegen rooms describe the changes; the source and test maps, their indexes and the source graph
describe them.

The docstrings of `Spellbook.bind`, `Spellbook.transaction` and `Spellbook.scan` describe the undone late bind, and
`SpellState` gains the member `late_bind_in_progress`, declared after the existing members (their legacy numbers are
unchanged). The source and test maps, their indexes and the source graph describe the change (GitHub issue #330).

Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8316.
