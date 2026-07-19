
- Completed: 2026-07-12T11:45:00Z
- Summary: Owner-directed turn-in on the green tree run. The loop is CLOSED:
  codegen -> materialize_codegen (M5) -> bind (M4, custody) -> crystal ->
  restore, with M1 introspection (getsource/traceback/pdb on synthetics),
  load_order-driven unfold, and R11 reverse-edge unseed all landed by
  mutation_0 (patches persistence_loop_m1_m5_residue_2026_07_12 +
  persistence_loop_load_order_r11_2026_07_12; one pre-existing advertisement
  contract test updated). PARKED RESIDUE: M8 production callsign/version-store
  wiring (awaits owner alias-semantics ruling) - probe-proven, unbuilt; plus
  the graph promotion debt and the deferred attention-board sync.
# Epic: Agent Object-Persistence Loop (codegen -> synthmodule -> bind -> crystal -> restore)

## Metadata
- Epic ID: EPIC-2026-07-02-agent-object-persistence-loop
- Status: done (owner-directed turn-in 2026-07-12; was: REACTIVATED 2026-07-11T22:05:00Z, melder_0 - owner
  correction: this is mine and stays on the active program. FIRST MOVE
  on open: re-derive the M1-M7 residue from SOURCE against what shipped
  since (M3 synthetic restore, S2 custody, graft lane, shared
  user_world_rebuild) - expected residue is the M1 introspection polish
  (getsource/linecache fixes B/C) and load_order-driven loader-chain
  depth; everything else looks delivered but must be proven, not
  assumed.)
- Park history: PARKED to backlog 2026-07-11T19:05:00Z (no story
  activated; canonical context = the three retained artifacts on
  artifact_board).
- Owner: cowork
- Agent Name: mutation_0 (owner-directed transfer 2026-07-12: mutation_0 owns ALL lanes; was melder_0 2026-07-05)
- Priority: p2
- Created: 2026-07-02T22:01:20Z
- Updated: 2026-07-11T19:05:00Z
- Target Window: 2026-Q3
- Related Program/Initiative: Crystallizer + MutationResearch (combined lane)

## Problem / Opportunity
An agent that builds a code object in the Nexus codegen room cannot yet SAVE it
as a durable, versioned, restorable runtime object. The intended loop -
`codegen -> materialize as SyntheticModule -> bind(class) -> SpellCrystal
(custody) -> reuse/restore` - is canonical intent (Crystallizer V2 Duty 1,
AR Codegen residency ladder) but is NOT wired. Evidence: `spellbook/` has ZERO
references to "crystal"; the only `SpellCrystal` constructor is
`Crystallizer.create_spell_crystal` (crystallizer.py ~318); the codegen room
execs into a throwaway namespace and stops (no synthetic module / bind /
crystal). The machinery mostly exists and is tested; this is a WIRING program.

Full findings + mechanism captured in:
`artifacts/2026-07-02_agent_object_persistence_loop_philosophy.md`.

## MRP Alignment (Most Reasonable Product)
This is the save/restore + custody spine that makes the north star (checkpoint a
live object world, unfold it from a small bootstrap) real. It must be right at
the core: importlib-state ownership, lifecycle coherence (seed/unseed tied to
spell state), and source custody are foundational - a wrong core here would
force a rewrite of restore, mutation checkout, and MR's impact engine.

## Ticket Contract
- ENTRY_GATE: this epic is routed on `attention_board.md`; the philosophy
  artifact is linked in `artifact_board.md`; prerequisite understanding is
  captured (done this session).
- EXECUTION_BOUNDARY: crystallizer save/restore + synthetic-module lifecycle +
  bind->crystal wiring + codegen->synthmodule materialize + introspection fix.
  EXCLUDES: the MR merge/lane/head model decision (parked), the full MR impact
  engine (later build-order step), and any invisible live-swap semantics.
- DEPENDENCIES: Crystallizer V2 + MR V2 canon; the notch/bind_inactive runtime
  (already landed); the persistence adapter contract (to be designed).
- EXIT_GATE: all required stories accepted; a codegen output can be promoted to
  a synthetic module, bound (minting a crystal), unfolded from a crystal on a
  clean bootstrap, and introspected - with seed/unseed coherent across spell
  active/inactive - and validated green on user-run 3.14t.
- FAILURE_ESCALATION: raise DECISION_REQUEST for the parked merge model and for
  the module-naming / import-vs-DI defaults; raise CONFLICT if another agent
  edits crystallizer/synthetic_module/spellbook bind surfaces concurrently.

## Goals (Outcomes)
- bind mints a SpellCrystal, default-ON in DYNAMIC MODE only (Nexus + MutationResearch
  enabled); the crystal is the loader's HANDLE for every module tied to it. Crystal
  creation is distinct from module loading.
- The loader LOADS a spell's module(s) + their dependencies/requirements into
  `sys.modules` (in dependency order) when the spell is ACTIVE, and UNLOADS/unwinds them
  when it goes INACTIVE - retaining the crystal.
