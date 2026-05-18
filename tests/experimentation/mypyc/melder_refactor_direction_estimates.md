# Melder Architecture Refactor Direction and Estimates

Date: 2026-05-18

This is a push plan for reducing architectural cycles in `src/melder` so the runtime becomes closer to a tree and more friendly to mypyc-style compiled islands.

The estimates below are directional. They are based on the architecture graph and docs, not a full AST import audit. Assume one developer, decent tests, and no major behavior redesign. If the affected areas are poorly covered by tests, multiply the time estimates by roughly **1.5x to 3x**.

---

## 1. Current read

The good news: the ownership/lifecycle graph is basically recoverable. The hard ownership graph is acyclic. The bad news: the borrowed/back-reference layer creates architectural cycles that are likely showing up as import and typing pressure.

Observed cycle state from the graph analysis:

| Metric | Value |
|---|---:|
| Nodes analyzed | 300 |
| Directed architecture edges | 380 |
| Strongly connected components, all edges | 4 |
| Largest SCC | 15 nodes |
| Simple directed cycles | 43 |
| Pure hard/lifecycle ownership graph | acyclic |

The root architectural problem is not that the runtime has object backrefs. Some runtime backrefs are normal. The problem is that backrefs are often **concrete upward references** to owners, roots, registries, or managers.

The main cycle clusters are:

| Priority | Cluster | Current shape | Direction |
|---:|---|---|---|
| P0 | Core runtime substrate | `Aether`, `AethericFrame`, `Conduit`, `Meld`, `Spellbook`, `Spell`, `SpellIndex`, `SpellCrafter`, `Nexus`, `Rift`, mutation research | Split owner construction from child service access. Replace concrete upward refs with IDs, narrow service protocols, weak refs, or event sinks. |
| P1 | ACL builder loop | `FrameACLContainer -> FrameACLBuilder -> FrameACLContainer` | Builder should produce drafts/commands; container should install. |
| P1 | Room command loop | `RiftSpace -> CommandSystem -> RiftSpace` | Command system should depend on room context/services, not concrete `RiftSpace`. |
| P1 | Viewer helper loop | `FrameViewer -> ViewMultiFrame -> FrameViewer` | Make `ViewMultiFrame` stateless or depend on a narrow provider. |

---

## 2. North-star direction

The target shape should be:

```text
Aether
  -> AethericFrame
       -> frame registries
       -> frame services
       -> DevOps / SpellSystemStates
       -> Conduit
            -> Meld
            -> Creations
            -> ConduitWard

Spellbook
  -> Bind
  -> SpellRegistry / SpellResolutionIndex
  -> Spell records
  -> SpellCrafter / validation pipeline
  -> Conduit creation request

Nexus
  -> FrameDescriptorManager
  -> FrameACLManager
  -> Rift
       -> RiftSpace
            -> FrameViewer
            -> Workstation
            -> CommandSystem
```

The important rule is not “never have backrefs.” The rule is:

```text
Concrete downward reference: okay.
Concrete sideways reference: suspicious.
Concrete upward/root reference: refactor target.
ID / Protocol / event sink upward reference: usually okay.
```

A good end state is where owner/root classes can construct children, but children do not import or hold concrete owners.

---

## 3. Estimate legend

| Size | Meaning | Typical effort |
|---|---|---:|
| XS | Local mechanical change | 0.5 day |
| S | Small interface split plus tests | 1-2 days |
| M | Several files, some behavior risk | 3-5 days |
| L | Major subsystem boundary | 1-2 weeks |
| XL | Multi-subsystem package split | 3-5 weeks |

Overall estimate:

| Goal | Estimate |
|---|---:|
| Remove the obvious 2-node architectural cycles | 3-5 days |
| Collapse the main 15-node SCC into small local islands | 2-4 weeks |
| Make a clean mypyc-friendly compiled-core package split | 6-10 weeks |

The 6-10 week number is not because the graph is impossible. It is because behavior-preserving refactors around lifecycle, cleanup, lazy validation, and AR projection surfaces need tests and incremental PRs.

