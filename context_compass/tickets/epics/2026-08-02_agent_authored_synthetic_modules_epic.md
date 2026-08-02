# Epic: Agent-authored synthetic modules as a codegen output

## Metadata
- Epic ID: EPIC-2026-08-02-agent-authored-synthetic-modules
- Status: ready (filed at owner request; UNASSIGNED, no board row until claimed)
- Owner: cowork
- Agent Name: UNASSIGNED
- Priority: p2
- Created: 2026-08-02T15:43:51Z
- Updated: 2026-08-02T15:43:51Z
- Target Window: UNKNOWN
- Related Program/Initiative: crystallizer persistence + codegen creation system

## Problem / Opportunity

`SyntheticModule` CAN BE RESTORED BUT CANNOT BE AUTHORED.

The class is a complete, working, in-memory managed module. It subclasses
`ModuleType`, ships its own `importlib.abc.Loader` and `MetaPathFinder`,
publishes to `sys.modules`, seeds `linecache` so `inspect` and tracebacks
resolve, and exposes a full write surface:

- `update_source_text(...)`      `synthetic_module.py:738`
- `update_analysis(...)`         `:772`
- `merge_namespace(...)`         `:835`
- `execute_source()`             `:901`
- `publish_to_sys_modules()`     `:930`
- `register_in_import_registry()` `:977`
- `materialize(...)`             `:1047`
- `reload_via_importlib(...)`    `:1096`
- `create_package_shell(...)`    `:1152`

That is everything an authoring path needs. It is already built and already
hardened through the restore lane.

WHAT IS MISSING IS AN ORIGIN. Every way a `SyntheticModule` comes into
existence today traces back to a module that ALREADY EXISTED as user source:

1. The constructor demands crystal-derived identity (`synthetic_module.py:327-341`):

   ```python
   def __init__(
           self,
           module_name: str,
           spell_crystal_id: str,      # <- must already have a crystal
           source_text: str,
           source_sha256: str,         # <- recorded as supplied, not computed
           binding_signature: str,     # <- derived from a binding that exists
           ...
   ```

2. The only persistence write path is `synthetic_module_sources`, and that dict
   is populated by `CrystalAnalysisResult` during `analyze_spell_root` - i.e.
   HARVESTED from a live user module at bind time
   (`crystal_analysis_result.py:336`, read out at `spell_crystal.py:1116-1117`).

3. The only construction call site is the restore lane, rebuilding from that
   harvest (`restore_engine.py:2556-2578`).

4. Participation in the activity/parking loop is gated on a crystal declaring
   the root module kind (`crystallizer.py:1436`):

   ```python
   if crystal.root_module_kind != "synthetic_module":
       return
   ```

So the lifecycle is closed: user writes a module -> binding harvests it ->
crystal stores the source -> restore reconstitutes it. There is no entry point
for a module that never had a user file behind it.

MEANWHILE, CODEGEN - the one subsystem that actually manufactures code at
runtime - does not use `SyntheticModule` at all. Zero references in
`nexus/rift/codegen_system/` or `aether/spellbook/spell_compiler/`. Every
generated artifact is `exec`'d into a bare `dict`:

- `codegen_executor.py:111` - `exec(compiled_code, execution_namespace, execution_namespace)`
- `creation_runtime_door_compiler.py:375-383` - `local_namespace: dict[...] = {}`
- `solo_no_overrides_codegen_creation_compiler.py:56`
- `executor_factory_cache.py:149`

Those namespaces carry no `__name__`, so generated callables have no
`__module__`. And `codegen_compiler.py:98` compiles with the filename
`"<melder-codegen:{transaction_id}>"` - the ANGLE-BRACKET form that
`synthetic_module.py:450` explicitly warns against, in a comment describing the
deliberate choice of a "non-angle-bracket, never-stat-resolvable file identity"
so `linecache` behaves. `linecache` appears in exactly one file in the entire
package: `synthetic_module.py`.

The problem was therefore SOLVED ONCE, CORRECTLY, ON THE RESTORE PATH, and the
creation path independently re-implemented the broken version.

