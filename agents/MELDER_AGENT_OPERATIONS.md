# Melder — Agent Operating Cheat Sheet

> **Target:** `melder==0.2.50` · Python **3.14+**, preferably free-threaded · Reviewed **2026-09-26**.  
> **Source pin:** `Synaptic724/melder`, commit `9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9` (`prod`).  
> **Evidence:** operational sections of `src_architecture.md` and `src_components.md`, checked against public implementation and executable-example source. **Source-reviewed and Python-syntax-checked; not runtime-tested here.** This environment has Python 3.13 and blocked repository/package downloads; source was read through connected GitHub access, not a completed local clone. Matching version labels do not establish wheel/source byte equivalence. [A], [C], [V]

## 0. Read first — the operating contract

**Use this file as a task router, not as permission to access a world.** `HOST` means trusted application/bootstrap code. `AGENT` means an operator confined to its granted Rift/handles. Never acquire additional authority through `Aether`, private maps, deep imports, or relaxed ACLs merely because an operation is refused.

1. **Identify** package version, target `frame_name`, conduit, binding/ID, room mode, and ownership before acting. Do not silently apply these recipes to another version.
2. **Discover** the actual room: `rift.space.command_system.list_supported_command_methods()`. Advertised method, authorized target, and activated subsystem are three separate requirements.
3. **Inspect before creating.** `meld()` can run constructors and retain objects. Use viewer records or `has_live_creation` / `describe_live_creation_status` to observe without construction.
4. **Choose the narrowest action.** `bind → conjure once → meld`; child scope for a job; SpellSpace for request-local state; dynamic links for inter-conduit sharing; codegen only when needed.
5. **Before a structural change:** inspect current selection, dependents, sharing, source drift, and an actual recovery route. A checkpoint saves structure, not arbitrary object state or external effects.
6. **Use public operations.** Structural verbs own their admission/coordination. Do not mutate registries, compiler caches, selected pointers, or internal transaction strategies yourself.
7. **Verify the result, not just the return.** Check payload flags, identity/selection, an application invariant, and affected consumers. After an exception, inspect before retrying: some failures occur after publication or disposal.
8. **Release only what you own.** End scopes; discard disposed/pooled handles. Report what changed, what was tested, remaining shortfalls, and the next safe action.