---

## 4. Simulated cut impact

This is a graph-level simulation: “what happens if these architectural backrefs are cut?” It does not prove source imports disappear, but it gives a useful priority order.

| Cut set applied | SCC count left | Max SCC size | Notes |
|---|---:|---:|---|
| Current graph | 4 | 15 | Baseline. |
| Cut leaf cycles: `FrameACLBuilder -> FrameACLContainer`, `CommandSystem -> RiftSpace`, `ViewMultiFrame -> FrameViewer` | 1 | 15 | Easy win: removes the small SCCs, leaves only core runtime. |
| Also cut `Nexus -> Aether`, `Rift -> Nexus` | 1 | 13 | AR layer detaches from substrate/root concrete refs. |
| Also cut `Research -> SpellIndex`, `SpellIndex -> Spellbook`, `SpellIndex -> Spell` | 1 | 10 | Lineage records stop mutating owners. |
| Also cut `Meld -> Spellbook` | 2 | 6 | Big break: resolution runtime no longer imports the public binding root. |
| Also cut `Spell -> Spellbook`, `Spell -> Conduit` | 3 | 3 | Core SCC collapses into small helper loops. |
| Also cut `Conduit -> Aether` | 2 | 3 | Runtime execution no longer depends on global substrate concrete. |
| Also cut helper backrefs: `SpellCrafter -> Spell`, `Scan -> Spellbook`, `SpellbookCreationSystem -> Spellbook`, `SpellbookCreationSystem -> Spell` | 0 | 0 | Architecture graph becomes acyclic. |

The key observation: do **not** start by trying to remove `Spellbook -> Aether` or `Spellbook -> Nexus`. Those are root-to-root orchestration edges. The first real wins come from cutting child-to-parent and record-to-owner edges.

---

## 5. Refactor phases

### Phase 0: Guardrails before surgery

Estimate: **S, 1-2 days**

Add a cheap architecture check before changing behavior.

Deliverables:

- A script that loads the graph and prints SCCs, sorted by size.
- A banned-edge list for concrete upward dependencies.
- A rule that distinguishes “allowed runtime reference” from “allowed import.”
- A small README explaining the intended package/layer direction.

Suggested forbidden concrete imports for compiled-core modules:

```text
child/runtime -> Aether
child/runtime -> Spellbook
record/model   -> Spellbook
record/model   -> Conduit
helper/builder -> owning container
RiftSpace child -> RiftSpace concrete
Rift child      -> Nexus concrete
Nexus child     -> Aether concrete
```

Keep this intentionally simple at first. The goal is to prevent new cycles while you cut existing ones.

---

### Phase 1: Kill the three small SCCs first

Estimate: **S/M, 3-5 days total**

These are good first PRs because they are local and prove the new design style.

#### 1. `FrameACLBuilder -> FrameACLContainer`

Estimate: **S, 1 day**

Current smell:

```text
FrameACLContainer owns FrameACLBuilder.
FrameACLBuilder borrows FrameACLContainer to install changes.
```

Direction:

```python
class ACLInstallSink(Protocol):
    def install_acl_draft(self, draft: FrameACLDraft) -> FrameACLConfiguration: ...
```

`FrameACLBuilder` should own draft state only. It should emit a draft or call a tiny install sink. It should not import or know the concrete container.

Better shape:

```text
FrameACLContainer
  -> FrameACLBuilder
       -> FrameACLDraft
       -> ACLInstallSink protocol
```

#### 2. `CommandSystem -> RiftSpace`

Estimate: **M, 2-3 days**

Current smell:

```text
RiftSpace owns CommandSystem.
CommandSystem borrows RiftSpace for room posture and supporting systems.
```

Direction:

```python
class RiftSpaceContext(Protocol):
    @property
    def space_id(self) -> str: ...
    @property
    def space_kind(self) -> str: ...
    @property
    def viewer(self) -> FrameViewer: ...
    @property
    def workstation(self) -> Workstation: ...
    def publish_memory(self, action_name: str, payload: Mapping[str, object]) -> None: ...
```

