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
