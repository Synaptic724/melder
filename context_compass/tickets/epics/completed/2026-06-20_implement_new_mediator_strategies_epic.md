- Completed: 2026-07-12T21:00:00Z
- Summary: Landed the owner-ruled conduit-lineage freeze (notch +
  add/remove/transfer parity: park-mode close_and_drain, quiesce plan key,
  on_start freeze / on_end reopen via the new finalize-owned dispatch that
  fires exactly once on every exit path - also healing the unelect D-A
  leak and the D-B terminal-verb defect), plus the owner-shaped
  ticket-first admission on CreationGate AND RiftGate closing the
  drain-race TOCTOU. Race probe rewritten to the gate-freeze contract.
  Closed on owner directive; pytest Not run by agent - reopen on red.
  Residue carried: unit rows for the 3 parity strategies (copy the 5
  notch rows); freeze+admission patch-dir promotion.

# Epic: Implement New Mediator Strategies (SpellSystemState lineage coordination)

## Metadata
- Epic ID: EPIC-2026-06-20-implement-new-mediator-strategies
- Status: ready (REACTIVATED + INHERITED 2026-07-11T22:05:00Z, melder_0
  - owner correction: stays on the active program. FIRST MOVE: source
  re-verification of the lineage-scope race gap (the transaction plane
  evolved since June - the notch/add_to_index/remove_from_index
  strategies landed and index-link emission runs under the owner op's
  seal, so parts of the gap may already be closed); then melder_0
  DRAFTS D1-D5 recommendations from source so the owner gets one
  consolidated ruling instead of five open questions.)
- Park history: PARKED 2026-07-11 orphan sweep (D1-D5 never answered;
  gap: validity/remediation writes hold no embargo claim).
- Owner: cowork
- Agent Name: melder_0 (inherited from mediator_builder_0)
- Priority: p1
- Created: 2026-06-20T22:46:32Z
- Updated: 2026-06-20T22:46:32Z
- Target Window: 2026-Q2
- Related Program/Initiative: DevOps change-control transaction plane (free-threaded 3.14t correctness)
- Seed: tickets/tasks/completed/2026-06-20_mediator_coverage_spike_conjure_bind_states_task.md
- Reference: artifacts/2026-06-05_devops_transaction_control_plane_philosophy.md,
  artifacts/2026-06-13_devops_mediator_system_map.md (retain_as_reference)

## Mediator Responsibility (the framing for this whole epic)
A mediator transaction manages ONLY the DevOps control plane: it acquires the SCOPE CLAIMS a
structural mutation needs (the embargo gate) and runs envelope-only start/end coordination. It does
NOT reach into the runtime and does NOT take another system's responsibility. The DOMAIN caller runs
the real effect INSIDE the held window (admit -> domain effect -> commit), exactly the
`Spellbook.notch_spell` -> `_apply_notch` shape. Evidence: the philosophy artifact (EmbargoManager =
the real gate; TransactionStrategy = "computes blast radius and claim scope"; strategies should not
maintain the registry directly), and the already-landed envelope strategies whose `on_start`/`on_end`
are deliberate no-ops -- bind_transaction_strategy.py:322-356, notch_transaction_strategy.py:143-151.

## Problem / Opportunity
SpellSystemState / ConduitResolutionState validity-and-remediation writes BYPASS the mediator
entirely. Every state writer takes only its own object `RLock`; it holds NO embargo claim, and the
embargo scope vocabulary has NO lineage-keyed scope. So two directions race on a single spell lineage:

1. A live post-conjure remediation ("a spell has an issue": gate / revalidate / clear-dirty / flip
   flags) writes conduit/lineage validity directly under a best-effort `try/except`, holding no seal.
2. A concurrent structural op (NOTCH / ADD_TO_INDEX / REMOVE_FROM_INDEX / TRANSFER_OWNERSHIP) on the
   SAME lineage holds a spellbook+conduit EXCLUSIVE embargo seal -- but that seal does NOT protect the
   state record, because the state writer ignores the embargo (different lock).

Because the validity verdict fans out through RiskManager onto the spellbook's
`validation_required` flag (the meld gate), a torn remediation-vs-structural interleave can leave the
meld gate inconsistent with the structural truth under no-GIL 3.14t.

Evidence:
- No lineage scope exists. The scope-key builders are spellbook / identity / transaction_owner /
  conduit / cluster / binding / contract only.
  EVIDENCE: src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_manager.py:262-415
- The bypass writer (no claim, best-effort), called during conjure AND live revalidation.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py:214-262
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:863-962
- Validity change -> RiskManager -> spellbook validation-required (the meld gate).
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:299-364
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py:223-274
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:317-372,525-542
- The structural seal that does NOT cover the state record (claims spellbook+conduit+binding, no
  lineage).
  EVIDENCE: src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py:110-141

## Context (focus: SpellSystemStates + pre-conjure + pre-conjure bind)
- Pre-conjure bind registers the lineage (`register_index` -> mark structural + dirty + `new_lineage`)
  on the Spellbook BEFORE any conduit exists; the bind strategy claims spellbook-INTENT only, conduit
  ids = (). This path runs single-threaded under the Spellbook lock and has no conduit resolution
  state yet -> low live-race risk, but it IS the genesis of the lineage state this epic governs.
  EVIDENCE:
  - src/.../strategies/bind_transaction_strategy.py:103-158 (pre-conjure plan)
  - src/.../spell_system_states/spell_system_states.py:246-300 (register_index)
- Conjure-time validity writes (Phase 6 `SpellSystemValidationSystem.validate(conduit_id=...)`) run
  under the Spellbook lock / single-conjure invariant -> serialized, not a live race.
- The LIVE race is post-conjure remediation / meld-time lazy revalidation
  (`Meld._ensure_lineage_resolvable` -> resolution-phase rerun) writing state with no seal while a
  structural op is admitted. THIS is what the new strategy must serialize.

## MRP Alignment
This is the one genuine correctness gap left in the admission plane: lineage remediation vs structural
ops can interleave. The MRP fix is small and coherent -- one new scope key, one envelope transaction,
and a lineage claim added to the existing lineage-affecting strategies -- not a redesign. It must be
right because it governs the meld gate's truthfulness under free-threading.

## Goals (Outcomes)
- Add a fine-grained `spell_lineage` scope so the mediator can serialize at lineage granularity
  WITHOUT taking the whole spellbook/conduit.
- Add a SPELL_STATE (remediation) transaction: an ENVELOPE-only strategy that claims the affected
  lineage scope(s) so DevOps can work a `SpellSystemState` / `ConduitResolutionState` inside a held
  window.