Keep the protocol narrow. Do not make `IRiftSpace` with every room method. That just recreates the cycle under a nicer name.

#### 3. `ViewMultiFrame -> FrameViewer`

Estimate: **XS/S, 0.5-1 day**

Current smell:

```text
FrameViewer owns ViewMultiFrame.
ViewMultiFrame borrows FrameViewer.
```

Direction:

- Make `ViewMultiFrame` stateless and pass the viewer/provider at method-call time, or
- Give it a `FrameViewProvider` protocol with only the descriptor/projection methods it needs.

This should be a quick confidence-building refactor.

---

### Phase 2: Stop lineage records from mutating owner registries

Estimate: **M/L, 4-8 days**

Target edges:

```text
Research -> SpellIndex
SpellIndex -> Spellbook
SpellIndex -> Spell
Spellbook -> SpellIndex
Spell -> SpellIndex
```

Do not try to make `SpellIndex` smarter. Make it dumber.

Current smell:

```text
SpellIndex stores owner and contract Spellbook attachments so version changes can update owner maps.
```

Direction:

```text
SpellIndex = stable lineage identity + current version pointer.
Spellbook/LineageRegistry = owner of maps and publication/update behavior.
Research = stores lineage id, not live SpellIndex object.
```

Suggested model:

```python
@dataclass(frozen=True)
class SpellLineageRef:
    index_id: str
    root_version_id: str | None = None
```

Suggested service:

```python
class LineageRegistry(Protocol):
    def current_spell_id_for_index(self, index_id: str) -> str | None: ...
    def update_current_spell_id(self, index_id: str, spell_id: str) -> None: ...
```

Expected result:

- `SpellIndex` becomes more like a value/record object.
- `Research` can live outside the core runtime SCC.
- Version propagation moves to `Spellbook` or `SpellSystemStates`, where registry mutation belongs.

Risk:

- Medium. Version-pointer behavior can be subtle.
- Add tests around rebinding, contracted spellbooks, and current-version lookup before this change.

---

### Phase 3: Replace `Meld -> Spellbook` with a resolution index

Estimate: **M, 3-5 days**

Target edge:

```text
Meld -> Spellbook
```

This is one of the most valuable cuts. `Meld` should not know about the full public binding/conjure root. It needs spell lookup and resolution metadata.

Direction:

```python
class SpellResolver(Protocol):
    def resolve_by_spell_id(self, spell_id: str) -> SpellRuntimeRecord: ...
    def resolve_by_lookup_key(self, frame_key: str, binding_key: str) -> SpellRuntimeRecord: ...
    def resolve_by_spell_name(self, spell_name: str, binding_name: str | None = None) -> SpellRuntimeRecord: ...
```

Better still, create an explicit concrete object:

```text
Spellbook
  -> SpellResolutionIndex
       -> local spell maps
       -> contracted spell maps
       -> lookup-key normalization

Meld
  -> SpellResolver protocol / SpellResolutionIndex
```

What not to do:

```python
class ISpellbook(Protocol):
    # 80 methods copied from Spellbook
    ...
```

That would technically remove an import but preserve the bad dependency. The protocol must be smaller than the thing it replaces.

Risk:

- Medium.
- The lookup path is central to `Conduit.meld`, live-creation probes, contracted spells, and lazy validation.

Payoff:

- This cut should break the biggest practical import dependency in the execution path.
- It opens `Meld`, `CreationContext`, and execution-plan modules as mypyc candidates later.

---

### Phase 4: Stop `Spell` from knowing concrete `Spellbook` and `Conduit`

Estimate: **L, 1-2 weeks**

Target edges:

```text
Spell -> Spellbook
Spell -> Conduit
SpellCrafter -> Spell
```

This is probably the hardest core refactor because `Spell` currently acts like both a record and a runtime participant.

Direction:

Split `Spell` into three conceptual responsibilities:

