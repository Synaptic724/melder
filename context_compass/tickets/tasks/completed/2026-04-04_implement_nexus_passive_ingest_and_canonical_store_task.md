# Task: Implement Nexus Passive Ingest And Canonical Store

- Completed: 2026-04-04T11:41:38Z
- Summary: Added the first Nexus canonical store and passive-ingest path,
  wired frame/spell/root-conduit publication, refined the Conduit-side publish
  events, and extended `FrameRecord` with cheap topology summary fields.

## Metadata
- Task ID: TASK-2026-04-04-implement-nexus-passive-ingest-and-canonical-store
- Story: STORY-2026-04-03-frameinfolink-hld
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-04T07:46:28Z
- Updated: 2026-04-04T11:41:38Z

## Objective
Implement the Nexus-side canonical record store and the passive ingest path so
frame/conduit/spell records can stay current before interactive Nexus/Rift
enablement is turned on.

## Ticket Contract
- ENTRY_GATE: the frame-level posture prerequisite is now implemented and the
  user has returned to the Nexus passive-ingest lane as the next concrete
  runtime slice.
- EXECUTION_BOUNDARY: Nexus-side canonical store, direct private publication
  methods, passive ingest gating, and focused producer wiring only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-03_design_frameinfolink_hld_task.md
  - tickets/tasks/2026-04-03_implement_aetheric_frame_configuration_task.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/aetheric_frame.py
  - src/melder/aether/aetheric_frame_configuration.py
  - src/melder/spellbook/spellbook.py
  - src/melder/spellbook/bind/bind.py
  - src/melder/aether/conduit/conduit.py
  - src/melder/spellbook/spell.py
- EXIT_GATE: Nexus can host canonical live records for frame/conduit/spell
  data, accept passive updates through private methods before interactive
  enablement, and gate publication using frame posture.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the implementation forces a
  record-model or lifecycle choice not yet approved in the HLD.

## Scope Boundaries
- In scope:
  - Nexus-side canonical store object(s)
  - live mutable canonical `FrameRecord` / `ConduitRecord` / `SpellRecord`
  - private direct publication methods on `Nexus`
  - passive ingest distinct from interactive `Nexus.enable(...)`
  - publication gating on `rift_enabled`
  - initial producer wiring from the relevant runtime objects
- Out of scope:
  - full viewer/query integration
  - full ACL matrix implementation
  - eventstream implementation
  - JSON/CommandOps transport work

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the first passive-ingest tranche is accepted as complete
  enough to archive while later viewer/repository work continues on top of the
  current store.

## Steps / Checklist
- [x] Define the first canonical store shape inside `Nexus`.
- [x] Implement `FrameRecord`, `ConduitRecord`, and `SpellRecord` as living
      Nexus-owned records.
- [x] Implement private direct publication methods on `Nexus`.
- [x] Gate publication on `AethericFrameConfiguration.rift_enabled`.
- [x] Keep passive ingest separate from interactive `Nexus.enable(...)`.
- [x] Wire the first producer paths into private Nexus publication.
- [x] Add focused tests around store lifecycle, publication gating, and
      interactive/passive separation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Nexus-side canonical store scaffold