- Route the LIVE post-conjure remediation / lazy-revalidation state writes through that transaction.
- Have the existing lineage-affecting strategies (NOTCH, ADD_TO_INDEX, REMOVE_FROM_INDEX,
  TRANSFER_OWNERSHIP) ALSO claim the lineage scope, so structural ops and remediation mutually
  serialize at lineage granularity.
- Keep every strategy envelope-only (mediator = DevOps only); the state write stays in the DevOps
  validation/remediation caller inside the window.

## Non-Goals (Explicit Exclusions)
- MUTATION wiring. `ChangeTransactionType.MUTATION` exists but is unregistered/unguarded; it stays a
  future subsystem (user-descoped). The lineage scope is to be designed so MUTATION adopts it later
  with zero rework.
- A CONJURE transaction. Conjure runs under the Spellbook lock / single-conjure invariant and is not a
  live race; deferred as a separate optional item.
- Any change to the meld hot path, to `Creations`, or to the structural seal already proven for
  link/bind/unlink/cluster/transfer.
- A generic reporting plane or eager metadata mirroring (the philosophy artifact is explicitly
  suspicious of these).

## Scope Boundaries
- In scope: `make_scope_key_spell_lineage`; the SPELL_STATE enum value + envelope strategy + builder
  registration + mediator allow-list; the lineage-claim additions to notch/add/remove/transfer;
  routing the live remediation/lazy-revalidation writes through the new transaction; tests at all
  three levels.