```text
SpellRecord
  - identity
  - binding metadata
  - existence/permissions
  - stable lineage ref

SpellBuildState
  - validation artifacts
  - crafter-owned artifacts
  - phase status

SpellRuntimeBinding
  - owner_conduit_id
  - owner_creations_id
  - runtime hooks
  - publication/gating service refs
```

You do not have to fully split files immediately. Start by moving concrete owner interactions behind services:

```python
class SpellOwnerServices(Protocol):
    def mark_structure_changed(self, spell_id: str) -> None: ...
    def publish_spell_change(self, spell_id: str) -> None: ...
    def run_resolution_phases_for_target_spell(self, conduit_id: str, spell_id: str) -> None: ...
```

For conduit ownership, prefer IDs and services:

```python
@dataclass(frozen=True)
class SpellRuntimeOwner:
    conduit_id: str
    creations_id: str | None = None
```

Risk:

- High.
- This touches lazy validation, ownership transfer, creation context factory wiring, and publication.

Recommended tactic:

- First replace fields with narrower aliases/services while keeping behavior.
- Then move methods.
- Then remove imports.

Do not try to rewrite `Spell` in one PR.

---

### Phase 5: Replace `Conduit -> Aether` with frame services

Estimate: **L, 1 week**

Target edge:

```text
Conduit -> Aether
```

Current smell:

```text
Conduit uses global Aether substrate for frame, registry, and cloud interactions.
```

Direction:

`Conduit` should receive a frame-local service object. The service may be implemented by Aether/AethericFrame, but `Conduit` should not import the global singleton.

Suggested service:

```python
class FrameRuntimeServices(Protocol):
    @property
    def frame_name(self) -> str: ...
    def register_conduit(self, conduit_id: str, handle: object) -> None: ...
    def unregister_conduit(self, conduit_id: str) -> None: ...
    def get_change_control(self) -> ChangeControlReader: ...
    def get_creation_gate_controller(self) -> CreationGateController: ...
    def get_conduit_cloud(self) -> ConduitCloudHandle: ...
```

Better shape:

```text
Aether / AethericFrame
  -> FrameRuntimeServices
       -> Conduit
```

Risk:

- Medium/high.
- Registration, cleanup, cloud, cluster, and gates are involved.

Payoff:

- Removes a global singleton dependency from the execution scope.
- Makes `Conduit` much more testable.
- Helps compiled/runtime package separation.

---

### Phase 6: Clean the AR substrate boundary

Estimate: **M/L, 5-10 days**

Target edges:

```text
Nexus -> Aether
Rift -> Nexus
Spellbook -> Nexus
```

These are less urgent than `Meld -> Spellbook`, but they matter for package layering.

Direction:

```text
Nexus -> AetherFrameProvider, not Aether
Rift -> NexusPolicyProvider / ProjectionProvider, not Nexus
Spellbook -> DescriptorPublisher, not Nexus
```

Suggested seams:

```python
class AetherFrameProvider(Protocol):
    def ensure_frame(self, frame_name: str) -> FrameHandle: ...
    def get_frame_descriptor_source(self, frame_name: str) -> object: ...

class RiftProjectionProvider(Protocol):
    def create_projection_sets_for_rift(self, rift_id: str, frame_names: Iterable[str]) -> Mapping[str, object]: ...

class DescriptorPublisher(Protocol):
    def publish_conduit(self, conduit_id: str) -> None: ...
    def publish_spell(self, spell_id: str) -> None: ...
```

Risk:

- Medium.
- AR behavior has a lot of policy and refresh coordination.

Recommended tactic:

- Do not move Nexus/Rift behavior yet.
- First introduce provider fields and route existing calls through them.
- Then remove concrete imports.

---

### Phase 7: Clean helper/backref orchestration objects

Estimate: **M, 3-7 days**

Target edges:

```text
SpellbookCreationSystem -> Spellbook
SpellbookCreationSystem -> Spell
Scan -> Spellbook
SpellCrafter -> Spell
```

Direction:

- `SpellbookCreationSystem` should accept a `SpellbookBuildContext`, not the full spellbook.
- `Scan` should emit discovered bind commands, not bind directly through a concrete spellbook.
- `SpellCrafter` should write to a `SpellBuildTarget` or return build artifacts that `Spell` installs.

Suggested build target:

```python
class SpellBuildTarget(Protocol):
    @property
    def spell_id(self) -> str: ...
    @property
    def lineage_id(self) -> str: ...
    def install_requirements(self, requirements: object) -> None: ...
    def install_execution_plan(self, plan: object) -> None: ...
```

This is a good later phase because it is easier after `Spell` has been partially split.

---

## 6. Concrete cut-edge backlog

| Edge | Priority | Estimate | Preferred replacement |
|---|---:|---:|---|
| `FrameACLBuilder -> FrameACLContainer` | P1 | 1 day | `ACLInstallSink`, draft object |
| `CommandSystem -> RiftSpace` | P1 | 2-3 days | `RiftSpaceContext` |
| `ViewMultiFrame -> FrameViewer` | P1 | 0.5-1 day | `FrameViewProvider` or stateless helper |
| `Research -> SpellIndex` | P2 | 1-2 days | `SpellLineageRef(index_id)` |
| `SpellIndex -> Spellbook` | P2 | 2-4 days | `LineageRegistry` owned by Spellbook/SpellSystemStates |
| `SpellIndex -> Spell` | P2 | 1-3 days | `current_spell_id`, not live object |
| `Meld -> Spellbook` | P3 | 3-5 days | `SpellResolver` / `SpellResolutionIndex` |
| `Spell -> Spellbook` | P4 | 4-8 days | `SpellOwnerServices` |
| `Spell -> Conduit` | P4 | 3-6 days | `SpellRuntimeOwner`, `conduit_id`, `creations_id` |
| `Conduit -> Aether` | P5 | 4-8 days | `FrameRuntimeServices` |
| `Nexus -> Aether` | P6 | 3-6 days | `AetherFrameProvider` |
| `Rift -> Nexus` | P6 | 2-5 days | `NexusPolicyProvider`, `RiftProjectionProvider` |
| `Spellbook -> Nexus` | P6 | 2-4 days | `DescriptorPublisher` |
| `SpellCrafter -> Spell` | P7 | 3-7 days | `SpellBuildTarget` or returned artifacts |
| `Scan -> Spellbook` | P7 | 1-2 days | bind command list / registration callback |
| `SpellbookCreationSystem -> Spellbook` | P7 | 2-4 days | `SpellbookBuildContext` |

---

## 7. Mypyc direction

Do not try to compile the roots first.

Bad first compile targets:

```text
Aether
Spellbook
Conduit
Nexus
Rift
RiftSpace
```

These are orchestration roots and lifecycle owners. They currently sit near the cycle pressure.

Better early compile islands:

```text
utilities / synchronization primitives
value objects and enums
DAG and targeting structures
blueprints and execution-plan payloads
validation issue/result/diagnostic objects
SpellMap / SpellContract / MutationContract descriptors
CreationContext executor-support code, after Meld is decoupled
```

Recommended compile strategy:

1. Make value/model/algorithm modules import only downward.
2. Compile those modules first.
3. Leave root orchestration interpreted until the dependency seams are stable.
4. Move `Meld` and `CreationContext` toward compiled status after `Meld -> Spellbook` is gone.
5. Move `Conduit` later, after `Conduit -> Aether` is gone.

A useful rule:

```text
If a module imports Aether, Spellbook, Nexus, RiftSpace, or FrameACLContainer,
it is probably not a good first mypyc target.
```

---

## 8. Forward reference policy

Forward refs and `TYPE_CHECKING` imports are allowed as short-term tourniquets, not as final architecture.

Allowed:

```text
TYPE_CHECKING imports for value objects, DTOs, immutable records, small protocols.
```

Suspicious:

```text
TYPE_CHECKING imports for owners, roots, managers, registries, builders, systems.
```

