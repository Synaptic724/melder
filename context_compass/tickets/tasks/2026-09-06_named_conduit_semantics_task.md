# Task: Discover conduit naming and compare tagged lifetime scopes

## Metadata
- Task ID: TASK-2026-09-06-named-conduit-semantics
- Story: none (owner-requested discovery)
- Status: review
- Owner: codex
- Agent Name: codex_1
- Priority: p2
- Created: 2026-09-06T16:48:36Z
- Updated: 2026-09-06T17:03:17Z

## Objective
Explain which Melder conduit/scope forms can be named, how names are registered and consumed,
and whether that is equivalent to Autofac's tagged/matching lifetime scopes.

## Ticket Contract
- ENTRY_GATE: Owner requested source-backed discovery and an Autofac comparison.
- EXECUTION_BOUNDARY: Relevant indexed system docs, complete source methods/call paths, focused
  existing tests or isolated diagnostic checks, official Autofac docs, and discovery records.
- DEPENDENCIES: Conduit, Spellbook/conjure, Aether/frame/cloud registration and existence semantics.
- EXIT_GATE: Name support, registration boundaries and lifetime implications are explained with evidence.
- FAILURE_ESCALATION: Ask before changing runtime APIs, lifetime behavior, names, or registries.

## Scope Boundaries
- In scope: normal/root, lesser/nested, upgraded conduits, Nexus-created roots, and SpellSpace naming.
- In scope: distinguish addressing/identity from service-instance lifetime selection.
- Out of scope: implementation, runtime fixes, CI changes, benchmarks, commits, pushes, or publication.
- Preserve concurrent workflow/version/generated-asset changes; do not regenerate assets for discovery.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Source tracing and naming probes are complete; owner is considering named lesser ergonomics.

## Steps / Checklist
- [x] Resolve relevant architecture/component slices and source methods.
- [x] Trace construction, name lookup, uniqueness and lifetime consumption.
- [x] Inspect focused tests and prove uncertain edges if needed.
- [x] Compare with official Autofac tagged lifetime semantics and report scope boundaries.

## Deliverables
- A concise support matrix and code-backed explanation, without source changes.

## Validation
- Three existing naming/upgrade integration tests passed (0.42s; pytest cache-write warning only).
- Isolated naming/lookup probe passed after source-path setup; all created roots/books were cleaned.
- No runtime implementation or asset regeneration was performed.

## Risks / Unknowns
- A conduit display/registry name may not select an instance-sharing lifetime.
- Lesser and upgraded conduits may have different registry participation from normal roots.
- Name uniqueness may be frame-local or process-global; verify before asserting.

## Artifact Links
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
Read one bounded call path completely, then record findings and exact evidence before continuing.

