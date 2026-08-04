Completed: 2026-06-12T11:58:04Z
Summary: Closed by user cleanup request after the bind-time disposal-signature
slice was recorded in the task notes and handoff state.

# Task: Enforce Bind-Time Disposal Signature

## Metadata
- Task ID: TASK-2026-06-10-enforce-bind-time-disposal-signature
- Story: none
- Epic: EPIC-2026-06-07-optimize-meld-hotpath
- Status: done
- Owner: codex
- Agent Name: hope_0
- Priority: p0
- Created: 2026-06-10T23:26:42Z
- Updated: 2026-06-12T11:58:04Z

## Objective
Move disposal-method resolution onto the bind boundary, block disposal-method
configuration changes after local spells are already bound, and widen the
bind-time spell fingerprint so cached/runtime identity includes compiler-
shaping bind inputs without mutating spell ids later.

## Ticket Contract
- ENTRY_GATE: the user explicitly redirected the active lane from unsafe-meld
  discussion into bind-time disposal-signature enforcement.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py`
  - `src/melder/aether/spellbook/bind/bind.py`
  - `src/melder/aether/spellbook/spell.py`
  - `src/melder/aether/spellbook/spellbook.py`
  - `codex/context_compass/tickets/tasks/2026-06-10_enforce_bind_time_disposal_signature_task.md`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-06-07_optimize_meld_hotpath_epic.md`
  - `tickets/tasks/2026-06-09_return_to_meld_hotpath_frontdoor_task.md`
- EXIT_GATE:
  - bind-time disposal configuration changes fail once any local spell is
    already bound,
  - bind resolves disposal metadata before `Spell` creation,
  - spell fingerprint includes `existence`, binding signature, and resolved
    disposal metadata,
  - no post-bind spell-id mutation is introduced.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the bind-time signature needs
  to include additional runtime policy fields beyond the current narrowed set.

## Scope Boundaries
- In scope:
  - disposal-method mutation guard on rich spellbook configuration
  - bind-time resolution of disposal metadata from current configuration
  - bind-time spell fingerprint widening
  - spell-owned storage of resolved disposal metadata
- Out of scope:
  - `SpellbookCreationSystem` cleanup/removal/refactor
  - cache-file format redesign
  - permissions-driven fingerprint widening

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user narrowed the implementation slice to config/bind
  enforcement and bind-time spell identity.

## Steps / Checklist
- [ ] Route the board to this task.
- [ ] Add a config-side guard for disposal-method mutation after any local bind.
- [ ] Resolve disposal metadata during bind.
- [ ] Widen bind-time spell fingerprint with the agreed inputs.
- [ ] Keep the current post-bind spell id immutable.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- bind-time disposal guard
- bind-time resolved disposal metadata on new spells
- widened bind fingerprint aligned to compiler-shaping inputs

## Files / Paths Impacted
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py`
- `src/melder/aether/spellbook/bind/bind.py`
- `src/melder/aether/spellbook/spell.py`
- `src/melder/aether/spellbook/spellbook.py`
- `codex/context_compass/tickets/tasks/2026-06-10_enforce_bind_time_disposal_signature_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `.venv_new\\Scripts\\python.exe -m pytest -q -s tests/unit`

## Risks / Rollback Notes
- Risk: bind-time fingerprint widening can change spell identity for existing
  callers that rely on the old structural-only hash.
- Risk: config guard may reject flows that previously mutated disposal names
  after local binds.
- Rollback: restore the old fingerprint inputs and remove the config guard,
  leaving disposal metadata conjure-derived only.

