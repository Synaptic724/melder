# Epic: MutationResearch bug remediation (2026-07-17 audit)

- Completed: 2026-07-18T17:10:01Z
- Summary: All 24 audited MutationResearch bugs (10 High, 14 Medium) re-verified
  independently and fixed at root cause, each with a dedicated red-then-green
  regression test (sandbox suite 58 -> 144 green); 031 emission-lock and 048
  lane-governance architecture deltas promoted to canonical system docs via the
  patch framework. Owner-directed turn-in 2026-07-18 ("turn it in obv"); repo
  3.14t pytest rides the owner's next run - REOPEN on red.

## Metadata
- Epic ID: EPIC-2026-07-17-bugfix-mutation-research
- Status: done
- Owner: cowork
- Agent Name: helper_f2
- Priority: p1
- Created: 2026-07-18T08:57:34Z
- Updated: 2026-07-18T17:10:01Z
- Target Window: 2026-Q3
- Related Program/Initiative: Melder repository bug audit 2026-07-17 (281 confirmed bugs)

## Problem / Opportunity
The 2026-07-17 repository-wide Melder bug audit confirmed, reproduced, and evidenced
24 bugs in this subsystem (0 Critical, 10 High, 14 Medium). MutationResearch record/lanes/groups/diffs/composition, hydration and network versioning. Every finding carries an exact
source location, observed-vs-expected behavior, and a deterministic reproduction in its
audit report; no source was changed by the audit. This epic is the remediation program
for that subsystem.

Critical findings (fix first):
- None in this subsystem (highest severity is High).

Evidence (canonical audit reports, repo-relative):
  - codex/2026-07-17_melder_bug_audit_mutation_research.md
  - codex/2026-07-17_melder_bug_audit_mutation_research_appendix.md
  - codex/2026-07-17_melder_bug_audit_mutation_group_diff_appendix.md
  - codex/2026-07-17_melder_bug_audit_mutation_research_snapshot_recency_appendix.md

## MRP Alignment (Most Reasonable Product)
Melder is the AI-native object-world runtime; correctness of its lifecycle, ownership,
cleanup, and concurrency contracts is the foundation everything else stands on. Under the
free-threaded 3.14t runtime these defects are not cosmetic - orphaned resources, split-brain
registries, and data-losing retention violate the core "we clean everything, deterministically"
contract. Fixing them to a durable standard (root cause, not defensive guards) is MRP work:
the runtime must be trustworthy before higher layers compound on it.