- Out of scope: the member-store SpellIndex model (general_0's lane); the structural seals themselves;
  MUTATION; CONJURE; doc-drift merges into canonical system_docs (codex lane).

## Ticket Contract
- ENTRY_GATE: this is SYSTEM-IMPACTING (admission contract + scope vocabulary + validation-system
  coordination), so per `patch_framework_gating.md` NO implementation starts until
  `system_docs/patches/active/<patch_id>/architecture_patch.md` + `component_patch_*.md` exist and are
  ticket-linked, the open decisions (D1-D5) are resolved by the user, and certification holds.
- EXECUTION_BOUNDARY: `transaction_manager.py` (one new scope helper); `transaction_request.py` (enum
  value); one new `spell_state_transaction_strategy.py`; `transaction_strategy_builder.py` +
  `transaction_mediator.py` (register + allow-list); the four lineage-affecting strategy files (add
  the lineage claim); the validation/remediation caller that opens the transaction; tests. NO change to
  meld, Creations, or the existing structural seals.
- DEPENDENCIES: landed mediator core (embargo claim modes x/s/ix; strategy base apply_commit_delta);
  the SpellSystemStates write surface (bulk_set_conduit_*_validity, set_validity, clear_*_dirty); the
  `ConduitLineageGateOps` envelope precedent.
  CROSS-LANE COUPLING: ADD_TO_INDEX / REMOVE_FROM_INDEX are being reshaped by general_0 under the
  corrected single-active-spell model (epic spellindex_genuine_index_operations; the multi-member
  premise was reverted -- "SpellIndex = ONE active spell; spell_id resolves"). Their lineage-claim work
  SEQUENCES AFTER that epic settles. NOTCH and TRANSFER_OWNERSHIP are stable today and can take the
  lineage claim independently. NOTE: the corrected model REINFORCES this epic -- the lineage scope keyed
  by `SpellIndex.id` (the organizing key) is exactly the right granularity.
- EXIT_GATE: lineage remediation and a concurrent structural op on the SAME lineage provably serialize
  (looped concurrency stress, mirror the 40x pattern); no regression to existing transactions; user
  runs the 3.14t suite green and accepts.
- FAILURE_ESCALATION: DECISION_REQUEST for D1-D5; CONFLICT if routing the remediation write through a
  transaction surfaces a real ordering bug in the validation system; BLOCKER if the validation/meld
  caller cannot supply the affected lineage id(s) to open the transaction.

## Proposed Design (grounded; subject to D1-D5)
1. Lineage scope: `ChangeControlTransactionManager.make_scope_key_spell_lineage(spell_index_id)` ->
   `"scope:spell_lineage:<spell_index_id>"`, sibling to the existing `scope:` family
   (transaction_manager.py:262-415).
2. SPELL_STATE strategy (`SpellStateTransactionStrategy`): envelope-only. `build_start_plan` claims
   `make_scope_key_spell_lineage(id)` EXCLUSIVE for each affected lineage (+ optionally the owning
   spellbook IX so it coexists with unrelated piece-work -- D2). `on_start`/`on_end` no-ops; inherits
   the base `apply_commit_delta` (fact-baseline stamp only -- transaction_strategy.py:123-185).
3. Routing: the live post-conjure remediation / meld-time lazy-revalidation path opens the SPELL_STATE
   transaction around its `bulk_set_conduit_*_validity` / `set_validity` writes (admit -> write ->
   commit), NOT the conjure-time bulk writes (already serialized under the spellbook lock).
4. Structural strategies claim the lineage: notch/add/remove/transfer add
   `make_scope_key_spell_lineage(spell_index_id)` EXCLUSIVE to their seal (notch today claims
   spellbook+conduit+binding only -- notch_transaction_strategy.py:110-141).

## Open Decisions (DECISION_REQUEST -- needed before patch artifacts)
- D1: lineage scope key form -- `scope:spell_lineage:<id>` (lean: yes, matches the `scope:` family) vs
  `lineage:<id>`.
- D2: SPELL_STATE seal granularity -- lineage-only EXCLUSIVE (lean) vs lineage EXCLUSIVE + owning
  spellbook IX.
- D3: which write paths route through SPELL_STATE -- only live/post-conjure remediation + meld-time
  lazy revalidation (lean) vs also conjure-time bulk writes (already serialized).
- D4: CONJURE transaction -- deferred (lean) vs in scope.
- D5: confirm strategies stay envelope-only -- the DevOps caller runs the state write in the window
  (lean: yes, per the mediator-is-DevOps-only philosophy).

## Stories (Required to Complete)
- [ ] STORY: Lineage scope vocabulary -- `make_scope_key_spell_lineage` + unit tests + (if needed)
      `affected_identity_keys` integration.
- [ ] STORY: SPELL_STATE remediation transaction -- enum value + envelope strategy + builder
      registration + mediator allow-list + unit tests (claim-set seal; resolve; envelope no-ops).
- [ ] STORY: Route the live remediation / lazy-revalidation state writes through SPELL_STATE
      (coordination boundary). CROSS-AGENT: touches the spell compiler / validation-system surface ->
      mailbox before any edit.
- [ ] STORY: Lineage-claim additions to NOTCH + TRANSFER_OWNERSHIP (stable today) + component/
      integration tests proving mutual serialization with SPELL_STATE on one lineage.
- [ ] STORY (sequenced after general_0): Lineage-claim additions to ADD_TO_INDEX / REMOVE_FROM_INDEX
      once the corrected single-active-spell index model settles (general_0 epic
      spellindex_genuine_index_operations). Coordinate via mailbox before editing those strategies.

## Milestones
- [ ] M0 (gate): D1-D5 resolved; patch artifacts authored + ticket-linked (architecture + component).
- [ ] M1: lineage scope + SPELL_STATE envelope strategy landed (unit).
- [ ] M2: remediation routing landed; structural strategies claim the lineage.
- [ ] M3: concurrency stress proves remediation vs structural serialize; user 3.14t suite green; accept.

## Acceptance Criteria (Epic Done)
- A `spell_lineage` scope exists and is emitted by the SPELL_STATE strategy and by
  notch/add/remove/transfer.
- Under N concurrent (structural op on lineage L) + (remediation on lineage L), the two NEVER
  interleave their state writes: one fully precedes the other (proven by a looped stress test); no
  torn `validation_required` gate vs structural truth.
- Unrelated lineages still admit in parallel (lineage EXCLUSIVE does not serialize the whole frame).
- No regression to bind/link/unlink/cluster/transfer/notch/add/remove or the meld gate.
- Strategies remain envelope-only (no strategy writes SpellSystemState directly).
- User runs the 3.14t suite and reports green (agent: "Not run.").

## Risks / Mitigations
- RISK: routing remediation through a transaction reorders or deadlocks validation. MITIGATION: open
  the transaction at the narrowest boundary (the remediation write), reuse the same admit->effect->
  commit shape as notch; raise CONFLICT on any real ordering surprise.
- RISK: meld-time lazy revalidation cannot cheaply name the affected lineage(s). MITIGATION: it already
  resolves the target spell/lineage; thread the `spell_index_id` into the transaction metadata.
- RISK: lineage EXCLUSIVE over-serializes if the key is too broad. MITIGATION: key strictly by
  `spell_index_id`; disjoint lineages stay parallel by construction.
- RISK: agent cannot run 3.14t (Py3.10 sandbox). MITIGATION: dense contract + concurrency tests; user
  runs the suite.

## Applicable Anti-Patterns
- [ ] No implementation before patch artifacts exist and D1-D5 are resolved (system-impacting gate).
- [ ] No strategy that reaches into the runtime / writes SpellSystemState (mediator = DevOps only).
- [ ] No new hot-path lock; coordination comes from the transaction envelope.
- [ ] No agent claim that pytest/coverage ran.

## State Transition Event
- from_state: (none)
- to_state: draft
- transition_reason: DevOps plane read end-to-end with the SpellSystemState focus; the lineage-scope +
  SPELL_STATE remediation design is grounded in source; open decisions surfaced for the user before the
  patch gate.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none (reference: artifacts/2026-06-05_devops_transaction_control_plane_philosophy.md,
    artifacts/2026-06-13_devops_mediator_system_map.md)
- DISPOSITION: n/a
- CLEANUP_TRIGGER: n/a

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Epic notes: program direction (lineage-scope model, what "serialize" means, envelope-only boundary),
  cross-story tradeoffs, and the cross-agent coordination on the validation-system surface.
- Defer tactical fixture/claim detail to the story notes.

## Notes
- DATETIME: 2026-07-12T00:25:00Z
  TYPE: FACT
  CLAIM: FIRST-MOVE SOURCE RE-VERIFICATION (melder_0, inherited lane;
    the plane evolved since June so the gap was re-derived, not
    trusted). CONFIRMED STILL TRUE: (a) meld.py contains ZERO mediator
    entries - _ensure_lineage_resolvable (:550, the lazy remediation
    writer) runs under spell._lock only, per the deliberate
    readers-never-enter law; (b) no lineage/spell-state scope exists in
    the embargo vocabulary. CHANGED SINCE JUNE: the notch/add/remove
    strategies LANDED and seal spellbook+conduit+binding_key ALL
    EXCLUSIVE (notch_transaction_strategy.py:137-167), so the
    structural side of the June picture is stronger than the draft
    assumed. NOT YET PROVEN: whether a genuinely CORRUPTING
    interleaving exists - the candidate window is a remediation
    verdict computed from pre-notch lineage state landing on the
    RiskManager/meld gate AFTER the notch commits its dirty-marking;
    if commit-side dirty-marking always forces a post-notch
    revalidation before any meld trusts the verdict, the race is
    benign by design. Per the root-cause law, NO lineage scope gets
    recommended until that window is traced (guard-sprawl applies to
    mediator scopes too). D1-D5 recommendations are GATED on that
    trace.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:550 (+ zero transaction hits file-wide)
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py:137-167
  IMPACT: the epic's premise is half-confirmed, half-open; the next
    discovery step is precise and small.
  NEXT: trace _apply_notch's commit-side dirty-marking
    (mark_contract_dependents_dirty / lineage dirty set) against
    Meld._ensure_lineage_resolvable's read window; verdict decides
    between "benign by design - close the epic" and "real window -
    draft D1-D5 w/ a lineage-scope recommendation".
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T00:45:00Z
  TYPE: FACT
  CLAIM: EMPIRICAL PROBE AUTHORED (owner: "make some tests for that and
    go find out if that happens") - NEW integration file
    test_lineage_remediation_notch_race.py (239 lines, ast OK, 2
    tests). The race test holds member A's remediation window OPEN via
    a delegating barrier at the EXACT seam
    (Meld._get_spell_compiler_system -> run_structural_phases, meld.py
    :579; CLASS-level patch - Meld types are slotted; the gate is
    forced twice to satisfy the double-checked entry :576-578), runs a
    concurrent notch to member B from a second thread, then asserts
    the POST-SETTLE truths that any legal interleaving must preserve:
    index selects B, fresh meld yields B (a stale-A here = the
    poisoning verdict), no deadlocks (every join timeout-guarded and
    FAILS LOUDLY as its own finding), notch completion required. The
    in-window meld's own outcome (A-instance or refusal) is accepted
    either way - pre-notch melds may complete pre-notch semantics; the
    probe prints the observed interleaving shape for the owner's read.
    Control test proves the harness invariant sequentially. Barrier
    self-opens at 15s so the suite can never hang.
  EVIDENCE:
  - tests/integration/melder/aether/conduit/test_lineage_remediation_notch_race.py:1-243
  - src/melder/aether/conduit/meld/meld.py:576-582
  IMPACT: the owner's run now ANSWERS the epic's question empirically:
    green = benign-by-design (close the epic, no new mediator
    machinery - matching the owner's "we rebuild through normal routes"
    instinct); a poisoning/deadlock failure = the real window, with the
    failure message naming which.
  NEXT: owner runs the probe (pytest -s for the interleaving-shape
    print); verdict routes the epic to closure or to D1-D5 drafting.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T01:00:00Z
  TYPE: FACT
  CLAIM: PROBE TRIAGE #1 (owner run: "window never opened - harness
    fault, not a runtime verdict"). ROOT CAUSE source-verified AND
    itself a discovery for this epic: the remediation path is DOUBLY
    gated - conduit_meld.py:306 calls _ensure_lineage_resolvable ONLY
    when the book's _spellbook_validation_required flag is up (plain
    slotted bool, real setter :4938; RiskManager raises it when a
    not-yet-validated member appears per the :3183 comment). A clean
    conjured book melds down the fast lane and NEVER consults the gate
    my probe forced - which NARROWS the epic's whole question: the
    remediation race can only exist while the validation-required flag
    is up, i.e. exactly when lineages are already in flux. FIXES: (a)
    the probe now raises the flag through the real setter pre-meld
    (faithful gated-lineage posture, not a synthetic state); (b) the
    window-timeout path now self-diagnoses (gate_calls counter +
    meld thread state + outcome repr) instead of a mute fail.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:305-309
  - src/melder/aether/spellbook/spellbook.py:289,3183,4938-4944
  - tests/integration/melder/aether/conduit/test_lineage_remediation_notch_race.py
  IMPACT: probe now recreates the true gated posture; the next run is
    the real verdict.
  NEXT: owner re-runs the probe (pytest -s).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T01:20:00Z
  TYPE: HYPOTHESIS
  CLAIM: PROBE RUN #2 LIKELY CAUGHT THE RACE. The interleaving executed
    fully (window opened, notch completed, index selected B, zero
    deadlocks) and the POST-SETTLE meld of B REFUSED:
    SpellbookValidationError from _ensure_resolution_resolvable
    (meld.py:822) with resolution_validity in
    {invalid|disabled|cleaned} and EMPTY diagnostics ("none recorded" -
    a poisoned validity VALUE, not a real validation failure). The
    sequential lifecycle tests prove meld-after-notch works, so the
    refusal is window-specific. SUSPECTED MECHANISM: the in-window
    remediation of A resumed post-notch and ran its
    structural/resolution passes on the now-PARKED A - meld.py:587
    set_validity(invalid) on the SHARED lineage state and/or the
    per-conduit resolution rerun writing invalid onto the lineage
    record B now heads (the exact writer needs one trace). NOT YET
    FACT: my monkeypatches were still live during the post-settle meld
    - probe hardened: monkeypatch.undo() now precedes the verdict
    phase (fully unpatched runtime) and the poisoning failure message
    carries the whole interleaving story. A refusal on the hardened
    rerun = FACT; then D1-D5 get drafted against the traced writer.
  EVIDENCE:
  - owner run: SpellbookValidationError, _RaceBeta, "(none recorded)" diagnostics, meld.py:822
  - src/melder/aether/conduit/meld/meld.py:585-592 (the stale-write candidate)
  IMPACT: the epic's question is one hardened rerun away from a
    factual verdict - and it currently points to REAL.
  NEXT: owner reruns the probe; on confirmed refusal -> trace the
    exact stale writer (structural :587 vs resolution rerun) and draft
    D1-D5 around serializing THAT write, nothing broader.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T01:45:00Z
  TYPE: FACT
  CLAIM: THE LINEAGE RACE IS REAL - confirmed on the FULLY UNPATCHED
    runtime (hardened probe, owner run #3). Full interleaving story
    from the verdict message: the notch completed DURING the open
    window; the resumed remediation of now-parked A refused
    (SpellbookValidationError _RaceAlpha, EMPTY diagnostics) and its
    stale write outlived the notch; post-settle meld of notched-in B
    refuses permanently (SpellbookValidationError _RaceBeta, empty
    diagnostics, via _ensure_resolution_resolvable's terminal
    invalid|disabled|cleaned arm at meld.py:822 - invalid never
    re-runs). Sequential control + the existing notch lifecycle suite
    prove the refusal is window-specific. The probe now carries
    strict xfail documenting the bug (flips loudly when fixed).
  EVIDENCE:
  - owner run #3 verdict message (both refusals + interleaving shape)
  - tests/integration/melder/aether/conduit/test_lineage_remediation_notch_race.py
  IMPACT: mediator_builder_0's June hypothesis is now empirical fact
    with a reproducer.
  NEXT: owner rules on the D-draft below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-12T01:50:00Z
  TYPE: DECISION_REQUEST
  CLAIM: D1-D5 CONSOLIDATED into ONE recommendation - EPOCH-GUARDED
    VALIDITY WRITES, no new mediator machinery. Mechanism: the lineage
    state (SpellSystemState + ConduitResolutionState) gains a
    monotonically increasing MEMBERSHIP EPOCH, bumped by the
    notch/add_to_index/remove_from_index/transfer commit paths INSIDE
    their already-held exclusive seals; remediation captures the epoch
    before running phases; the validity SETTERS discard a write whose
    captured epoch is stale (downgrade to UNKNOWN so the next meld
    re-runs - never a terminal verdict from a stale world-view). WHY
    THIS SHAPE: (a) preserves the readers-never-enter law (no
    remediation claims, no lineage scope, meld paths untouched by the
    mediator - the owner's "we rebuild through normal routes" instinct
    holds); (b) zero admission-plane cost; (c) the runtime ALREADY
    uses this pattern - meld entries carry an invalidation epoch
    captured before execution (conduit_meld.py:313 comment); (d) it
    kills the race at the only place it exists: the stale WRITE, not
    the concurrency around it. REJECTED alternatives recorded: lineage
    scope claim for remediation (readers enter the plane - law break +
    hot-path admission cost); SPELL_STATE envelope transactions (the
    original June D2 - machinery for what one guarded setter fixes);
    notch-clears-validity (write-order still loses to a late stale
    writer). The original D1-D5 all collapse: D1 scope-key form MOOT
    (no new scope), D2 seal granularity MOOT, D3 routed-write-paths =
    exactly the four membership commit paths above, D4 CONJURE stays
    out, D5 envelope-only preserved trivially (mediator untouched).
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:311-315 (epoch precedent)
  - src/melder/aether/conduit/meld/meld.py:585-592 + 822 (the two stale-write arms)
  IMPACT: one owner YES starts a small, patch-gated implementation
    (epoch slot + four bump sites + two guarded setters + the xfail
    probe flipping green as the acceptance test).
  NEXT: owner ruling. On YES: patch dir, implement, the probe IS the
    validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-12T02:05:00Z
  TYPE: DECISION
  CLAIM: OWNER RULED - MEDIATE BOTH THREADS ("the mediator can manage
    this properly... isn't that the point?"). The epoch-guard
    recommendation is OVERRULED and the owner's correction is
    accepted on the merits: remediation is a WRITER wearing a reader's
    coat - it writes lineage/resolution validity - and in this system
    writers ride admission. The readers-never-enter law survives
    intact for actual READS (warm melds, validity lookups); only the
    lazy RERUN-AND-WRITE branch enters the plane. The hot-path
    objection dissolves: admission wraps only the gated rerun branch
    (engaged solely while _spellbook_validation_required is up AND
    validity is unknown/gated) - the warm lane never pays. DESIGN
    (answers the original D1-D5 under the ruling):
    - D1 scope-key form: lineage scope keyed by the spell_index id -
      new make_scope_key_lineage(index_id) on the transaction manager.
    - D2 granularity: remediation claims lineage-X EXCLUSIVE (it
      writes a verdict); the notch/add_to_index/remove_from_index/
      transfer strategies ADD lineage-X for every affected index to
      their existing seals. Mutual exclusion kills the straddle: no
      window can span a notch, no notch can land mid-window.
    - D3 routed write-paths: exactly TWO - the structural rerun branch
      (meld.py:577-592) and the conduit resolution rerun
      (_ensure_resolution_resolvable's rerun lane). New "remediation"
      transaction family + strategy (static-execute, mirrors the
      family pattern). Plain reads stay out of the plane.
    - D4: CONJURE stays OUT (pre-world; already admitted via its own
      family).
    - D5: envelope-only preserved - the mediator carries scopes,
      never payloads.
    - ORDERING LAW: admission BEFORE spell._lock (mediator first, then
      internals - the same one-way order the notch family already
      obeys; no AB-BA). Bonus: remediation transactions inherit the
      LoadGate wait_for_passage ingress like every new root - world
      loads now park remediation too, strengthening load authority.
    - The strict-xfail race probe IS the acceptance test (flips green
      when the mediation lands).
  EVIDENCE:
  - owner ruling (this session) + the confirmed-race FACT note above
  IMPACT: the epic finally executes its original purpose with a proven
    reproducer as its exit gate.
  NEXT: patch dir (remediation_lineage_mediation) BEFORE code, then:
    make_scope_key_lineage -> RemediationTransactionStrategy +
    registration -> wrap the two rerun sites -> lineage claims added
    to the four membership strategies -> probe xfail removal rides the
    green flip. Test additions: remediation-vs-notch serialization
    probe variant (window must now PARK the notch or vice versa,
    deadlock-free) + scope-claim unit rows per amended strategy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-12T02:50:00Z
  TYPE: FACT
  CLAIM: THE FIX IS IMPLEMENTED (patch remediation_lineage_mediation_
    2026_07_12 authored first; owner: "implement the fix in the
    mediator strategy then fix the test as a regression"). LANDED:
    (1) make_scope_key_lineage ("lineage:<index_id>",
    transaction_manager.py beside the binding maker); (2)
    ChangeTransactionType.REMEDIATION enum member; (3) NEW
    RemediationTransactionStrategy - claims EXACTLY the lineage scope
    EXCLUSIVE (no book/conduit claims, no staged binding keys,
    envelope-only; spell_index_id required in metadata w/ teach-grade
    ValueError); (4) registered in TransactionStrategyBuilder; (5)
    NotchTransactionStrategy seal gains the lineage claim (metadata
    already carried spell_index_id from conduit.notch_spell:3975);
    (6) meld.py wiring - _admit_remediation_transaction helper
    (spellbook identity, frame CCM mediator via the verified
    dev_ops_manager chain, admission BEFORE spell._lock) wrapping BOTH
    write sites: the structural rerun branch and the extracted
    _locked_resolution_rerun (pulled out of _ensure_resolution_
    resolvable so its early-return shape gets clean transaction ends);
    ChangeTransactionType import added. (7) The probe's strict xfail
    REMOVED - reframed as the permanent REGRESSION MONITOR with
    post-fix expectations documented (notch parks behind the window or
    completes before it; post-settle coherent; ends must flip it
    green). File-tool verified: remediation ends at meld.py :609/:613
    (structural) + :862/:866 (resolution), helpers :871/:929, enum use
    :977. RESIDUE for the next pass: add_to_index/remove_from_index/
    transfer strategies still need their lineage claims (notch was the
    proven attacker; the other three are the same one-line pattern);
    scope-claim unit rows; KNOWN RISK flagged: the notch's scope-wait
    during the probe's ~5s window rides
    max_transaction_wait_time_in_seconds - if the configured bound is
    shorter, the probe will surface a scope-timeout instead of a park
    (a tuning finding, not a regression). AST: Not run (standing
    replica rot; all seams file-tool verified).
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:576-613,824-989
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/remediation_transaction_strategy.py
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py (lineage claim)
  - system_docs/patches/active/remediation_lineage_mediation_2026_07_12/architecture_patch.md
  IMPACT: the probe-proven race is closed by mediation in both
    directions; the regression test monitors it forever.
  NEXT: owner runs the tree (the regression test + the notch/index
    suites + full); then the three remaining lineage claims + unit
    rows; then closure + promotion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-12T13:10:00Z
  TYPE: FACT
  CLAIM: OWNER ADJUDICATION + REDIRECT recorded: the remediation
    transaction fix was REVERTED by the owner (commit 7abb39e62; revert
    verified faithful - zero mediation residue; probe re-run confirms
    the baseline race is back with the same poisoning verdict). New
    owner direction: NO new strategy/transaction family - make the
    NOTCH side guarantee that the transaction-holding thread has
    exclusive rights over everything; understand the plane first, talk
    before changing. DEEP-READ COMPLETE (mediator + strategies + notch
    chain + writers). Plane mechanics: _start_strategy_transaction ->
    build_start_plan -> begin_transaction (identity gate -> LoadGate
    wait_for_passage for new roots -> build_request ->
    _admit_with_scope_wait bounded retry -> session) -> strategy
    on_start AFTER admission with claims HELD (abort-on-failure built
    in); end_transaction -> _finalize_root_session -> commit pipeline
    -> apply_commit_delta (scopes still held) -> orchestrator release.
    on_start/on_end receive ONLY (registry, identity, metadata) - no
    runtime objects, envelope-only by design. RACE MECHANICS pinned to
    the line: (a) Spell.system_state resolves the SHARED per-index
    record by spell_index.id (spell.py:1188); (b) resolution validity
    reads/writes key by spell_index.selected_spell_id AT CALL TIME
    (meld.py:1023, :986, :745); (c) _apply_notch flips
    selected_spell_id + parks the outgoing member under the SPELLBOOK
    lock only - it never touches outgoing._lock (spellbook.py:
    3140-3167); (d) both remediation writers run under spell._lock
    (meld.py structural branch + resolution rerun). So a remediation
    holding spell._lock(A) mid-phases cannot be excluded by ANY claim
    set - it never requests admission - and after the notch flips, its
    verdict writes land keyed to B (terminal invalid, empty
    diagnostics: the probe's exact signature). Compiler phases 1-4
    take no locks (spell_compiler_system.py grep clean), so a
    spell-lock-first order in the notch is AB-BA-safe.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:1183-1188
  - src/melder/aether/conduit/meld/meld.py:1006-1029
  - src/melder/aether/spellbook/spellbook.py:3140-3235
  - src/melder/aether/conduit/conduit.py:3970-3995
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:1133-1198,932-1002
  IMPACT: the exclusivity the owner wants is deliverable, but not by
    widening the strategy's claim set (claims only exclude admission
    participants); it requires the notch's held window to ALSO hold
    the one lock the remediation thread respects: the outgoing
    member's spell._lock, plus a selection precondition check under
    that lock on the remediation side to close the resolve-then-lock
    TOCTOU tail.
  NEXT: present the two-piece design to the owner for ruling BEFORE
    any edit (owner-directed talk-first).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-12T13:45:00Z
  TYPE: FACT
  CLAIM: THE OWNER'S MECHANISM EXISTS IN-TREE - the unelect-leader
    strategy IS the "transaction thread gets exclusive runtime rights"
    pattern: caller threads the DevOps ConduitLineageGateOps facade
    into transaction METADATA (conduit_cluster.py:868-877); the
    strategy's on_start (runs AFTER admission with claims held,
    abort-on-failure) drains every affected root lineage's
    CreationGates - and since EVERY dynamic meld holds a gate ticket
    across its whole executor (conduit.py:3592-3603, remediation
    included), the drain waits out any in-flight meld and parks/refuses
    new ones; on_end reopens on every exit path (fail-closed law,
    unelect_conduit_cluster_leader_transaction_strategy.py:95-130).
    The notch strategy simply never received this freeze (its
    on_start/on_end are no-ops, notch_transaction_strategy.py:169-177).
    TWO LATENT DEFECTS found in the precedent lane while verifying:
    (D-A) strategy on_end NEVER FIRES on the normal success path -
    only end_transaction_for_identity (:654) and the start-failure
    path (:1192) dispatch it, and callers (cluster :885, notch :3993)
    use plain end_transaction, which skips it -> the unelect freeze
    leaks closed gates on success; (D-B) the freeze verb is TERMINAL -
    close_and_wait_until_conduit_lineage_free -> per-gate
    close_and_wait_until_free sets _closed=True
    (creation_gate.py:371-374), melds then RAISE "CreationGate is
    closed" (conduit.py:3582-3583) instead of parking, and gate.open()
    never clears _closed (creation_gate.py:146-148 contract) so the
    documented reopen cannot resurrect the gate. Park-mode primitives
    exist (close() = park at wait(), :150-176; open() releases) but no
    park+drain quiesce verb exists at gate/controller/facade level.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/unelect_conduit_cluster_leader_transaction_strategy.py:22-130
  - src/melder/aether/conduit/conduit_cluster.py:855-888
  - src/melder/aether/conduit/conduit.py:3575-3603
  - src/melder/utilities/synchronization/creation_gate.py:123-207,328-380
  - src/melder/utilities/synchronization/creation_gate_controller.py:595-637
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:628-658,675-706,1176-1197
  IMPACT: the notch fix is the owner's shape exactly - give the notch
    strategy the unelect freeze in PARK mode - plus two small
    mechanism repairs the freeze pattern needs to actually hold
    (on_end on every end path; a non-terminal quiesce verb). The
    remediation thread needs zero special handling: it is a ticketed
    meld the drain waits out.
  NEXT: owner GO/no-go on the 4-piece design (quiesce verb chain;
    notch strategy freeze; notch caller metadata; mediator on_end
    dispatch relocation to _finalize_root_session) + ruling on
    switching unelect to park-mode quiesce in the same pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-12T14:30:00Z
  TYPE: FACT
  CLAIM: TWO GATE FAMILIES exist, not one (owner-directed deeper
    investigation; "use the ConduitCreationGate"). (1) CONDUIT gate:
    one per conduit, ticketed at Conduit.meld ENTRY (:3579-3603) -
    ticket spans the ENTIRE meld including the gated validator; park
    point is BEFORE spell resolution. (2) SPELL-INDEX gate: shared per
    SpellIndex.id, minted by CreationContextFactory
    (_resolve_or_create_spell_index_gate, creation_context_factory.py
    :146-195), injected into every dynamic CreationContext; consumers
    already implement park-then-proceed (closed->raise,
    disabled->wait(), ticket around the executor;
    creation_context.py:201-270). Controller carries full index-gate
    verbs (create/register/unregister/get + enable/disable-all,
    creation_gate_controller.py:684-896). CRITICAL GAP: the index
    gate's ticket covers EXECUTES ONLY - the gated validator
    (_ensure_lineage_resolvable) runs earlier and holds NO index
    ticket, so an index-gate drain today would NOT wait out the
    poisoning writer. PARK-POINT SUBTLETY that decides the design: a
    validator parked mid-meld (spell object already resolved = A)
    that resumes post-flip re-poisons (same stale-keyed write), so an
    index-gate freeze is only sound if the validator (a) parks/tickets
    on the index gate AND (b) re-checks the premise
    (spell.spell_index.selected_spell_id == spell.spell_id) AFTER
    passing the gate, under its held ticket - the ticket then makes
    the premise durable (a later notch's drain must wait for it).
    Conduit-gate freeze needs no premise check (parks before
    resolution) but pauses the whole conduit.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:130-214
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:182-270
  - src/melder/utilities/synchronization/creation_gate_controller.py:684-896
  - src/melder/aether/conduit/conduit.py:3575-3603
  IMPACT: index-grain freeze (owner instinct) is achievable and
    surgical: only melds touching the notched index pause; the notch
    metadata ALREADY carries spell_index_id (conduit.py:3975). Requires
    the cold-branch validator to join the index gate's protocol
    (additive; warm melds unaffected) + the premise re-check + the
    mediator on_end dispatch fix + park-mode drain verb.
  NEXT: owner picks index-grain (B, recommended) vs conduit-grain (A);
    then patch dir + implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-12T15:30:00Z
  TYPE: FACT
  CLAIM: NOTCH CONDUIT-GATE FREEZE IMPLEMENTED (owner GO: "use the
    conduit gate... block the whole conduit lineage... devops must use
    devops tools"; patch notch_conduit_gate_freeze_2026_07_12 authored
    FIRST - architecture + 2 component patches). LANDED: (1)
    CreationGate.close_and_drain (:382) - PARK-mode freeze (close +
    ticket drain; _closed untouched; open() fully resumes; timeout
    teach-grade); (2) CreationGateController
    .close_and_drain_conduit_lineage (:639); (3) DevOps facade
    ConduitLineageGateOps.quiesce_conduit_lineage (:156); (4)
    NotchTransactionStrategy - plan stashes the sealed conduit set as
    quiesce_root_conduit_ids (:114), on_start freezes+drains each via
    the metadata-carried facade (:221-226; absent facade = no-op,
    unelect precedent), on_end reopens (:239+); (5) conduit.notch_spell
    supplies the facade (:3983); (6) MEDIATOR RELIABILITY FIX -
    strategy on_end now dispatches from _finalize_root_session's
    finally via new _dispatch_strategy_on_end (:886/:888; guards mirror
    _apply_strategy_commit_delta), the two old dispatch sites removed
    (identity-end finally + start-failure explicit) - on_end now fires
    EXACTLY ONCE per root end on every exit path, which also HEALS the
    unelect success-path freeze leak (defect D-A from the 13:45Z note).
    Probe docstring truth-synced to the gate-freeze design. TESTS: 5
    notch-freeze strategy rows + 3 mediator dispatch-law rows
    (success/abort/identity-end single-fire) + 4 gate park-mode rows +
    1 controller lineage row + cleanup-guard parametrize row;
    _ExplodingBuilder fake gained the builder protocol's resolve. The
    race probe is the acceptance test. RESIDUE recorded: (a) unelect
    still uses the TERMINAL drain verb + open() cannot clear _closed
    (defect D-B) - owner question pending: switch unelect to
    quiesce or ticket separately; (b) add_to_index/remove_from_index/
    transfer freeze parity = later slice (same pattern); (c) the
    single-conduit-conjure invariant means borrower/provider peer
    conduits in the seal are roots - lineage walk covers lessers.
    AST/pytest: Not run (3.14t owner-run; replica rot standing) - all
    seams file-tool verified at the line numbers above.
  EVIDENCE:
  - src/melder/utilities/synchronization/creation_gate.py:382-449
  - src/melder/utilities/synchronization/creation_gate_controller.py:639-686
  - src/melder/aether/aetheric_frame/dev_ops/conduit_lineage_gate_ops.py:156-211
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py:47-247
  - src/melder/aether/conduit/conduit.py:3971-3987
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:842-935
  - system_docs/patches/active/notch_conduit_gate_freeze_2026_07_12/
  IMPACT: the notch transaction thread now holds exclusive RUNTIME
    rights (park + drain) on top of its plane seal; the probe-proven
    poison is impossible in both directions by ordering.
  NEXT: owner runs the race probe + notch/index/mediator/gate suites +
    full tree; green routes to closure walk + promotion + the unelect
    D-B ruling.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-12T15:50:00Z
  TYPE: FACT
  CLAIM: DEFECT D-B FIXED (owner: "go fix the next defect"): unelect's
    freeze switched from the TERMINAL close_and_wait_conduit_lineage to
    the park-mode quiesce_conduit_lineage - in-window melds now park and
    resume instead of raising "CreationGate is closed", and the member
    gates stay reopenable (open() cannot clear terminal closure by
    design; the terminal verb remains for shutdown consumers). Class +
    on_start docstrings truth-synced (lifecycle section records both the
    defect and the finalize-dispatch dependency). Tests: the two unelect
    freeze rows reworked to the park-mode contract (quiesced footprint +
    terminal-verb-never-used assertion + symmetry row); the reopen row
    unchanged. Grep-clean: no other gate_ops.close_and_wait_ callers in
    src. With D-A (finalize on_end dispatch) + D-B both fixed, ZERO
    known defects remain in this lane; the freeze pattern (notch +
    unelect) opens and closes correctly on every exit path. AST/pytest:
    Not run (owner-run 3.14t).
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/unelect_conduit_cluster_leader_transaction_strategy.py:42-135
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_index_and_leader_transaction_strategies_expansion.py (unelect rows)
  - system_docs/patches/active/notch_conduit_gate_freeze_2026_07_12/component_patch_dev_ops_transactions.md (delta appended)
  IMPACT: both freeze-bearing strategies now use the reversible verb;
    the lane is implementation-complete pending the owner run.
  NEXT: owner run (probe + suites + tree); melder_0 pivots to the
    crystallizer persistence adapter epic per owner directive
    (mutation_0's handoff: his MR twin rows are DB-storable; the
    kind->table SQLite adapter is this epic's scope).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T17:20:00Z
  TYPE: FACT
  CLAIM: OWNER-RUN TRIAGE (D-B fallout): test_transaction_strategy_
    builder_and_strategies.py carries its OWN _RecordingGateOps copy
    which I missed in the D-B pass -> AttributeError on
    quiesce_conduit_lineage. Fixed: that double gains the quiesce log
    (+docstring), its unelect row reworked to the park-mode contract
    (quiesced footprint + closed==[] terminal-verb-never-used +
    reopen), the elect row additionally asserts quiesced==[]. Sweep
    verified: the only remaining close_and_wait_conduit_lineage test
    references target the MANAGER's terminal verb directly (unchanged
    surface). AST floor OK.
  EVIDENCE:
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_strategy_builder_and_strategies.py:997-1200
  IMPACT: both test files' doubles now speak the freeze protocol; the
    unelect park-mode contract is asserted in both suites.
  NEXT: owner re-run of the builder/strategies file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-12T18:00:00Z
  TYPE: FACT
  CLAIM: DRAIN-RACE FIX LANDED (owner finding + owner-chosen shape:
    ticket-first, NO lock). The consumer protocol (check state -> later
    register) let a meld pass its checks, get preempted while a
    freeze-and-drain disabled admission and observed zero tickets, then
    register late and execute INSIDE the drained exclusive window -
    breaking the freeze guarantee the notch/unelect strategies stand
    on. NEW CreationGate.admit_ticket() (creation_gate.py:259): append
    the ticket FIRST (visible to every drain poll), then validate -
    closed pops+raises "CreationGate is closed."; disabled pops+parks+
    retries; enabled returns HOLDING the ticket. Lock-free by
    append-before-read ordering (deque ops are thread-safe primitives):
    either the drain poll counts the ticket and waits, or the
    admitter's post-append read sees the freeze and backs out. ALL FOUR
    consumers rewired to admit_ticket + try/finally unregister
    (conduit.py meld + meld_existing_spell; creation_context.py
    execute :209 + execute_no_hooks :247); parked admitters hold ZERO
    steady tickets so freezes never wait on waiters. TESTS: 3 new gate
    admission rows (open-admits-holding-ticket; terminal-refusal leaks
    nothing; parked-admitter invisible through a freeze + admits on
    open); creation-context _Gate stub gained the admit contract
    (pre-existing wait/register counters still assert); two conduit
    facade rows rewritten to the admit/unregister bracket (the old
    rows encoded the racy protocol). RiftGate (command_system.py:1029)
    has its own admission shape - flagged for separate audit, not
    touched (scope control). Patch component amended. AST: Not run
    (severe replica rot this pass - phantom unterminated strings +
    null bytes on stale copies; every flagged line verified clean on
    real disk via file-tool). pytest: Not run (owner-run 3.14t).
  EVIDENCE:
  - src/melder/utilities/synchronization/creation_gate.py:259-350
  - src/melder/aether/conduit/conduit.py:3579-3600,3665-3679
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:201-254
  - tests/unit/melder/utilities/synchronization/test_creation_gate.py (admission rows)
  - tests/unit/melder/aether/conduit/test_conduit_facade.py:925-986
  - system_docs/patches/active/notch_conduit_gate_freeze_2026_07_12/component_patch_synchronization_gates.md (amendment)
  IMPACT: the freeze/drain guarantee the whole notch-exclusivity design
    rests on is now real under 3.14t; without this, the race probe's
    fix had a hole at its foundation.
  NEXT: owner-run (gate/facade/context suites + probe + tree).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-12T20:30:00Z
  TYPE: FACT
  CLAIM: OWNER-DELEGATED RULINGS EXECUTED (owner: "You do these 3").
    (1) FREEZE PARITY LANDED: add_to_index / remove_from_index /
    transfer_ownership strategies now carry the notch freeze - plans
    stash quiesce_root_conduit_ids (= their sealed conduit sets;
    transfer uses the full participant set), on_start quiesces PARK-mode
    via the metadata facade (absent = no-op), on_end reopens (fires via
    the finalize dispatch); all three conduit callers supply
    conduit_lineage_gate_ops (add :4032+, remove :4104+, transfer
    begin_transaction branch :2530+ via setdefault). The epic's original
    Story-4/5 residue is now COMPLETE - every lineage-affecting family
    freezes. (2) RIFTGATE AUDIT: the flagged same-class TOCTOU was REAL
    - command_system._begin_command_action did admit() THEN
    register_ticket() as two steps, so a projection refresh's drain
    could observe zero tickets mid-admission. Fixed identically:
    RiftGate.admit_ticket() (ticket-first loop honoring entry_mode
    wait/raise; terminal pops+raises; parked callers hold no steady
    ticket) + the single consumer rewired. Grep-clean: zero .admit()
    callers and zero direct rift-gate register_ticket callers remain.
    AST: Not run (replica rot; edited regions file-tool verified).
    pytest: Not run.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/add_to_index_transaction_strategy.py
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/remove_from_index_transaction_strategy.py
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transfer_ownership_transaction_strategy.py
  - src/melder/aether/conduit/conduit.py:2530-2549,4032-4050,4104-4122
  - src/melder/nexus/rift/rift_gate/rift_gate.py (admit_ticket)
  - src/melder/nexus/rift/command_system/command_system.py:1024-1033
  IMPACT: every index/ownership mutation family now holds exclusive
    runtime rights during its window, and both gate families
    (CreationGate + RiftGate) share the race-free admission protocol.
  NEXT: owner run covers these with the same suites; unit rows for the
    three new freezes = closure-walk residue (the notch rows prove the
    pattern; parity rows are copy-shape).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-20T22:46:32Z
  TYPE: FACT
  CLAIM: DevOps plane read end-to-end with the SpellSystemState focus. Confirmed: (1) NO lineage scope
    in the embargo vocabulary; (2) the validation/remediation writer holds no claim and is best-effort;
    (3) validity fans out through RiskManager onto the spellbook meld gate; (4) the index/transfer
    seals cover spellbook+conduit+binding but never the lineage record. The race is lineage remediation
    vs a structural op on the same lineage.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_manager.py:262-415
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py:214-262
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:317-372,525-542
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py:110-141
  IMPACT: Defines a small, evidence-backed strategy set (lineage scope + SPELL_STATE envelope tx +
    structural lineage claims) that closes the gap without touching meld or the existing seals.
  NEXT: Get D1-D5 from the user; then author the patch artifacts (M0 gate); then M1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
New mediator strategies to bring SpellSystemState lineage remediation under the admission plane.
Today validity/remediation writes bypass the mediator (no claim, no lineage scope) and can race a
structural op on the same lineage; the verdict feeds the spellbook meld gate, so the interleave is a
real free-threaded correctness gap. Plan: add a `spell_lineage` scope, a SPELL_STATE envelope
transaction (DevOps-only; the caller writes state in the window), route the live remediation /
lazy-revalidation writes through it, and have notch/add/remove/transfer also claim the lineage scope so
the two mutually serialize at lineage granularity. MUTATION and CONJURE are explicitly deferred. This is
system-impacting: DRAFT pending user decisions D1-D5 and the patch-framework gate before any edit.