- canonical living-record classes
- private publication methods
- passive ingest semantics
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/
- src/melder/spellbook/
- src/melder/aether/conduit/
- tests/unit/melder/aether/
- codex/context_compass/tickets/tasks/2026-04-04_implement_nexus_passive_ingest_and_canonical_store_task.md
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m py_compile src/melder/aether/nexus/canonical_store/frame_record.py src/melder/aether/nexus/canonical_store/conduit_record.py src/melder/aether/nexus/canonical_store/spell_record.py src/melder/aether/nexus/canonical_store/nexus_canonical_store.py src/melder/aether/nexus/nexus.py src/melder/spellbook/spellbook.py src/melder/spellbook/spellbook_creation_system.py src/melder/aether/conduit/conduit.py tests/unit/melder/aether/test_nexus_passive_ingest.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus_passive_ingest.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/spellbook/test_spellbook.py`

## Risks / Rollback Notes
- Risk: passive ingest and interactive enablement remain conflated.
  Rollback: keep store publication methods free of `_require_enabled()` and
  leave interactive gating only on Rift/public interaction paths.
- Risk: the implementation accidentally treats canonical records as snapshots
  or viewer payloads rather than living Nexus-owned state.
  Rollback: centralize mutation through Nexus-owned record/repository methods.
- Risk: producers reach around the store and mutate repository internals.
  Rollback: keep publication through private Nexus methods only.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/architecture_patch.md
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/component_patch_nexus.md
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/component_patch_spellbook.md
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/component_patch_conduit.md
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/code_description_patch_nexus.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-04T11:20:00Z
  TYPE: FACT
  CLAIM: The next reasonable `FrameRecord` expansion is cheap topology summary,
    not deep subsystem state. The real frame-owned data sources already exist:
    `AethericFrame._conduits` for root conduit inventory,
    `AethericFrame._conduit_cloud._registry` for named cloud entries, and
    `AethericFrame._conduit_clusters` for cluster names. That makes the
    following additions cheap enough to derive inside
    `Nexus._publish_frame_record(...)`: `config_origin_spellbook_id` (rename of
    the current weak provenance field), `root_conduit_count`,
    `root_conduit_ids`, `named_root_conduits`, `conduit_cloud_entry_count`,
    `conduit_cloud_names`, `cluster_count`, and `cluster_names`. By contrast,
    lineage/version counts are real frame data but not worth adding to the
    first overview layer right now. If we only add cluster names/counts, frame
    republish must happen on root conjure, lesser->normal promotion, normal
    cleanup, cloud register/unregister, and cluster create/delete. Join/leave
    only matter if we later decide to add cluster member counts.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:63-84
  - src/melder/aether/conduit_cloud.py:24-35
  - src/melder/aether/conduit/conduit_cluster.py:22-47
  - src/melder/spellbook/spellbook.py:3033-3055
  - src/melder/aether/aether.py:538-586
  - src/melder/aether/aether.py:736-900
  - src/melder/aether/conduit/conduit.py:741-852
  - src/melder/aether/conduit/conduit.py:1096-1286
  - src/melder/aether/conduit/conduit.py:2184-2229
  IMPACT: We can make `FrameRecord` materially more useful for orientation
    without turning it into a subsystem dump or adding high write overhead.
  NEXT: extend `FrameRecord` and `Nexus._publish_frame_record(...)` with the
    cheap topology summary fields, then republish frame state at the narrow
    event points that actually change those fields.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T10:30:00Z
  TYPE: FACT
  CLAIM: The current Conduit-side passive-ingest hooks are close but still
    incomplete. The runtime already publishes/removes normal conduit records on
    link, sever, and normal cleanup, and lesser conduits inherit the
    `_nexus_publish_enabled` flag without publishing by default. The remaining
    concrete gaps are: `upgrade_to_normal(...)` does not publish the newly
    normal conduit into Nexus, `set_new_policy(...)` mutates a record-visible
    field without republishing, and the new owned `_nexus` reference is not
    explicitly nulled during cleanup. These are all within the intended first
    Conduit publication boundary and do not require broad store redesign.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1264-1349
  - src/melder/aether/conduit/conduit.py:1096-1240
  - src/melder/aether/conduit/conduit.py:196-361
  - src/melder/aether/conduit/conduit.py:2462-2564
  - src/melder/aether/conduit/conduit.py:1242-1263
  IMPACT: The passive-ingest slice should add these missing Conduit-side
    publication transitions before we build more on top of the current record
    model, otherwise Nexus can miss normal-conduit promotion and policy
    changes while also carrying one more uncleared owned reference at teardown.
  NEXT: patch `Conduit` so normal-conduit cleanup nulls `_nexus`, promotion to
    normal republishes, and policy changes republish when Nexus publication is
    enabled.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T07:46:28Z
  TYPE: DECISION
  CLAIM: The implementation plan is now concrete. Passive ingest should accept
    direct private publication into `Nexus` from the existing internal runtime
    objects rather than routing through `Aether` or waiting for interactive
    enablement. Publication should be gated by the bound frame posture: if
    `rift_enabled` is false, nothing publishes; if true, Nexus may
    receive and store canonical updates even while `Nexus.enable(...)` remains
    off. Interactive enablement should continue to gate only Rift creation and
    direct interaction.
  EVIDENCE:
  - user_instruction: "they publish directly to the nexus not the aether"
  - user_instruction: "if the system is not enabled for that conduit, then it does nothing"
  - user_instruction: "if the nexus is not enabled it still receives those updates"
  - src/melder/aether/nexus/nexus.py:323-351
  - src/melder/aether/aetheric_frame_configuration.py:1-233
  IMPACT: The next code slice should focus on private Nexus publish methods,
    lazy canonical store creation, and frame-posture publication gating rather
    than building a backfill/catch-up mechanism after interactive enablement.
  NEXT: define the initial repository/store object shape and the first private
    Nexus publish methods before wiring Spellbook/Bind/Conduit into them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T07:54:30Z
  TYPE: FACT
  CLAIM: The current runtime seams confirm the first passive-ingest boundary.
    Spellbook already owns the cleanest spell publication point at
    `Spellbook.bind(...)`, where a fully built `Spell` with binding profile and
    local registry identity exists. Conduit already owns the cleanest conduit
    publication points at construction/link/sever/cleanup. Nexus already has a
    hard split between interactive methods that require `_require_enabled()`
    and internal validation helpers that do not. Combined with the new
    `AethericFrameConfiguration`, this supports a straightforward first slice:
    private direct publication into Nexus from runtime producers, gated only by
    `frame_configuration.rift_enabled`, while `Nexus.enable(...)`
    continues to gate only Rift/public interaction.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:2358-2508
  - src/melder/aether/conduit/conduit.py:63-193
  - src/melder/aether/conduit/conduit.py:2456-2555
  - src/melder/aether/conduit/conduit.py:193-361
  - src/melder/aether/nexus/nexus.py:323-351
  - src/melder/aether/nexus/nexus.py:483-555
  - src/melder/aether/aetheric_frame_configuration.py:1-233
  IMPACT: We do not need a separate event bus or Aether proxy for the first
    ingest slice. The next implementation step can stay narrow: add the Nexus
    canonical store plus private publish methods and wire those producer seams
    directly into it.
  NEXT: implement the first canonical store shape inside `Nexus` and add the
    private publish methods before touching producer call sites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T08:00:00Z
  TYPE: FACT
  CLAIM: The passive-ingest slice is now patch-gated properly. A dedicated
    active patch set exists covering the system-level scope, the Nexus store
    boundary, the Spellbook publication boundary, the Conduit publication
    boundary, and the Nexus-side publication/gating control flow. This makes
    the next implementation step compliant with the patch-framework gate
    instead of relying on chat memory.
  EVIDENCE:
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/architecture_patch.md:1-61
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/component_patch_nexus.md:1-37
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/component_patch_spellbook.md:1-37
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/component_patch_conduit.md:1-34
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/code_description_patch_nexus.md:1-39
  IMPACT: The task now satisfies the required patch-artifact entry gate for a
    system-impacting implementation slice.
  NEXT: map the patch sections into the first concrete Nexus store
    implementation steps before editing runtime code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T08:03:00Z
  TYPE: PLAN
  CLAIM: The patch-set-to-implementation mapping for the first runtime tranche
    is now explicit.
  EVIDENCE:
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/architecture_patch.md:9-40
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/component_patch_nexus.md:1-37
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/component_patch_spellbook.md:1-37
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/component_patch_conduit.md:1-34
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/code_description_patch_nexus.md:1-39
  IMPACT: The next edit tranche can stay narrow and auditable.
  NEXT: implementation mapping:
    1. `architecture_patch.md`
       -> add the first canonical store shape and publication gate split inside `Nexus`
       -> validate passive vs interactive separation in focused tests
    2. `component_patch_nexus.md`
       -> add living record classes/store ownership/private publish methods
       -> keep store/index mutation centralized in Nexus
    3. `component_patch_spellbook.md`
       -> wire frame publication on conjure
       -> wire spell catch-up publication on conjure
       -> wire spell incremental publication on bind-after-conjure
    4. `component_patch_conduit.md`
       -> wire root conduit publication/update/remove on conjure/link/sever/cleanup
       -> do not publish ordinary lesser conduits in this slice
    5. `code_description_patch_nexus.md`
       -> enforce publishability check from frame posture
       -> keep `_require_enabled()` off passive publication paths
       -> keep primary store + secondary index mutation in one Nexus-owned path
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T09:19:22Z
  TYPE: FACT
  CLAIM: The first passive-ingest tranche is now implemented. Nexus now owns a
    canonical-store package with `FrameRecord`, `ConduitRecord`,
    `SpellRecord`, and `NexusCanonicalStore`; private Nexus publish/remove
    methods centralize primary-store and secondary-index mutation; Spellbook
    now publishes frame state on conjure, publishes existing local spells on
    conjure catch-up, and publishes incremental spell records on
    bind-after-conjure; Conduit now updates/removes root conduit records on
    link/sever/cleanup while ignoring ordinary lesser conduits. Focused passive
    ingest tests passed, and the existing Nexus and Spellbook unit surfaces
    still passed after the runtime wiring landed.
  EVIDENCE:
  - src/melder/aether/nexus/canonical_store/frame_record.py:1-90
  - src/melder/aether/nexus/canonical_store/conduit_record.py:1-97
  - src/melder/aether/nexus/canonical_store/spell_record.py:1-134
  - src/melder/aether/nexus/canonical_store/nexus_canonical_store.py:1-320
  - src/melder/aether/nexus/nexus.py:1-1244
  - src/melder/spellbook/spellbook.py:118-3077
  - src/melder/spellbook/spellbook_creation_system.py:144-310
  - src/melder/aether/conduit/conduit.py:63-2684
  - tests/unit/melder/aether/test_nexus_passive_ingest.py:1-213
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus_passive_ingest.py
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/spellbook/test_spellbook.py
  IMPACT: Nexus can now host canonical living records before interactive
    enablement, using frame posture as the publication gate, and the first
    viewer/store prerequisite is materially real instead of still only a design
    note.
  NEXT: review the first passive-ingest slice with the user and decide whether
    the next expansion should add spell removal/ownership-transfer publication,
    viewer consumption, or canonical store refinement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T10:02:00Z
  TYPE: FACT
  CLAIM: The first passive-ingest implementation still carries a few owned-code
    anti-patterns that should be removed before treating the slice as clean.
    Specifically, the recent code introduced defensive `getattr(...)` calls on
    known owned attributes (`_nexus_publish_enabled`) and a duck-typed
    `getattr(...)` helper lookup in Spellbook's frame-posture derivation path.
    The user explicitly rejected that style for owned code. The cleanup should
    replace those with direct owned-attribute access and a concrete type-driven
    branch where uncertainty is actually real.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:209-233
  - src/melder/aether/conduit/conduit.py:2514-2523
  - src/melder/aether/conduit/conduit.py:2565-2574
  - src/melder/spellbook/spellbook.py:2742-2746
  - src/melder/spellbook/spellbook.py:2991-2994
  IMPACT: The passive-ingest slice is functionally correct but should be
    cleaned to match the repo's owned-code access rules before we build more on
    top of it.
  NEXT: remove the introduced `getattr(...)` usage and pointless self-field
    caching from the passive-ingest runtime paths, then rerun focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T10:35:07Z
  TYPE: FACT
  CLAIM: The remaining Conduit-side publication gaps are now closed within the
    current first slice. `Conduit` now owns a narrow internal
    `_publish_conduit_record_to_nexus()` / `_remove_conduit_record_from_nexus()`
    pair, normal-conduit cleanup removes the record through that helper,
    `upgrade_to_normal(...)` now publishes the newly normal conduit,
    `set_new_policy(...)` now republishes because policy is record-visible
    state, and teardown now explicitly nulls the conduit-owned `_nexus`
    reference for both lesser and normal cleanup. Focused conduit dynamic,
    conduit lifecycle, conduit contracts, and passive-ingest tests all passed.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:241-289
  - src/melder/aether/conduit/conduit.py:293-386
  - src/melder/aether/conduit/conduit.py:1096-1242
  - src/melder/aether/conduit/conduit.py:1244-1265
  - src/melder/aether/conduit/conduit.py:2462-2564
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:129-148
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:314-347
  - tests/unit/melder/aether/conduit/test_conduit_lifecycle.py:358-407
  - command:python -m pytest -q tests/unit/melder/aether/conduit/test_conduit_dynamic.py tests/unit/melder/aether/conduit/test_conduit_lifecycle.py tests/unit/melder/aether/test_nexus_passive_ingest.py
  - command:python -m pytest -q tests/unit/melder/aether/conduit/test_conduit_contracts.py
  IMPACT: The current Conduit publication boundary now consistently covers the
    record-visible lifecycle events we said this first slice should own:
    link, sever, policy change, promotion to normal, and cleanup. Ordinary
    lesser creation still remains intentionally non-publishing.
  NEXT: review this narrowed Conduit refinement with the user and only expand
    ConduitRecord events further if the record model itself grows new fields.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T11:39:25Z
  TYPE: FACT
  CLAIM: `FrameRecord` is now more useful as an overview record without turning
    into a subsystem dump. The record now carries cheap frame-summary fields
    derived directly from `AethericFrame`: `config_origin_spellbook_id`,
    `root_conduit_count`, `root_conduit_ids`, `named_root_conduits`,
    `conduit_cloud_entry_count`, `conduit_cloud_names`, `cluster_count`, and
    `cluster_names`. `Nexus._publish_frame_record(...)` now snapshots those
    fields from the frame under the existing publish path. Republish hooks were
    added only at the narrow event points that actually change those summary
    fields in this first slice: lesser->normal promotion, conduit-cloud
    register/unregister, cluster create/delete, and normal conduit cleanup.
    We intentionally did not add lineage/version summaries or cluster member
    counts, so join/leave cluster does not republish frame state yet.
  EVIDENCE:
  - src/melder/aether/nexus/canonical_store/frame_record.py:1-128
  - src/melder/aether/nexus/nexus.py:752-793
  - src/melder/aether/conduit/conduit.py:374-420
  - src/melder/aether/conduit/conduit.py:781-852
  - src/melder/aether/conduit/conduit.py:1280-1309
  - src/melder/aether/conduit/conduit.py:2180-2194
  - tests/unit/melder/aether/test_nexus_passive_ingest.py:55-122
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:314-359
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:519-661
  - tests/unit/melder/aether/conduit/test_conduit_lifecycle.py:465-489
  - tests/unit/melder/aether/conduit/conftest.py:1-33
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus_passive_ingest.py tests/unit/melder/aether/conduit/test_conduit_dynamic.py tests/unit/melder/aether/conduit/test_conduit_lifecycle.py
  - command:python -m pytest -q tests/unit/melder/aether/conduit/test_conduit_contracts.py
  IMPACT: The frame-level overview is now strong enough to help an agent orient
    around root conduits, named cloud entrypoints, and cluster topology without
    paying the cost of deep subsystem aggregation on every publish.
  NEXT: review whether this frame overview is sufficient before adding any
    deeper viewer/tool aggregation surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task activates the passive Nexus ingest lane. The intended model is
private direct publication into `Nexus`, gated by `rift_enabled`, with
interactive `Nexus.enable(...)` remaining separate from canonical record
hosting. The latest refinement closed the remaining first-slice Conduit
publication gaps for policy change, lesser-to-normal promotion, and teardown
nulling of the owned Nexus reference, and extended `FrameRecord` with cheap
topology summary fields for root conduits, conduit-cloud entries, and clusters.