## The Capability This Epic Is Actually About

Not "make codegen emit modules" as a tidiness exercise. The owner's framing:

> an agent should be able to author a module - with real content, setters,
> getters, functions - have it become a `SyntheticModule`, register into the
> crystallizer by default, and be saved there.

That is a DIFFERENT capability from anything in the system today. Today an agent
in codegen mode can generate a creation door or an executor: a fragment, bound
to one spell, anonymous, unaddressable, and gone when the frame dies. It cannot
author a NAMED, ADDRESSABLE, PERSISTED UNIT OF CODE that other code can import
and that survives a checkpoint.

The gap in one sentence: MELDER CAN GENERATE CODE BUT CANNOT AUTHOR A MODULE.

## MRP Alignment

The reasonable core is an ORIGINATION PATH plus a PERSISTENCE IDENTITY, not a
new module system.

- `SyntheticModule` is not rewritten. It gains an authoring constructor or
  classmethod that computes `source_sha256` from `source_text` instead of
  demanding it, and accepts a generated identity where a `spell_crystal_id` is
  required today.
- The crystallizer gains a crystal kind (or an equivalent discriminator) for a
  module whose origin is GENERATED rather than HARVESTED, so
  `crystallizer.py:1436` and the custody strategies have something true to
  match on. `synthetic_custody_strategy.py:119` already classifies by
  `isinstance(module_obj, SyntheticModule)`, so custody may need no change -
  that must be confirmed, not assumed.
- Codegen gains one seam: a compile/exec path that targets a `SyntheticModule`
  namespace instead of a bare dict.

Anything less (e.g. minting modules without a persistence identity) forces a
rewrite the first time someone checkpoints a world containing one. Anything
more (user-module custody, module existence modes, injected globals) is
explicitly out - see Non-Goals.

## Ticket Contract
- ENTRY_GATE: owner activation and an assigned agent. Unassigned at filing.
- EXECUTION_BOUNDARY: `crystallizer/synthetic_module.py`, the crystallizer
  registration/persistence seam, and the codegen exec target. NO changes to
  user-module import behaviour. NO changes to `sys.modules` handling for
  modules Melder did not create.
- DEPENDENCIES: none blocking. Coupled to any in-flight work on
  `codegen_creation_system` compilers, since the exec seam is shared.
- EXIT_GATE: an agent can author a module with real members, it is importable
  by name, `inspect.getsource` returns its source, it survives a checkpoint /
  restore round trip, and its teardown leaves no `sys.modules` or `linecache`
  residue.
- FAILURE_ESCALATION: RAISE if generated-module naming can collide with user
  module names, or if per-spell granularity produces `sys.modules` growth that
  teardown does not reclaim.

## Goals
- An authoring entry point on `SyntheticModule` that does not require a
  pre-existing spell crystal.
- Codegen output lands in a `SyntheticModule` namespace instead of a bare dict.
- Generated modules register into the crystallizer by default and are captured
  by the existing checkpoint path.
- `inspect.getsource` and tracebacks resolve for generated code.
- A reserved namespace under which generated modules live, that can never
  shadow user modules.

## Non-Goals (explicit)
- NO custody or adoption of user-authored modules. The owner's position:
  friction with the default Python ecosystem is not worth managing; extending
  is smarter than substituting. This epic extends only.
- NO module-level existence modes (`many` / `unique_per_conduit` module state).
- NO injection of names into module globals at exec time.
- NO changes to how `bind` resolves or harvests user source.
- NOT a security boundary. Namespace control here is organizational. CPython
  offers no real sandbox and this epic must not be described as providing one.

## Scope Boundaries
- IN: `SyntheticModule` authoring surface, crystallizer registration for
  generated origin, codegen exec target, generated-module namespace policy,
  filename/linecache fix at `codegen_compiler.py:98`.
- OUT: user module custody, `importlib` extension beyond the finder/loader that
  `SyntheticModule` already ships, agent-facing authoring API design beyond
  what is needed to prove the path (that is a follow-on).

