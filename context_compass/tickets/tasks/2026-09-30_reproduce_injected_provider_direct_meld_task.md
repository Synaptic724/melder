

# Task: Reproduce and explain the failed direct meld of an injected provider on current Melder source

## Metadata
- Task ID: TASK-2026-09-30-reproduce-injected-provider-direct-meld
- Story: none; carries work packages A and B of EPIC-2026-09-30-injected_dependency_direct_resolution
  (tickets/epics/2026-09-30_injected_dependency_direct_resolution_epic.md)
- Status: review
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-30T16:18:36Z
- Updated: 2026-09-30T17:03:33Z

## Objective
Owner direction (chat, 2026-09-30): "also please take on this epic too # Epic: Make an injected dependency directly
resolvable from the same Melder scope this is important". This task is the epic's first tranche: reproduce the
failure (a unique_per_conduit service injected into a consumer through a lesser conduit, then a direct meld of the
service from that lesser raising "Cannot build CreationContext before spell_codegen_creation exists") on current
melder_private source without the MelderOps Spectrum host, reduce it to the smallest native sequence, and establish
from source which readiness or publication step leaves the service without its creation payload - ending in a
repair proposal for the owner. No source edit in this task.

## Ticket Contract
- ENTRY_GATE: the owner's assignment; this board row; the epic's starting FACT noted before any probe.
- EXECUTION_BOUNDARY: read-only in src/ (Conduit.meld, ConduitMeld.meld, Meld._execute_admitted and its
  revalidation gates, Spell._get_or_build_creation_context, CreationContextFactory, CreationContextBuilder, the
  Spellbook's meld-time resolution entry points and the compiler phases 5-11 publication); probes and logs under
  artifacts/injected_provider_direct_meld_20260930/; runs in the VM mirror (~/wt2_new, 3.14.7t, GIL off).
- DEPENDENCIES: the epic and its evidence bundle, the shared context rebuild windows (2026-09-26), which touched
  the same guard. Evidence bundle:
  artifacts/2026-09-30_injected_dependency_direct_resolution/
- EXIT_GATE: the reproduction result on current source and its variation matrix (MEASURE); the cause with source
  ranges (FACT); a DECISION_REQUEST with repair options; status review.
- FAILURE_ESCALATION: if bare Melder does not reproduce, record the host difference as the finding and reproduce
  through the MelderOps environment before asking the owner; BLOCKER if the VM cannot run the probe.

## Scope Boundaries
- In scope: the epic's work packages A (reproduce and reduce) and B (the violated invariant).
- Out of scope: the repair itself (work package C, after the owner's pick), the MelderOps consumer revalidation
  (work package D), and the separate MelderOps Toolbox fixture failure (missing root_conduit argument).

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: (2026-09-30T16:33:36Z) reproduced on bare Melder, matrix run, cause read from source;
  DECISION_REQUEST filed. Earlier: draft -> in_progress (2026-09-30T16:18:36Z, the owner's assignment).

## Steps / Checklist
- [x] Confirm the installed 0.2.8212 files at the failure boundary match current source.
- [x] Bare-Melder probe of the diagnostic body (dynamic root, late binds, named lesser); record the outcome.
- [x] Variation matrix: root versus lesser, provider first, binds before conjure, service lifetimes, creation cache.
- [x] Read the failing call path and the readiness/publication path that should give the service its payload.
- [x] Record the cause and the smallest repair boundary; file a DECISION_REQUEST with repair options.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Probe script, run records and notes; the cause with evidence; repair options for the owner.

## Files / Paths Impacted
- None in the repository tree (investigation); artifacts only.

## Validation
- Not run.
- Recommended commands:
  - the probe commands recorded in the MEASURE notes

## Risks / Rollback Notes
- Read-only; nothing to roll back.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No catch-and-retry or guard removal proposed as the repair before the cause is established.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/injected_provider_direct_meld_20260930/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the epic's closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-30T16:18:36Z
  TYPE: FACT
  CLAIM: Starting point, from the epic's evidence. On installed Melder 0.2.8212 (Windows, 3.14.7t, GIL off) a
    Spectrum-prepared dynamic root gets two late binds - NativeService (unique_per_conduit) and NativeConsumer (many,
    requiring NativeService) at spellframe native_probe - then a named lesser melds the consumer (its service holds
    value 7) and a direct meld of NativeService from the same lesser raises "Cannot build CreationContext before
    spell_codegen_creation exists" from CreationContextBuilder.build, reached through Meld._execute_admitted and
    Spell._get_or_build_creation_context. The three installed files at that boundary (meld.py,
    creation_context_factory.py, creation_context_builder.py) are byte-identical to current melder_private source
    and to the VM mirror (sha256 0c3239b0476b96a1, be275f0a16588b5c, 49100a2cc7bb7a1a; the epic's manifest).
  EVIDENCE:
  - tickets/epics/2026-09-30_injected_dependency_direct_resolution_epic.md:473-488
  - artifacts/2026-09-30_injected_dependency_direct_resolution/test_native_dependency_lookup.py:25-35
  - artifacts/2026-09-30_injected_dependency_direct_resolution/native_dependency_lookup.xml:1-17
  - artifacts/2026-09-30_injected_dependency_direct_resolution/evidence_manifest.json
  IMPACT: The failure boundary is current source, not an older wheel; whether bare Melder reproduces it (without the
    Spectrum host) is the first open question.
  NEXT: Write the bare-Melder probe of the diagnostic body and run it in the VM mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T16:23:24Z
  TYPE: MEASURE
  CLAIM: Reproduced on bare Melder, current source, without the Spectrum host. Probe (VM mirror of 0.2.8212,
    3.14.7t, GIL off, system caching off, fresh process): an empty Book postured dynamic through
    configure_aether_frame, conjured as a named root; root.bind of NativeService (unique_per_conduit) and
    NativeConsumer (many) at spellframe native_probe; a named lesser melds the consumer (service value 7), then
    melds NativeService directly and raises the epic's RuntimeError through the same frames and lines as the
    installed traceback (conduit.py:4845, conduit_meld.py:593, meld.py:882, spell.py:847,
    creation_context_factory.py:361, creation_context_builder.py:121). Right after the consumer meld the service
    spell has a compiler artifact but no codegen payload and no creation context; a second direct meld raises
    the same way, and a second consumer meld succeeds and reuses the same stored service.
  EVIDENCE:
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs/diagnostic_cacheoff.txt:1-1
  - context_compass/artifacts/injected_provider_direct_meld_20260930/direct_meld_probe.py:101-173
  IMPACT: Neither the MelderOps host nor a warm creation cache is needed; the defect is native, and the service's
    payload is absent (not stale) after its injection succeeded, so the direct path finds nothing to build from.
  NEXT: Run the variation matrix (root scope, unnamed lesser, provider first, binds before conjure, other service
    lifetimes, sibling scopes, cache on cold and warm).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T16:24:14Z
  TYPE: MEASURE
  CLAIM: Variation matrix, same probe, one fresh process per run. FAILS the same way (direct service meld raises;
    the service has no codegen payload and no creation context after the consumer meld; a consumer re-meld keeps
    reusing its stored service): melding on the root instead of a lesser; an unnamed lesser; a root holding an
    unrelated spell at conjure; the service bound many or unique instead of unique_per_conduit; each of two
    sibling lessers; system caching on, cold and warm (same frame run twice). PASSES: the direct service meld
    first (then the consumer receives that same object, and a second direct meld works); and both binds made on
    the Book before conjure (the service already has its payload after the consumer meld; the direct meld returns
    the consumer's service, identity true).
  EVIDENCE:
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs/root_scope_cacheoff.txt:1-1
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs/anonymous_lesser_cacheoff.txt:1-1
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs/resident_cacheoff.txt:1-1
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs/service_many_cacheoff.txt:1-1
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs/service_unique_cacheoff.txt:1-1
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs/sibling_scopes_cacheoff.txt:1-1
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs/diagnostic_cacheon_cold.txt:1-1
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs/diagnostic_cacheon_warm.txt:1-1
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs/provider_first_cacheoff.txt:1-1
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs/binds_before_conjure_cacheoff.txt:1-1
  IMPACT: The trigger is narrow and common: a provider bound after conjure whose first resolution happens as a
    consumer's dependency. Scope kind, lifetime and cache are irrelevant; conjure-time binds are safe because
    conjure resolves and publishes for every owned spell. HYPOTHESIS: meld-time resolution for the consumer
    marks the dependency resolvable for the conduit without publishing the dependency's own codegen payload, so
    the service's later direct meld skips its own resolution and reaches the builder with nothing to build.
  NEXT: Read the meld path: ConduitMeld.meld, Meld._execute_admitted and its revalidation gates, then the
    Spellbook's meld-time resolution entry and phases 5-11 publication.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T16:28:30Z
  TYPE: FACT
  CLAIM: The cause, read from source and confirmed by state reads in the probe. (1) The consumer's first meld runs
    target-local resolution (Meld._ensure_resolution_resolvable -> run_resolution_phases_for_target_spell). Its
    Phase 5 builds the index and blueprints over the consumer's whole dependency closure but attaches artifacts
    only to publication_spell_ids=(target,) - the service gets no Phase 5 root blueprint and phases 8-11 build no
    payload for it (the 2026-09-19 publication restriction). (2) Phase 6 local then validates that graph and
    SpellSystemValidationSystem._record_conduit_resolution_state stamps SpellValidity.valid on EVERY node of the
    local index for the conduit - the service included - although this pass established nothing for it.
    (3) The direct service meld reads its verdict through Meld._get_resolution_validity: the service is not a
    Phase 5 root (is_current_spell_phase5_root is False without a blueprint), so its spell validity answers -
    valid - and _ensure_resolution_resolvable returns without resolving it; _execute_admitted then asks
    CreationContextBuilder.build for a context and the guard raises on the absent payload. Probe state: before
    the consumer meld the root's resolution state does not exist; after it the service reads spell validity valid,
    root validity unknown, no blueprint, no payload, no context. Controls: a direct meld first resolves the service
    as its own target (payload, blueprint, context, both verdicts valid); binds before conjure get payloads from
    conjure's conduit-wide pass, which publishes for every owned spell.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:628-729
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:318-383
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:394-512
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py:105-268
  - src/melder/aether/conduit/meld/meld.py:1141-1202
  - src/melder/aether/conduit/meld/meld.py:1369-1392
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:644-684
  - src/melder/aether/conduit/meld/meld.py:826-891
  - src/melder/aether/conduit/meld/conduit_meld.py:558-598
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:69-152
  - src/melder/aether/spellbook/spellbook_creation_system.py:1654-1754
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs/diagnostic_cacheoff_state.txt:1-1
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs/provider_first_cacheoff_state.txt:1-1
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs/binds_before_conjure_cacheoff_state.txt:1-1
  IMPACT: The violated invariant: a conduit-local "valid" verdict must mean the spell is resolved for direct use on
    that conduit (its own payload published), but local Phase 6 writes it for dependencies the pass did not publish.
    The guard is right; the verdict is wrong. Any provider bound after conjure and first reached as a dependency is
    affected, whatever its lifetime or scope. RiskManager reads the same verdict (risk model only).
  NEXT: Write the repair options (verdict scope at local Phase 6; meld-side readiness check; publishing dependency
    payloads) with their costs and file the DECISION_REQUEST.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-30T16:33:36Z
  TYPE: MEASURE
  CLAIM: The Book-wide validation flag (Spellbook._spellbook_validation_required, driven by RiskManager from the
    conduit-local verdicts) is raised after the two late binds and cleared once the consumer's pass stamps both
    verdicts valid, so the failing direct meld does not enter the validation lane at all (ConduitMeld.meld runs
    _ensure_lineage_resolvable only while the flag is raised; it reads spell.resolution_required on every meld).
  EVIDENCE:
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs/diagnostic_cacheoff_flag.txt:1-1
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:597-655
  - src/melder/aether/conduit/meld/conduit_meld.py:558-562
  - src/melder/aether/conduit/meld/spellspace_meld.py:524-528
  IMPACT: Any repair that keeps a dependency's verdict below valid also keeps this flag raised for the whole Book, so
    every meld on it would run the validation lane; that is the cost that separates the repair options.
  NEXT: File the DECISION_REQUEST.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T16:33:36Z
  TYPE: DECISION_REQUEST
  CLAIM: Owner pick needed for the repair (the epic's work package C); nothing in src/ has changed. Options:
    A. Truthful verdict at its writer: local Phase 6 stamps valid only on the pass's target and on dependencies
       that already have their own plan. The service stays unknown and its first direct meld takes the existing
       validation lane (the full target pass). Cost: RiskManager keeps the Book's validation flag raised while any
       such dependency exists, so every meld of that Book runs the validation lane (including an inspect.signature
       contract scan per meld) until each one is melded directly - possibly never in hosts that bind late.
    B. Resolve on first direct use (recommended). The consumer's target pass flags each owned dependency that has no
       plan of its own (no Phase 5 blueprint, payload or context; not an existing object) with resolution_required,
       the per-spell "work pending before the next meld" flag every meld door already reads; the deferred lane
       (Meld._ensure_runtime_resolution_ready) runs the full target pass (phases 5-11) for a spell with no Phase 5
       blueprint and keeps today's 8-11 pass for the rest. The first direct meld builds the service's own plan and
       returns the object the consumer's plan stored (identity kept, as the provider-first control shows). Warm
       melds, verdicts and the validation flag are unchanged. It departs from one stated rule - post-conjure spells
       compile through the gated revalidation lane, never a deferred flag - because that lane is closed once the
       flag clears; the rule's reason (the deferred lane cannot compile without a blueprint) is removed by the lane
       change. Files: spellbook_creation_system.py (target pass tail), meld.py (deferred lane); a symptom-named
       component regression plus root, sibling and lifetime variants; patch docs, notch, release note, rebuild.
    C. Publish dependency plans inside the consumer's pass: every first consumer meld also compiles its unpublished
       dependencies, and publishing to them needs their rebuild windows and locks inside the consumer's (a new lock
       order). Heavier and riskier; not recommended.
    Not an option: removing the builder guard, or catching its error and retrying - the guard is right.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:966-1019
  - src/melder/aether/conduit/meld/meld.py:1204-1319
  - src/melder/aether/spellbook/spellbook.py:5382-5385
  - src/melder/aether/spellbook/spellbook.py:3798-3807
  - src/melder/aether/spellbook/spellbook_creation_system.py:1757-1825
  - src/melder/aether/spellbook/spellbook_creation_system.py:1654-1754
  IMPACT: Until a pick lands, a provider bound after conjure cannot be melded directly once a consumer has
    received it; the host workaround is to meld the provider directly first, or to bind it before conjure.
  NEXT: Owner picks A, B or C (or drops it); the pick opens work package C as a patch lane (Propose -> Confirm).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-30T17:03:33Z
  TYPE: MEASURE
  CLAIM: Host-side confirmation from command_0 (two mailbox NOTICEs, 16:42:33Z and 16:46:08Z, consumed here):
    installed 0.2.8212 in MelderOps, a fresh Aether per case (the isolation fixture asserts no Spectrum and no
    frames before the host is built), the original ScopeService (unique_per_conduit) and AssistedTool. The service
    alone melds; service first, then AssistedTool built through Toolbox, gets the same service object; AssistedTool
    first, then a direct ScopeService meld, raises the missing-payload RuntimeError through the same frames
    (conduit.py:4845 down to creation_context_builder.py:121). Same order dependence as the bare-Melder matrix
    (provider_first passes, the consumer-first diagnostic fails).
  EVIDENCE:
  - priv_commandops/context_compass/artifacts/2026-09-30_toolbox_native_dispense/test_dependency_resolution_order.py:17-63
  - priv_commandops/context_compass/artifacts/2026-09-30_toolbox_native_dispense/resolution_order.xml:1-17
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs/provider_first_cacheoff.txt:1-1
  IMPACT: The host and the bare runtime agree on the trigger (a provider first reached as a dependency has no plan
    of its own); the repair options and the recommendation are unchanged.
  NEXT: The owner's repair pick; the lane stays parked behind the per-frame spell-id lane.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Opened 2026-09-30T16:18:36Z on the owner's assignment of the epic; in review since 2026-09-30T16:33:36Z. Read-only.
Result: reproduced on bare Melder at 0.2.8212 (no Spectrum, cache on or off): a provider bound after conjure and
first built as a consumer's dependency cannot be melded directly afterwards, in any scope or lifetime. Cause: the
consumer's target-local pass publishes only the consumer, yet local Phase 6 stamps the dependency's conduit verdict
valid, and the Book's validation flag then clears, so the direct meld never resolves the dependency and the
builder's (correct) guard raises. Repair options A/B/C are in the DECISION_REQUEST (recommendation B: resolve on
first direct use through the deferred lane). Next: the owner's pick. Probe:
artifacts/injected_provider_direct_meld_20260930/ (direct_meld_probe.py, direct_meld_services.py, runs/).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