**Fast routing:** [Core](#core) · [Bindings/DI](#bindings) · [Scopes](#scopes) · [Sharing](#sharing) · [Agent rooms](#rooms) · [Codegen](#codegen) · [Research/change](#research) · [Persistence](#persistence) · [Failures](#failures) · [Source lookup](#source-lookup).

<a id="core"></a>

## 1. Core runtime in one screen

| Object | What the operator needs to know |
|---|---|
| `Aether` | Process root; owns isolated runtime frames and hosted support subsystems. Usually leave it to bootstrap. |
| `AethericFrame` | World boundary: posture, registries, conduit cloud, and DevOps control plane. |
| `Spellbook` | Registers definitions and configuration; conjures **one** normal/root Conduit. |
| `Spell` / `SpellIndex` | One definition/version / stable lineage identity selecting its current active member. Neither is the application instance. |
| `SpellCompiler` | Structural work in phases 1–4; resolution/execution planning in phases 5–11; changed graphs can revalidate lazily. |
| `Conduit → Meld → Creations` | Scope/authority → resolve/construct → retain and dispose objects according to lifetime. |
| `SpellSpace` | Narrow request-local resolution scope, entered from a Conduit. |
| `Nexus → Rift → space` | Policy root → one agent workspace → viewer, workstation, commands, optional codegen. |
| `Crystallizer` / `MutationResearch` | Structural/source recording and replay / version history, lanes, comparisons, and impact. |

**Four distinctions:** definition ≠ instance; world ≠ room; current live selection ≠ historical version; source materialization ≠ binding. Normal application code uses `import melder as md` and public facades. [A], [C]

## 2. Install and obtain a first object

Run inside an environment whose `python` is Python 3.14+:

```bash
python -m pip install "melder==0.2.50"
python -c "import sys, melder as md; print(sys.version); print(md.__version__); print('GIL enabled:', sys._is_gil_enabled())"
```

A GIL-enabled build warns; do not mistake it for a free-threaded test. For a reproducible source checkout instead of PyPI, these are **instructions for the receiving environment**, not a claim that a clone was completed during this review:

```bash
git clone --branch prod https://github.com/Synaptic724/melder.git melder
git -C melder checkout 9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9
python -m pip install -e ./melder
```

**HOST · standalone starter.** Define classes before registering them; required annotations establish dependency edges.

```python
import melder as md

class Settings:
    def __init__(self) -> None:
        self.region = "local"

class Worker:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

book = md.Spellbook(aetheric_frame="starter")
root = None
try:
    settings_id = book.bind(spell=Settings, existence="unique")
    worker_id = book.bind(spell=Worker, existence="many")
    root = book.conjure(name="starter-root")
    first = root.meld(spell_id=worker_id)
    second = root.meld("Worker")
    assert first is not second
    assert first.settings is second.settings
    assert root.meld(spell_id=settings_id).region == "local"
finally:
    if root is not None:
        root.cleanup()
    book.cleanup()
```

`Spellbook.bind()` returns a **spell ID**, not a `Spell` or instance. `conjure()` returns the root; `meld()` returns the application object. Do not call `conjure()` again to get another instance. Ordinary missing/ambiguous dependencies and cycles can fail graph validation; intentional late contracts and later structural changes also have meld-time gates. [C], [E]

<a id="bindings"></a>

## 3. Addressing, binding, and dependency injection

### Select deliberately

| Need | Public shape |
|---|---|
| Human registered name | `root.meld("Worker")` |
| Exact machine ID lane | `root.meld(spell_id=worker_id)` — never pass a SHA as an ordinary name string. |
| Category + role | `root.meld(spellframe="storage", binding_name="primary")` |
| Register class | `book.bind(spell=Store, existence="unique", spellframe="storage", binding_name="primary")` |
| Register existing value | `book.bind(spell=value, existence="unique")`; lookup normally uses its type name, not the Python variable name. |
| Register function/factory | `book.bind(spell=make_settings, existence="unique")`; meld runs the factory and reuses its product. |
| Observe definitions | `book.describe_spells_in_spellbook()`; active inventory is not parked-version inventory. |
| Observe live presence | `root.has_live_creation(spell_id=sid)` / `root.describe_live_creation_status(spell_id=sid)` |

`spellframe` classifies definitions **inside** a world; `aetheric_frame` selects the world. Binding names normalize case; do not use capitalization as an isolation strategy. Use IDs or complete selectors after discovery. [C: Binding / Meld][C], [E]

**Collision rules:** duplicate binding fingerprints/keys are refused. Runtime spell IDs are process-wide; a different world name alone does not make an identical registration unique. Give separate-world bindings deliberate distinct identities. Within one visible graph, do not assume rebinding the same named class under different binding names/categories will pass validation; the documented working pattern is distinctly named role subclasses, e.g. `PrimaryStore(Store)` and `ArchiveStore(Store)`. Do not alter `__name__` or private registries to evade this. [NAMES]

### Constructor decision table

| Parameter | Meaning |
|---|---|
| `store: Store` without a default | Infer a required provider. |
| `store: Store = ordinary_value` | Keep the Python default; **ordinary defaults suppress inferred DI**. |
| `store = md.SpellMap(Store)` | Explicit local DI selector. |
| `store = md.SpellMap(spellframe=StoreProtocol, binding_name="primary")` | Explicit category/role; exactly one provider must match. |
| `handlers: list[HandlerProtocol]` | Collection DI over matching providers; do not invent an ordering guarantee. |
| `store = md.SpellContract(spellframe=StoreProtocol, binding_name="primary")` | Intentional late socket, for a dynamic world; wire provider/link/grant before using it. |

`SpellMap` / `SpellContract` require at least `spell` or `spellframe`. Protocol-as-category checks are limited to directly declared public members/presence/callability; they are **not complete signature, inherited-member, or field conformance proofs**. Test the actual interface behavior. [C: DI Descriptors / Binding][C]

### Native capability versus staging

`bind(..., resolvable=False)` registers a **non-executable definition/reference**. It is independent of permissions, active/parked membership, and validity. Application Protocol definitions require this flag when they are themselves the bind target. Direct meld and reuse reject non-resolvable registrations, even if an existing value can be described. A required consumer input referencing one must be supplied through the ordinary override path; registration does not provide its value. `bind_inactive(...)`, in contrast, parks a version in an index. **Do not substitute one mechanism for the other.** [C]

### Optional registration conveniences

`@md.scan_bind(...)` stores declaration metadata only; `book.scan(module)` performs registration later and returns IDs. Imports alone do not register those declarations. `SpellBinder` is the fluent adapter; inspect its current surface instead of guessing chained setters. Bind classes for fresh populations: function/method/lambda and prebuilt-object bindings are unique-only; modules and guarded Melder internals are not application spells. [C], [E]

<a id="scopes"></a>

## 4. Lifetimes, scopes, and memory

| `existence` | Reuse boundary | Operating rule |
|---|---|---|
| `unique` | One object for that binding in its owning runtime world | Shared consumers can receive the same object; not a process-wide singleton by Python class. |
| `many` | New instance per meld | Bound resources may be retained for disposal; fresh does not mean automatically short-lived. |
| `unique_per_conduit` | One per Conduit | Use child scopes for job/session state. |
| `unique_per_conduit_lineage` | Shared within the lineage tree | A child is not necessarily isolated from its root's state. |
| `unique_per_spell_space` | One per SpellSpace | Resolve through the Space, not an ordinary Conduit door. |
| `unique_per_conduit_cluster` | Shared cluster store | Needs dynamic cluster setup, links, and an elected leader. |

**Scope recipes** — assume `root` already exists and the relevant definitions are registered:

```python
child = root.create_lesser_conduit(name="job-42")
try:
    job_state = child.meld("SessionState")
finally:
    child.cleanup()

with root.enter_spellspace() as request:
    request_state = request.meld("RequestState")
    assert request.meld("RequestState") is request_state
```

Register `SessionState` as `unique_per_conduit` and `RequestState` as `unique_per_spell_space` for the intended behavior. Direct manual `enter_spellspace()` handles also exist; managed `with` is the easier cleanup discipline. Managed stacks are thread-local, not a promise of asyncio task-local isolation. Do not interleave scope exits out of order or share a request handle across unrelated tasks/threads. [C: Creations / SpellSpace Thread State][C], [PURGE]

**Named scopes:** nonempty names are frame-wide unique across roots and active named lessers. Naming does not create a new Book or grant root authority. A pooled ID/name identifies a current use, not a durable lease. A returned handle may become stale when its owner cleans/recycles it. Keep application ownership explicit; discover again after lifecycle changes. [A], [NAMED]

## 5. Cleanup, purge, and hooks

### Disposal is registered behavior

```python
resource_id = book.bind(
    spell=Connection,
    existence="unique",
    disposal_method_names=["close", "shutdown"],
)
```

Methods are matched once at binding. Missing names are omitted; duplicates run once. Matching uses declared class-profile methods, not an automatic cleanup protocol for inherited-only methods, factory products, or prebuilt values. Explicitly arrange ownership/cleanup for those cases. Book-level method names own overlaps; default order is spell-only block then Book block, reversed by `with_enforce_priority_disposal_methods(True)`. [C: Binding][C]

Cleanup walks retained disposal keys/buckets newest-first, not a promised total chronological order across all scopes. A failing method stops the remaining methods for that object; other objects are attempted and failures can aggregate into `ExceptionGroup`. Dropping your Python variable does not free an object still retained by Melder or a workstation. [C: Creations][C]

### Retire instances without deleting their definition

```python
removed_one = root.purge(instance, purge_all=False)
removed_all = root.purge("Connection")  # default purge_all=True
replacement = root.meld("Connection")
```

`purge_all=False` requires an actual instance; a selector alone is insufficient. Return value is the number removed; absent/unretained entries give zero. Qualified registrations may require explicit selectors—do not assume an instance can recover an unknown qualifier. A SpellSpace purges only its local supported lifetimes; a Conduit can purge local `many`/per-conduit stores, while unique/lineage/cluster stores require the owning scope/root/leader. Disposal occurs **after detachment**; a cleanup failure does not restore the removed entries. Existing application references still point to disposed objects: stop using them. [PURGE], [C]

### Registration hooks are not construction hooks

`book.add_bind_hooks(pre=[...], activation=[...], post=[...])` appends callbacks; normal Conduits expose the same facade. Configuration seeds use `configuration.with_bind_hooks(...)`. Lesser scopes cannot edit the borrowed Book's hooks.

| Stage | Input | Failure meaning |
|---|---|---|
| `pre` | Original supplied reference | Refusal creates no Spell. |
| `activation` | New, not-yet-published `md.Spell` | Failure retires the unpublished allocation. |
| `post` | Actual published active **or parked** `md.Spell` | Publication already occurred; do not assume rollback. |

Return values are ignored. In-flight binds keep their captured callback sequence. `clear_bind_hooks()` clears **all** future stages, not just your callback; never use it to remove one hook from a shared application. Bind post is not an outer-transaction commit callback. Instance-construction hooks and Conduit/Meld lifecycle hooks are separate surfaces. Pool-local hook overlays are reset after owned creations are disposed; do not retain pooled handles or mutate frozen configuration to change runtime hooks. [HOOKS], [C]

## 6. Overrides — construction input, not automatic rollback

```python
worker = root.meld("Worker", override={"settings": supplied_settings})
pipeline = root.meld(
    "MailPipeline", override={"transport>credentials": supplied_credentials},
)
```

Paths traverse **constructor parameter names** from the melded root, not class names. Dict/list/tuple are supported payload families; use the simple dictionary form unless the task needs positional/deeper forms. Unmatched deep paths refuse. Inspect the actual signature and graph before composing wildcards/broadcasts. [C: Meld][C], [OVERRIDE]

**Lifetime wins:** an override can construct a canonical singleton around the supplied value, so the substitution survives the call. Making only the outer object `many` does not isolate shared inner singletons. Use isolated/scoped bindings for fixtures and verify every affected lifetime. Nor is an override a promise to rewrite an already-created singleton; check live presence and choose explicit authorized replacement/purge only when appropriate. [OVERRIDE]

<a id="sharing"></a>

## 7. Dynamic composition and permissions

**Mode belongs to the frame.** On an unsettled world, `conjure(dynamic=True)` settles dynamic posture. Later roots inherit settled posture—even a contradictory flag does not convert an existing world. Configure posture before binding/conjuring when required. Automatic worlds permit only the default policy; link, sever, ownership transfer, and lesser-to-normal upgrade require dynamic posture. Frame-level operation-disable policy can still refuse a dynamic operation. [A], [C], [CONDUIT]

**Same-world sharing is a pull:**

```python
# owner_book and borrower_book belong to the same unsettled/dynamic frame.
shared_id = owner_book.bind(spell=SharedService, existence="unique", permissions="create")
owner = owner_book.conjure(dynamic=True, name="owner")
borrower = borrower_book.conjure(name="borrower")
owner.link(borrower)
borrower.add_spell_to_contract(
    spell_id=shared_id, conduit=owner, permissions="create",
)
shared = borrower.meld(spell_id=shared_id)
```

The **borrower** requests from the **owner**, after both normal roots exist and are linked. A link alone does not grant every spell. No self-link, lesser peer-link, or cross-`aetheric_frame` link. For `SpellContract`, assemble each edge in provider → consumer → link → borrower grant → consumer meld order. An unresolved intentional contract is not permission to execute a broken graph. [CONDUIT], [C]

`create` authorizes construction/resolution across the contract; `read` is reuse/resolve-only without granting borrower construction rights; `block` blocks sharing. Owner policy, link policy, and effective grants remain relevant. A read grant does **not** imply a cold instance will appear: inspect live status or have the owner create it. [PERMISSIONS]

For sever/ownership transfer/upgrade, discover the exact public signature on the installed Conduit and inspect all affected consumers first. An upgraded lesser gets a **new empty Book** and its selected configuration; old definitions and local hook overrides do not automatically transfer. Same Conduit identity does not imply the same registry. [A], [C]

### Cluster recipe

Assumes dynamic normal `owner` and `member`, with a class bound on owner as `unique_per_conduit_cluster`, `permissions="create"`:

```python
owner.link(member)
cloud = owner.get_conduit_cloud()
cloud.create_cluster("workers")
cloud.add_conduit_to_cluster(owner, "workers")
cloud.get_cluster("workers").elect_leader(owner.id)
cloud.add_conduit_to_cluster(member, "workers")
assert owner.meld("ClusterBus") is member.meld("ClusterBus")
```

Link first; elect the owner/leader before additional members join. A cluster name without the links/leader is not working shared storage. [CLUSTER]

## 8. Bootstrap order and configuration ownership

For a recorded, agent-enabled world, configure in this order:

**Aether/utility → Crystallizer → MutationResearch → Nexus → frame posture → Book → Conduit.**

Enable recording/research **before the events you want recorded**; later activation does not backfill an earlier application world. Inactive recording seams are no-ops. A finalized configuration, an activated configuration, and an activated subsystem are different states. Do not interchange `.finalize()` and `.activate()` by analogy across builders. Nexus's activation flow differs from the root configuration ladders. [A], [PERSIST], [RESEARCH]

**HOST · optional recording/research setup, before the room bootstrap below:**

```python
import melder as md

recorder = md.Crystallizer()
recorder.activate(md.CrystallizerConfigurationBuilder().with_defaults().activate())

research = md.MutationResearch()
research_config = research.create_configuration()
research_config.with_defaults().finalize()
research_config.activate()
research.activate(research_config)
```

These are process-hosted services; do not repeat activation in an existing application without understanding its configuration ownership. Shared frame-wide Book configuration means shared frozen **policy**, not a shared Book/registry/lifecycle. Configure logging explicitly when operational logs are required; no output does not prove inactivity or success. [A], [C]

<a id="rooms"></a>

## 9. Open an agent room — HOST bootstrap

**Illustrative dedicated world, not a production least-privilege ACL policy.** Host must choose explicit target/command/codegen permissions before exposing the Rift. Existing applications should recover authorized frames/rooms rather than recreate or overwrite their process configuration. [ROOMS], [BUILD]

```python
import melder as md

FRAME = "agent-ops"

nexus = md.Nexus()
nexus_config = nexus.create_configuration()
nexus_config.with_rift_creation_enabled(True)
nexus_config.with_allowed_target_frame_names([FRAME])
nexus.activate(nexus_config)

book_config = md.SpellbookConfiguration(FRAME).with_defaults().finalize()
book = md.Spellbook(aetheric_frame=FRAME, configuration=book_config)
book.configure_aether_frame(
    system_state="dynamic",
    disposal=None,
    disposal_method_names=None,
    rift_enabled=True,
    ai_native=True,
)
root = book.conjure(name="ops-root")

rift_config = nexus.create_rift_configuration()
rift_config.with_space_type("codegen")  # choose static/capability when enough
rift = nexus.create_rift(configuration=rift_config, rift_name="operator")
rift.mark_active()
rift.create_frame_link(FRAME)

space = rift.space
viewer = space.frame_viewer
workstation = space.workstation
commands = space.command_system
# Own this session's lifetime: rift.cleanup(), then root/book cleanup when done.
```

A Rift owns exactly **one** space. Each Rift needs a fresh configuration object; a bare Rift may have no attached frames. Target attachment requires published descriptor truth, target opt-in, Nexus permission, and the applicable room posture. Static observation needs `rift_enabled`; dynamic agent access also needs dynamic and AI-native posture. `create_nexus_frame(...)` is strict-create and returns a rooted Conduit; `get_nexus_frame(...)` is recovery. Neither returns the underlying frame object. [C: AR Runtime][C]

| Room | Actual operating surface |
|---|---|
| `static` | Permitted already-live spell views/reuse paths; no direct creating `meld`, raw conduit exposure, or topology mutation. |
| `capability` | Broad manual runtime/object commands plus research reads; no codegen. |
| `codegen` | Selected runtime helper subset, codegen, and research authoring. **Not a guaranteed superset of capability commands.** |

View, command, and codegen ACLs are separate concerns. A method being listed does not authorize all frames/objects. AST validation and room policies are application controls, **not an OS sandbox**; hostile/untrusted Python requires an appropriately isolated execution environment outside this library. Already-granted Python handles are not continuously re-policed by acquisition ACLs. [COMMANDS], [ROOMS]

## 10. First minute inside a room — AGENT

```python
commands = rift.space.command_system
viewer = rift.space.frame_viewer

supported = commands.list_supported_command_methods()
assigned = rift.list_assigned_frame_names()
visible = viewer.list_frame_names()
onboarding_json = viewer.describe_agent_onboarding_json()
method_surface = viewer.describe_viewer_method_surface()

# Pick an explicitly authorized FRAME from assigned/visible, not an invented name.
frame_view = viewer.get_view_frame(frame_name=FRAME)
conduit_view = viewer.get_view_conduit(frame_name=FRAME)
spell_view = viewer.get_view_spell(frame_name=FRAME)
```

Frame-local viewer operations require an explicit frame; `get_view_multiframe()` is host-scoped. The helpers read current Rift projection truth, **not necessarily all newly published runtime IDs**. An empty view can mean unattached, unauthorized, unpublished, or not-yet-live—not that the application has no definitions. Ask the viewer's missing-surface/description APIs through its advertised surface before escalating. [VIEWER], [C]

**When supported and authorized**, acquire a normal root through the command boundary:

```python
root_handle = commands.get_conduit_by_name("ops-root", frame_name=FRAME)
```

That raw handle is meaningful authority; use it only for the host-approved task. Do not reach around the command boundary to find a denied root. With capability-room named child creation:

```python
job = commands.create_lesser_conduit(root_handle.id, frame_name=FRAME, name="job-42")
rift.refresh_runtime_projections(frame_names=(FRAME,))  # outside the creation command
assert commands.get_conduit_by_name("job-42", frame_name=FRAME) is job
```

New/deleted IDs require explicit projection refresh. Same-ID named pool reuse replaces descriptor values and can retain already-compiled membership; reacquire/verify the current name and ownership. Never assume descriptor and Cloud reads form one atomic snapshot. [NAMED]

**Workstation:** store only approved handles. `bind_object(name, value)` does not register a Spell. `set_target(name)` selects a handle; `call_target(...)` requires a callable target. For a method, keep the method handle alive or use the discovered method-binding surface—not `call_target()` on an arbitrary service instance. Strong bindings retain objects; weak bindings can disappear. `workstation.cleanup()` drops its bindings, **not the lifetime of the underlying objects**. [C: Workstation][C]

<a id="codegen"></a>

## 11. Codegen — validate → materialize → import → bind → meld

Prerequisites: codegen room, eligible target, relevant ACLs, and explicit approval for the change. Use one bounded source unit and unique module/binding names. Generated execution can have ordinary Python/application effects. Keep secrets out of generated source and command payloads that may be recorded. [COMMANDS], [BUILD]

**AGENT validation/materialization; HOST or explicitly authorized Python executor for import/bind.** This follows the public example's split; it does not assume an unadvertised `commands.bind()`.

```python
source = '''class GeneratedCounter:
    def __init__(self) -> None:
        self.total = 0

    def add(self, amount: int) -> int:
        self.total += amount
        return self.total
'''

verdict = commands.validate_codegen(source, frame_name=FRAME)
if verdict.get("accepted") is not True:
    raise RuntimeError(f"Codegen rejected: {verdict}")

published = commands.materialize_codegen(
    source, module_name="agent_counter_v1", frame_name=FRAME,
)
if published.get("materialized") is not True:
    raise RuntimeError(f"Materialization failed: {published}")

# Host side, or an execution environment explicitly allowed these operations:
import importlib
GeneratedCounter = importlib.import_module("agent_counter_v1").GeneratedCounter
counter_id = root.bind(
    spell=GeneratedCounter, existence="many",
    permissions="create", binding_name="counter-v1",
)
one = root.meld(spell_id=counter_id)
two = root.meld(spell_id=counter_id)
assert one is not two
assert one.add(3) == 3 and two.total == 0
```

For ephemeral computation, `commands.execute_codegen(source, frame_name=FRAME)` returns an execution payload. Inspect the complete status/error information before trusting `result`; a returned dictionary alone is not success. Do not invent a universal `success` key shared by every command. [BUILD]

Typical generated namespace names are `viewer`, `workstation`, `target`, `command`, `codegen`; imports/builtins/reflection still depend on the compiled policy. Relevant codegen policy fields include `imports_enabled`, `allowed_import_module_roots`, `denied_builtin_names`, `unsafe_reflection_allowed`, `dunder_access_allowed`, and `recursive_codegen_allowed`. Ask the host to author policy; do not enable a denied facility to make a snippet pass. [COMMANDS], [C]

**What each step does not do:** validation does not prove safety; execution does not necessarily retain a module; materialization gives a module address but not a registered Spell; binding is the custody/version entry; melding constructs/returns an object. Generated source can be retained even without a file. Ordinary Python/module caching and duplicate-name checks still matter; a new materialization is not an automatic in-place rewrite of existing objects. [BUILD], [PERSIST]

<a id="research"></a>

## 12. Research — inspect before changing

Research must already be active. Host/direct authorized access is `root.mutation_research` or `md.MutationResearch()`; the old `get_mutation_research()` accessor is not the current route. Room users discover `research_*` commands; capability rooms have reads, codegen rooms add authoring, static rooms do not expose this family. [C], [COMMANDS], [RESEARCH]

| Question | Direct research surface / room family |
|---|---|
| What just happened? | Room `research_recent`, history/walk/heads/campaign reads. |
| What is live/parked/stored? | `residency_view(spell_id)` / `research_residency`. |
| What would be affected? | `impact_view(spell_id=...)` / `research_impact`. |
| What source is available? | `source_view`, `module_view`, `parts_view`, `part_view`; room `research_source/module/parts/part`. |
| What depends on a module? | `module_graph_view` / `research_module_graph`. |
| Did the file change outside recording? | `source_drift_view` / `research_source_drift`. |
| What differs between recorded versions? | `diff_research` / `research_diff`: source, structural, or parts strategy. |
| What would proposed code do structurally? | `preview_candidate(code, against_spell_id=...)` / codegen-only `research_preview`. |
| Can donor parts be composed? | `synthesize_candidate` / `research_synthesize`; preview/composition, not automatic deployment. |
| What is the subsystem-sized impact? | Group view/diff/impact/footprint/drift/history families. |

Use discovery/help for each less-common verb's selector and return schema; these names are a routing map, not interchangeable signatures. `source_view` can fall back to current disk with a drift marker; **version comparisons use recorded material, not today's file for both sides**. Missing custody is not “no changes.” A part-level diff still has module-grain impact. [C: Workstation / MutationResearch][C]

```python
# HOST or explicitly granted research handle; no code executes in this preview.
research = root.mutation_research
residency = research.residency_view(current_id)
impact = research.impact_view(spell_id=current_id)
preview = research.preview_candidate(candidate_source, against_spell_id=current_id)
# Review parse/validation findings, recorded-vs-live evidence, and affected consumers.
```

A `ResearchSet` is an independent organization of history, not a runtime frame or persistence profile. `research.create_research_set("change-review")` creates one; `research.research_set(name)` accesses one. A lane's **state** is open/joined/archived; **type** is development/experiment/production/test. Type enforcement is an explicit policy. Lane attachment/joining changes research organization; it does **not** by itself notch the live implementation. Grouped compositions pin members and are informational, not another executable Spell. [RESEARCH], [C]

Campaigns (`set_active_campaign` / `clear_active_campaign`) and staged ancestry are ambient recording context. Set/clear deliberately, especially around concurrent work; next-entry ancestry is one-shot, not a permanent override. Do not infer a completed automatic promotion/quarantine controller merely from enum names—the architecture records incomplete producer/runtime seams. [A], [C]

## 13. Stage, select, verify, and revert

**Public verbs:** `root.bind_inactive(...)`, `root.notch_spell(spell_index=..., spell=...)`, `root.add_to_spell_index(...)`, `root.remove_from_spell_index(...)`. The Conduit owns admission; do not call private Book mutation seams. [CONDUIT]

**Critical lookup trap:** `get_spell_by_id()` / `find_spell_by_id()` can resolve a parked lineage ID to the **currently selected** member. They are not a reliable exact parked-object lookup. `notch_spell` requires the actual candidate `Spell`, not its ID or the application class. Never fabricate it or read `_inactive_spells` to obtain it. [NOTCH]

### Host-controlled exact-handle pattern

The older notch lesson stops at this lookup boundary. The newer public post-bind hooks deliver the actual registered active **and parked** `Spell`. A host can capture those handles at registration, and promote only after the bind itself returns successfully. The following is a **source-derived composition of public APIs, syntax-checked but not runtime-executed here**; validate it in a disposable 0.2.50 world before deployment. It installs its own hook on its own Book, not on a shared production Book. [HOOKS][C: Spellbook][C], [CONDUIT]

```python
import melder as md

class PriceV1:
    def quote(self) -> int:
        return 100

class PriceV2:
    def quote(self) -> int:
        return 125

versions: dict[str, md.Spell] = {}

def capture(spell: md.Spell) -> None:
    versions[spell.spell_id] = spell

book = md.Spellbook(aetheric_frame="version-lab")
root = None
try:
    book.add_bind_hooks(post=[capture])
    old_id = book.bind(spell=PriceV1, existence="unique", permissions="create")
    root = book.conjure(dynamic=True, name="version-root")
    old_spell = versions[old_id]
    index = old_spell.spell_index

    new_id = root.bind_inactive(
        spell=PriceV2, spell_index=index,
        existence="unique", permissions="create", binding_name="v2",
    )
    candidate = versions[new_id]  # exact object from the successful bind's hook
    assert candidate.spell_id == new_id
    assert index.selected_spell_id == old_id

    root.notch_spell(spell_index=index, spell=candidate)
    try:
        assert index.selected_spell_id == new_id
        assert root.meld(spell_id=new_id).quote() == 125
    except Exception:
        root.notch_spell(spell_index=index, spell=old_spell)
        raise

    # Deliberate revert demonstration, not undo of arbitrary external effects.
    root.notch_spell(spell_index=index, spell=old_spell)
    assert index.selected_spell_id == old_id
    assert root.meld(spell_id=old_id).quote() == 100
finally:
    if root is not None:
        root.cleanup()
    book.cleanup()
    versions.clear()
```

**Operational limits:**
- Selection parks the outgoing version; it is not automatic disposal, resource retirement, or a rewrite of already-held application objects. Retire versions explicitly after consumers no longer need them.
- The architecture's “owner-side only” warning describes an internal seam, not the whole current public operation. The inspected `Conduit.notch_spell` performs the local transaction, then deactivates stale borrowed copies and emits an index-notch notification for index-linked receivers. **Do not assume all borrowers automatically gain the new version**, or that the post-transaction fan-out is one indivisible action. Re-read grants, selection, and affected consumer behavior. [CONDUIT]
- On a notch exception, inspect the selected ID and consumer state before retrying: the owner switch may already have occurred. Preserve both failure and recovery reports; a recovery failure must not be labeled success.
- Moving/separating active index members is refused; first select another member. Separating the sole member is not the retirement route. No manual edits of `selected_spell_id`.
- Class-version fingerprints do not cover every method-body edit. Do not assume a source edit creates a new Spell ID; verify IDs, selected membership, recorded source, and behavior. Use deliberate version identities. [C: Binding][C]

<a id="persistence"></a>

## 14. Checkpoint and restore

**Four different operations:**

| Operation | What it establishes |
|---|---|
| `recorder.create_checkpoint(description=...)` | Checkpoint in the in-process ledger. |
| `recorder.flush_checkpoint(checkpoint_id)` | Local sealed cache; optional remote delivery is a separate guarantee. |
| `recorder.reload_cached_checkpoint(checkpoint_id)` | Recorded data loaded back into the ledger, not a live world. |
| `recorder.load_checkpoint(checkpoint_id)` | Attempts structural replay through public operations. |

```python
checkpoint_id = recorder.create_checkpoint(description="before-approved-change")
record_summary = recorder.describe_checkpoint(checkpoint_id)
flushed_ids = recorder.flush_checkpoint(checkpoint_id)
if checkpoint_id not in recorder.list_cached_checkpoint_ids():
    raise RuntimeError("Required checkpoint is not present in the local cache")
```

**A successful local flush does not prove remote receipt.** Default remote handling is lenient; use your persistence handler's independent acknowledgment/verification. Local cache is FIFO-bounded; another flush may evict older data. Preserve and verify the required **chain**, not just one latest ID. Profiles partition recording windows; changing the active profile does not copy previous content, and checkpoint ID listing is a process-wide ledger read. [RESTORE], [CACHE], [PERSIST]

**Controlled replay:** quiesce application work and ordinary lesser/SpellSpace acquisition/cleanup; retire conflicting live roots only with host authorization. Keep the recorder alive for in-memory replay, or configure storage and reload the complete required chain after a process restart. Do not unconditionally destroy a production world just because load reports a collision.

```python
# PRECONDITION: authorized, quiescent target; required record chain already loaded.
report = recorder.load_checkpoint(checkpoint_id)
if report.get("status") != "complete":
    raise RuntimeError(f"Restore not complete: {report}")
identity_map = report["identity_map"]
# Inspect built counts/shortfalls, reacquire handles, then run application tests.
```

Fresh structural ULIDs are expected; use the report's old→new map and reacquire all room/conduit handles. Stable spell hashes require equivalent binding inputs/policy; do not assume every old identifier survives. Named lesser topology and required unnamed ancestors can replay; prior application object contents do not. Callback code, external resources, and other unreplayable material must appear as shortfalls or require host participation. An all-or-nothing build rollback is not undo of every possible external effect. [NAMED], [RESTORE], [A]

`CrystallizerBootstrap().with_profile("default").bootstrap()` is the one-shot cold-start facade; configure external persistence first when needed, then inspect activation, reloaded material, restored checkpoint, restore report, and shortfalls. Melder does not supply your database/cloud SDK; handler durability, access control, and acknowledgments are your responsibility. Do not disable drift/preflight blockers to force a green status. [A], [RESTORE]

## 15. Concurrency and advanced change discipline

Use separate Rifts/workstations for independent agents; one room's commands/workstation have their own locks. Distinct rooms do not make shared application objects race-free. Choose per-worker lifetimes or synchronize application state explicitly. Free-threaded Python removes a safety illusion, not the need for locks. [C]

Structural operations are coordinated by scope claims; runtime resolution uses creation/validity machinery rather than entering the structural transaction plane. Leave admission, dirty-root invalidation, recompilation, and gates to the public operations. Disjoint structural changes may proceed concurrently; shared scope changes may wait/refuse. A timeout requires identifying conflicting work/scope, not turning off the gate. [A], [C]

For shutdown, restore, or multi-step governance, quiesce the relevant application work yourself. Do not assume a transaction freezes every business method or every ordinary pool cycle. Internal failure postures such as `UNWIND` versus `LEAVE_BROKEN` are not universal rollback promises; inspect any recorded residue/incident before continuing. [A], [RESTORE]

<a id="failures"></a>

## 16. Failure routing

| Symptom | Inspect / next safe action |
|---|---|
| Import/runtime warning | Check Python floor, GIL mode, installed Melder version; do not claim tested compatibility from syntax alone. |
| Duplicate name/key/ID | Reuse existing registration or choose explicit distinct role/version identities; inspect both local and process-wide collisions. |
| Missing/ambiguous provider or `SpellbookValidationError` | Read validation issues and constructor selectors; distinguish local DI from intentional late `SpellContract`. |
| Non-resolvable registration refusal | Supply the consumer input or select a legitimately resolvable definition; changing metadata/permissions is not the fix. |
| Request-local dependency refused at Conduit door | Resolve through the proper `enter_spellspace()` scope; do not bypass scope checks. |
| `HookExecutionError` | Read phase, callback, chained cause. Especially after `post`, inspect whether the binding is already published before retrying. |
| Meld invalid/gated/dirty | Inspect graph validity, contracts, prior failed structural change, and revalidation report; don't clear flags manually. |
| Dynamic action refused | Check settled frame posture and operation-disable policy, then normal-root ownership. Repeating `dynamic=True` is not conversion. |
| Static/capability/codegen method missing | Query supported commands; codegen is not capability parity. Ask host for a justified different room, not a bypass. |
| Empty/incomplete viewer | Check assigned frame, publication, ACL visibility, live-only filtering, and explicit projection refresh. |
| Codegen rejected or returned errors | Inspect verdict/payload and allowed namespace. Revise the requested operation; do not relax policy silently. |
| Parked ID lookup returns old version | That lookup follows active selection. Use a host-provided exact candidate handle, not a private-map workaround. |
| Notch failed | Re-read selected ID and borrower/index-link state; distinguish local commit from later fan-out and application verification. |
| Purge/cleanup `ExceptionGroup` | Entries may already be detached and resources partially closed. Inspect each failure; don't use or blindly re-dispose old handles. |
| History/source absent | Check recording activation timing, custody policy, profile/set, and drift. “Unavailable” is not “unchanged.” |
| Flush succeeded but backup missing | Verify local cache retention and remote acknowledgment separately. |
| Restore returns but world incomplete | Require `status == "complete"`, then inspect counts, shortfalls, ID translations, and application checks. |

**Agent completion record:** `version; frame/conduit; requested action; exact public call/selector; before→after IDs/selection; payload verdict; invariant tests; disposal/ownership changes; remaining shortfalls; recovery status`. Never report “rolled back” solely because a revert was attempted.

<a id="source-lookup"></a>

## 17. Expand context without dumping the repository

The package ships addressable documents **before any world is conjured**:

```python
import melder as md

architecture = md.__architecture__
components = md.__components__
network = md.__graph_network__
details = md.__graph_details__

if not components.available or not components.verify():
    raise RuntimeError(f"Component document unavailable/unverified: {components.reason}")

# Find headings cheaply, choose a bounded section, then read it.
sections = components.find("Meld Resolution Runtime")
for section in sections:
    print(section.key, section.line_count)
# After selecting a real returned key:
# text = components.get(key)
# citation = components.cite(key)
```

`addressing` tells whether keys are heading paths or source paths. `keys()/groups(depth)/index()` survey cost; `find()` matches keys; `search(needle, limit=...)` searches bodies with previews. `section(key)` gives line cost; `get(key)` reads one section; `reader(key, line_target=...)` pages that section. `verify()` checks content against its index, **not that every prose claim is current code truth**. Avoid unbounded `render_markdown()` and whole-repository ingestion. [DOCS]

**Escalation order:** this guide → installed method surface → relevant architecture/component section → exact public method implementation and current example/test. Host-side `inspect.signature()` or `help()` can verify uncertain calls; an agent in a reflection-denied room uses its advertised description surface or requests host-supplied API information instead.

| Need to investigate | Source owner / component heading |
|---|---|
| Binding, identities, config | `src/melder/aether/spellbook/{spellbook.py,bind/bind.py,bind/spell_index.py}`; “Spellbook Core”, “Binding Pipeline”, “DI Descriptors”. |
| Root/child/link/notch | `src/melder/aether/conduit/conduit.py`; “Conduit Runtime”, “ConduitWard and Contracts”. |
| Overrides/live probes/lifetimes | `src/melder/aether/conduit/meld/{meld.py,conduit_meld.py,spellspace_meld.py}`; “Meld Resolution Runtime”. |
| Disposal/scopes | `src/melder/aether/conduit/{creations,spell_space}/`; “Creations and SpellSpace”, “SpellSpace Thread State”. |
| Validation/recompile | `src/melder/aether/spellbook/spell_compiler/`; “SpellCompiler and Validation Pipeline”. |
| Admissions/incidents | `src/melder/aether/aetheric_frame/dev_ops/`; “DevOps Control Plane”, “Transaction Admission Plane”. |
| Frame/room/ACL/view | `src/melder/nexus/`; “AR Runtime Surface”, “Nexus Descriptor And ACL Managers”. |
| Actual agent commands | `src/melder/nexus/rift/command_system/`; inspect the **room-specific** class, not a merged imagined API. |
| Code validation/execution | `src/melder/nexus/rift/codegen_system/`; “Codegen Internal Engine”. |
| Checkpoint/restore/graft | `src/melder/crystallizer/`; “Crystallizer Root, Persistence Record, And Module-World Surfaces”. |
| Versions/compositions | Public `md.MutationResearch`; locate its source through “MutationResearch Root” / “MutationResearch ResearchSet Package”. |

This is a navigation map, not permission to drive internals. In prose/code conflicts, inspect the **whole public call chain**: a statement about `_apply_notch` is not automatically true of `Conduit.notch_spell` and its post-call work. Old names such as `SpellCrafter`, generic `Configuration`, `MutationContract`, `get_mutation_research()`, and imagined public Spellbook index-mutation verbs are not a fallback API. [A], [C], [CONDUIT]

## 18. Evidence and verification boundary

Primary source documents are much larger than this guide: their pinned indices report **2,646 architecture lines** and **8,957 component lines**. This guide extracts operational material, not every internal class or historical patch narrative. Document integrity hashes and package archive hashes were **not independently rechecked**; no wheel/sdist was installed here. All Python fences were parsed for syntax on the available Python 3.13 interpreter; that does not check imports, runtime signatures, free-threading, disposal, permissions, or restore behavior. Treat assertions as checks to execute in an authorized disposable Python 3.14+ world.

Most recipes follow upstream example source. The exact parked-handle promotion pattern is explicitly identified as a new composition of public hooks and notching, not an upstream-tested end-to-end example. Before production use, test cold/warm resolution, lifetime reuse, refusal paths, hook publication failures, borrower behavior, cleanup, and complete replay under the installed build. Do not promote historical example headers saying “run green” into evidence that this review ran them.

**Reference key:** `[C: …]` means the named section in the component document; `[A]` is architecture. Section-qualified component links point to `[C]`; use the named heading inside it. All GitHub references are pinned to the reviewed commit; hosted `/latest/` and PyPI are moving publication surfaces.

[A]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/context_compass/system_docs/src_architecture.md
[C]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/context_compass/system_docs/src_components.md
[V]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/src/melder/__version__.py
[E]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/docs/catalog.toml
[CONDUIT]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/src/melder/aether/conduit/conduit.py
[COMMANDS]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/src/melder/nexus/rift/command_system/codegen_command_system.py
[ROOMS]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/docs/expert/agent-rooms.md
[BUILD]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/UX_and_AIX_experiences/04_expert/36_an_agent_builds_a_working_system.py
[NAMES]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/UX_and_AIX_experiences/01_beginner/24_same_class_many_names.py
[PERMISSIONS]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/UX_and_AIX_experiences/02_intermediate/22_permissions_create_vs_read.py
[PURGE]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/UX_and_AIX_experiences/02_intermediate/39_purge_unneeded_objects.py
[HOOKS]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/UX_and_AIX_experiences/02_intermediate/40_bind_lifecycle_hooks.py
[OVERRIDE]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/UX_and_AIX_experiences/03_advanced/01_deep_spell_override_paths.py
[CLUSTER]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/UX_and_AIX_experiences/02_intermediate/25_clusters_unique_per_cluster.py
[VIEWER]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/UX_and_AIX_experiences/03_advanced/13_the_frame_viewer_facade.py
[NOTCH]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/UX_and_AIX_experiences/04_expert/17_notch_swapping_a_live_object.py
[RESEARCH]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/UX_and_AIX_experiences/04_expert/03_research_sets_lanes_and_residency.py
[PERSIST]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/docs/expert/persistence.md
[RESTORE]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/docs/expert/restore.md
[CACHE]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/UX_and_AIX_experiences/03_advanced/18_loading_it_back.py
[NAMED]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/UX_and_AIX_experiences/04_expert/38_named_scopes_in_nexus_and_restore.py
[DOCS]: https://github.com/Synaptic724/melder/blob/9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9/UX_and_AIX_experiences/04_expert/18_the_package_reads_itself_to_you.py

Publication entry points: <https://pypi.org/project/melder/0.2.50/> · <https://melder.readthedocs.io/en/latest/>. For source development, consult the pinned repository's `CONTRIBUTING.md` rather than inventing test/build commands.
