# Task: Reorient Crystallizer Against Live Nexus Runtime

## Metadata
- Task ID: TASK-2026-04-26-reorient-crystallizer-against-live-nexus-runtime
- Story:
- Epic: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: in_progress
- Owner: codex
- Agent Name: codex_0
- Priority: p1
- Created: 2026-04-26T22:22:00Z
- Updated: 2026-04-26T22:22:00Z
- Updated: 2026-05-02T23:48:49Z
- Updated: 2026-05-03T09:28:22Z
- Updated: 2026-05-03T09:40:45Z
- Updated: 2026-05-03T11:01:42Z
- Updated: 2026-05-03T09:27:48Z

## Objective
Re-ground the crystallizer design discussion in the actual live Nexus/Rift/
Spellbook runtime code so later crystallizer mechanics match the repo's real
runtime grammar rather than generic Python/module assumptions.

## Ticket Contract
- ENTRY_GATE: the user explicitly said the current crystallizer discussion had
  drifted and directed a return to the live Nexus/runtime code.
- EXECUTION_BOUNDARY:
  - targeted runtime-source reading only
  - this task ticket
  - `attention_board.md`
- DEPENDENCIES:
  - `src/melder/aether/nexus/**`
  - `src/melder/spellbook/**`
  - `src/melder/aether/conduit/**`
  - crystallizer design lane
- EXIT_GATE: the concrete runtime semantics that crystallizer must respect are
  restated from source evidence, with explicit notes about where the earlier
  framing drifted.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the runtime code reveals a
  materially different crystallizer boundary than the current artifact stack
  assumes.

## Scope Boundaries
- In scope:
  - Nexus/Rift/RiftSpace mechanics
  - Spellbook/Bind/Spell mechanics relevant to crystallizer
  - Conduit/runtime ownership mechanics relevant to active crystal state
- Out of scope:
  - new crystallizer implementation
  - refactors to runtime code
  - patching docs yet

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a source-level reorientation
  to stop the crystallizer discussion from drifting.

## Steps / Checklist
- [ ] Count and read the key runtime files manually with `Get-Content`.
- [ ] Record the concrete mechanics that crystallizer must respect.
- [ ] Document where the previous crystallizer framing drifted from runtime truth.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed runtime restatement for crystallizer discussion

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-26_reorient_crystallizer_against_live_nexus_runtime_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - manual `Get-Content` reads of the selected runtime files