- Controlling these load PHASES is how name collisions stay manageable (only active
  spells' modules occupy `sys.modules`; inactive names stay free).
- A codegen result can be promoted to a synthetic module and bound.
- Synthetic modules are introspectable (`inspect.getsource`/tracebacks/pdb).
- Module seed/unseed is symmetric and tied to spell activate/deactivate (notch).

## Non-Goals (Explicit Exclusions)
- Invisible live hot-swap of already-imported code (forbidden; boundary-only).
- The MR merge/lane/head model (parked DECISION_REQUEST).
- The full MR impact engine (later build-order step).
- Checkpointing, bootstrapping, and fast-loading the system + configs - these are
  SEPARATE later systems, explicitly NOT part of this in-memory load/unload first step.
- Non-dynamic mode: without Nexus + MutationResearch enabled, synthetic modules are not
  needed and this machinery stays off (both subsystems are dynamic-mode-only).
- Crystallizer becoming a package manager (uv-first validation only).

## Scope Boundaries
- In scope: `src/melder/crystallizer/*` (crystallizer, spell_crystal,
  synthetic_module, crystal_analysis, crystal_loader, asset_management), the
  bind->crystal seam in `spellbook`/`bind`, the codegen->synthmodule materialize
  seam in the Nexus codegen room, the persistence adapter contract.
- Out of scope: MR tool internals beyond the crystallizer hydration/persistence
  contract; world-merge; the codegen validation-policy strategies (already built).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: epic created to hold the retraced findings and sequence the
  wiring program; stays draft until the owner picks the first story to activate.

## Success Metrics
- codegen -> synthetic module -> bind -> crystal round-trips on 3.14t.
- a checkpointed conduit world unfolds from crystals on a fresh bootstrap.
- `inspect.getsource` works on a bound synthetic spell.
- no stale synthetic module resolves after a spell goes inactive (notch).

## Requirements (Functional + Non-Functional)
- Thread-safe (Python 3.14t no-GIL) registry + sys.modules lifecycle.
- Deterministic dependency-ordered unfold; cycle-safe (publish-before-exec).
- Adapter boundary: typed contract canonical + JSON codec; CRUD verbs; host owns
  storage; SQLite mock + JSON-file reference adapters.
- No secrets in crystals/adapters.

## Constraints / Assumptions
- Hot-swap coherence holds only at bind/rebuild/bootstrap boundaries.
- MR reads `source_text` off the object (introspection fix is for external tools).
- Recurring file-tool write-fault (mount truncation) - verify writes.

## Dependencies / External References
- `artifacts/2026-07-02_agent_object_persistence_loop_philosophy.md` (findings)
- `artifacts/2026-07-01_crystallizer_philosophy_v2.md`,
  `artifacts/2026-07-01_mutation_research_philosophy_v2.md` (canon)
- `artifacts/2026-04-26_ar_codegen_capability_surface_philosophy.md`,
  `artifacts/crystallizer_configuration.md`,
  `artifacts/2026-05-02_file_to_memory_bridge_mechanic.md`,
  `artifacts/Archived/2026-04-26_crystallizer_v2_synthetic_module_graph_and_requirements.md`
- Probe: `tests/experimentation/physical_imports_synthetic_limits_probe.py`
  (mount-truncated; needs clean re-lay).

## Milestones (Track Progress)
- [x] M1: Introspection fix (non-`<>` `__file__` + `get_source` or linecache
      seed) + linecache clear on unseed, with tests. DONE 2026-07-12 (mutation_0,
      patch persistence_loop_m1_m5_residue_2026_07_12; owner run pending).
- [ ] M2: `crystal_analysis` formalized (lift AST out of spell_crystal into the
      strategy layer + add `exports`).
- [ ] M3: Loader chain + `load_order` (topo sort) -> unfold a crystal's synthetic
      graph into `sys.modules` in dependency order.
- [ ] M4: bind -> crystal auto-wire, default-ON in dynamic mode only (Nexus + MR
      enabled). Refines V2 Duty 1's unconditional "always" -> "always in dynamic mode".
- [x] M5: codegen-result -> SyntheticModule materialize step (the `X`).
      DONE 2026-07-12 (mutation_0: `materialize_codegen` room verb, validation-
      gated + R8 teardown + advertised; owner run pending).
- [ ] M6: synthetic publish/unpublish tied to notch/activate/deactivate.
- [ ] M7: persistence adapter contract (typed + JSON, CRUD; SQLite/JSON adapters).
- [ ] M8: Content-addressed version store + canonical->active alias (the callsign
      layer): append-only SHA256-keyed modules (`<canonical>__<hex12>`), canonical
      imports resolve via the alias, version-pin by callsign. FOUNDATIONAL - de-risks
      removal (reshapes M6 into repoint + evict-cold).

## Stories (Required to Complete)
- [ ] Story: <TBD> - introspection fix (M1)
- [ ] Story: <TBD> - crystal_analysis + exports (M2)
- [ ] Story: <TBD> - loader chain + load_order (M3)
- [ ] Story: <TBD> - bind->crystal auto-wire (M4)
- [ ] Story: <TBD> - codegen->synthmodule materialize (M5)
- [ ] Story: <TBD> - lifecycle tie-in to notch (M6)
- [ ] Story: <TBD> - persistence adapter contract (M7)

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Re-lay the mount-truncated probe file cleanly + fold in the getsource
      A/B/C scenarios; run on 3.14t.
- [ ] Task: Re-read the three not-fully-read archived crystallizer_v1/v2/v3 +
      Codegen Interaction Model + Workstation Codegen Guardrails docs.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories.

## Acceptance Criteria (Epic Done)
- The core loop works end to end on user-run 3.14t; crystals unfold on a fresh
  bootstrap; synthetic spells are introspectable; unseed leaves no stale module
  but retains the crystal; owner accepts.

## Risks / Mitigations
- Risk: hot-swap misuse -> Mitigation: enforce boundary-only copy mode.
- Risk: linecache seed leaks stale source -> Mitigation: clear on unseed.
- Risk: mount write-fault corrupts durable docs -> Mitigation: verify every write
  (wc/tail) and repair.
- Risk: merge-model ambiguity blocks MR -> Mitigation: keep parked; loop does not
  depend on it.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.
- [ ] No invisible live-swap semantics (boundary-only).

## Validation / Test Approach
- pytest unit/component/integration under `tests/.../crystallizer`; experimentation
  benches for importlib/synthetic-module behavior; user-run on 3.14t (agents
  report "Not run" otherwise).

## Rollout / Adoption Plan
- Land introspection + loader chain first (no bind coupling), then bind->crystal,
  then codegen wiring, then persistence.

## Open Questions
- MR merge/lane/head model (parked; IMPORTANT_CONSIDERATION governs).
- Module naming for `X` (agent-chosen vs derived).
- Default reference mode (import vs DI).

## Decision Log
- 2026-07-02: Created epic to hold retraced findings; sequenced as a wiring
  program over mostly-existing machinery. Merge model stays parked.
- 2026-07-02T23:03:09Z (owner decisions, memory-recovered):
  (1) FRAME - the machine is the `SyntheticModule` registry of live world objects; the
  import protocol is only the doorway (the loader creates/execs nothing, delegates to the
  world object). Not an "importlib takeover"; world-first, no normal-Python analogy.
  (2) STEP ONE = in-memory load/unload tied to spell state: bind creates a crystal; the
  crystal is the loader's handle for all its modules; ACTIVE -> load module + deps;
  INACTIVE -> unload/unwind (crystal retained).
  (3) COLLISIONS are managed by controlling load phases (only active spells in
  `sys.modules`).
  (4) DYNAMIC-MODE GATE - bind->crystal default-ON only when Nexus + MR enabled; both
  subsystems run ONLY in dynamic mode; without agents synthetic modules are unneeded.
  Refines V2 Duty 1 "always" -> "always in dynamic mode".
  (5) AST job = map how code populates `sys.modules` + `__dict__` and enable the reverse
  unwind; the loader takes on importlib's dependency load/order work and MAY re-delegate
  to importlib.
  (6) MR = a thin API over existing features: in-memory objects DERIVED from crystallizer,
  keyed by each spell's unique SHA256, that report active/inactive + fork, diff versions,
  and compute blast radius by scanning impacted code via the SAME dependency systems
  crystallizer uses - MR re-derives nothing.
  (7) OUT OF SCOPE (separate systems): checkpointing, bootstrapping, fast-loading + configs.
  Parked + cross-linked: the MR merge/lane/head-model DECISION_REQUEST lives on
  `tickets/tasks/2026-07-01_reframe_spellindex_in_crystallizer_mutation_philosophy_artifacts_task.md`.

- 2026-07-03T12:33:54Z: Mapped the full 2026-07-02 import/module-lifecycle findings into
  `artifacts/2026-07-02_import_and_module_lifecycle_findings.md` (evidence-backed;
  every claim proven by a probe) and derived the Findings-Derived Requirements
  section (R1-R14, T-F1..T-F5). World-first frame + dynamic-mode gate unchanged.

- 2026-07-03T13:09:12Z: Adopted the CONTENT-ADDRESSED VERSION STORE (SHA256 callsign
  `<canonical>__<hex>`) + canonical->active alias (= SpellIndex). Removal RELOCATED
  from correctness-necessity to alias-repoint (notch) + cold-eviction. importlib is
  PLUGGED-IN (we don't reimplement detection); the manual materialize path is a
  maintained mirror (needs an equivalence test). Concurrency surface narrowed to
  registry/materialize/alias/eviction (the importlib path is already no-GIL-safe).
  Added R15-R19, M8, T-F6..T-F8. See findings artifact sections 12-17.

- 2026-07-03T13:29:44Z: Spun out the FIRST-CUT wiring as child epic EPIC-2026-07-03-wire-crystallizer-into-melder (create_spell_crystal path + importlib
  seed/unseed + bind participation + remove_inactive_synthmodules knob). M4/M6/M8 execute
  through it; bootloader/history/storage/mutations stay deferred.

- 2026-07-03T15:05:24Z: Refined the activation-gate model (child epic EPIC-2026-07-03, C1 Findings +
  Subsystem Dependency section): CRYSTALLIZER is STANDALONE (no deps; bootstrapping +
  custody + other mechanics). MUTATIONRESEARCH REQUIRES NEXUS (dependency) + Crystallizer
  and may be enabled ONLY under the codegen conditions (dynamic + rift_enabled + ai_native).
  The codegen lane requires Nexus + Crystallizer + MR all active; enforced in Nexus
  `_validate_target_frame_runtime_requirements` + the MR enable path. One-way: enabling MR
  forces the codegen lane; enabling crystallizer forces nothing.

- 2026-07-03T15:21:55Z: Sequenced the crystallizer program into 3 child epics under this parent:
  (1) EPIC-2026-07-03-wire-crystallizer-into-melder (first cut: wire + custody + seed/unseed),
  (2) EPIC-2026-07-03-crystallizer-bootstrap-checkpoint (crystal-twin snapshots +
  snapshot/restore_aether), (3) EPIC-2026-07-03-crystallizer-persistence (CRUD adapter +
  MutationResearchCrystal). Dependency: bootstrap + MR ride persistence; all ride first-cut
  custody. Parent M3/M7 are realized through epics 2 + 3.

- 2026-07-05T12:25:04Z (owner + melder_0 design session; program-level DECISIONS):
  OWNERSHIP: all 4 program epics -> melder_0 (crystal_0 = backup, owner directive).
  VALUE SCOPING: crystallizer is DYNAMIC-LANE POSITIONED. Automatic mode ships mechanism, not
  product: custody duplicates on-disk source, the world cannot drift there (dynamic ops are
  gated off), the compiler artifact cache owns warm-boot savings, and the devops registry owns
  observability. Fileless/bytecode bootstrap parked as a future niche.
  HARD GATE (supersedes the wire epic's "bind participates whenever crystallizer.activated"):
  participation seams check `crystallizer.activated AND frame posture == dynamic`; automatic
  frames emit NOTHING and mint NOTHING.
  VALUE DECOMPOSITION (why bootstrap exists): (1) fastboot - reheat vs recook; (2) the record
  as queryable configured-truth (MR hydration + tooling); (3) THE case - the drifted world:
  agent-built objects whose only source is crystal custody; the authored bootstrap rebuilds
  day-0, only the record rebuilds day-N.
  KITS = PLUGINS (north star): named profiles are distributable capability packages -
  frame-scoped restore summons a configured agent station (CommandOps package-posture
  analogy); synthetic-containing profiles only unfold into dynamic frames (Activation Rules);
  content-addressing = integrity; sealer trust/signing deferred to a kit-distribution epic.
  PROFILES MODEL (owner naming): Crystallizer._persistence_crystal -> PersistenceCrystal ->
  PersistenceProfile. "default" = the live mirror, ALWAYS exists, emissions always target it
  (first setup IS the default bootstrap); named profiles = saved worlds/kits;
  clear_bootstrap generalized to clear_profile; save/hydrate land with bootstrap+persistence
  epics.
  TWIN HIERARCHY (owner): AetherCrystal -> MutationResearchCrystal & NexusCrystal &
  AethericFrameCrystal -> SpellbookCrystal -> SpellBindingCrystal(+SpellCrystal manifest ref)
  & ConduitCrystal. Mirrors the verified pull-in-init runtime graph. THIN Aether twin: config
  only, retained whenever crystallizer is active regardless of posture (root config sits above
  the gate). Flat maps per level + tree presented at the API (the aetheric_frame storage
  pattern); replace-on-emit under one profile lock; L3 intra-level order: binds before
  conjure; link edges replay LAST; lesser conduits never emit (root only, call-site gate).
  HYDRATION BOUNDARY: configs hydrate minus hook callables; class spells hydrate (physical
  re-import / synthetic materialize-from-crystal); method/lambda/existing-object spells and
  hooks are replay_required; SpellBindingCrystal carries `rebindability` so restore REPORTS
  shortfalls instead of under-building.
  FREEZE-AT-FIRST-BIND: adopted in principle (posture must be final before the first crystal
  decision; config twin emits at freeze -> config-first ordering falls out mechanically);
  ENTRY GATE before landing: census of config-mutation-between-bind-and-conjure usage in
  tests/examples; fallback if census blocks = freeze-at-conjure + catch-up mint at freeze.
  EMIT GATE STYLE: read-through on `activated` at call-sites (structural frequency, one attr
  read) + one catch-up snapshot walk at activate() for pre-activation worlds; cached flags
  remain for per-frame POSTURE only (the Nexus precedent's correct half).
  S1 LANDED: placeholder scaffold under src/melder/crystallizer/persistence/** (story
  2026-07-05_persistence_crystal_profile_and_twin_family_scaffold_story.md; compileall-clean;
  runtime import 3.14t-only via the package-root Nexus import chain).

- 2026-07-05T15:55:00Z (owner, DECISION - emission factor + setup canon): CONFIGURATION
  LOCK-IN IS THE EMISSION FACTOR - twins spawn when configurations confirm, giving spell
  crystals their custody shells before any bind emission: Aether twin at root-config
  activation (OPTIONAL - only when the user configures Aether; sits above the posture gate);
  AethericFrame twin at posture freeze (dynamic frames only); Spellbook twin at configuration
  lock (dynamic only; hooks project as labeled replay-required markers; bind_order captured);
  Conduit twin at conjure (deferred to the bind/emit story). Crystallizer.emit(twin) is the
  passive sink (NO-OP when inactive; call-sites pre-gate to avoid payload cost). SETUP CANON:
  Aether -> Crystallizer -> MutationResearch -> Nexus for full AI features ("the maximum you
  can get - you learn a few configs"); then per-frame: aetheric_frame + spellbook, then
  build. CONJURE GUARD (same session): dynamic conjure + active crystallizer + binds-before-
  configuration-finalize = refused with a teach-grade error (recorded worlds must not be
  born config-incoherent); automatic/crystallizer-off worlds byte-identical; test fallout
  assigned to a separate agent by owner.

- 2026-07-05T12:55:00Z (owner revision pass, same session): ACTIVE-PROFILE MODEL - the
  persistence root mirrors Aether/frames: guaranteed "default" + named profiles + one ACTIVE
  selection; emissions route to the active profile; create_profile activates by default;
  deleting the active falls back to "default". SPELLCRYSTAL IS THE L3 NODE - spell_crystal.py
  migrated to persistence/crystals/ and now captures the bind signatures itself (spell_name,
  binding_name, spellframe_name, existence_name, permissions_name, optional spellbook_id
  parent edge, derived rebindability); SpellBindingCrystal retired as absorbed. CLEANUP
  POSITION LAW: cleanup() sits directly under __init__ in every persistence class (the
  spellbook/spell model); slots follow the Cleanable.__slots__ + [...] idiom.

- 2026-07-05T15:45:26Z (owner, DECISION - runtime-identity policy): EMIT the runtime ULIDs,
  NEVER rehydrate them, NORMALIZE them out of the content-address. Twins carry ULIDs as
  record-local foreign keys + log correlation (internally consistent within one boot; the
  only emission-time handle for unnamed units). Restore mints fresh identities and keeps an
  old->new translation map while walking edges (recorded ids die at the boundary). Seal
  fingerprinting (bootstrap epic) replaces ULIDs with first-seen ordinals in the canonical
  form so identical worlds compare identical across boots - this is what makes the boot-time
  default-bootstrap match check able to hit. Hydration of a persisted default profile is
  checkpoint-shaped replay, never a raw map-merge (mixed ULID generations would duplicate
  the world). Stable cross-session coordinates remain: spell SHA256s, frame names, conduit
  names (when given), profile names. Contract lines stamped on SpellbookCrystal,
  ConduitCrystal, and SpellCrystal docstrings.

- 2026-07-05T19:45:00Z (melder_0, COMPLETION LEDGER for the 2026-07-05 build day):
  M4 DONE (bind->crystal uniform at the bind seam, posture-gated; sweep retired by owner
  correction; bind_inactive emits inactive custody). M6 FIRST SLICE DONE (park/promote
  mirrored into the record via emit_spell_activity at the two _active choke points;
  knob-gated depth-2 unpublish on park, always-republish on promote; full reverse-edge
  unseed awaits M2). M7 SEAMS DONE (PersistenceSystem + CrystallizerCache placeholder;
  adapter contract still open). M8 DATA GROUNDWORK (ULID policy: emit / never-rehydrate /
  normalize-out-of-fingerprint; callsign behavior still open). BEYOND-SCOPE LANDINGS:
  profiles model + checkpoint crystals (incremental segments) + config-owned emissions (5)
  + conduit twin + conjure guard + custody lookup + cache-root restructure. OPEN: M1
  (introspection), M2 (crystal_analysis edge model), M3 (loader chain), M5 (codegen
  materialize), removal events, catch-up walk, restore engine, adapter behavior, MR tool.
  3.14t: NOT RUN - the whole day awaits the owner's verdict.

## Notes
- DATETIME: 2026-07-02T22:01:20Z
  TYPE: FACT
  CLAIM: Session retraced the full codegen->synthmodule->bind->crystal loop and
    the importlib-takeover mechanism, and PROVED physical<->synthetic interop
    limits by experiment (6/7 green; the getsource limit is the `<synthetic:..>`
    linecache angle-bracket guard, fixed by non-`<>` __file__ + get_source or
    linecache seed). Machinery mostly exists; remaining work is wiring.
  EVIDENCE:
  - artifacts/2026-07-02_agent_object_persistence_loop_philosophy.md:1-999
  - src/melder/crystallizer/synthetic_module.py:1142-1231
  - src/melder/aether/spellbook/spellbook.py:3063-3149
  IMPACT: Durable capture before compaction; sequences the build program.
  NEXT: Owner picks the first story (recommend M1 introspection fix or M3 loader
    chain + load_order - both crystallizer-native, no bind coupling).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T10:20:00Z
  TYPE: FACT
  CLAIM: M1 + M5 residue IMPLEMENTED (mutation_0, owner-directed; patch
    persistence_loop_m1_m5_residue_2026_07_12). M1: `__file__` ->
    `synthetic://<name>.py`, loader `get_source` (InspectLoader), linecache
    pops in unpublish/cleanup/execute_source; 7-row introspection suite. M5:
    `materialize_codegen(code, *, module_name, frame_name)` on the codegen
    room - validation-gated, sentinel pre-bind identity (unbound_codegen /
    codegen_materialized), R8 exec-failure teardown, advertised in
    _CODEGEN_COMMAND_METHOD_NAMES; 5-row verb suite. Design law (owner,
    2026-07-12): NOT all codegen becomes a synthetic module - promotion is
    the explicit opt-in Progenitor act; execute/preview lanes stay ephemeral.
  EVIDENCE:
  - src/melder/crystallizer/synthetic_module.py:80-120
  - src/melder/nexus/rift/command_system/codegen_command_system.py:707-860
  - tests/unit/melder/crystallizer/test_synthetic_module_introspection.py:1-140
  - tests/unit/melder/aether/test_codegen_materialize_verb.py:1-150
  IMPACT: The loop's agent-facing gap is closed pending the owner run; bind
    already mints custody (M4), so materialize -> bind -> crystal now works
    end to end once green.
  NEXT: Owner 3.14t tree run; remaining residue = load_order-driven unfold
    depth proof, R11 reverse-edge unseed, M8 callsign wiring (staged slices).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-12T10:20:00Z
  TYPE: RISK
  CLAIM: attention_board.md sync is DEFERRED: this bridge session serves a
    poisoned stale replica for the board (content-read shows the pre-session
    NUL-tailed snapshot while disk stat shows a newer 13,642-byte rewrite by
    a concurrent agent). Editing through the stale replica would clobber
    disk truth - the exact historical fault class.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-07-12_mutation_research_accessor_doors_task.md:1-1
  IMPACT: Board rows still name melder_0; ownership flip + M1/M5 routing
    update ride the next fresh session (or any agent with clean reads).
  NEXT: Next session: board sync (all rows agent_name -> mutation_0; epic row
    -> review; accessor-doors row verify).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Findings-Derived Requirements (2026-07-02, evidence-backed)
Source: `artifacts/2026-07-02_import_and_module_lifecycle_findings.md` (every item has a
runnable probe). Grouped by component; these refine/extend the milestones above.

crystal_analysis (AST / dependency layer):
- R1. Classify each import edge by AUTHORITY: synthetic_module | user_source |
  site_package | stdlib | missing.
- R2. Tag each edge with SCOPE: load-time (top-level) | deferred (in-method).
- R3. Record `from b import a` as a MODULE edge PLUS the imported NAME(s) (name-level
  edges for MR impact analysis; production `_extract_import_targets_from_ast` already
  returns the from-import map).
- R4. Build the graph BIDIRECTIONALLY (dependencies AND dependents), including
  physical->synthetic edges scanned from physical sources (we cannot enumerate physical
  importers at runtime).

loader chain (M3):
- R5. Publish-before-exec (cycle-safe) in materialize and restore.
- R6. EAGER-SEED world-internal synthetic deps on activation (install finder + register
  the graph in load order) BEFORE physicals can import them.
- R7. VALIDATE-BEFORE-ACTIVATE: confirm load-time EXTERNAL deps are present (find_spec /
  uv.lock) before executing a crystal; throw if missing.
- R8. ROLLBACK-ON-EXEC-FAILURE: if a module's exec raises, unpublish + unregister it (no
  half-published modules).
- R9. Physical-backed managed modules COMPILE with the real filename (introspection /
  tracebacks work for free).

lifecycle / removal depth (M6):
- R10. THREE depths: publish / UNPUBLISH (notch-inactive: reversible, crystal retained,
  holders survive) / CLEANUP (hard teardown: clear namespace, del owned refs, logger
  last, clear linecache). Deterministic teardown, not GC-reliant (no-GIL 3.14t).
- R11. Reverse-edge-aware unseed: consult dependents (incl. DEFERRED and PHYSICAL) before
  unpublish/cleanup; keep resident if live dependents exist; coordinate at a rebuild
  boundary.
- R12. Clear the linecache entry on unpublish/cleanup.

introspection:
- R13. FIX B for codegen-backed modules: loader `get_source` + non-`<>` `__file__` where
  possible; FIX C (seed linecache) as fallback.

physical <-> synthetic:
- R14. Record physical->synthetic edges explicitly at analysis time; keep-resident policy
  while physical dependents are live.

content-addressed version store + concurrency + mirror (M8):
- R15. VERSION STORE: key each module version by an identifier-safe content-SHA256 callsign
  `<canonical>__<hex12>` (= module-version identity = the crystal's module-version SHA).
  Append-only; identical content DEDUPS; versions coexist in `sys.modules` (no collision).
- R16. CANONICAL ALIAS = SpellIndex: `import svc` / `from svc import a` resolve via the finder
  through a canonical->active-callsign alias; the SHA never appears in code. Version-pin (MR
  checkout) via `import <callsign>` (identifier-safe) or `importlib.import_module(callsign)`.
- R17. REMOVAL RELOCATED (reshapes M6): not collision-driven teardown, but (a) repoint the
  active alias on notch (invalidate the canonical `sys.modules` entry - the one bounded
  removal, at the hot-swap boundary) + (b) evict COLD callsigns for memory (no live refs, safe
  boundary). Versions never vanish, so most "unseed strands dependents" cases evaporate.
- R18. CONCURRENCY (narrowed): importlib + module `__dict__` + the import-driven path are
  already no-GIL-safe. Guard only OUR surface with RLocks: registry mutations, the manual
  materialize sequence, alias repoint, eviction. Append-only + dedup make concurrent identical
  stores converge.
- R19. EQUIVALENCE: the manual materialize path must produce byte-identical module state to the
  import-driven path (regression test); prefer routing through importlib where possible.

Tasks (findings-derived):
- [ ] T-F1. Run the probe suite on user 3.14t (external-lib [done], owned-physical,
  import_lifecycle_management_suite).
- [ ] T-F2. Implement the crystal_analysis edge model (R1-R4): lift AST into the strategy
  layer + add scope/name/authority + bidirectional edges.
- [ ] T-F3. Loader chain (R5-R9).
- [ ] T-F4. Lifecycle / removal-depth tied to notch (R10-R12).
- [ ] T-F5. Introspection fix (R13).
- [ ] T-F6. no-GIL concurrency stress test (concurrent import of one callsign;
  repoint racing an in-flight import; store racing importlib's `_ModuleLock`).
- [ ] T-F7. import-driven vs manual-materialize equivalence regression test.
- [x] T-F8. DONE 2026-07-03: former-inline probes persisted as standalone files -
  content_addressed_version_store_probe.py (6/6), importlib_mirror_and_cycle_breaker_probe.py
  (5/5), activation_footprint_insert_only_probe.py (2/2). All 6 probes now on disk.

Acceptance additions:
- external deps resolve free + are validated at restore; owned-physical is served by our
  loader and introspectable; physical->synthetic seed/unseed is coherent; cycles are safe
  (publish-before-exec); teardown is deterministic (no GC reliance).

## Context / Handoff Summary
crystal_0 created this epic + the linked philosophy artifact to preserve the
2026-07-02 retrace before compaction. The loop and its importlib mechanics are
understood and partly proven by experiment; the machinery is mostly built; the
program is a wiring sequence (M1-M7). Merge model parked. First recommended
slice: M1 (introspection fix) or M3 (loader chain + load_order).

## HANDOFF (2026-07-12, melder_0 -> incoming agent; owner-directed)
The owner is assigning this epic to a NEW agent. State at handoff:
- OWNERSHIP: melder_0 releases this lane; the board row is marked for
  the incoming agent. Read the three retained artifacts on
  artifact_board (philosophy / findings / code-map+proof-ledger) FIRST -
  they are the canonical context, deliberately redundant.
- FRESH VERIFICATION (melder_0, 2026-07-12, bounded source check): the
  epic's CORE GAP IS STILL REAL, this is NOT stale work. (a) The codegen
  room STILL has no materialization lane - grep of
  nexus/rift/command_system/codegen_command_system.py finds NO
  SyntheticModule/bind/materialize verb (the only "synthetic" hit is a
  describe docstring at :1167); executed code still evaporates into a
  throwaway namespace. (b) The M1 introspection residue is also still
  open - grep of crystallizer/synthetic_module.py finds ZERO
  getsource/linecache handling, so the angle-bracket __file__ limit
  (philosophy artifact, fixes B/C) remains unfixed.
- WHAT SHIPPED SINCE 07-02 (verify, then strike from the residue map):
  M3-adjacent synthetic restore (restore_engine + shared
  user_world_rebuild lane), S2 user-source retention, graft lanes incl.
  merge mode, MR synthesis/preview (recorded-material composition), the
  SQLite mesh adapter, and the crystallizer decomposition. The epic's
  FIRST MOVE stands as written in the Status header: a source-derived
  M1-M7 residue map - prove delivery, don't assume it.
- COORDINATION: melder_0 remains active on adjacent lanes (mesh/adapter,
  mediator freezes); mailbox me before editing crystallizer/
  asset_management/ or the transaction strategies.

## Digital-Twin Family + Conditional-Feature Emit Directive (2026-07-04, owner)
Program-level directive for ALL agents on the crystallizer epics (wire / bootstrap / persistence).
Extends the wire epic's "EMIT model" + "Activation Rules" DECISIONs; read those with this.

DIGITAL TWIN FAMILY — we keep a digital twin (a pure-data crystal) of each of these five structural
owners:
- Aether            -> AetherCrystal
- AethericFrame     -> AethericFrameCrystal
- Spellbook         -> SpellbookCrystal
- Conduit           -> ConduitCrystal
- MutationResearch  -> MutationResearchCrystal
- Nexus             -> NexusCrystal
`SpellCrystal` already exists as the spell-level twin leaf beneath them (crystallizer.create_spell_
crystal). GOVERNING PRINCIPLE: we twin ANYTHING we want to configure/persist (that is why Nexus is
IN the family — its NexusConfiguration is a configured surface). AethericFrame additionally carries
DEV-OPS state, so its twin captures that dev-ops config surface too, not just the frame basics. Each
of the six now holds a NON-OWNING
`_crystallizer` reference pulled at __init__ (Aether owns/creates/cleans it; the rest pull from their
parent) — that is the seam the emit rides on.

CONDITIONAL FEATURES — under specific conditions we allow specific features (see Activation Rules):
plain / crystallizer-standalone (automatic; physical+bytecode bootstrap, no synth) / Nexus AR
(automatic+rift_enabled; command+view) / codegen lane (dynamic+ai_native+rift_enabled + Nexus +
Crystallizer + MR; synthetic modules). Feature availability is a function of the FRAME posture
(rift_enabled, system_state, ai_native), not a global switch.

EMIT-WHEN-ENABLED (default) — when the crystallizer is ENABLED, these units EMIT their twin +
lifecycle/config data to the crystallizer BY DEFAULT: configuration setups first (what each unit is
configured as — the thing worth cloning + remembering), then the bind / spell-crystal pathing at the
pivotal points (what is being bound, in what order). The crystallizer records + persists this so it
"just knows what is configured", and the bootstrap is rebuilt dynamically from that record
(restore_conduit / restore_frame / restore_aether = one op at different subtrees). When the
crystallizer is DISABLED the emit is a no-op and hosts stay byte-identical.

GATING STYLE — follow the proven Nexus publish precedent (see
artifacts/2026-07-03_first_cut_design_detail.md, "Nexus emission gating precedent"): the emitter
holds a cached config flag and checks it before emitting; the sink stays dumb. Per-frame posture,
pushed/cached at pivotal points (conjure/bind), not a live global lookup.

## Phase-A Closure (2026-07-06T20:45:00Z, melder_0 - owner-directed)
- Wire epic (EPIC-2026-07-03-wire-crystallizer-into-melder) CLOSED, owner-accepted ->
  tickets/epics/completed/. The full recorded world landed: twin family (9 kinds),
  custody lifecycle, removal ladder + tombstones, state switches (RecordedUnitState),
  memberships (SpellIndexCrystal), links (link_targets), contracts (ContractCrystal,
  8 verb seams + fan-outs + transfer both sides), clusters (ClusterCrystal), cadenced
  checkpoints + retention + auto-flush, atomic local cache. 136 tests / 22 files
  (user runs 3.14t; one residual failure is the collection-DI lane, not this program).
- Scaffold story CLOSED -> tickets/stories/completed/ (canonical evidence trail).
- Orientation task CLOSED -> tickets/tasks/completed/.
- Requirements R1-R19 status: record-side requirements SATISFIED; restore-side
  (unfold/rebind) remain OPEN -> bootstrap epic (next lane). Adapter LAST
  (persistence epic). MR crystal = other agent.
- 2026-07-07T01:05:00Z closure-sync completion (melder_0, post-REONBOARD): 3 closed-anchor
  rows added to attention_board.md (cap now exactly 12); artifact disposition applied -
  both V2 philosophy docs + the first-cut design detail moved to Recently Cleared as
  retain_as_reference (they stay canonical program references on disk).
- WRITE-FAULT INCIDENT (2026-07-06/07): melder_0's 20:45 bash append (read-whole/
  rewrite-whole) baked stale replicas into this epic + the bootstrap + persistence epics,
  truncating the R1-R19 section here, the bootstrap Design Note body, and the persistence
  15:45 decision tail. ALL REPAIRED 2026-07-07T02:20:00Z from git 9eba1ba92/32e751d4f +
  in-session verbatim text. Ticket/board writes are FILE-TOOL-ONLY for melder_0 now.
