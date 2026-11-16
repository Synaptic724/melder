# Melder 0.2.8303

**Unreleased**

## Removing a Rift waits for the agents inside it

**Breaking change:** `Nexus.remove_rift` can now wait, and can refuse. It closes the Rift's gate first: from that
moment a newcomer at any of the Rift's doors - a workstation call, a viewer read, a room command, or one of the Rift's
own methods such as `get_frame_viewer` - is refused at once with RuntimeError ("RiftGate is closed."). The agents
already inside finish their calls, and their calls into the same Rift on the way pass the closed gate; once the last
of them has left, the Rift is removed and cleaned up. Until now the removal tore the Rift down under those agents,
which met an AttributeError or a "has already been cleaned" RuntimeError partway through their work (GitHub issue
#274).

The wait is bounded by the Nexus setting `projection_refresh_gate_timeout_seconds` (polled every
`projection_refresh_gate_poll_interval_seconds`), the bound an ACL refresh already used. If agents are still inside
when it runs out, `remove_rift` logs a warning and raises RuntimeError naming the Rift and how many threads are still
inside; the Rift stays registered with its gate closed to newcomers, and calling `remove_rift` again once they have
left removes it. Code that removed a busy Rift and expected the call to return at once should allow for that wait,
or retry on the RuntimeError.

An agent that removes its own Rift from inside one of that Rift's calls is not waited for - it is the one inside -
and its call returns normally once the removal is done. `Nexus.cleanup` drains every Rift the same way before it tears
anything down: it closes every gate, waits under one shared timeout, logs a warning for each Rift whose agents
outstay it, and cleans up anyway.

`Nexus.close_and_wait_rift` no longer waits for the calling thread's own place in the Rift, and
`Nexus.count_active_rift_threads` and `count_active_rift_threads_total` now count threads inside a Rift, not calls -
a thread making nested calls counts once. Removing an idle Rift is unchanged.

## A Rift's ACL refresh no longer stalls agents inside it or swaps projections under their reads

A call nested in another call of the same Rift - a codegen script that runs a room command, a command that reads the
viewer - stalled behind an ACL refresh of that Rift until the refresh timed out, and the frame's ACL change then
failed. A thread already inside a Rift now passes its gate while a refresh drains it, so the nested call returns at
once and the refresh completes after the agent leaves.

Viewer reads and direct workstation calls now hold the Rift's gate while they run, as room commands already did. An
ACL refresh of a frame (with `projection_refresh_gate_enabled`, the default) therefore waits for the reads in flight
before it replaces that frame's projections, and holds new reads until it is done, so a read no longer fails with the
cleaned error of the projection it was reading during an ACL change. A frame link - `Rift.create_frame_link` or the
room's `link_frame` - still replaces projections without waiting for other agents' reads, and so does a refresh with
`projection_refresh_gate_enabled` turned off; a read that meets one of those still raises the cleaned RuntimeError,
and a retry reads the new projection. A workstation `call_target` that runs longer than
`projection_refresh_gate_timeout_seconds` now makes an ACL refresh of its Rift time out, as a long room command
already did. Each viewer read costs about 1.3 to 2.8 microseconds more (7 to 21% on reads of 6 to 22 microseconds,
measured with the GIL off).

## Spell crystals no longer walk a project's virtual environment, and one analysis asks each question once

With the Crystallizer active, every bind builds a spell crystal, and its analysis walks the modules the spell's module
imports. `CrystallizerConfiguration.with_defaults()` makes the working directory the user source root, so a virtual
environment kept inside the project (`.venv`) counted as the user's own source: each bind's analysis walked every
installed package the project imports - Melder itself included - fingerprinted them, and with `retain_user_sources`
on kept their source text in the record. A module inside a Python environment - under one of the interpreter's site
roots, under `sys.prefix`, `sys.base_prefix` or `sys.exec_prefix`, or in a `site-packages` or `dist-packages`
directory - is now never user source, even under a user source root. It records as a site package (or an unknown
leaf) with no fingerprint and no retained text, and the walk goes into it only when `site_package_dependency_descent`
is on (GitHub issue #327).

One analysis also resolves and classifies each module once, instead of once for every module that imports it. In a
measured project with about 400 modules of its own and a `.venv` inside it, analyzing a spell rooted in one of 50 of
those modules took 0.15 s on average instead of 3.9 s, the module worlds walked falling from 789 to 173 modules on
average (Windows, GIL off).

Records written from now on list such modules as site packages; a record written before keeps what it listed. The
record version moves to 5.0.1 to say so; the shape is unchanged and 5.0.0 records read as before. Source kept inside a
Python environment - for instance in a virtual environment created in the project directory itself - is no longer user
source; keep it outside the environment, or point `user_source_root_paths` at a directory outside it. Every analysis
is still made fresh against the live environment: nothing is kept from one bind to the next.

## A SpellMap consumer bound before its provider waits for it

A spell whose constructor asks for its dependency through a SpellMap - `SpellMap(spellframe="spectrum",
binding_name="ServiceBuilder")`, `SpellMap(ServiceBuilder)` - was refused when nothing was bound at that address yet:
conjure failed with PhaseExecutionError, and in a conjured book the spell's own bind raised "SpellCrafter Phase 3:
SpellMap default could not be resolved", so its provider had to be bound first (GitHub #329). A constructor asking by
class annotation already waited. A SpellMap now waits the same way: the bind and the conjure succeed, the spell's meld
raises UnresolvedInputError naming the SpellMap until a spell is bound at that address (or the meld supplies the value
through `override`), and binding that spell re-gates the consumer, whose next meld wires it. Bind order no longer
matters:

```python
class SpectrumBuilders:
    def __init__(self, service_builder=SpellMap(spellframe="spectrum", binding_name="ServiceBuilder")):
        self.service_builder = service_builder

world = book.conjure(name="world", dynamic=True)
book.bind(spell=SpectrumBuilders, existence="many", permissions="create")  # refused here before
book.bind(spell=ServiceBuilder, existence="many", permissions="create",
          spellframe="spectrum", binding_name="ServiceBuilder")
world.meld(SpectrumBuilders).service_builder  # the ServiceBuilder
```

**Breaking change:** a SpellMap whose address has nothing bound is reported when its spell is melded -
UnresolvedInputError naming the SpellMap - instead of failing conjure or the bind, so a mistyped address surfaces at
meld; `conjure(validation_warnings=True)` lists it as a warning first. Code that relied on conjure refusing such a
SpellMap should meld the spell or read the warnings. Unchanged: a SpellMap that matches several spells still fails at
conjure or bind, a `SpellMap(Class)` whose class is bound only where a class lookup does not reach is still refused
with HIDDEN_PROVIDER, and a SpellMap without a spellframe still reaches only a spell bound with no spellframe.

The warning and the error name a SpellMap parameter by its SpellMap as written - "SpectrumBuilders.service_builder
asks for the spell its default SpellMap(spellframe='spectrum', binding_name='ServiceBuilder') names, but nothing is
bound there ..." - where they named the parameter's annotation, or the frame, before.

## Packaging and documentation

`RiftGate` holds one ticket per thread inside, lets a thread already inside through whatever the gate's state, never
makes a drain wait for its caller's own ticket, and treats a release after cleanup as a no-op; it gains
`close_terminally()`, `wait_until_free()` and `RiftGateDrainTimeoutError`, a RuntimeError carrying `threads_inside`.
The docstrings of `RiftGate`, `RiftGateController`, `Nexus`, `Rift`, `RiftSpace`, `Workstation`, `FrameViewer`,
`CommandSystem` and `CodegenCommandSystem` say which methods hold a Rift's gate and why the rest do not.
`RiftSpace.register_action_pre_hook` checks that its room is live itself, like the other hook methods. The source
and test maps, their indexes and the source graph describe the Rift gate.

`UserSourceCustodyStrategy` takes the roots that are never user source as `environment_root_paths`, and the new
`CrystalAnalyzer.resolve_environment_root_paths` computes them from the site roots and the interpreter's prefixes. The
docstrings of `CrystalAnalyzer` and `UserSourceCustodyStrategy`, the source and test maps, their indexes and the
source graph describe the environment rule and the once-per-pass answers.

Melder's one runtime dependency, pip, now needs 26.3 or later (it was pinned at exactly 26.2.2): installing Melder
upgrades an older pip and leaves a newer one alone. CI, the documentation build's lock and `uv.lock` install 26.3, and
`requirements.txt` names pip as that one dependency (it said there was none) (GitHub issue #286).

The internal-bind guard manifest holds 633 entries at 0.2.8301 (631 at 0.2.8300): `RiftGateDrainTimeoutError` and
the gate's per-thread ticket holder are kernel classes and cannot be bound.

The docstrings of `SpellMap`, `CompilerPhase3`, `RequiredHolesStrategy`, `UnresolvedInputError`, `SocketKind` and
`SpellSystemStates` say that a SpellMap matching nothing waits as an unresolved input; the source and test maps, their
indexes and the source graph describe it.

Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8303.