## Risks / Rollback Notes
- Risk: reading too broadly creates more drift instead of less.
  Rollback: keep the readset bounded to the concrete runtime seams that shape
  crystallizer semantics.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: task closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-26T22:22:00Z
  TYPE: PLAN
  CLAIM: The crystallizer discussion drifted too far into generic Python/module
    semantics. The next move is to re-anchor directly in live Nexus/Rift/
    Spellbook/Conduit code before touching more crystallizer design or
    implementation.
  EVIDENCE:
  - user_instruction: "go read nexus go read some of my code because your not undertanding how this all works"
  IMPACT: The immediate work is source reorientation, not more subsystem invention.
  NEXT: count and read the key runtime files manually.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T22:22:00Z
  TYPE: FACT
  CLAIM: The direct runtime readset is large, so this reorientation pass has to
    be seam-driven rather than full-file brute force. The files most relevant to
    crystallizer semantics are the Nexus/Rift/room surfaces plus the Spellbook,
    Bind, Spell, and Conduit seams. Several of those files are well above the
    500-line chunk limit and need targeted section reads.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py: 2362 LOC
  - src/melder/aether/nexus/rift/rift.py: 904 LOC
  - src/melder/aether/nexus/rift/rift_space/rift_space.py: 763 LOC
  - src/melder/aether/nexus/rift/rift_space/workstation.py: 761 LOC
  - src/melder/aether/nexus/rift/command_system/command_system.py: 1416 LOC
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py: 695 LOC
  - src/melder/aether\nexus\rift\codegen_system\codegen_system.py: 460 LOC
  - src/melder/spellbook/spellbook.py: 3135 LOC
  - src/melder/spellbook/bind/bind.py: 591 LOC
  - src/melder/spellbook/spell.py: 1393 LOC
  - src/melder/aether/conduit/conduit.py: 3400 LOC
  IMPACT: The next step should read the relevant symbols and lifecycle sections
    only, not whole giant files front-to-back.
  NEXT: locate and read the runtime sections that define bind, conjure,
    registration, frame/link ownership, room ownership, and codegen-room
    behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T22:26:03Z
  TYPE: FACT
  CLAIM: The live runtime mechanics are now much sharper. `Nexus` is a
    singleton public root that owns Rift registry/configuration/ACL/descriptor
    management and creates bare Rifts without choosing a target frame first.
    `Rift` owns exactly one primary room plus explicit frame-link contracts and
    later delegates Nexus-managed frame creation/recovery back into Nexus.
    `RiftSpace` owns the durable room-local assets (`FrameViewer`,
    `Workstation`, `CommandSystem`, `RiftEventSystem`, `RiftMemorySystem`).
    `CodegenRiftSpace` owns the internal `CodegenSystem`, while
    `CodegenCommandSystem` is the public room-facing facade that delegates
    validate/execute into that engine. On the Spellbook side, `bind(...)`
    registers the spell into local spell maps and `SpellSystemStates`, and if a
    conduit already exists it stamps conduit ownership/runtime metadata into the
    new spell and may register existing-object spells into Creations. `conjure`
    then creates exactly one root conduit for the Spellbook. `Conduit` owns the
    live resolution/runtime surface and later controls lesser-conduit creation,
    upgrade-to-normal, meld gating, and ownership transfer.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:58-176
  - src/melder/aether/nexus/nexus.py:564-740
  - src/melder/aether/nexus/nexus.py:2040-2190
  - src/melder/aether/nexus/rift/rift.py:28-176
  - src/melder/aether/nexus/rift/rift.py:212-247
  - src/melder/aether/nexus/rift/rift.py:368-520
  - src/melder/aether/nexus/rift/rift.py:920-1005
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:112-223
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:223-270
  - src/melder/aether/nexus/rift/rift_space/workstation.py:67-121
  - src/melder/aether/nexus/rift/rift_space/workstation.py:188-371
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:79-250
  - src/melder/aether/nexus/rift/codegen_system/codegen_system.py:90-409
  - src/melder/spellbook/spellbook.py:136-224
  - src/melder/spellbook/spellbook.py:2598-2750
  - src/melder/spellbook/spellbook.py:3379-3560
  - src/melder/spellbook/bind/bind.py:57-250
  - src/melder/spellbook/spell.py:224-360
  - src/melder/aether/conduit/conduit.py:93-220
  - src/melder/aether/conduit/conduit.py:1251-1450
  - src/melder/aether/conduit/conduit.py:2362-2580
  IMPACT: Crystallizer should be discussed against live spell registration,
    room ownership, and explicit frame-link/runtime semantics, not generic
    module-loader assumptions.
  NEXT: restate the crystallizer semantics that should now be corrected based
    on this runtime reading.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T16:10:43Z
  TYPE: FACT
  CLAIM: The Rift codegen path is much more concrete than a generic "run some
    generated code" story. `CodegenRiftSpace` owns the internal
    `CodegenSystem` and attaches it to the room-owned `CodegenCommandSystem`.
    The command facade owns the room-facing `validate_codegen(...)` and
    `execute_codegen(...)` seams plus the full-source memory emission wrapper.
    `CodegenSystem` itself owns transaction construction, projection-aware
    namespace policy selection, validation, namespace building, compile/exec,
    and room-event publication through `CodegenMonitor`. That means codegen is
    already a governed room-native runtime facility, not a loose scripting
    helper.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:1-109
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:1-695
  - src/melder/aether/nexus/rift/codegen_system/codegen_system.py:1-460
  - src/melder/aether/nexus/rift/codegen_system/codegen_transaction_context.py:1-228
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py:1-175
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py:1-305
  - src/melder/aether/nexus/rift/codegen_system/validation/codegen_validator.py:1-234
  - src/melder/aether/nexus/rift/codegen_system/execution/codegen_compiler.py:1-62
  - src/melder/aether/nexus/rift/codegen_system/execution/codegen_executor.py:1-90
  - src/melder/aether/nexus/rift/codegen_system/observability/codegen_monitor.py:1-129
  IMPACT: Crystallizer and synthetic-module design should assume codegen already
    has a real transaction/validation/namespace/execution/event pipeline in the
    room, not treat codegen as an afterthought or only as mutation tooling.
  NEXT: use this runtime codegen model when reasoning about workstation
    retention, synthetic-module lifecycles, and spell-crystal creation
    boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T16:10:43Z
  TYPE: FACT
  CLAIM: The current codegen runtime does not create module-backed provenance
    by default. `CodegenNamespace` is just a live `globals_dict` /
    `locals_dict` container plus metadata, and `CodegenExecutor` runs `exec(...)`
    directly against that namespace. So objects created by current codegen are
    namespace-backed values, not synthetic-module-backed values, unless we add a
    new module embodiment step ourselves.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace.py:1-158
  - src/melder/aether/nexus/rift/codegen_system/execution/codegen_executor.py:1-90
  IMPACT: This is the direct reason bind provenance is currently weak for
    codegen-origin values. The present runtime has no module identity layer to
    attach those created objects to by default.
  NEXT: use this exact namespace-backed execution fact when deciding whether
    each codegen iteration should automatically materialize as a synthetic
    module before binding is allowed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T23:48:49Z
  TYPE: FACT
  CLAIM: The live attachment boundary is now sharper than the artifact lane had
    made explicit. `Spell` owns runtime-phase, creation-context, and mutation
    state but still carries no crystallizer or provenance field. `SpellCrystal`
    and `SyntheticModule` are standalone crystallizer-layer contracts, while
    the live codegen path is `CodegenRiftSpace -> CodegenCommandSystem ->
    CodegenSystem` and `Rift` owns the frame-link contracts plus installed
    view/command/codegen projection sets. The first real crystallizer handoff
    therefore still needs a deliberate attachment path instead of piggybacking
    on preexisting spell-side source ownership.
  EVIDENCE:
  - src/melder/spellbook/spell.py:31-352
  - src/melder/spellbook/spell.py:1501-1649
  - src/melder/crystallizer/spell_crystal.py:7-686
  - src/melder/crystallizer/synthetic_module.py:6-455
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:1-109
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:27-769
  - src/melder/aether/nexus/rift/codegen_system/codegen_system.py:1-460
  - src/melder/aether/nexus/rift/rift.py:28-928
  IMPACT: The next crystallizer slice should choose the smallest honest handoff
    between Bind/Spell/runtime ownership and crystallizer records instead of
    assuming source/provenance already lives on the spell.
  NEXT: decide whether the first live handoff belongs on `Spell`, on the Bind
    path, or at the codegen/synthetic-module promotion boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T09:27:48Z
  TYPE: PLAN
  CLAIM: The next world-first read tranche is the synthetic-module experiment
    lane under `tests/experimentation/`. The concrete source readset is four
    testbenches, and two of them exceed the 500-line manual read cap, so the
    experiment pass needs explicit chunked reads rather than one-shot dumps.
  EVIDENCE:
  - user_instruction: "ok so just understand your working on world first new shit, go read test/experimentation syntheticmodules"
  - filesystem_inventory:
    - tests/experimentation/pytest_synthetic_module_testbench.py (247 LOC)
    - tests/experimentation/synthetic_module_import_testbench.py (434 LOC)
    - tests/experimentation/unittest_synthetic_module_edge_cases_testbench.py (803 LOC)
    - tests/experimentation/unittest_synthetic_module_testbench.py (582 LOC)
  IMPACT: The active crystallizer/runtime lane is now grounded not just in live
    runtime ownership but also in the concrete synthetic-module experiment
    suite that has been shaping the current design assumptions.
  NEXT: read the four source testbenches, chunk the two large unittest files,
    and extract the runtime assumptions they prove about synthetic modules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T09:28:22Z
  TYPE: FACT
  CLAIM: The synthetic-module experiment suite proves a much richer same-process
    world than the live runtime currently exposes by default: direct unittest
    loading from synthetic module objects, import-hook loading by fully
    qualified synthetic module name, pytest bridge files against preloaded
    synthetic helpers, deep package/submodule graphs, circular imports,
    aggressive sibling patching, lifecycle hooks, concurrent import/use,
    unload/reactivate cycles, collision authority behavior, and file-backed
    morph interaction. But those proofs currently live in bench-local
    `SyntheticModule` / `SyntheticModuleLoader` implementations rather than the
    production `src/melder/crystallizer/` classes or the live codegen runtime.
  EVIDENCE:
  - tests/experimentation/pytest_synthetic_module_testbench.py:1-247
  - tests/experimentation/synthetic_module_import_testbench.py:1-434
  - tests/experimentation/unittest_synthetic_module_testbench.py:1-582
  - tests/experimentation/unittest_synthetic_module_edge_cases_testbench.py:1-803
  IMPACT: The benches justify the world-first crystallizer direction, but they
    also show the current gap clearly: production runtime still needs an
    explicit promotion path from namespace-backed or bench-local synthetic
    module behavior into the actual crystallizer/runtime boundary.
  NEXT: compare the bench-local loader/module contract against
    `src/melder/crystallizer/spell_crystal.py`,
    `src/melder/crystallizer/synthetic_module.py`, and the current
    codegen/bind path to choose the first production integration slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T09:40:45Z
  TYPE: TRADEOFF
  CLAIM: Letting `SpellCrystal` initialize from `ISpell` directly would reduce
    call-site boilerplate, but the current `ISpell` surface still does not
    carry the persisted-source fields a crystal needs. `ISpell` exposes
    identity, lifecycle, profile, dependency, owner-conduit, and mutation
    state, but not `module_name`, `source_text`, `source_sha256`, or
    `source_authority_kind`. So a constructor that only accepts `ISpell` would
    either hide additional source-resolution work inside the crystal class or
    force the crystal to depend on live runtime-only semantics too early.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:362-1043
  - src/melder/crystallizer/spell_crystal.py:28-167
  - src/melder/crystallizer/synthetic_module.py:27-107
  - src/melder/spellbook/spell.py:31-352
  IMPACT: The cleaner first move is likely a `from_spell(...)` factory or
    builder that snapshots `ISpell` identity plus separately resolved source
    truth, rather than collapsing all extraction logic into
    `SpellCrystal.__init__`.
  NEXT: decide whether the first production handoff should be a crystal factory
    on the bind path or a synthetic-module promotion boundary that already has
    source/module truth in hand.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T11:01:42Z
  TYPE: FACT
  CLAIM: The live mutation code already thinks in lineage-first,
    conduit-gated terms. `Conduit` exposes mutation research only for normal
    conduits in dynamic mode, and `MutationResearch` anchors sessions to
    stable `SpellIndex.id` lineage while treating concrete `spell_id` values as
    versions under that lineage. The current code has promotion of new spell
    versions, but it does not yet define explicit branch/head/rebase/merge
    semantics.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:3970-4004
  - src/melder/spellbook/mutations/mutation_research.py:11-64
  - src/melder/spellbook/mutations/research/research.py:13-41
  - src/melder/spellbook/mutations/research/research.py:337-408
  IMPACT: Treating mutation manifests as conduit-level snapshot content fits
    the current runtime better than making mutation a free-floating spell-only
    persistence concern. Branch/fork semantics remain an open layer above the
    current lineage/version model.
  NEXT: discuss whether forks should create a new lineage, a new head under the
    same lineage, or a conduit-local parallel binding surface when multiple
    versions need to coexist.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded runtime reorientation pass for crystallizer design.
