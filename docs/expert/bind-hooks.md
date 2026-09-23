# Review agent proposals with bind hooks

Prerequisite: [bind and runtime hooks](../intermediate/hooks.md). Expert 37 shows an
application installing its own registration policy on a live normal Conduit, then
passing it object references supplied by an agent workflow. Use the existing
[codegen lessons](codegen.md) when the workflow must first produce those references.

## Check the actual supplied reference

The example registers two ordered `pre` strategies:

1. Require an existing `ReportTool` object.
2. Require its `schema_version` to be `1`.

The second check sees the same object as the first, including its current instance
state. An unrelated object and a tool with an unsupported schema both fail in
`pre_bind`, before a Spell is created or registered.

```python
conduit.add_bind_hooks(
    pre=[review.require_report_tool, review.require_supported_schema],
    activation=[review.configure_spell],
    post=[review.record_registration],
)

supplied = ReportTool()
spell_id = conduit.bind(
    spell=supplied,
    existence="unique",
    submitted_by="report-agent",
)
assert conduit.meld("ReportTool") is supplied
```

The unique-only lifetime is Melder's existing rule for supplied objects. The hook
pipeline checks and annotates that registration; resolution returns the same supplied
reference. The example's type/schema checks are application policy, not new built-in
restrictions on every Melder binding.

## Modify the Spell at the right stage

Pre-bind receives only the target reference. Bind keyword metadata becomes available
on the new `Spell` in activation. The example checks its `submitted_by` label there,
then sets `spell.metadata["review_policy"]` and appends an `agent-reviewed` tag.
The label is application-provided metadata; trusted caller identity must come from
the application's own authenticated context if that distinction is required.

Post-bind receives the same Spell after registration. The example verifies that
`book.find_spell_by_id(spell.spell_id)` returns it, sets
`spell.metadata["post_checked"] = True`, and records its ID in the application's audit.
The caller then inspects those changes through the public lookup.

These are **live metadata changes**. They do not replace source code, create a new
version, recompute a Spell ID or automatically republish a recorded snapshot. Native
identity is established before bind activation; identity-bearing changes need the
normal binding/version workflow. Recording and Nexus publication can precede post-bind,
so a post-hook metadata edit is not a promise that an earlier published record changed.

This example uses active `bind` registrations. `bind_inactive` also runs the lifecycle,
but its post callback receives a parked candidate. A callback for that path should
not assume ordinary selected-version lookup returns the parked Spell.

## Handle failure according to its phase

| Failure phase | Demonstrated result |
| --- | --- |
| `pre_bind` | An unsuitable reference is refused; activation and post do not run |
| `bind_activation` | An unsupported submitter label is refused; the unpublished Spell is retired and the caller's object remains usable |
| `post_bind` | The notification fails after registration; the binding and earlier post metadata changes remain |

Inspect `HookExecutionError.original_exception` for the application's cause. Raising
stops the remaining callbacks in that stage; return values are ignored.

Expert 37 appends a simulated failing audit callback after its normal post callback.
It catches the resulting `post_bind` error and proves `meld("BackupReport")` still
returns the registered object. Inspect existing state before retrying such a bind;
a failed notification does not mean a second registration is needed.

## Keep policy updates on the Book's existing lifecycle

`add_bind_hooks` appends and `clear_bind_hooks` clears all stages for future binds.
Each bind retains its captured callbacks, including when callbacks change the registry.
Use the Book or its normal-Conduit facade for updates. Configuration seeds are captured
when a Book is constructed; changing another Book's runtime registry is separate.

The example's audit is sequential and in memory. Concurrent callbacks must coordinate
any application state they share, and external notifications keep their own failure
and retry policy. The existing [transaction admission](transactions.md) and
[versioning workflow](governed-change.md) continue to govern structural changes.