Forbidden in compiled-core modules:

```text
Concrete upward references to Aether, Spellbook, Nexus, RiftSpace,
FrameACLContainer, or similar owner/root classes.
```

Smell test:

```text
If the annotation points to a parent/root/manager, the type hint is probably hiding an architecture problem.
```

---

## 9. What not to do

Avoid these traps:

1. **Do not create giant protocols.**  
   `ISpellbook` with every method from `Spellbook` is just `Spellbook` with a fake mustache.

2. **Do not move everything into `interfaces.py`.**  
   Protocols should live near the consumer or in small boundary modules. A giant interface module can become a new global dependency hub.

3. **Do not replace parent refs with a service locator.**  
   `services.get("spellbook")` is worse than an explicit dependency.

4. **Do not over-event the system immediately.**  
   Events are useful for publication and invalidation, but overusing them for ordinary synchronous queries will make the runtime harder to reason about.

5. **Do not start with the hardest root split.**  
   Start with local SCCs and resolution/lineage boundaries. Leave full root package moves until the graph is already calmer.

---

## 10. Suggested first 10 PRs

1. **Add architecture SCC check.**  
   No behavior change. Print SCCs and highest-impact backrefs.

2. **Cut `ViewMultiFrame -> FrameViewer`.**  
   Make it stateless or provider-based.

3. **Cut `FrameACLBuilder -> FrameACLContainer`.**  
   Introduce `ACLInstallSink` and/or `FrameACLDraft`.

4. **Cut `CommandSystem -> RiftSpace`.**  
   Introduce `RiftSpaceContext` with only the methods the command layer actually needs.

5. **Change `Research` to store lineage ids.**  
   Replace live `SpellIndex` storage with `SpellLineageRef`.

6. **Move owner-map update behavior out of `SpellIndex`.**  
   `SpellIndex` should stop knowing owner/contract spellbooks.

7. **Create `SpellResolutionIndex`.**  
   Move local/contracted lookup behavior out of the full `Spellbook` surface.

8. **Point `Meld` at `SpellResolver`.**  
   Remove direct concrete `Spellbook` dependency from resolution runtime.

9. **Introduce `SpellOwnerServices` and `SpellRuntimeOwner`.**  
   Start removing concrete `Spell -> Spellbook` and `Spell -> Conduit` coupling.

10. **Introduce `FrameRuntimeServices` for `Conduit`.**  
    Begin routing Aether/frame/cloud/gate/change-control access through a frame-local service boundary.

After PR 8, reassess the graph. The biggest SCC should already be substantially smaller.

---

## 11. Acceptance metrics

Use these as stop/go checks.

Architecture metrics:

```text
All-edge SCC count trends down after each phase.
No 2-node parent/child cycles remain.
No record/model object imports concrete owner/root classes.
No builder/helper imports its owning container unless explicitly documented.
```

Mypyc/readiness metrics:

```text
Pure value/model modules compile independently.
DAG/blueprint/validation modules have no root imports.
Meld does not import Spellbook.
Conduit does not import Aether.
Compiled target modules do not require TYPE_CHECKING imports of roots/managers.
```

Behavior metrics:

```text
Conjure pipeline still passes.
Meld resolution by spell id, spell name, spell object, spellframe, and binding name still passes.
Contracted spell lookup still passes.
Lazy validation still passes.
Cleanup remains idempotent.
Rift projection refresh still passes.
ACL family revision flow still passes.
```

---

## 12. My opinionated recommendation

Start with the small SCCs, but do not spend too long there. They are morale wins and style proofs.

The first major architectural push should be:

```text
SpellIndex becomes dumb.
Meld stops knowing Spellbook.
Spell stops knowing concrete Spellbook/Conduit.
Conduit stops knowing Aether.
```

That sequence attacks the actual core runtime knot without forcing a rewrite of the public API.

The guiding principle:

```text
Roots own.
Children request capabilities.
Records hold ids.
Builders emit drafts.
Runtime execution depends on narrow services, not public orchestration roots.
```
