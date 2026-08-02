# Story: Binding & SpellIndex contract remediation (BUG-110-113, STORY-conduit_binding_meld-04)

## Metadata
- Story ID: STORY-2026-07-18-conduit-binding-meld-04
- Parent Epic: EPIC-2026-07-17-bugfix-conduit-binding-meld
- Status: in_progress
- Owner: cowork
- Agent Name: helper_f2
- Priority: p0 (3 High + 1 Medium inside the p0 epic)
- Created: 2026-07-18T17:15:00Z
- Updated: 2026-07-18T17:15:00Z

## Problem / Opportunity
Four audited defects in the Spellbook binding/index layer (audit appendix
codex/2026-07-17_melder_bug_audit_binding_index_appendix.md): (110) an aborted bind
leaves a live spell + claimed frame lookup + five populated maps behind (no transaction
rollback); (111) Spellbook cleanup never calls Spell.cleanup() on parked
`_inactive_spells` members before discarding their registries; (112) `_apply_notch`
accepts a spell from ANOTHER index and splits ownership/membership/active-map/selection
truth; (113) add-to-index infers ownership from a caller-controlled `selected_spell_id`
instead of validating the target index object against the owned registry.

## MRP Alignment
Bind/index integrity is the runtime's ownership spine under 3.14t; partial-bind residue
and split-brain index membership violate the "one truth, deterministic cleanup" law.
Root-cause fixes with regression tests, no defensive guards.

## Ticket Contract
- ENTRY_GATE: Routed from attention_board.md (helper_f2 row); epic claim NOTICE sent to
  helper_f (epic owner) with the spellbook-side partition (04 now, 06 next unless
  objected); binding_index appendix read in full.