## Requirements
1. Authoring construction computes `source_sha256` from `source_text` rather
   than trusting a caller-supplied value. Restore keeps today's behaviour of
   recording as supplied - the two origins have different trust models and the
   difference must be explicit.
2. Generated modules carry an origin discriminator distinguishing GENERATED
   from HARVESTED, readable from the crystal.
3. Generated module names live under a reserved prefix. The prefix is chosen
   BEFORE any crystal records a generated module name - it is unchangeable
   afterward without a migration.
4. Teardown reclaims `sys.modules` and `linecache` entries. `cleanup()` already
   does both (`:503`, `:928`, `:975`); the requirement is that every creation
   path is wired to a teardown that calls it.
5. Round trip: author -> checkpoint -> fresh process -> restore -> the module
   is importable and its members behave identically.

## Success Metrics / Acceptance Criteria
- An agent-authored module containing at least one class with a property
  getter/setter, one module-level function, and module-level state can be
  created at runtime, imported by name, and used.
- `inspect.getsource` on a member of a generated module returns real source.
- A traceback raised inside generated code shows source lines, not
  `<melder-codegen:...>` with no body.
- The module appears in a checkpoint without bespoke serialization work and
  restores in a fresh process.
- After frame teardown, the generated module name is absent from `sys.modules`
  and its file identity is absent from `linecache.cache`.
- A live-built world and a restore-built world expose the SAME introspection
  surface for generated code. (Today the restored one is richer, which is
  backwards.)

## Milestones
- [ ] M1 - Authoring constructor lands; a `SyntheticModule` can be built from
      source text alone, with no crystal, and executed.
- [ ] M2 - Namespace policy decided and recorded; reserved prefix fixed.
- [ ] M3 - Codegen exec seam retargeted from bare dict to module namespace for
      ONE strategy (solo is the smallest surface), filename fixed.
- [ ] M4 - Generated origin registers into the crystallizer and is captured by
      an automatic checkpoint.
- [ ] M5 - Round trip proven in a fresh process.
- [ ] M6 - Teardown residue check green; granularity decision recorded.

## Stories
- STORY-AASM-01 - Authoring surface on `SyntheticModule` (M1).
- STORY-AASM-02 - Generated-module namespace policy and collision guard (M2).
- STORY-AASM-03 - Retarget one codegen exec path to a module namespace (M3).
- STORY-AASM-04 - Generated origin discriminator + crystallizer registration (M4).
- STORY-AASM-05 - Checkpoint / restore round trip for generated modules (M5).
- STORY-AASM-06 - Teardown residue and granularity decision (M6).

## Epic-level Tasks
- [ ] Complete story STORY-AASM-01
- [ ] Complete story STORY-AASM-02
- [ ] Complete story STORY-AASM-03
- [ ] Complete story STORY-AASM-04
- [ ] Complete story STORY-AASM-05
- [ ] Complete story STORY-AASM-06

## Risks / Mitigations
- RISK: generated module names collide with or shadow user modules.
  MITIGATION: reserved prefix decided at M2, before any crystal records a name.
- RISK: `sys.modules` growth. One synthetic module per generated door in a large
  world is a lot of process-global entries, released only if `cleanup()` runs.
  A missed frame teardown becomes a permanent leak in a dict Melder does not own.
  MITIGATION: M6 decides granularity. Per-frame or per-strategy is the safer
  default; per-spell should be opt-in, not the starting point.
- RISK: scope creep into user-module custody. The design conversation that
  produced this epic explored custody and the owner explicitly rejected it.
  MITIGATION: Non-Goals are binding; custody is a separate epic if ever wanted.
- RISK: treating the reserved namespace as a security boundary.
  MITIGATION: stated as a Non-Goal; any doc that implies isolation is a defect.
- RISK: re-executing a generated module's source mints new class objects while
  live instances keep the old ones. MITIGATION: same law as settle-then-inherit -
  source is mutable until creations exist, then mutation is a rebuild, not an
  edit. Must be written down at the authoring surface.

