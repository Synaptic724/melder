# Epic: Conduit / binding / meld bug remediation (2026-07-17 audit)

## Metadata
- Epic ID: EPIC-2026-07-17-bugfix-conduit-binding-meld
- Status: in_progress
- Owner: cowork
- Agent Name: helper_f
- Priority: p0
- Created: 2026-07-18T08:57:34Z
- Updated: 2026-07-18T20:50:00Z
- Target Window: 2026-Q3
- Related Program/Initiative: Melder repository bug audit 2026-07-17 (281 confirmed bugs)

## Problem / Opportunity
The 2026-07-17 repository-wide Melder bug audit confirmed, reproduced, and evidenced
25 bugs in this subsystem (1 Critical, 17 High, 6 Medium, 1 Low). Conduit runtime scopes/cache, lifetimes & existence, gates/pools, binding & SpellIndex contracts, spellbinder teardown, ConduitMeld / SpellSpaceMeld. Every finding carries an exact
source location, observed-vs-expected behavior, and a deterministic reproduction in its
audit report; no source was changed by the audit. This epic is the remediation program
for that subsystem.

Critical findings (fix first):
- BUG-073 - Concurrent first use of `Existence.many` loses a live instance (lifecycle race).

Evidence (canonical audit reports, repo-relative):
  - codex/2026-07-17_melder_bug_audit_runtime_scopes_and_cache.md
  - codex/2026-07-17_melder_bug_audit_lifetime_appendix.md
  - codex/2026-07-17_melder_bug_audit_conduit_gates_pools_appendix.md
  - codex/2026-07-17_melder_bug_audit_binding_index_appendix.md
  - codex/2026-07-17_melder_bug_audit_conduit_contract_detail_appendix.md
  - codex/2026-07-17_melder_bug_audit_spellbinder_teardown_appendix.md
  - codex/2026-07-17_melder_bug_audit_spellspace_meld_many_status_appendix.md

## MRP Alignment (Most Reasonable Product)
Melder is the AI-native object-world runtime; correctness of its lifecycle, ownership,
cleanup, and concurrency contracts is the foundation everything else stands on. Under the
free-threaded 3.14t runtime these defects are not cosmetic - orphaned resources, split-brain
registries, and data-losing retention violate the core "we clean everything, deterministically"
contract. Fixing them to a durable standard (root cause, not defensive guards) is MRP work:
the runtime must be trustworthy before higher layers compound on it.

## Ticket Contract
- ENTRY_GATE: This epic is routed on attention_board.md to helper_f; the story set below is defined; the owning agent has read the relevant audit report(s) for the story it starts.
- EXECUTION_BOUNDARY: Only the 25 audited bugs in this subsystem and their direct fixes + regression tests. No drive-by refactors; no cross-subsystem edits without a DECISION note and owner confirm.
- DEPENDENCIES: The audit reports listed above; system_docs/src_architecture.md + src_components.md (read the relevant sections on-demand per engineer context_protocol); patch-framework gating for any system-impacting change.
- EXIT_GATE: Every listed bug is either fixed with a regression test proving the corrected behavior, or explicitly reclassified (duplicate / intentional) with evidence and owner acceptance; board + closure sync complete.
- FAILURE_ESCALATION: Raise DECISION_REQUEST for any fix that changes public API shape/semantics or crosses subsystem boundaries; BLOCKER if a fix cannot be made without violating a documented invariant; CONFLICT if the audit finding contradicts current source on re-read.

## Goals (Outcomes)
- All Critical and High findings in this subsystem fixed at root cause with regression tests.
- Medium/Low findings fixed or explicitly, evidencedly deferred with owner sign-off.
- No new invariant violations introduced; existing focused test suites stay green (user-run).

## Non-Goals (Explicit Exclusions)
- Feature work, redesign, or optimization beyond correcting the audited defects.
- Bugs in other subsystems (owned by their own epics).
- Re-litigating findings the audit already excluded as intentional/duplicate without new evidence.