- EXECUTION_BOUNDARY: BUG-110/111/112/113 fixes + regression tests inside
  src/melder/aether/spellbook/** (and tests). No conduit-side edits (helper_f's files).
  No drive-by refactors.
- DEPENDENCIES: audit appendix; live spellbook.py re-verification (audit line anchors may
  be stale - path-correction precedent from helper_f's Story 02); md5-verify staged reads
  vs device before use as edit base (stale-stage law).
- EXIT_GATE: 4/4 bugs fixed-with-regression-test or evidencedly reclassified; epic
  checklist + board synced; validation truthfully reported (owner runs 3.14t).
- FAILURE_ESCALATION: DECISION_REQUEST on any public-shape change; CONFLICT if live
  source contradicts the audit; BLOCKER if a fix would violate a documented invariant.

## Goals
- Aborted bind restores exact pre-bind state (BUG-110).
- Parked spells cleaned exactly once in Spellbook teardown (BUG-111).
- Notch refuses non-member spells before any mutation (BUG-112).
- Add-to-index validates target-index identity against the owned registry (BUG-113).

## Non-Goals
- Stories 01/02/03/05/07 (helper_f); Story 06 only after its own claim note.
- Bind-path redesign or performance work.

## Validation Plan
- Unit-first regression tests per bug, symptom-named, red-then-green where the sandbox
  import closure allows; thread-safety assertions where the defect is lifecycle-racy.
- Full-repo / focused 3.14t pytest: owner-run; agent reports "Not run." truthfully.

## Decision Log
- 2026-07-18T17:15:00Z: Story claimed by helper_f2 with spellbook-side partition
  (04 now, 06 intent) to keep spellbook.py single-writer beside helper_f's conduit lanes.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: helper_f2 opened the lane after turning in the MR audit epic;
  disjoint-story claim beside the epic owner.

## Applicable Anti-Patterns (lane checklist)
- [ ] No defensive None-guards standing in for lifecycle proof.
- [ ] No snapshotting owned registries without documented correctness need.
- [ ] No test assertions on private shape without contract backing.
- [ ] No cross-file drive-bys outside spellbook scope.

## Noting Behavior
- Story notes: cross-task synthesis, dependency movement, gate transitions; per-bug
  tactical detail stays in the notes here (no child tasks unless scope forces them).

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS:
  - Spellbook bind transaction, inactive-spell lifecycle, notch/index membership law.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-07-18T17:15:00Z
  TYPE: PLAN
  CLAIM: Lane opened. Appendix read in full: 110 (High, bind rollback - five maps + frame
    claim + live Spell survive an aborted bind), 111 (High, parked spells discarded
    uncleaned), 112 (High, notch accepts foreign-index spell - split-brain selection), 113
    (Medium, ownership inferred from caller-controlled selected id). First step is live
    re-verification: the audit's spellbook.py anchors (3988-4005, 4580-4688, 380-525,
    1443-1467, 3151-3168, 3336-3358) predate recent lanes and may have drifted.
  EVIDENCE:
  - codex/2026-07-17_melder_bug_audit_binding_index_appendix.md:1-107
  IMPACT: Story scope pinned before any code read; partition prevents spellbook.py write
    collisions between agents.
  NEXT: Stage spellbook.py fresh (md5-verified), locate the four sites in live source,
    one FACT note per confirmed/corrected finding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-18T17:20:00Z
  TYPE: DECISION
  CLAIM: OWNER RULING (standing law for this story): the agent that authored the
    spellbook/binding code worked with a 250k context window and DID NOT KNOW the Mediator
    system exists - it could not read the whole repo. Consequence for fixes: before
    implementing, verify how each defect relates to the mediator layer (transaction /
    admission / lineage strategies); prefer routing corrections through the existing
    mediator machinery over hand-rolled local logic when it is the system-correct seam
    (BUG-110 bind rollback is the prime candidate). Do not treat spellbook.py's local
    patterns as the whole truth.
  EVIDENCE:
  - tickets/epics/completed/2026-06-20_implement_new_mediator_strategies_epic.md:1-1
  IMPACT: Fix design must be mediator-aware; prevents re-implementing rollback beside an
    existing transaction system.
  NEXT: Locate the mediator package + its transaction strategies, map bind's current
    (non-)integration with it, then re-verify BUG-110-113 sites in live spellbook.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-18T17:32:00Z
  TYPE: FACT
  CLAIM: BUG-110 CONFIRMED on live source + mediator map complete. The `with
    self.transaction("bind", ...)` window (spellbook.py:4713) is ADMISSION-ONLY: the
    mediator (ChangeControl: embargo/conflict/lock scopes, ChangeControlStagedMutation
    commit/abort hook payloads) governs admission and window lifecycle but never owns the
    spellbook's local mutations - the 250k-window author opened the window, then mutated
    directly. Mutation order inside bind (4741-4877): create live Spell -> frame
    `claim_lookup` (4771) -> `_lookup_spells`/`_spells`/`_register_owned_spell_id`
    (4772-4774, = _spells_by_id + _spell_id_pool + _spell_ids) -> version cache -> conduit
    stamping -> THEN the fallible tail: `register_index` (4826, audit's injection point),
    risk manager, structural staging, crystallizer emissions, research record, nexus
    publish. The except (4877-4879) only logs + re-raises: zero rollback, exactly the
    audited five-map + frame-claim + live-Spell residue. Reorder-to-commit-last is NOT
    viable (the fallible tail reads through the committed maps), so the root-cause fix is
    compensating rollback in the exception path: unwind in reverse (release frame claim -
    `AethericFrame.release_lookup`/`release_lookup_by_spell_id` exist at
    aetheric_frame.py:811/823 - pop the five maps via `_unregister_owned_spell_id`
    (spellbook.py:1105) + lookup/spells removal, then `new_spell.cleanup()`), then
    re-raise. Wire it INSIDE the transaction window so the mediator window closes after
    local state is restored.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4713-4879
  - src/melder/aether/aetheric_frame/aetheric_frame.py:793-823
  - src/melder/aether/spellbook/spellbook.py:993-1105
  IMPACT: Fix design pinned and mediator-aligned per the owner ruling; no parallel
    rollback system invented.
  NEXT: Implement the BUG-110 compensating unwind (staged locals: claim_done, maps_done,
    spell live) + symptom-named regression (inject register_index failure, assert all five
    maps + frame lookup + spell cleaned state restored); then re-verify 111/112/113.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-18T17:50:00Z
  TYPE: DECISION
  CLAIM: OWNER-DIRECTED RESTORE executed: the hand-rolled BUG-005 reversible-detach pair
    (spellbook.py +191 @2948: _detach/_reattach/_destroy_detached_link_contract;
    conduit_ward.py unlink-flow callers @948-1035) is REMOVED - both files rewritten to
    exact HEAD blobs (git-free restore; git stash aborted on the bridge's no-unlink law,
    stale .git/index.lock parked-or-remaining - owner should delete it before his next git
    write). Diff vs HEAD now empty (--ignore-cr-at-eol); py_compile green both. Feature
    backups: _to_delete/spellbook_bug005_feature_backup.py + conduit_ward_bug005_feature_backup.py.
    Owner ruling: that compensation belongs in the MEDIATOR (Add/RemoveSpellOrIndexFromContract
    strategies). Consequence: committed BUG-005 test repairs (HEAD 27e914adf) now assert a
    removed contract - expected red until the mediator-routed redesign. Kept intact:
    creations.py (Critical 073), conduit.py (071 + link guard).
  EVIDENCE:
  - _to_delete/spellbook_bug005_feature_backup.py:2948-3139
  IMPACT: Spellbook back to HEAD; my BUG-110-113 targets unaffected.
  NEXT: Resume BUG-110 red test + compensating unwind on the restored file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
helper_f2 owns the spellbook-side stories of the conduit/binding/meld epic (04 active,
06 intended next). Status in_progress, mode discovery. Resume from the latest note's NEXT.