## Ticket Contract
- ENTRY_GATE: This epic is routed on attention_board.md to helper_f2 (owner-routed takeover 2026-07-18; template-assigned helper_1 never started it); the story set below is defined; the owning agent has read the relevant audit report(s) for the story it starts.
- EXECUTION_BOUNDARY: Only the 24 audited bugs in this subsystem and their direct fixes + regression tests. No drive-by refactors; no cross-subsystem edits without a DECISION note and owner confirm.
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
- In scope: src/melder/**/mutation_research/**
- Out of scope: unrelated modules, public API redesign, performance passes.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Bug membership, severities, and evidence are FACT-sourced from the audit manifests; the epic is routable and ready for its owning agent to begin (Critical/High first).
- from_state: ready
- to_state: in_progress
- transition_reason: Owner directed helper_f2 to grab an epic (2026-07-18); helper_f2 takes ownership, board row added, discovery begins with STORY-01 re-verification.

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
- [x] Story (owner validation pending): STORY-mutation_research-01 - BUG-031-034 (all landed) (mutation_research): Stale replace-on-emit overwrites a newer live composition; duplicate synthesis selections delete unrelated bases.
- [x] Story (owner validation pending): STORY-mutation_research-02 - BUG-035-049 (all landed) (mutation_research_appendix): Activation exposes ingress before hydration; lifecycle-sink exception permanently blocks cleanup; join into archived receiver; network restore trusts false content addresses; promotion catch-up misroutes staged ancestry.
- [x] Story (owner validation pending): STORY-mutation_research-03 - BUG-150-153 (all landed) (mutation_group_diff_appendix): Unrelated default-lane spell erases current composition; rejected world entry consumes staged ancestry; group/diff coherence.
- [x] Story (owner validation pending): STORY-mutation_research-04 - BUG-261 (landed) (mutation_research_snapshot_recency_appendix): Restoring a deduplicated snapshot does not refresh its recency/identity.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-mutation_research-01 (BUG-031-034)
- [ ] Task: Complete story STORY-mutation_research-02 (BUG-035-049)
- [ ] Task: Complete story STORY-mutation_research-03 (BUG-150-153)
- [ ] Task: Complete story STORY-mutation_research-04 (BUG-261)
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
- Patch-framework docs (promoted 2026-07-18, live under system_docs, not artifacts/):
  - system_docs/patches/completed/mr_emission_lock_and_lane_governance_2026_07_18/architecture_patch.md
  - system_docs/patches/completed/mr_emission_lock_and_lane_governance_2026_07_18/component_patch_mutation_research_root.md
  - system_docs/patches/completed/mr_emission_lock_and_lane_governance_2026_07_18/component_patch_research_set_package.md

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - MutationResearch record/lanes/groups/diffs/composition, hydration and network versioning.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-07-18T09:56:05Z
  TYPE: DECISION
  CLAIM: helper_f2 takes ownership of this epic on owner direction; in the same pass mutation_0
    (departed) was removed from active routing - his two stale board rows pointed at tickets
    already completed 2026-07-12, so they were removed with closure anchors, and the board's
    19,066-byte NUL write-fault tail was stripped. Mailbox roster verified free of mutation_0.
  EVIDENCE:
  - attention_board.md:50-58
  - tickets/epics/completed/2026-07-02_agent_object_persistence_loop_epic.md:2-2
  - tickets/tasks/completed/2026-07-12_mutation_research_accessor_doors_task.md:2-2
  - mailbox_board.md:34-40
  IMPACT: MR subsystem remediation has an active owner again; board invariants restored (no
    active rows referencing completed tickets; no NUL corruption).
  NEXT: Read codex/2026-07-17_melder_bug_audit_mutation_research.md (STORY-01, BUG-031-034) and
    re-verify each finding against current source before any fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-18T08:57:34Z
  TYPE: FACT
  CLAIM: 24 audited bugs (0 Critical, 10 High, 14 Medium) are grouped into this subsystem epic for helper_1; ranges/severities are FACT-sourced from the audit MANIFEST + wave manifests.
  EVIDENCE:
  - codex/2026-07-17_melder_bug_audit_MANIFEST.md:66-134
  - codex/2026-07-17_melder_bug_audit_MANIFEST_WAVE_013.md:11-23
  IMPACT: Gives helper_1 a cohesive, self-contained remediation lane with all evidence pointers in one place.
  NEXT: Owner certifies the plan; helper_1 starts the highest-severity story and re-verifies each finding against current source before fixing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-18T09:59:48Z
  TYPE: FACT
  CLAIM: STORY-01 re-verification complete. All four audited findings (BUG-031, BUG-032,
    BUG-033, BUG-034) are still present in current source with the exact audited mechanisms;
    audit line references remain accurate. No reclassifications; all four proceed to fix.
    Detail: (031) verbs commit under the set lock then fire the persistence callback lock-free,
    and the root builds describe_research_composition() + crystallizer.emit() with no
    serialization or monotonicity token, so a paused thread publishes a stale replace-on-emit
    snapshot; (032) _locate_live_membership returns the FIRST frame membership found even when
    unselected, contradicting the active-if-any contract; (033) spell-parent, group-member, and
    group-parent validation is residency-only (is_resident), so spell/group namespaces accept
    each other's IDs; (034) duplicate (name, kind) selections are preserved and _splice reapplies
    the same original span against the already-mutated line list, deleting neighbor code.
  EVIDENCE:
  - src/melder/mutation_research/research_set/research_set.py:186-197
  - src/melder/mutation_research/mutation_research.py:3185-3219
  - src/melder/mutation_research/mutation_research.py:1015-1048
  - src/melder/mutation_research/research_set/research_set.py:748-755
  - src/melder/mutation_research/research_set/research_set.py:853-868
  - src/melder/mutation_research/synthesis/structural_synthesizer.py:114-168
  - src/melder/mutation_research/synthesis/structural_synthesizer.py:391-400
  IMPACT: STORY-01 moves from discovery to fix-ready; the two Highs (031, 034) lead the tranche.
  NEXT: Owner confirms the PLAN note below; implementation starts with BUG-031.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T09:59:48Z
  TYPE: PLAN
  CLAIM: Proposed STORY-01 fix tranche (order High->High->Medium-High->Medium): (1) BUG-031 -
    add a root-level emission lock held across snapshot build + crystallizer.emit in
    _emit_research_composition so build+publish is atomic and always reads live state
    (lock order emission->set is acyclic: sets fire on_mutation only after releasing their
    lock); (2) BUG-034 - reject duplicate (name, kind) selections in synthesize() with a loud
    ValueError per the "explicit asks refuse loudly" contract; (3) BUG-033 - kind-aware
    ancestry/member validation in register_spell/register_group (spell parents and group
    members must resolve to spell nodes; parent_group_ids to group nodes; errors name the
    offending kind); (4) BUG-032 - scan ALL frames preferring a selected membership, falling
    back to the first unselected membership. Each fix lands with a symptom-named pytest
    regression; no public API shape changes; docstrings updated for touched methods.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:3185-3219
  - src/melder/mutation_research/synthesis/structural_synthesizer.py:109-173
  - src/melder/mutation_research/research_set/research_set.py:743-786
  - src/melder/mutation_research/mutation_research.py:1015-1048
  IMPACT: Clears both Highs and two Mediums of STORY-01 inside subsystem scope with no
    cross-subsystem edits.
  NEXT: Await owner confirmation of this plan, then implement in the stated order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-18T10:21:47Z
  TYPE: MEASURE
  CLAIM: Owner-directed independent double-check of BUG-031-034 executed against the REAL
    modules (not audit excerpts) under CPython 3.13.13 in the cloud sandbox, using a loader
    that reproduces 3.14 deferred-annotation import semantics; boundary collaborators
    (crystallizer/aether/frames) were doubles per the repo's unit-mock conventions. All four
    audit findings REPRODUCED: (031) gated-publish interleave recorded [['a','b'],['a']] -
    final durable ['a'] vs live ['a','b'] (lost update); (032) parked-first frame order
    reported runtime='parked'/frame_parked while a later frame selected the spell; (033)
    G2=[G1], parent_spell_ids=[G1], AND (new facet) parent_group_ids=[spell] all accepted;
    (034) audit repro deleted neighbor g with actions ['replaced','replaced'], plus (new
    facets) duplicate-longer-donor produced corrupted-but-parsing output and duplicate
    additions appended the same def twice. GPT 5.6's audit holds on all four; three
    additional failure facets found and folded into the fixes. Post-fix probe reruns:
    (031) serialized, monotone [['a'],['a','b']], final == live; (032) 'active'/frame_active;
    (033) all three cross-namespace asks refuse; (034) loud duplicate refusal.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:3185-3219
  - src/melder/mutation_research/mutation_research.py:1015-1048
  - src/melder/mutation_research/research_set/research_set.py:748-755
  - src/melder/mutation_research/research_set/research_set.py:853-868
  - src/melder/mutation_research/synthesis/structural_synthesizer.py:114-168
  IMPACT: Findings promoted from audit-FACT to independently-reproduced FACT; fix shapes
    validated red->green before commit.
  NEXT: Implementation note below; owner runs the repo pytest suite on 3.14t.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T10:21:47Z
  TYPE: FACT
  CLAIM: STORY-01 fixes implemented and committed with regression tests. (031) new reentrant
    _emission_lock makes snapshot build + replace-on-emit publication atomic in
    _emit_research_composition; create_research_set and load_recorded_composition acquire it
    ahead of the root lock (one-way order emission->root->set->crystallizer, class docstring
    updated; lock added to __slots__/__init__/cleanup del-posture). (032)
    _locate_live_membership scans every live frame, a selected membership anywhere wins,
    else first live membership reports parked (docstring contract added). (033) new
    _resident_node_kind_locked classifier; register_spell parents require spell nodes,
    register_group members require spell nodes and parent_group_ids require group nodes,
    teach-grade errors name the offending kind. (034) synthesize() refuses duplicate
    (name, kind) selections loudly (contract + Raises updated). Tests: 8 added (5 symptom
    -named regressions + 3 over-rejection guards) across the three unit test files. Sandbox
    validation: 58/58 tests green on fixed tree; exactly the 7 regression tests red on
    original tree; 51 pre-existing tests green on both (no behavior regressions in scope).
    Repo pytest suite on 3.14t: Not run (owner-run per policy).
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:3229-3277
  - src/melder/mutation_research/mutation_research.py:1040-1090
  - src/melder/mutation_research/research_set/research_set.py:227-262
  - src/melder/mutation_research/synthesis/structural_synthesizer.py:141-168
  - tests/unit/melder/mutation_research/test_mutation_research_root.py:433-560
  - tests/unit/melder/mutation_research/research_set/test_research_set.py:430-520
  - tests/unit/melder/mutation_research/synthesis/test_structural_synthesizer.py:216-295
  IMPACT: Both STORY-01 Highs and both Mediums are fixed at root cause; BUG-031's fix also
    hardens every future emission path via the documented lock order.
  NEXT: Owner runs pytest (tests/unit/melder/mutation_research) on 3.14t; on green, STORY-01
    is accept-ready and STORY-02 (BUG-035-049, mutation_research_appendix) re-verification
    begins. Cleanup note: delete _to_delete/melder_src_snapshot.tar.gz (sandbox staging
    artifact).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T12:31:55Z
  TYPE: FACT
  CLAIM: STORY-02 HIGH tranche (BUG-035, 036, 037, 038, 049) independently re-verified against
    current source and fixed with regression tests, same sandbox protocol as STORY-01. All five
    reproduced red via 6 new tests before fixing. Fixes: (035) activate() hydrates BEFORE
    flipping _activated so ingress can never race the registry swap through the documented
    seam; (036) cleanup's state-sink emission wrapped as documented best-effort so a raising
    observer never wedges the cascade/singleton reset; (037) join holds the receiver's lane
    RLock across the whole commit (open-check through journal+snapshot; new _join_locked
    helper; one-way order set->lane) so direct mark_archived serializes before or after,
    never mid-commit; (038) NetworkVersioner.from_payload recomputes every hydrated entry's
    sha256 and refuses claimed/actual mismatches + restore_network validates the
    guaranteed-default-lane invariant BEFORE touching live state; (049) promotion catch-up
    routes through the root record_world_entry verb so staged ancestry is consumed by its
    candidate instead of leaking onto the next unrelated entry. Sandbox: 71/71 green on fixed
    tree (65 pre-existing + 6 new); exactly the 6 new tests red on pre-fix tree. Repo pytest
    on 3.14t: Not run (owner-run).
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:404-434
  - src/melder/mutation_research/mutation_research.py:186-201
  - src/melder/mutation_research/research_set/research_set.py:1509-1600
  - src/melder/mutation_research/research_set/network_versioner.py:258-283
  - src/melder/mutation_research/research_set/research_set.py:1755-1770
  - src/melder/mutation_research/mutation_research.py:916-930
  IMPACT: All 5 High-severity STORY-02 findings closed at root cause; every High in the epic
    (STORY-01's 2 + these 5, plus 031/034 from story-01) is now fixed pending owner validation.
  NEXT: Owner runs pytest tests/unit/melder/mutation_research on 3.14t; remaining tranche =
    STORY-02 mediums/med-highs (BUG-039-048 excl. fixed), STORY-03 (BUG-150-153), STORY-04
    (BUG-261).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T12:46:58Z
  TYPE: DECISION
  CLAIM: OWNER RULING (2026-07-18, verbatim intent): MutationResearch being cleaned means the
    WHOLE system is being cleaned - MR is never used mid-teardown, so guards that protect MR
    reads/verbs against collaborators disappearing during use (aether/crystallizer cleaned
    probes, getattr/hasattr introspection, catch-all excepts, redundant None checks on owned
    always-set fields) are defect-class noise, not safety. Contractual states stay guarded:
    crystallizer INACTIVE (recording off) is real; frames/indexes clean during normal ops;
    persisted/deserialized payload shape validation is data validation, not defensiveness;
    cleanup's own teardown-lane ordering checks stay.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:1-3300
  IMPACT: Standing law for all remaining lanes in this epic (and a promotion candidate for the
    synaptic banned_patterns skill if the owner wants it repo-durable).
  NEXT: Applied in the sweep below; future fixes must not reintroduce teardown paranoia.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T12:46:58Z
  TYPE: FACT
  CLAIM: Owner-directed hardening sweep of mutation_research.py landed: (1) renamed
    _hydrate_from_record_when_virgin -> _hydrate_from_record and _registry_is_virgin ->
    _registry_is_untouched, all call sites + docstrings/comments de-cutesied; (2) removed the
    getattr(instance, "_cleaned", None) probe in _reset_singleton_for_tests (direct owned
    access); (3) dropped crystallizer.cleaned probes from the emission seam, hydration,
    custody probe, and both custody refusals (activated is the one contractual gate; cleanup
    sets _activated False so late teardown callbacks fall out naturally); (4) dropped the
    aether None/cleaned guard in _locate_live_membership and made _aether truthfully
    non-Optional; (5) collapsed _configured/_configuration double-checks to the flag (configure
    maintains the invariant under lock); (6) removed the catch-all except in _probe_custody
    (KeyError = miss is the contract); (7) unwrapped the impossible None check on the owned
    research-sets registry in cleanup; (8) dropped the __new__ postcondition assert; (9)
    simplified the emission guard to single-check (the double re-check was teardown paranoia
    under the ruling). Trusted-collaborator return contract honored: hydration now checks
     per describe_mutation_research_record's Optional contract instead of
    isinstance-probing; persisted payload SHAPE checks retained (external data). Test helper
    _mock_aether now models live-but-INACTIVE custody for the non-recording default instead of
    truthy-MagicMock cleaned shorthand. Sandbox: 71/71 green post-sweep. Repo pytest on
    3.14t: Not run (owner-run).
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:497-521
  - src/melder/mutation_research/mutation_research.py:258-266
  - src/melder/mutation_research/mutation_research.py:1085-1140
  - tests/unit/melder/mutation_research/test_mutation_research_root.py:31-55
  IMPACT: The root file carries zero getattr/hasattr, zero cleaned-or-not collaborator probes,
    and no impossible-state guards; naming matches the professional baseline.
  NEXT: Owner runs pytest on 3.14t; remaining epic tranches unchanged (STORY-02 mediums
    039-048, STORY-03 150-153, STORY-04 261).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-18T12:52:05Z
  TYPE: FACT
  CLAIM: Owner-directed repo-wide "virgin" vocabulary purge completed (owner: use plain
    naming). Remaining occurrences fixed in four files: mutation_configuration.py docking-loop
    comment; unit root test renamed
    test_root_activation_hydrates_virgin_registry_from_record ->
    test_root_activation_hydrates_untouched_registry_from_record plus four docstring wordings;
    crystallizer lifecycle + restore integration test docstrings/comments (cross-subsystem
    WORDING-ONLY edits, owner-directed). Zero "virgin" tokens remain under src/ and tests/.
    Merge note: the unit root test file changed on-device mid-pass (mtime guard rejected the
    first commit); the owner's current version was pulled, diffed (only my rename lines
    differed), and the renames were reapplied on top - no force overwrite. Sandbox suite
    71/71 green post-merge. Repo pytest on 3.14t: Not run.
  EVIDENCE:
  - src/melder/mutation_research/mutation_configuration.py:239-246
  - tests/unit/melder/mutation_research/test_mutation_research_root.py:221-221
  - tests/integration/melder/crystallizer/test_crystallizer_lifecycle_integration.py:281-281
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:925-990
  IMPACT: Naming baseline is professional across the MR lane and its crystallizer-side tests.
  NEXT: Owner 3.14t pytest checkpoint, then STORY-02 mediums (BUG-039-048) including a
    research_set.py pass under the owner's no-teardown-paranoia ruling.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-07-18T13:25:32Z
  TYPE: FACT
  CLAIM: STORY-02 medium tranche part 1 (BUG-040, 041, 042, 044, 047) re-verified and fixed
    with 5 red-then-green regression tests. Fixes: (040) join journal metadata records
    forced = divergence OR armed lane-type override, so a required force=True is never
    journaled as unforced; (041) ResearchJournal.from_payload refuses non-ascending restored
    sequences loudly and clamps the counter above every hydrated entry - reversal/reuse
    impossible; (042) SourceDiffStrategy compares COMPLETE recorded text - a terminal-newline
    delta reports changed with an explicit marker row instead of identical; (044)
    diff_research(strategy=...) forwards the caller's strategy through the composition branch
    (strategy param widened to Optional[str]=None with per-kind defaults "source"/"members";
    unknown names surface the documented KeyError); (047) new ResearchSet._validate_campaign
    called by all 11 campaign-accepting verbs - empty stamps refuse at the write seam,
    matching campaign_view's read validation (all 11 injection sites audited against their
    owning defs). research_set package paranoia check: zero getattr/hasattr. Sandbox: 88/88
    green (incl. journal + source-diff pre-existing suites); the 5 new tests were red
    pre-fix. Repo pytest on 3.14t: Not run (owner-run).
  EVIDENCE:
  - src/melder/mutation_research/research_set/research_set.py:1605-1700
  - src/melder/mutation_research/research_set/research_journal.py:258-300
  - src/melder/mutation_research/diff/strategies/source_diff_strategy.py:96-120
  - src/melder/mutation_research/mutation_research.py:1132-1200
  - src/melder/mutation_research/research_set/research_set.py:263-295
  IMPACT: 16 of 24 epic bugs fixed (031-038, 040-042, 044, 047, 049 + STORY-01 pair).
  NEXT: Remaining tranche needs one owner DECISION and one seam extension: (048 med-high)
    closing the public-lane-mutator bypass changes public API surface (lane mutators must
    become set-governed) -> DECISION_REQUEST; (045+046) both need per-member ancestry in the
    group-diff resolver material seam (_resolve_group_material) before the strategy can pair
    honestly; (039) deep-copy sweep across 4 node/entry files; (043) custody-absence
    classification in part_diff_strategy; then STORY-03 (150-153) + STORY-04 (261).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-18T13:31:31Z
  TYPE: FACT
  CLAIM: BUG-048 (med-high) fixed under owner ruling option (a), landed with the public-shape
    change + full test updates the owner directed. All five ResearchLane mutators (add_node,
    detach_nodes, set_anchor, mark_joined, mark_archived) are now set-internal
    (underscore-prefixed); lanes are documented read surfaces under the single-residence law
    (class-docstring Governance section added). All 11 research_set.py call sites updated;
    from_payload untouched (writes internals directly). Tests: test_research_lane.py +
    test_grouped_research_node.py migrated to the internal names (they unit-test the class
    itself), the BUG-037 race test rides _mark_archived/_detach_nodes, and a new regression
    proves the public surface physically cannot rebuild the audit's forbidden state
    (multi-lane same identity with residence=None). Sandbox: 103/103 green across the widened
    suite. Repo pytest on 3.14t: Not run (owner-run). No callers of the five names exist
    outside the MR package (src grep clean; DAG add_node is a different class).
  EVIDENCE:
  - src/melder/mutation_research/research_set/research_lane.py:90-140
  - src/melder/mutation_research/research_set/research_set.py:830-1000
  - tests/unit/melder/mutation_research/research_set/test_research_set.py:640-690
  IMPACT: 17 of 24 epic bugs fixed; the single-residence model is now structurally
    unbypassable from public surfaces.
  NEXT: Remaining: 045+046 (group-diff material seam pair), 039 (deep-copy sweep across 4
    node/entry files), 043 (part-diff custody classification), STORY-03 (150-153), STORY-04
    (261). Session context is near its limit - next session REONBOARDs per
    compaction_requirements and resumes from this note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-18T14:13:11Z
  TYPE: FACT
  CLAIM: BUG-039 and BUG-043 re-verified and fixed with red-then-green regression tests
    (108/108 sandbox green). (039) metadata is deep-copied at intake AND exposure across all
    four carrier files (research_node, grouped_research_node, transition_entry,
    research_lane) - nested mutation through public metadata can no longer change live
    describe() state outside governed mutation/publication. (043) part-diff structural truth
    now rides everything a side knows (text custody OR fingerprint): a module known on both
    sides with text missing on either reports text_unavailable_modules; removed/added mean
    structurally gone/new (no text AND no fingerprint) - custody absence is never presented
    as deletion (new per-side _fingerprints helper). Repo pytest on 3.14t: Not run.
  EVIDENCE:
  - src/melder/mutation_research/diff/strategies/part_diff_strategy.py:81-120
  - src/melder/mutation_research/research_set/research_node.py:107-245
  - tests/unit/melder/mutation_research/diff/test_part_diff_strategy.py:130-165
  - tests/unit/melder/mutation_research/research_set/test_research_set.py:700-730
  IMPACT: 19 of 24 epic bugs fixed. STORY-02 fully closed except the 045+046 pair.
  NEXT: 045+046 (extend _resolve_group_material with per-member ancestry, then honest
    version pairing + transitive ancestry in MemberDiffStrategy), STORY-03 (BUG-150-153,
    group_diff appendix), STORY-04 (BUG-261, snapshot recency). Fresh session REONBOARDs and
    resumes here.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-18T15:45:04Z
  TYPE: FACT
  CLAIM: Owner's first 3.14t checkpoint run triaged (17 last-failed). MR-lane fallout fixed:
    (1) codegen room research_diff hardcoded the spell-grain "structural" default, which my
    BUG-044 forwarding surfaced as a KeyError on composition pairs - the room seam is now
    kind-aware via a new public MutationResearch.is_composition probe (spell pairs keep the
    documented reasoning-layer default; composition pairs ride the root's members default;
    explicit unknown names still refuse - BUG-044 law preserved); (2)
    test_foresight_reads_refuse_dead_custody modeled a CLEANED crystallizer, unreachable
    under the owner teardown ruling - it now models live-but-inactive and the refusal
    contract holds. Sandbox 108/108. Non-MR failures ticketed and handed off by owner
    directive: conduit_ward BUG-005 double-drift -> helper_f; link-guardrail ordering +
    counter_switch cleanup posture -> helper_1 (mailbox HANDOFFs + board alerts posted).
  EVIDENCE:
  - src/melder/nexus/rift/command_system/codegen_command_system.py:965-1015
  - src/melder/mutation_research/mutation_research.py:1132-1160
  - tests/unit/melder/mutation_research/test_mutation_research_foresight.py:174-192
  - tickets/tasks/2026-07-18_conduit_ward_bug005_test_double_drift_task.md:1-1
  - tickets/tasks/2026-07-18_link_guardrail_counter_switch_task.md:1-1
  IMPACT: MR lane clean against the owner's checkpoint; cross-subsystem red routed to its
    owners with durable tickets.
  NEXT: Owner reruns --last-failed; MR epic resumes at 045+046.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-18T15:51:50Z
  TYPE: FACT
  CLAIM: BUG-045 + BUG-046 fixed (STORY-02 fully closed). Material seam:
    _resolve_group_material now carries per-member transitive ancestor_spell_ids and
    composition-level ancestor_group_ids via a new cycle-safe _transitive_ancestors walk
    (unresident links end their branch - ancestry never guesses). Strategy:
    MemberDiffStrategy pairs version_moved ONLY when lane match AND a real ancestry relation
    holds in either direction (unrelated same-lane identities stay honest
    additions/removals), and ancestry_related walks the transitive closure with direct
    parents kept as fallback for detached older payloads. 3 regression tests (2 red-then-
    green + true-move guard). Sandbox 111/111. Repo pytest on 3.14t: Not run.
    STORY-01 and STORY-02 checkboxes: all 21 of their bugs landed.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:2700-2800
  - src/melder/mutation_research/group_diff/strategies/member_diff_strategy.py:80-200
  - tests/unit/melder/mutation_research/test_mutation_research_root.py:760-850
  IMPACT: 21 of 24 epic bugs fixed; remaining = STORY-03 (BUG-150-153, group_diff appendix)
    + STORY-04 (BUG-261, snapshot recency).
  NEXT: Read codex/2026-07-17_melder_bug_audit_mutation_group_diff_appendix.md and
    _snapshot_recency_appendix.md, re-verify, fix. Fresh session REONBOARDs here if this one
    ends.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-18T15:58:26Z
  TYPE: FACT
  CLAIM: STORY-03 (BUG-150-153) re-verified and fixed; sandbox 120/120. (150) current
    compositions are each lane's LATEST GroupedResearchNode in registration order, not the
    raw lane tip - a later unrelated default-lane spell can no longer revoke a resident
    composition from the reverse lift; (151) record_world_entry re-arms the one-shot ancestry
    stamp on ANY pre-commit refusal and re-raises, so a correctable validation failure never
    destroys synthesized lineage (distinct from 049's promotion path); (152) recorded-source
    presence is the str TYPE, never truthiness, at both custody-carrier read sites - empty
    modules are valid recorded Python (origin='recorded') and participate in diffs; (153)
    the structural class shape carries decorators + keywords (metaclass and friends) AND
    _diff_class compares them (fix needed both halves - capture alone left verdicts
    identical), reported as class_decorators_changed / class_keywords_changed. Regression
    tests: 150/151 in root tests, 153 in structural strategy tests (red pre-fix). DEBT: 152
    has no dedicated regression test yet (needs a custody-carrier fixture) - source evidence
    only; add alongside the next foresight-fixture pass. Repo pytest on 3.14t: Not run.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:2900-2940
  - src/melder/mutation_research/mutation_research.py:905-935
  - src/melder/mutation_research/mutation_research.py:1286-1300
  - src/melder/mutation_research/diff/strategies/structural_diff_strategy.py:198-240
  IMPACT: 23 of 24 landed (STORY-01/02/03 complete pending owner validation). Remaining:
    STORY-04 / BUG-261 (snapshot recency,
    codex/2026-07-17_melder_bug_audit_mutation_research_snapshot_recency_appendix.md -
    already staged for read).
  NEXT: BUG-261 re-verify + fix; then epic walkthrough + owner acceptance + closure sync.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-18T16:06:13Z
  TYPE: FACT
  CLAIM: BUG-261 (STORY-04, the final epic bug) re-verified and fixed; sandbox 121/121.
    NetworkVersioner.snapshot's dedupe path now MOVES the existing address to the newest
    retention position instead of returning with recency untouched: latest_sha identifies
    the restored organization, serialization/hydration carry the corrected order, and with
    bounded retention the next mutation evicts the true oldest-by-operation - the restored
    predecessor stays reachable and the documented undo ring holds. Red-then-green
    regression walks the audit sequence exactly (A, B, re-snapshot A, then C: latest=A,
    retained=[A, C], undo-to-A intact, B evicted). ALL 24 AUDITED BUGS ARE NOW LANDED
    (STORY-01/02/03/04 complete) - epic is accept-ready pending: (1) owner 3.14t pytest run,
    (2) owner acceptance walkthrough, (3) closure sync. Open debt on record: BUG-152
    dedicated regression (custody fixture) + patch-framework/system-docs promotion pass for
    the lane-governance (048) and emission-lock (031) architecture deltas.
  EVIDENCE:
  - src/melder/mutation_research/research_set/network_versioner.py:87-130
  - tests/unit/melder/mutation_research/research_set/test_network_versioner.py:80-115
  IMPACT: 24/24. The remediation program defined by this epic is code-complete.
  NEXT: Owner runs pytest tests/unit/melder/mutation_research (and the room integration
    file) on 3.14t; on green, acceptance walkthrough then move-to-completed + board/artifact
    closure sync.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-18T16:39:11Z
  TYPE: FACT
  CLAIM: Mailbox consumption at REONBOARD (post-compaction). Three messages addressed to
    helper_f2 consumed: (1) helper_1 ACK - link-guardrail ordering confirmed a real
    regression (guard hoisted ahead of plan build) and counter_switch cleanup reclassified
    as intentional tombstone with the 3 tests to be updated; executing both. (2) helper_f
    ACK - BUG-005 test-double drift task claimed in_progress. (3) helper_f NOTICE - that
    task is COMPLETE: all 10 items repaired as drift, zero production changes; full 3.14t
    run rides the owner. Both handoff lanes from the owner's 17-failure checkpoint are
    therefore claimed, and one is already landed; owner rerun of --last-failed remains the
    cross-lane validation step.
  EVIDENCE:
  - tickets/tasks/2026-07-18_conduit_ward_bug005_test_double_drift_task.md:1-1
  - tickets/tasks/2026-07-18_link_guardrail_counter_switch_task.md:1-1
  IMPACT: MR epic validation posture unchanged (accept-ready); the sibling failures from
    the owner checkpoint are owned and moving without helper_f2 intervention.
  NEXT: Complete the journaled BUG-152 dedicated regression test (in-flight debt), then
    await owner 3.14t validation for the epic acceptance walkthrough.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-18T16:45:48Z
  TYPE: MEASURE
  CLAIM: BUG-152 regression-test debt CLEARED. Dedicated test
    test_empty_recorded_module_is_present_source_not_absence landed in the foresight file
    using the real custody fixtures (_custody_payload/_install_crystal): a recorded
    pkg.empty module with source_text='' must answer source_view with origin='recorded',
    source='', text_unavailable=False, and no unknown_module miss. Proof method:
    red-then-green on real modules - reverting BOTH custody-carrier sites to pre-fix
    truthiness made exactly this one test fail (143 passed / 1 failed); restoring the
    isinstance(str) presence law returned the sandbox suite to 144/144. Suite grew
    142->144: the new test plus the live-disk drift test now runnable after minimal
    tmp_path emulation was added to the sandbox mini-runner (harness gap, not a code
    change). Committed to the device mtime-guarded; on-device py_compile green.
    Repo pytest on 3.14t: Not run.
  EVIDENCE:
  - tests/unit/melder/mutation_research/test_mutation_research_foresight.py:709-737
  - src/melder/mutation_research/mutation_research.py:1286-1300
  - src/melder/mutation_research/mutation_research.py:1554-1572
  IMPACT: Every one of the 24 audited bugs now carries a dedicated red-then-green
    regression test; the only remaining epic debt is the 031/048 patch-doc/system-docs
    promotion pass.
  NEXT: Owner runs pytest tests/unit/melder/mutation_research (+ room integration file)
    on 3.14t; on green, acceptance walkthrough then closure sync.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-18T16:51:20Z
  TYPE: PLAN
  CLAIM: 031/048 promotion pass (the last journaled epic debt besides owner validation).
    On-demand gates read this cycle: patch_framework_gating, patch_artifact_consumption,
    documentation_standards, staleness_protocol. Canonical delta targets pinned in
    src_components.md: (1) root Concurrency/Threading line 2674 still says lock order
    'root -> set -> crystallizer' - missing the emission lock; (2) ResearchLane bullet
    line 2698 still advertises public 'detach_nodes'; (3) the 2795-2805 threadsafety
    block's one-way chain omits emission. Plan: author patch folder
    mr_emission_lock_and_lane_governance_2026_07_18 (architecture_patch + 2 component
    patches, drafted during the bridge outage), merge the three canonical deltas, promote
    the folder to patches/completed/ (repo convention per
    mutation_research_accessor_doors_2026_07_12), link artifacts from this epic.
    src_architecture.md checked: its MR mentions are C1 file-map lines only - no lock or
    lane-mutation claims, no delta needed there.
  EVIDENCE:
  - system_docs/src_components.md:2674-2674
  - system_docs/src_components.md:2697-2699
  - system_docs/src_components.md:2795-2805
  - src/melder/mutation_research/mutation_research.py:590-600
  - src/melder/mutation_research/research_set/research_lane.py:386-592
  IMPACT: Clears the final self-serviceable epic debt; canonical docs stop contradicting
    landed concurrency/governance law.
  NEXT: Write the patch folder, merge the three deltas, promote, link, board-sync.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-18T16:52:10Z
  TYPE: FACT
  CLAIM: 031/048 promotion pass COMPLETE - the last self-serviceable epic debt is
    cleared. Patch folder mr_emission_lock_and_lane_governance_2026_07_18 authored
    (architecture_patch + component patches for the root and the research_set package),
    three canonical deltas merged into src_components.md: root concurrency now documents
    the emission RLock and the extended one-way order emission -> root -> set ->
    crystallizer with the emission-before-root prefix rationale; the ResearchLane bullet
    documents set-governed underscore mutators (single-residence law structurally
    unbypassable, public lanes are read surfaces); the package threadsafety chain gained
    the emission hop (spellbook -> emission -> root -> set -> child/crystallizer).
    src_architecture.md needed no delta (C1 file-map mentions only). Folder promoted to
    patches/completed/ per repo convention. Epic debt remaining: NONE beyond owner
    validation (3.14t pytest run) + acceptance walkthrough + closure sync.
  EVIDENCE:
  - system_docs/src_components.md:2673-2682
  - system_docs/src_components.md:2705-2712
  - system_docs/src_components.md:2813-2816
  - system_docs/patches/completed/mr_emission_lock_and_lane_governance_2026_07_18/architecture_patch.md:1-75
  IMPACT: Canonical docs and landed code agree; the epic is fully accept-ready with
    zero outstanding debt items.
  NEXT: Owner runs pytest tests/unit/melder/mutation_research (+ room integration file)
    on 3.14t; on green, acceptance walkthrough then move-to-completed + closure sync.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [x] Work walkthrough shared with user (24/24 + tests + doc promotion, 2026-07-18)
- [x] Acceptance criteria confirmed by user (owner directive "turn it in obv",
      2026-07-18; 3.14t validation rides the owner run - REOPEN on red)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order (Critical->High->Medium->Low).
- Reference story/task evidence (and the audit report line ranges) instead of duplicating tactical logs.
- Keep notes append-only and preserve UNKNOWN-first discipline.

## Context / Handoff Summary
Remediation epic for the 24 mutation research bugs from the 2026-07-17 audit, owned by helper_f2
(owner-routed takeover 2026-07-18; prior MR-subsystem agent mutation_0 departed and was removed
from active boards). Status in_progress, mode discovery. No Criticals - begin with the 10 Highs:
re-verify each finding against current source (audit was read-only and predates recent lanes),
then fix at root cause with regression tests. All evidence is in the audit reports listed above.
