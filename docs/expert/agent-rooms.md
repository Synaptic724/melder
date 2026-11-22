# Give each agent an explicit room and target

Prerequisites: [Nexus setup](../advanced/nexus.md) and
[world posture](../advanced/posture.md). A Rift owns one room, including its viewer,
workstation, command surface, and optional codegen machinery.

| Room | Main purpose |
| --- | --- |
| `static` | Inspect the permitted live surface |
| `capability` | Use the broader runtime command surface and research reads |
| `codegen` | Add source validation/execution/materialization and research authoring operations |

Ask `list_supported_command_methods()` for the commands the actual room exposes.
A method may also require an active subsystem. Availability and authority are
different: activating research does not add its authoring commands to a capability room.

## Learn and run commands by name

Every room also describes and runs its own commands, read from their signatures and
docstrings. `describe_commands()` lists each command in
`list_supported_command_methods()` with its signature and the first line of its
docstring; `describe_command(name)` gives one command's arguments (`name`, `type`,
`required`, and `default` when it has one) and its full docstring. Both are in every
room's command list, at its end.

`run_command(name, arguments)` runs a listed command with keyword arguments and returns
exactly what the command returns. A call it cannot make comes back as a refusal
instead of an exception:

```python
link_help = commands.describe_command("link_frame")
assert link_help["signature"] == "link_frame(frame_name: str) -> None"

refusal = commands.run_command("link_frame", {})
assert refusal["accepted"] is False
assert refusal["reason"] == "command_arguments_invalid"
assert refusal["missing_arguments"] == ("frame_name",)
assert commands.run_command("cleanup", {})["reason"] == "command_not_supported"
```

The refusal's `message` names the command, the problem and how to call it. An
argument no parameter takes is listed under `unknown_arguments`, and a name outside the
list is answered with `supported_commands`. Argument values are not checked, whatever
the command raises reaches the caller unchanged, and `arguments` that is not a mapping
of names raises `TypeError`. `run_command` adds no authority: it runs only listed
commands, each through its own checks.

`tool_definitions()` returns one `name`, `description` and `input_schema` per listed
command. The description is the docstring's text before its `Args:`, `Returns:`,
`Raises:` or `Yields:` section, and the input schema is a JSON Schema object built from
the signature, whose `required` names the arguments `run_command` requires:

```python
tools = commands.tool_definitions()
link_tool = next(tool for tool in tools if tool["name"] == "link_frame")
assert link_tool["input_schema"]["required"] == ["frame_name"]
```

A harness offers these to a model as its tools and passes each tool call to
`run_command(name, arguments)`. The answer can be a live object, such as a conduit;
how to show it to the model is the harness's choice.

## Attach with both sides configured

The target frame must opt into observation before conjure. Nexus policy must allow
the target. Conjure publishes the world, then the Rift attaches with
`create_frame_link(frame_name)`. Codegen targets also require dynamic and AI-native
posture. The target-attachment lesson exercises refusals from both sides.

For multiple worlds, configure the allowed names, permit multiple targets, and
set the target count. Attach each world explicitly. A shared observer leaves
the underlying worlds isolated.

## Find a named live scope

[Named scopes in Nexus and restore](../examples/expert/38-named-scopes-in-nexus-and-restore.md)
shows the complete public setup. Capability rooms can create a named child directly:

```python
job = commands.create_lesser_conduit(root.id, frame_name="jobs", name="job-42")
rift.refresh_runtime_projections(frame_names=("jobs",))
assert commands.get_conduit_by_name("job-42", frame_name="jobs") is job
```

The refresh admits a new published ID into the room's compiled access set. Named
getters in capability and codegen rooms still enforce the selected ID's command
ACL. Naming never grants normal-root bind/link/cluster rights, and static rooms
still do not expose raw conduit objects.

Named cleanup clears its Nexus name and parent metadata while retaining a pooled
record for the reusable ID. Named reuse updates that record. A projection that
already admitted the ID can read those replacement values without recompiling.
Anonymous pool cycles retain their existing local-only publication behavior.

A new ID or permanent record deletion still uses explicit projection refresh.
A stale view of a permanently deleted record can raise until refreshed. Creation
commands do not synchronously refresh while inside their own Rift gate. Neither
published records nor raw lookup results are leases on a scope's lifetime.

## Hold objects deliberately

The workstation holds named handles; the command system resolves permitted world
access. A bound object retains its ordinary Python behavior. Post-bind use of an
already-granted handle is a different boundary from acquiring it. See
[workstation ownership](../advanced/workstation.md) and the complete workbench lesson.

Room policy and code validation are application controls. They are not an operating
system sandbox or a proof that arbitrary hostile Python is safely isolated.