## Notes
- DATETIME: 2026-09-06T16:48:36Z
  TYPE: PLAN
  CLAIM: Start with the Conduit Runtime and ConduitCloud component slices, then follow their
    constructors and registration methods. Compare addressing with Autofac matching-scope lifetimes.
  EVIDENCE:
  - system_docs/src_components_index.md:51-56
  - https://docs.autofac.org/en/latest/lifetime/instance-scope.html
  IMPACT: Discovery only; do not assume name metadata determines resolution lifetime.
  NEXT: Verify indexes and read the selected component slices.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-06T16:52:51Z
  TYPE: FACT
  CLAIM: Frame registration accepts only normal conduits and requires a unique nonempty name
    within that frame. ConduitCloud reads the frame's same id/name maps; registration/lookup is
    not gated on dynamic mode. Lesser creation exposes only logger, and constructor configuration
    erases a lesser name. However, the public name setter merely assigns an unset _name, without
    a state check or registry update. Upgrade(name) changes a lesser into a normal lineage root
    and registers it. Component prose claiming dynamic-only cloud naming is stale against this source.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:160-196
  - src/melder/aether/aetheric_frame/aetheric_frame.py:340-378
  - src/melder/aether/aetheric_frame/conduit_cloud.py:321-389
  - src/melder/aether/conduit/conduit.py:1365-1384
  - src/melder/aether/conduit/conduit.py:1557-1630
  - src/melder/aether/conduit/conduit.py:1960-2142
  - src/melder/aether/conduit/conduit.py:2227-2385
  IMPACT: Separate supported named roots from a lesser metadata-label setter. Neither alone
    establishes an Autofac-style matching lifetime; verify the existence/store routing next.
  NEXT: Confirm default root names, lifetime routing and focused naming tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T16:57:00Z
  TYPE: FACT
  CLAIM: SpellbookCreationSystem supplies default when a conjure name is absent/empty, then
    constructs a normal conduit. Nexus supplies its configured root_conduit_name through the same
    public conjure path (builder default root). SpellSpace construction has no name/tag field.
    Existence declares six modes with no matching-name lifetime; reuse reads conduit/root stores
    keyed by spell id. Autofac matching lifetime scopes instead select a tagged ancestor scope.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:856-908
  - src/melder/nexus/nexus_frame_builder.py:195-218
  - src/melder/nexus/nexus_frame_manager.py:994-1030
  - src/melder/aether/conduit/spell_space/spell_space.py:97-206
  - src/melder/aether/conduit/creations/conduit_creations.py:65-97
  - src/melder/aether/conduit/meld/conduit_meld.py:556-608
  - src/melder/aether/spellbook/existence/existence.py:62-117
  - https://docs.autofac.org/en/latest/lifetime/instance-scope.html#instance-per-matching-lifetime-scope
  IMPACT: Naming/lookup and matching-scope lifetime are separate capabilities. A label-only
    lesser setter does not provide tagged lifetime ownership or cloud registration.
  NEXT: Run existing root/upgrade naming tests and a small isolated label/lookup probe.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T16:58:10Z
  TYPE: MEASURE
  CLAIM: Existing integration tests for successful named upgrade, duplicate-name rejection and
    default root naming all pass (3 tests, 0.42s). Pytest reported a cache-write warning only.
    The standalone probe stopped before creating any object because Melder is not installed in
    this interpreter; pytest supplies source-path setup, while standalone Python does not.
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_lifecycle.py:318-387
  - tests/integration/melder/conduit/test_conduit_integration_lifecycle.py:641-668
  - Standalone probe: ModuleNotFoundError at import melder (exit 1)
  IMPACT: Integration behavior is verified. Adjust only diagnostic import setup, not runtime code.
  NEXT: Rerun the naming/lookup probe with src on its import path.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-06T17:03:17Z
  TYPE: MEASURE
  CLAIM: The isolated probe passed: automatic roots resolve through cloud; the same root name
    works in different frames; omitted root name becomes default. Lesser name= creation rejects,
    but the setter accepts request on two children and neither appears in cloud names.
  EVIDENCE:
  - Source-path-enabled naming/lookup probe (exit 0, JSON assertions passed)
  - src/melder/aether/conduit/conduit.py:1588-1630
  - src/melder/aether/aetheric_frame/aetheric_frame.py:340-378
  IMPACT: Current lesser labeling is not first-class named-scope registration or lifetime selection.
  NEXT: Discuss named lesser discovery separately from root promotion and tagged lifetime routing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T17:03:17Z
  TYPE: DECISION_REQUEST
  CLAIM: Owner is open to dynamic-mode lesser naming and cloud registration as an ergonomic
    improvement without creating/promoting another root and arranging peer borrowing. Proposed
    boundary: retain lesser ownership/lifetimes; introduce optional discoverability, not a new
    Existence mode. Cloud currently borrows root-only frame maps, so blindly putting lessers into
    register_root_conduit would violate that ownership contract. Pooled cleanup/reacquisition must
    define unregistering and clearing labels; existing _prepare_for_pool does not clear _name.
  EVIDENCE:
  - Owner discussion: dynamic lesser naming/registration and scope ergonomics.
  - src/melder/aether/aetheric_frame/aetheric_frame.py:160-196
  - src/melder/aether/aetheric_frame/aetheric_frame.py:340-378
  - src/melder/aether/conduit/conduit.py:564-585
  - src/melder/aether/conduit/conduit_pool.py:108-161
  IMPACT: Name uniqueness/discovery and pooled-name lifecycle need an explicit contract. Do not
    alter compiler, instance lifetime, frame root accounting, or source code during this discussion.
  NEXT: Agree the naming/discovery semantics before creating implementation tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Discovery complete: names identify frame-unique normal roots (automatic or dynamic); absent root
name defaults to default. Upgrade creates a named normal root. Nexus roots use the same path.
Lessers have no creation name argument, but the setter permits unregistered labels. SpellSpace
has no naming surface. No Autofac-style matching-name lifetime exists in Existence.
Owner is considering dynamic named lesser registration without root promotion. Discuss a separate
discovery contract, name uniqueness and pool-reset lifecycle; no runtime changes are authorized yet.