## Scope Boundaries
- In scope: src/melder/aether/conduit/**; src/melder/aether/spellbook/**bind**; src/melder/**/spellindex/**
- Out of scope: unrelated modules, public API redesign, performance passes.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Bug membership, severities, and evidence are FACT-sourced from the audit manifests; the epic is routable and ready for its owning agent to begin (Critical/High first).

## State Transition Event (2026-07-18T16:30:00Z)
- from_state: ready
- to_state: in_progress
- transition_reason: helper_f claimed the lane after completing bugfix_aether_core_logging (code-complete, owner-validation pending). Starting with the Critical: Story 02 (BUG-071-073, lifetime_appendix), BUG-073 first, re-verifying against current source before any fix.

## Success Metrics
- 100% of Critical + High bugs in this subsystem closed with a passing regression test each.
- 0 audit findings left in an undocumented state at closure.

## Requirements (Functional + Non-Functional)
- Root-cause fixes per technical_expertise: no blanket defensive guards; prove optionality via lifecycle/call-path evidence.
- Every touched function/class keeps a rich, accurate docstring; comments preserved/improved.
- Tests: pytest, unit-first; component/integration only where correctness cannot be proven by unit tests. Thread-safety is a first-class assertion target given 3.14t.
- Truthful validation: never claim tests/coverage ran unless actually run; otherwise report "Not run."

## Constraints / Assumptions
- Runtime is Python 3.14t (free-threaded, nogil); real threading, no multiprocessing; thread-safety is priority #1.
- synaptic_python_developer craft rules apply (Optional/Union not PEP 604; no `from __future__ import annotations`; TYPE_CHECKING-first; empty __init__.py; deterministic del-based cleanup; banned patterns).
- Audit env was CPython 3.13.5; reproductions may need the repo venv/import path.

## Dependencies / External References
- Audit reports listed under Problem/Opportunity.
- system_docs/src_architecture.md, system_docs/src_components.md, readable_src_graph.json (on-demand).

## Milestones (Track Progress)
- [ ] Milestone 1: Criticals closed - every Critical bug fixed + regression test green (user-run).
- [ ] Milestone 2: Highs closed - every High bug fixed + regression tests.
- [ ] Milestone 3: Mediums/Lows resolved or owner-accepted deferrals recorded.
- [ ] Milestone 4: Subsystem focused suites green (user-run) + docs/graph updated where boundaries changed.

## Stories (Required to Complete)
- [ ] Story: STORY-conduit_binding_meld-01 - BUG-008-012 (runtime_scopes_and_cache): Double cleanup returns a Conduit/SpellSpace to the pool twice; ownership transfer orphans live creations; cache transfer deletes a newer concurrent source.
- [ ] Story: STORY-conduit_binding_meld-02 - BUG-071-073 (lifetime_appendix): CRITICAL BUG-073 Existence.many race; failed lesser-to-normal upgrade irreversibly commits; None-returning singleton factory misread.
- [ ] Story: STORY-conduit_binding_meld-03 - BUG-155 ONLY (conduit_gates_pools_appendix). STRIPPED per owner-directed source-verified triage 2026-07-18: BUG-154 (caller-sequencing misuse per the owner's loud-by-contract ruling), BUG-156 (post-terminal gate pokes = same ruling), BUG-157 (documented drain-interval semantics, Low) - see codex/context_compass/2026-07-18_helper_f_bug_triage_conduit_utilities.md FINAL VERDICTS.
- [ ] Story: STORY-conduit_binding_meld-04 - BUG-110-113 (binding_index_appendix): Failed bind leaves a live spell and claimed lookup; cleanup drops parked spells; notch accepts a foreign-index spell and corrupts state.
- [ ] Story: STORY-conduit_binding_meld-05 - BUG-175-179 (conduit_contract_detail_appendix): Removing an index link revokes an independent standalone; permission-conflicting add commits a ghost; multi-member unlink destroys state; active policies bypassed by link/detail path.
- [ ] Story: STORY-conduit_binding_meld-06 - BUG-271-273 (spellbinder_teardown_appendix): Bind teardown breaks retained decorators/in-flight binds; Spellbook cleanup erases state beneath an admitted bind.
- [ ] Story: STORY-conduit_binding_meld-07 - BUG-270 (spellspace_meld_many_status_appendix): ConduitMeld/SpellSpaceMeld many-status defect.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-conduit_binding_meld-01 (BUG-008-012)
- [ ] Task: Complete story STORY-conduit_binding_meld-02 (BUG-071-073)
- [ ] Task: Complete story STORY-conduit_binding_meld-03 (BUG-154-157)
- [ ] Task: Complete story STORY-conduit_binding_meld-04 (BUG-110-113)
- [ ] Task: Complete story STORY-conduit_binding_meld-05 (BUG-175-179)
- [ ] Task: Complete story STORY-conduit_binding_meld-06 (BUG-271-273)
- [ ] Task: Complete story STORY-conduit_binding_meld-07 (BUG-270)
- [ ] Task: Re-verify each finding against current source before fixing (audit was read-only; some may already be partially addressed).
- [ ] Task: Verify Ticket Microcycle enforcement across active stories/tasks.

## Acceptance Criteria (Epic Done)
- Every listed bug id is fixed-with-test or documented as duplicate/intentional/deferred with owner acceptance.
- attention_board.md + artifact_board.md synced; epic moved to completed/ with summary.

## Risks / Mitigations
- Risk: cross-subsystem coupling means a fix here shifts behavior elsewhere. Mitigation: DECISION note + owner confirm before crossing boundaries.
- Risk: concurrency fixes are hard to test deterministically. Mitigation: controlled interleave/barrier probes as the audit used; mark thread-safety assertions explicitly.
- Risk: audit finding is stale vs current source. Mitigation: re-verify each before fixing; reclassify with evidence if not reproducible.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No "fix" from UNKNOWN/HYPOTHESIS - reproduce first, then fix at root cause.
- [ ] No defensive-guard sprawl to paper over a contract violation.

## Validation / Test Approach
- Reproduce each bug (deterministic probe/test) -> fix -> regression test asserts corrected behavior.
- Focused pytest per touched module; thread-safety via controlled interleaves. Coverage verified by the user (agents report "Not run" until then).

## Rollout / Adoption Plan
- Land fixes in small, reviewable, per-bug (or per-tight-group) changes; keep public API stable.

## Open Questions
- Are any listed findings already partially fixed since the 2026-07-17 audit snapshot? (Re-verify at story start.)

## Decision Log
- DATETIME: 2026-07-18T08:57:34Z
  DECISION: Epic scoped by subsystem so each owning agent keeps a tight, coherent context window. Bug membership and ranges are FACT-sourced from the 2026-07-17 audit MANIFEST + wave manifests. Fix order within the epic: Critical -> High -> Medium -> Low.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a until an artifact (e.g., a fix design note) is produced.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - Conduit runtime scopes/cache, lifetimes & existence, gates/pools, binding & SpellIndex contracts, spellbinder teardown, ConduitMeld / SpellSpaceMeld.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-07-18T08:57:34Z
  TYPE: FACT
  CLAIM: 25 audited bugs (1 Critical, 17 High, 6 Medium, 1 Low) are grouped into this subsystem epic for helper_f; ranges/severities are FACT-sourced from the audit MANIFEST + wave manifests.
  EVIDENCE:
  - codex/2026-07-17_melder_bug_audit_MANIFEST.md:66-134
  - codex/2026-07-17_melder_bug_audit_MANIFEST_WAVE_013.md:11-23
  IMPACT: Gives helper_f a cohesive, self-contained remediation lane with all evidence pointers in one place.
  NEXT: Owner certifies the plan; helper_f starts the highest-severity story and re-verifies each finding against current source before fixing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-18T16:30:00Z
  TYPE: PLAN
  CLAIM: helper_f claimed this epic (status in_progress; board row added). Execution order per
    the epic decision log (Critical -> High -> Medium -> Low): Story 02 first for its Critical
    BUG-073 (Existence.many concurrent-first-use loses a live instance) with its High siblings
    BUG-071/072, then the remaining stories by severity mix. Session laws carried over from the
    aether lane: md5-verify every staged read against live device_bash hashes before use as an
    edit base (stale-stage illusion, aether epic 14:29Z note); preserve BOM/CRLF byte-fidelity
    on edits; sandbox-execute whatever import closures allow, report full-repo pytest Not run.
  EVIDENCE:
  - tickets/epics/2026-07-17_bugfix_conduit_binding_meld_epic.md:94-102
  - codex/2026-07-17_melder_bug_audit_lifetime_appendix.md
  IMPACT: The p0 lane is owned and ordered; the Critical is first in line.
  NEXT: Read the lifetime appendix, re-verify BUG-071/072/073 against live source, record
    FACT notes, then fix at root cause with interleave regression tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-18T17:10:00Z
  TYPE: FACT
  CLAIM: Story 02 (BUG-071/072/073) re-verified - all three CONFIRMED, with a PATH CORRECTION:
    the audit's `creation_management/` file paths are stale; the code moved to
    `conduit/creations/creations.py` and `spellbook/spell_compiler/codegen_creation_system/`
    (shared_assets/creation_runtime_door_compiler.py + strategies/solo/compilers/). BUG-073
    (Critical): the racy lazy-bucket init moved INTO `Creations.add_many_creations`
    (creations.py:241-267) - unsynchronized get/assign/append although the store owns an RLock;
    two first-resolvers overwrite each other's bucket and one live creation escapes both
    lifetime and disposal tracking. Value-sentinel init (`.get(key) is None`) also silently
    replaces a stored-None singleton slot with a bucket. BUG-072: the emitted door lanes
    (all 5 singleton routes x no-overrides + with-overrides builders, door compiler 536-683 +
    727-865) use None as the absent marker - a stored-None unique creation re-runs its
    provider and dies on the duplicate-store ValueError; the overrides lanes would create
    OVER an existing stored-None singleton. BUG-071: upgrade_to_normal registers hooks at
    Step 6 (conduit.py:1891) after state flip, root re-id, rename, pool, meld rewire, ward
    conversion, spellbook preset, and root registration - invalid hooks raise into an
    irreversible half-upgrade; retry refused ("Only lesser conduits can be upgraded").
  EVIDENCE:
  - codex/2026-07-17_melder_bug_audit_lifetime_appendix.md:1-120
  - src/melder/aether/conduit/creations/creations.py:222-267
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:498-686
  - src/melder/aether/conduit/conduit.py:1789-1899
  IMPACT: Story 02 scope pinned with corrected paths; the Critical's root cause is one
    store method, so a single fix covers every emitted many lane (solo/generalized/fallback).
  NEXT: Implement per severity: 073 store-atomicity, 072 sentinel presence, 071
    validate-before-mutate; symptom-named suites; sandbox-execute what imports allow.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T17:10:00Z
  TYPE: DECISION
  CLAIM: Story 02 IMPLEMENTED - Critical closed. BUG-073: `add_many_creations` now runs its
    ENTIRE live+disposable mutation under the store `_lock` with membership-based (never
    value-based) bucket-presence tests; every emitted many lane (solo, generalized, fallback,
    many_only - all delegate here) inherits the atomicity from the single root-cause site;
    docstring gained the atomicity + membership Contract and a Threading section. BUG-072:
    the door compiler gained a private module sentinel `_CREATION_MISSING` injected into
    every emitted template namespace as `_creation_missing`; all 20 singleton get-lines now
    read `.get(_spell_id, _creation_missing)` and all 20 presence tests compare identity
    against the sentinel (10 no-overrides + 10 with-overrides), so a stored None is PRESENT:
    repeat resolution returns it without re-running the provider, and the overrides lanes
    refuse to override it; both template param lists + all 4 compile call sites thread the
    sentinel; the source-hash-keyed executor cache makes the new emissions self-versioning.
    BUG-071: new `_validate_conduit_hooks_payload` seam on Conduit validates by merging into
    a throwaway map (exact `_merge_conduit_hooks` rules, zero duplicated logic, zero state
    touched) and `upgrade_to_normal` calls it BEFORE the first mutation - an invalid hooks
    payload now fails with zero state change and the upgrade is retryable; docstrings updated.
    VALIDATION: BUG-072+073 suites EXECUTED in the sandbox harness (real Creations +
    executor_code_cache [md5-matched device] + fixed door compiler; gated-read interleave
    choreography): 7/7 green on fixed code; red on old code with the audited symptoms
    verbatim ("a successfully returned creation escaped lifetime storage"; duplicate-store
    "ValueError: Key spell-none already exists in creations"; overrides lane created over a
    stored-None singleton). BUG-071 suite (3 tests on the conftest conduit_dynamic_lesser
    harness: zero-state-change on ValueError + TypeError lanes with retry-recovery proof,
    valid-hooks behavior guard) rides the owner's 3.14t run. py_compile green on all three
    sources sandbox-side AND device-side. Full-repo pytest Not run - REOPEN on red.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:222-282
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:1-16
  - src/melder/aether/conduit/conduit.py:1531-1580
  - tests/unit/melder/aether/conduit/creations/test_creations_many_first_use_atomicity_regression.py:1-230
  - tests/unit/melder/spellbook/spell_compiler/test_creation_door_none_singleton_regression.py:1-215
  - tests/unit/melder/aether/conduit/test_conduit_upgrade_validate_before_mutate_regression.py:1-140
  IMPACT: Milestone 1 (Criticals closed) reached pending owner run; Story 02 done (3 of 25
    epic bugs). Next tranche by severity: the High-density stories (01, 04, 05).
  NEXT: Proceed to Story 01 (BUG-008-012, runtime_scopes_and_cache) on user direction;
    owner runs the suites on 3.14t, REOPEN on red.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T19:20:00Z
  TYPE: CONFLICT
  CLAIM: OWNER CHALLENGE UPHELD - BUG-072 is RECLASSIFIED (audit premise contradicts the
    architecture) and the 17:10Z door-compiler change is REVERTED. The owner asked how the
    bug could occur if the whole architecture is used; tracing the REAL meld surface answers
    it: `meld_existing_spell` (conduit_meld.py:516-553) and every liveness read across
    ConduitMeld/SpellSpaceMeld (~10 `get_creation` call sites) uniformly treat a None
    creation as NOT LIVE - "Spell '<id>' is not live." raises on a stored None. None-as-
    absent is the runtime's LAW, not a defect of the door lanes; a None-returning
    Existence.unique provider is not a supported citizen of this architecture. My sentinel
    change made the door lanes accept a stored None as present while meld_existing_spell
    calls the same state not-live - an internal split-brain, strictly worse than the audited
    behavior. PROCESS FAULT (mine): I validated the defect MECHANISM at the store layer and
    "reproduced" it by driving the door directly with a hand-built executor - bypassing the
    architecture - instead of proving the premise reachable through bind -> compile -> meld.
    The audit itself calls its reproductions "isolated"; isolation is exactly what hid the
    contradiction. REVERT executed: door compiler restored byte-identical to the owner
    original (md5 6d02a7be, mtime-guarded, device-verified); creations.py reduced to the
    MINIMAL BUG-073 fix (original body, original presence checks, wrapped in the store
    `_lock` + atomicity docstring - no membership/None semantics changes); the BUG-072
    regression suite moved to _to_delete/ (bridge cannot rm); the BUG-073 suite trimmed to
    its two architecture-valid tests (race choreography + sequential guard), re-run GREEN in
    sandbox against the minimal fix with the reverted compiler. BUG-071 (validate-before-
    mutate upgrade) is untouched by this ruling - no None semantics involved.
    DISPOSITION: BUG-072 -> reclassify per EXIT_GATE ("duplicate / intentional with
    evidence and owner acceptance"): the None-ambiguity is resolved architecture-level by
    the not-live contract. If the owner wants belt-and-braces, the aligned option is a
    LOUD creation-time rejection of None provider results (fail-fast at store time), NOT
    None-tolerant presence tests - owner ruling required before any such change.
    NEW LAW for every remaining bug in my lanes: an audit finding is UNKNOWN until its
    trigger is proven reachable through the real architecture path; reproduce at the
    public-surface level (or evidence the full call chain) BEFORE any fix; premise
    contradictions escalate as CONFLICT instead of being "fixed".
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:505-560
  - src/melder/aether/conduit/meld/spellspace_meld.py:519-560
  - src/melder/aether/conduit/creations/creations.py:222-290
  - codex/2026-07-17_melder_bug_audit_lifetime_appendix.md:96-100
  IMPACT: Story 02 stands as: BUG-073 fixed (minimal, lock-only), BUG-071 fixed,
    BUG-072 reclassified pending owner acceptance. Hot-path emitted code is back to the
    owner's original bytes.
  NEXT: Owner accepts/overrides the BUG-072 reclassification; remaining stories proceed
    under the new reachability law. helper_f2's Story-04/06 partition NOTICE seen - ACK
    coming via mailbox; the reachability law is flagged to them there too.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T20:05:00Z
  TYPE: FACT
  CLAIM: FULL-CONTEXT TRIAGE COMPLETE on owner directive: all fourteen audit reports for
    both helper_f epics read in one context before any further fixing. Key discovery: the
    audit waves CONTRADICT each other - the synchronization-residual appendix (the only
    caller-aware wave) excluded as documented/existing the exact behaviors earlier waves
    filed as BUG-090/091/092/156/157/230; those six are contested by the audit itself and
    are frozen pending owner ruling. Verdicts for this epic's remaining 22: 17 KEEP (177 is
    the top-confidence High - ordinary two-member unlink self-corrupts with zero
    injection), VERIFY-FIRST on 154 (intentional registry omission + thread-confinement
    contract = likely caller-sequencing premise), 156 (contested + gates reworked
    post-audit), 112/113 (BUG-072-pattern: repro invokes private seams / caller-built
    indexes - public-path proof required), RECLASSIFY-PROPOSED on 157 (contested, Low).
    Full per-bug verdicts, family plan, and refined injection-vs-premise law:
    codex/context_compass/2026-07-18_helper_f_bug_triage_conduit_utilities.md.
  EVIDENCE:
  - codex/context_compass/2026-07-18_helper_f_bug_triage_conduit_utilities.md:1-999
  - codex/2026-07-17_melder_bug_audit_synchronization_residual_appendix.md:100-113
  IMPACT: Fix order is now evidence-ranked; six contested findings cannot waste fix effort;
    helper_f2 receives the Story-04/06 traps (112/113 premise checks) via mailbox.
  NEXT: Owner reviews the triage (esp. the contested six + reclassify proposals); Story 05
    (BUG-175-179) leads the KEEP work with BUG-177 first, under the reachability law.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T20:50:00Z
  TYPE: DECISION
  CLAIM: SOURCE-VERIFIED STRIP executed on owner directive ("investigate the code wide,
    strip the useless, fix regardless of assignment"). Sweep read live source WITH callers
    for every contested/suspect finding. THIS EPIC: BUG-154/156/157 STRIPPED from Story 03
    (owner's own 2026-07-12 loud-by-contract ruling, live in admit_ticket's docstring,
    classifies teardown-vs-racing-use and post-terminal gate pokes as lifecycle misuse;
    157 is documented interval semantics). BUG-112 and BUG-113 FLIPPED TO CONFIRMED-REAL:
    the public Conduit.notch_spell -> _notch_spell path delivers the caller's unvalidated
    (spell_index, spell) pair straight to _apply_notch (no membership check at any layer),
    and the add-to-index ownership gate validates selected_spell_id instead of registry
    identity - a real guard checking the wrong property. Remaining epic scope: 18 bugs
    (Story 01 x5, Story 03 x1, Story 04 x4, Story 05 x5, Story 06 x3, Story 07 x1).
    OWNER OVERRIDE: helper_f proceeds across ALL stories regardless of the helper_f2
    partition; helper_f2 notified via mailbox to sync before touching 04/06.
  EVIDENCE:
  - codex/context_compass/2026-07-18_helper_f_bug_triage_conduit_utilities.md
  - src/melder/utilities/synchronization/creation_gate.py (admit_ticket ruling docstring)
  - src/melder/aether/spellbook/spellbook.py:3056-3107,3336-3358
  IMPACT: The epic's fix queue is now source-verified: 18 real bugs, zero contested.
  NEXT: Fix in confidence order: BUG-177 (ordinary-path corruption) -> Story 05 cluster ->
    Story 01 (076-family root first) -> 112/113 -> Story 04/06/07.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T19:16:00Z
  TYPE: FACT
  CLAIM: SESSION BOUNDARY + SINGLE-AGENT CONSOLIDATION. A fresh session re-onboarded as
    helper_f (full general->engineer->synaptic_python_developer chain; owner-certified
    AGENT_NAME helper_f / CERTIFY: APPROVED). Owner declared ALL other agents departed
    (helper_0/helper_1/helper_f2) - marked departed on mailbox_board.md. Consumed
    helper_f2's 17:15Z story-04 partition NOTICE (message deleted, both helper_f alert
    lines cleared): its content was already actioned last session (ACK 20:05Z, owner
    override 20:50Z), and with helper_f2 departed the partition is VOID - the story-04
    ticket and board row revert to helper_f (row agent_name synced, status ready,
    sequenced behind BUG-177/Story-05 per the 20:50Z fix order). The two outbound
    messages TO helper_f2 are unconsumable dead letters pending owner directive.
    Repo layout ruling this session: context_compass/ moved up one level (codex/ removed),
    so older codex/-prefixed evidence paths now resolve from the repo root; owner also
    waived the readable_src_graph.json onboarding read (engineer SKILLS raise-to-user).
    CLOCK NOTE: prior-session stamps (20:05Z/20:50Z) run AHEAD of this session's UTC
    clock (19:1xZ) - note sequence in this file is positional and append-only.
  EVIDENCE:
  - mailbox_board.md:34-40
  - attention_board.md:19-27
  - tickets/stories/2026-07-18_conduit_binding_meld_story04_binding_index_story.md:1-1
  - tickets/epics/2026-07-17_bugfix_conduit_binding_meld_epic.md:326-349
  IMPACT: Single-agent state is durable on the boards; the epic queue is unchanged
    (18 source-verified bugs) and every story is now unambiguously helper_f's.
  NEXT: Await the owner's work directive; the standing queue default is BUG-177 first
    (Story 05), under the reachability law from the 19:20Z CONFLICT note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order (Critical->High->Medium->Low).
- Reference story/task evidence (and the audit report line ranges) instead of duplicating tactical logs.
- Keep notes append-only and preserve UNKNOWN-first discipline.

- DATETIME: 2026-07-18T17:15:00Z
  TYPE: PLAN
  CLAIM: helper_f2 joins the epic on a DISJOINT story set after turning in the MR audit
    epic: STORY-04 (BUG-110-113) claimed now via its own story ticket, STORY-06
    (BUG-271-273) intended next - the spellbook-side partition keeps spellbook.py
    single-writer while helper_f owns the conduit-side stories. NOTICE with ACK request
    sent to helper_f; an objecting ACK rebalances the split.
  EVIDENCE:
  - tickets/stories/2026-07-18_conduit_binding_meld_story04_binding_index_story.md:1-1
  - codex/2026-07-17_melder_bug_audit_binding_index_appendix.md:1-107
  IMPACT: Two agents advance the p0 epic in parallel without file-level write collisions.
  NEXT: helper_f2 re-verifies BUG-110-113 against live spellbook.py and journals per-bug
    FACT notes in the story ticket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Remediation epic for the 25 conduit binding meld bugs from the 2026-07-17 audit, owned by helper_f.
Status ready. Start with the Critical findings (BUG-073),
re-verify against current source, fix at root cause with regression tests. All evidence is in the audit reports listed above.