## Applicable Anti-Patterns
- [ ] No adopting, shadowing, or rewriting user-authored modules.
- [ ] No describing the reserved namespace as a sandbox or security boundary.
- [ ] No shipping an authoring path without a teardown that reclaims
      `sys.modules` and `linecache`.
- [ ] No trusting a caller-supplied `source_sha256` on the authoring path.
- [ ] No assuming the custody strategies work unchanged - confirm against
      `synthetic_custody_strategy.py:119` rather than reasoning about it.

## Validation / Test Approach
Not run - filing stage. Planned:
- Unit: authoring construction, sha256 computation, execute, cleanup residue.
- Component: codegen path producing a module for one strategy.
- Integration: checkpoint / restore round trip in a fresh interpreter.
- Introspection: `inspect.getsource` and a deliberately raised traceback.

## Open Questions
- Does `synthetic_custody_strategy` work unchanged for a generated origin, or
  does `harvest_payload` assume harvested provenance?
  (`crystal_analysis/custody/synthetic_custody_strategy.py:155-206`)
- Is `root_module_kind` the right discriminator to extend, or does a generated
  module need its own crystal kind entirely? (`crystallizer.py:1436`)
- Does the R11 reverse-edge parking law (`crystallizer.py:1445-1458`) apply to
  generated modules, or are they always safe to unpublish?
- What is the agent-facing surface? A spellbook method, a codegen API, or a
  rift capability? Deliberately deferred - the path must exist before the
  ergonomics are designed.
- Should generated modules be materializable to disk by default, or only on
  request? `materialize()` exists; the policy does not.

## Decision Log
- 2026-08-02: Filed at owner request following a design discussion that started
  from "should Melder support module registration / extend importlib".
- 2026-08-02: DECISION (owner) - NO user-module custody or substitution.
  Rationale: friction with the default Python ecosystem is not worth managing;
  extending code beats substitution unless there is a clear win understandable
  by everyone with minimal tradeoffs, and custody is not that. Extending codegen
  to support synthetic modules and giving agents the ability to use it is the
  chosen direction.