## Applicable Anti-Patterns
- [ ] No post-bind spell-id mutation.
- [ ] No permissions expansion into compiler/cache identity in this slice.
- [ ] No `SpellbookCreationSystem` scope drift in this task.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - bind-time spell identity
  - disposal-method configuration
  - compiler-shaping spell metadata
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-10T23:26:42Z
  TYPE: PLAN
  CLAIM: The user narrowed the next implementation slice to config/bind only.
    The target is not a late cache-variant system and not SpellbookCreationSystem
    cleanup. The target is: disposal-method config cannot change after local
    binds, bind resolves disposal metadata immediately, and bind-time spell
    identity widens with the agreed compiler-shaping inputs while leaving
    permissions out.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/bind/bind.py:271-333
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:162-193
  - src/melder/aether/spellbook/spellbook_creation_system.py:1010-1046
  IMPACT: The implementation boundary is smaller and cleaner: config mutation
    guard plus bind-time disposal/signature work only.
  NEXT: switch the board row to this task, then patch config ownership and bind-time
    disposal/signature logic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-10T23:26:42Z
  TYPE: FACT
  CLAIM: The config guard must live on the rich configuration object itself,
    not only on Spellbook convenience methods. `Spellbook.get_configuration()`
    returns the raw `SpellbookConfiguration`, so callers can mutate disposal
    settings directly through `set_property(...)`, `with_disposal_method_names(...)`,
    or `add_disposal_methods(...)`. Also, bind currently computes the SHA from
    `binding_profile` before `spellframe`, `binding_name`, `existence`, or any
    resolved disposal metadata are carried into the `Spell`.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3806-3814
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:162-193
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:744-796
  - src/melder/aether/spellbook/bind/bind.py:271-333
  - src/melder/aether/spellbook/spellbook_creation_system.py:1010-1046
  IMPACT: A guard only in `configure_aether_frame(...)` would be bypassable,
    and a bind-time compiler/cached identity fix must patch the bind fingerprint
    seam directly.
  NEXT: patch `SpellbookConfiguration` ownership + disposal guard, then widen
    `Bind` fingerprinting and spell construction using bind-time resolved
    disposal metadata.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-10T23:26:42Z
  TYPE: MEASURE
  CLAIM: The first focused validation pass exposed two compatibility seams in
    the narrowed implementation. First, bind unit stubs do not expose a real
    configuration API, so bind-time disposal resolution needs an empty-tuple
    fallback for configless/test-only spellbooks. Second, spell-owned disposal
    metadata can stay internally frozen while the public accessor returns a
    detached list view so existing tests and callers that compare against lists
    keep working. After patching those two seams, the focused subset over
    configuration, bind, spellbook creation-system resolution fastpath, and the
    spellbook disposal component ring passed `350` tests.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:271-333
  - src/melder/aether/spellbook/bind/bind.py:500-512
  - src/melder/aether/spellbook/spell.py:344-345
  - src/melder/aether/spellbook/spell.py:504-559
  IMPACT: The core scope patch is viable without widening into
    SpellbookCreationSystem cleanup. Remaining work is optional hardening via
    direct regression coverage for the new config guard and widened fingerprint.
  NEXT: add direct regression tests for the disposal-method config guard and
    widened bind fingerprint inputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-10T23:41:21Z
  TYPE: MEASURE
  CLAIM: The narrowed bind-time disposal/signature slice is now implemented.
    `SpellbookConfiguration` keeps a temporary owner Spellbook reference while
    mutable and blocks `disposal_method_names` changes once local binds exist.
    Bind now resolves disposal metadata at bind time, widens the SHA payload to
    include lookup signature plus `existence` and resolved disposal metadata,
    and passes that resolved disposal tuple into `Spell` immediately. `Spell`
    now stores disposal metadata internally as an immutable tuple while
    returning a detached list view for compatibility with existing callers and
    tests. This slice intentionally left `SpellbookCreationSystem` in place;
    its later pass now writes the same resolved data rather than being the
    primary source of truth.
  EVIDENCE:
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:119-119
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:231-236
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:383-414
  - src/melder/aether/spellbook/bind/bind.py:273-282
  - src/melder/aether/spellbook/bind/bind.py:416-489
  - src/melder/aether/spellbook/bind/bind.py:494-512
  - src/melder/aether/spellbook/spell.py:346-347
  - src/melder/aether/spellbook/spell.py:512-569
  IMPACT: Bind-time spell identity is now closer to compiler/cached-item truth
    without post-bind spell-id mutation, and disposal-method config drift after
    local binds is blocked.
  NEXT: review whether the remaining late `SpellbookCreationSystem`
    disposal-metadata pass should be removed or reduced to an assertion-only
    drift check in a follow-up slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-10T23:41:21Z
  TYPE: FACT
  CLAIM: The landed slice still contains a few low-value local aliases in the
    new code paths. They do not carry their weight and violate the profile rule
    against defensive/short-lived aliases that are not reused enough to justify
    the indirection.
  EVIDENCE:
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:231-236
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:407-412
  - src/melder/aether/spellbook/bind/bind.py:273-282
  - src/melder/aether/spellbook/bind/bind.py:474-489
  - src/melder/aether/spellbook/bind/bind.py:517-522
  IMPACT: The patch needs one cleanup pass before we treat it as finished.
  NEXT: remove the new one-use/two-use aliases from the touched runtime files,
    then rerun the focused config/bind validation subset.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-11T00:20:49Z
  TYPE: DECISION
  CLAIM: The cleanup scope is now narrower than the first implementation pass.
    The user explicitly redirected the repair to runtime-facing files only:
    fix the new `Bind` / `Spell` / `Spellbook` changes, do not touch
    `SpellbookConfiguration`, and do not touch `SpellbookCreationSystem` in
    this pass. The direct correction target is to remove the overbuilt bind-time
    key/metadata logic that recomputes lookup semantics or adds garbage helper
    layers while preserving only the agreed bind-time identity inputs.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/bind/bind.py:269-347
  - src/melder/aether/spellbook/spell.py:343-569
  - src/melder/aether/spellbook/spellbook.py:2985-2989
  IMPACT: This pass is a repair pass on the new runtime code only, not a full
    disposal-system redesign.
  NEXT: strip the extra bind lookup-key computation and spell disposal freezing
    layer from the touched runtime files, then rerun the focused bind subset.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-11T10:41:29Z
  TYPE: FACT
  CLAIM: The live runtime still has two disposal-metadata paths. `Spellbook.bind`
    latches configured disposal names and passes them into `Bind`, `Bind`
    hashes and stamps the resolved disposal set onto `Spell`, and `Spell`
    stores that frozen set immediately. But `SpellbookCreationSystem` still
    runs a second conjure-time pass that re-reads configuration, re-matches
    class methods, and overwrites `spell.disposal_method_names` /
    `spell.has_disposal_methods` after bind.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:274-355
  - src/melder/aether/spellbook/spell.py:352-357
  - src/melder/aether/spellbook/spellbook.py:2974-2998
  - src/melder/aether/spellbook/spellbook.py:4003-4016
  - src/melder/aether/spellbook/spellbook_creation_system.py:263-264
  - src/melder/aether/spellbook/spellbook_creation_system.py:1025-1046
  IMPACT: The code is still wider than the user-approved bind-owned metadata
    boundary, and the late conjure-time rewrite is both semantic drift risk
    and avoidable extra work on the runtime path.
  NEXT: measure the focused bind/conjure regression surface, then remove the
    late `SpellbookCreationSystem` disposal rewrite path and keep disposal
    metadata bind-owned only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-11T10:41:29Z
  TYPE: PLAN
  CLAIM: The repair pass can stay narrow and runtime-facing. The concrete patch
    is: keep disposal metadata bind-owned only, remove the conjure-time
    rewrite/check path, restore `spell_name` into the live bind fingerprint
    call, and replace the remaining bind-time `getattr(...)` spell-name
    resolution with profile-driven name selection.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:256-291
  - src/melder/aether/spellbook/bind/bind.py:403-493
  - src/melder/aether/spellbook/spellbook.py:2974-2998
  - src/melder/aether/spellbook/spellbook.py:4003-4016
  - src/melder/aether/spellbook/spellbook_creation_system.py:263-264
  - src/melder/aether/spellbook/spellbook_creation_system.py:1025-1046
  IMPACT: This removes the extra disposal churn without widening into config
    redesign and fixes the current spell-id correctness gap at the same seam.
  NEXT: patch `bind.py`, `spellbook.py`, and `spellbook_creation_system.py`,
    then rerun the focused bind/conjure/test ring and compare timings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-11T10:49:12Z
  TYPE: MEASURE
  CLAIM: The runtime boundary is now narrower and correct: bind keeps ownership
    of resolved disposal metadata, the late conjure-time disposal rewrite is
    gone, and the live bind fingerprint call now includes `spell_name` again.
    The focused validation ring passed (`288` tests). The performance result is
    modest, not dramatic: shallow JIT conjure moved from about `3.653 ms` to
    `3.617 ms`, shallow AOT conjure stayed effectively flat (`6.029 ms` ->
    `6.053 ms`), and the shallow single-resolve lane stayed within noise
    (`4.41 us` total spellspace cycle before vs `4.57 us` after in this run).
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:244-356
  - src/melder/aether/spellbook/spellbook.py:2974-2998
  - src/melder/aether/spellbook/spellbook.py:4003-4012
  - src/melder/aether/spellbook/spellbook_creation_system.py:236-253
  - tests/unit/melder/spellbook/bind/test_bind.py:1656-1693
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:769-793
  - tests/component/melder/spellbook/test_spellbook_component_spellbook.py:547-629
  - benchmarks/testing_other_di/test_melder_jit_aot_conjure.py:180-230
  - benchmarks/testing_other_di/test_shallow_all.py:1739-1778
  IMPACT: The correctness drift is repaired and the deleted late path no longer
    mutates spell metadata after bind, but this slice is not a major speed
    lever by itself. If the user still sees a meaningful slowdown, the next
    investigation should target another path, not pretend this disposal cleanup
    was the whole answer.
  NEXT: share the exact before/after numbers with the user, then decide whether
    to stop at this cleanup or inspect a different runtime regression path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