## Notes
- DATETIME: 2026-08-02T15:43:51Z
  TYPE: FACT
  CLAIM: `SyntheticModule` can be restored but not authored. Its constructor
    requires `spell_crystal_id`, `source_sha256`, and `binding_signature` - all
    derived from a spell that already exists. Its only construction call site is
    the restore lane, and its only persistence write path is
    `synthetic_module_sources`, harvested from live user modules at bind time.
  EVIDENCE:
  - src/melder/crystallizer/synthetic_module.py:327-341
  - src/melder/crystallizer/crystal_analysis/crystal_analysis_result.py:336
  - src/melder/crystallizer/crystals/spell_crystal.py:1116-1117
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2556-2578
  - src/melder/crystallizer/crystallizer.py:1436
  IMPACT: There is no origin for a module that never had a user file behind it.
    An agent cannot author a named, addressable, persisted unit of code.
  NEXT: STORY-AASM-01 - authoring construction that computes its own sha256.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-08-02T15:43:51Z
  TYPE: FACT
  CLAIM: Codegen never mints a module. Zero `SyntheticModule` references in
    `nexus/rift/codegen_system/` or `aether/spellbook/spell_compiler/`. Every
    generated artifact is `exec`'d into a bare dict carrying no `__name__`, so
    generated callables have no `__module__`.
  EVIDENCE:
  - src/melder/nexus/rift/codegen_system/execution/codegen_executor.py:111
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:375-383
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:56
  - src/melder/aether/spellbook/spell_compiler/executor_factory_cache.py:149
  IMPACT: Generated code is anonymous and unaddressable. It is the one class of
    code in the system Melder fully owns, and it is the one class of code
    nothing can introspect.
  NEXT: STORY-AASM-03 - retarget one exec path (solo is smallest).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-08-02T15:43:51Z
  TYPE: FACT
  CLAIM: The generated-code filename problem was solved once and then
    re-broken. `codegen_compiler.py:98` compiles with
    `"<melder-codegen:{transaction_id}>"`, the angle-bracket form that
    `synthetic_module.py:450` explicitly avoids in a comment describing a
    deliberate "non-angle-bracket, never-stat-resolvable file identity" chosen
    so `linecache` resolves. `linecache` appears in exactly one file in the
    package.
  EVIDENCE:
  - src/melder/nexus/rift/codegen_system/execution/codegen_compiler.py:98
  - src/melder/crystallizer/synthetic_module.py:450
  - src/melder/crystallizer/synthetic_module.py:122,503,928,975
  IMPACT: Tracebacks through generated code show a filename nothing can resolve
    and no source lines. A live-built world and a restore-built world therefore
    have DIFFERENT debug surfaces, and the restored one is better - backwards.
  NEXT: Fix as part of STORY-AASM-03; it is close to a one-line change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-08-02T15:43:51Z
  TYPE: DECISION
  CLAIM: User-module custody is rejected. Melder will not adopt, shadow, or
    rewrite modules it did not create.
  EVIDENCE: owner statement, 2026-08-02 - extending code beats substitution
    absent a clear win with minimal tradeoffs; ecosystem friction is not worth
    managing.
  IMPACT: Removes the entire hazard class that made the broader idea risky -
    `isinstance` breakage, stale class references, `sys.modules` shadowing that
    does not reach through existing references. All of those derive from
    PRE-EXISTING IDENTITY. Generated code has none, so the remaining scope is
    greenfield.
  NEXT: Non-Goals are binding for this epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-08-02T15:43:51Z
  TYPE: RISK
  CLAIM: Per-spell module granularity could grow `sys.modules` without bound in
    a large world, since entries are released only when `cleanup()` runs.
  EVIDENCE:
  - src/melder/crystallizer/synthetic_module.py:951 (unpublish)
  - src/melder/crystallizer/crystallizer.py:1445-1458 (R11 parking law)
  IMPACT: A missed frame teardown becomes a permanent leak in a process-global
    dict Melder does not own. This is the decision most expensive to reverse.
  NEXT: M6 - decide granularity. Per-frame or per-strategy default, per-spell
    opt-in.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-08-02T15:43:51Z
  TYPE: UNKNOWN
  CLAIM: Whether the existing custody strategies handle a generated origin
    unchanged. `synthetic_custody_strategy` classifies by `isinstance`, which
    would pass - but `harvest_payload` may assume harvested provenance.
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/custody/synthetic_custody_strategy.py:119
  - src/melder/crystallizer/crystal_analysis/custody/synthetic_custody_strategy.py:155-206
  IMPACT: If custody works unchanged, M4 is small. If it does not, generated
    origin needs its own custody class and M4 grows.
  NEXT: Read `harvest_payload` before scoping STORY-AASM-04.
  REREAD: REQUIRED
  SCORE_0_TO_10: 6

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Artifact Links (Optional)
None at filing.

## Context / Handoff Summary

Filed unassigned at owner request. No board row until claimed.

The one-line version: `SyntheticModule` IS A RESTORE ARTIFACT, NOT AN AUTHORING
PRIMITIVE. Everything needed to author with it already exists on the class -
`update_source_text`, `execute_source`, `merge_namespace`, `materialize`,
`register_in_import_registry`. What does not exist is a way to make one that
was not harvested from a user module first, because the constructor demands a
`spell_crystal_id` and the persistence path only fills from
`analyze_spell_root`.

Meanwhile codegen - the subsystem that actually manufactures code - never uses
the class at all, and `exec`s into bare dicts. So the system's own generated
code is the least introspectable code in it, which is exactly backwards.

Do NOT open this by designing an agent-facing API. The ergonomics are the last
question, not the first. Prove the path end to end on the smallest strategy
(solo), with a real checkpoint round trip, then design the surface.

Two decisions are expensive to reverse and should be made early: the reserved
namespace prefix (before any crystal records a generated module name) and the
granularity (before teardown wiring is spread across every creation path).

Custody of user modules is OUT and was explicitly rejected by the owner. If a
future reader finds that idea attractive, the reasoning against it is in the
Decision Log - the short form is that every hazard in it comes from
pre-existing identity, and this epic deliberately stays in greenfield.
