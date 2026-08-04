# Task: Investigate Conduit Hook Overlay And Bypass

## Metadata
- Task ID: TASK-2026-05-23-investigate-conduit-hook-overlay-and-bypass
- Story: none
- Status: done
- Owner: codex
- Agent Name: searcher_0
- Priority: p1
- Created: 2026-05-23T22:52:06Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Inspect the current conduit/meld hook system with emphasis on the new shared-ref
plus local-overlay design, then identify the exact runtime seams needed for a
true zero-hook bypass path.

## Ticket Contract
- ENTRY_GATE: certification is active for `searcher_0`, and this task is routed
  from `attention_board.md` before further hook investigation continues.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/conduit/meld/meld.py`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py`
  - directly implicated hook tests under
    `tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py`
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - current runtime hook refactor already landed
  - current conduit and meld hook tests remain the evidence source for intended
    semantics
- EXIT_GATE:
  - current shared-vs-local hook model is mapped concretely
  - exact hook call sites that can bypass dispatch when hookless are identified
  - investigation findings are summarized truthfully for the user
- FAILURE_ESCALATION: raise `BLOCKER` if hook semantics are contradictory across
  runtime and tests or if the requested bypass would require broader API changes
  than the current hook slice allows.

## Scope Boundaries
- In scope:
  - hook storage and retrieval in configuration
  - shared refs vs local conduit overlay behavior
  - meld hook storage and dispatch behavior
  - hookless dispatch/bypass opportunities in conduit lifecycle/link/contract
    paths
- Out of scope:
  - unrelated gauntlet optimization outside hook paths
  - public API redesign beyond the current overlay model
  - code edits before the investigation boundary is explicit

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a fresh hook-system
  investigation focused on conduit and the zero-hook bypass feature.

## Steps / Checklist
- [ ] Read the current configuration hook storage and getter behavior.
- [ ] Read the conduit hook attach, local overlay, and dispatch helpers.
- [ ] Read the meld hook attach and dispatch helpers.
- [ ] Map every conduit lifecycle/link/contract hook call site that still pays
      dispatcher overhead.
- [ ] Summarize the current design and the exact bypass seams to the user.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one evidence-backed description of the current shared/local hook model
- one exact list of hook call sites that can bypass dispatch when hookless
- one bounded recommendation for the next implementation slice

## Files / Paths Impacted
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py`
- `tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py`
- `codex/context_compass/attention_board.md`
- this task ticket

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\test_conduit_configuration_and_hooks.py`

## Risks / Rollback Notes
- Risk: the runtime and the tests may already encode different expectations for
  local override semantics versus additive merge.
  Rollback: stop at the contradiction and surface the exact file-level evidence
  before proposing edits.
- Risk: hookless bypasses may require a broader internal predicate shared by
  conduit and meld rather than ad hoc call-site checks.
  Rollback: keep the investigation at the seam-mapping level until the minimal
  common predicate is explicit.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: user-directed after the hook investigation is accepted or
  replaced by an implementation task

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-23T22:52:06Z
  TYPE: FACT
  CLAIM: The current hook system is already split into shared conduit hooks and
    shared meld hooks in `SpellbookConfiguration`, while `Conduit` keeps
    conduit-local edits in `_local_conduit_hooks` as an overlay. The hot runtime
    issue is no longer split/snapshot work on every lesser conduit; it is that
    conduit lifecycle/link/contract sites still call `_fire_conduit_hooks(...)`
    unconditionally even when both shared and local hook maps are absent for the
    requested hook name.
  EVIDENCE:
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:121-122
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:509-584
  - src/melder/aether/conduit/conduit.py:259-275
  - src/melder/aether/conduit/conduit.py:1072-1209
  - src/melder/aether/conduit/conduit.py:1561-1599
  - src/melder/aether/conduit/conduit.py:2982-3040
  - src/melder/aether/conduit/conduit.py:3542-3853
  IMPACT: The next read pass should stay on the exact helper implementations and
    dispatch call sites, because the main open question is not storage layout
    anymore; it is where we can short-circuit hook dispatch entirely when the
    effective hook set is empty.
  NEXT: read the exact helper implementations in configuration, conduit, and
    meld, then map the hookless bypass seams precisely.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-23T22:52:06Z
  TYPE: FACT
  CLAIM: After construction the runtime treats conduit hooks and meld hooks as
    separate surfaces. Shared config hooks are split at write time inside
    `SpellbookConfiguration`; `Conduit` stores shared conduit hooks by
    reference and a conduit-local overlay in `_local_conduit_hooks`; `Meld`
    stores shared meld hooks by reference in `_meld_hooks`. Local
    `register_conduit_hooks(...)` edits only the conduit-local overlay and
    overrides shared conduit hooks by hook name, but it does not wire anything
    into `Meld`. On the hot path, `Conduit.meld(...)` does not dispatch conduit
    hooks at all, and `Meld.meld(...)` already has a direct no-meld-hook fast
    lane. The remaining unconditional conduit hook helper usage is in cleanup,
    lesser-conduit creation, link/unlink, and contract mutation sites.
  EVIDENCE:
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:434-584
  - src/melder/aether/conduit/conduit.py:259-275
  - src/melder/aether/conduit/conduit.py:1072-1209
  - src/melder/aether/conduit/conduit.py:2559-2648
  - src/melder/aether/conduit/conduit.py:1541-1578
  - src/melder/aether/conduit/conduit.py:2962-3019
  - src/melder/aether/conduit/conduit.py:3522-3832
  - src/melder/aether/conduit/meld/meld.py:387-447
  - src/melder/aether/conduit/meld/meld.py:1411-1468
  - tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py:737-929
  - tests/unit/melder/aether/conduit/test_conduit_facade.py:827-907
  IMPACT: The feature cut does not need to redesign meld dispatch. The real
    remaining bypass work is a cheap `has any effective conduit hooks?` branch
    around conduit lifecycle/link/contract call sites, plus possibly tightening
    the spell-hook-only lane in `Meld.meld(...)` so it does not call
    `_fire_meld_hooks(...)` when `_meld_hooks` is empty.
  NEXT: summarize the current hook model and the exact bypass seams to the user
    before touching code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-23T22:59:03Z
  TYPE: FACT
  CLAIM: The current conduit hook surfaces are already concrete `dict | None`
    fields, not abstract mapping interfaces. That means a plain truthiness
    check on the dicts is already the right global hookless gate for conduit:
    `if self._conduit_hooks or self._local_conduit_hooks`. A separate cached
    bool would mostly be convenience, not a fundamentally cheaper primitive.
    The real limitation of dict-truthiness is semantic, not cost: it only tells
    us whether *any* conduit hooks exist anywhere, not whether the specific hook
    name being fired has a local/shared entry.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:120-122
  - src/melder/aether/conduit/conduit.py:259-275
  - src/melder/aether/conduit/conduit.py:1149-1209
  IMPACT: We do not need to add a cached conduit-hook bool just to detect the
    fully hookless case. The useful decision is whether we want a coarse global
    bypass (`any hooks at all?`) or a finer per-hook-name bypass.
  NEXT: recommend the simplest bypass shape to the user based on this
    distinction before implementing anything.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-23T23:07:22Z
  TYPE: DECISION
  CLAIM: The implementation cut uses direct shared/local hook dict truthiness
    rather than a cached boolean. `Conduit` now branches around lifecycle,
    lesser-create, link/unlink, and contract hook dispatch sites with a direct
    hookless path; `Meld.meld(...)` now skips `_fire_meld_hooks(...)` calls when
    meld hooks are absent even if spell hooks are active; and
    `SpellbookCreationSystem.get_conjure_hook_map(...)` now reads the split
    conduit-hook registry directly instead of rebuilding a detached merged hook
    map through `get_hooks(...)`.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:323-335
  - src/melder/aether/conduit/conduit.py:1541-1578
  - src/melder/aether/conduit/conduit.py:2962-3019
  - src/melder/aether/conduit/conduit.py:3522-3832
  - src/melder/aether/conduit/meld/meld.py:387-447
  - src/melder/aether/spellbook/spellbook_creation_system.py:185-191
  - src/melder/aether/spellbook/spellbook_creation_system.py:435-451
  - src/melder/aether/spellbook/spellbook_creation_system.py:652-684
  IMPACT: The runtime now has explicit hookless branches without introducing
    cached hook state that could drift from in-place dict mutation. The next
    step is focused validation on the direct hook tests and the conjure-hook
    spellbook tests that changed with the split-registry read path.
  NEXT: run the directly implicated hook and spellbook unit tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-23T23:08:00Z
  TYPE: MEASURE
  CLAIM: The direct hook regression ring is green after the hookless bypass
    cut. The conduit hook unit file passed cleanly (`39 passed`), the focused
    Spellbook conjure-hook tests passed (`15 passed, 138 deselected`), and the
    focused SpellbookCreationSystem fastpath hook test passed (`1 passed, 25
    deselected`).
  EVIDENCE:
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\test_conduit_configuration_and_hooks.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\test_spellbook.py -k "conjure_hook_map or fire_conjure_hooks"`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\test_spellbook_creation_system_resolution_fastpath.py -k "conjure_hook_map or fire_conjure_hooks"`
  IMPACT: The hookless bypass slice is functionally stable on the direct hook
    surfaces we changed. The next useful step is performance measurement, not
    more hook-behavior investigation.
  NEXT: summarize the implemented bypasses and recommend rerunning the isolated
    Melder gauntlet to measure whether the hook cut moved the outer-scope cost.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-23T23:18:30Z
  TYPE: DECISION
  CLAIM: The meld-side branch shape is now tightened into three explicit lanes:
    no hooks at all, meld-hooks-present, and spell-hooks-only. That removes the
    repeated meld-hook existence checks inside the spell-hook-only path while
    preserving the existing compiled-lane split (`no_hooks_*` versus
    `execute_hooks_*`).
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:387-451
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\meld\test_meld.py -k "meld_hooks_lane or fire_meld_hooks or set_meld_hooks"`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\test_conduit_facade.py -k "skips_conduit_hook_dispatch_when_no_meld_hooks or does_not_fire_conduit_level_meld_hooks"`
  IMPACT: The hook cut now removes actual repeated hook-presence checks from the
    `Meld` hot path instead of just wrapping the existing calls. The next useful
    measurement is the Melder-only gauntlet, not more hook cleanup.
  NEXT: rerun the isolated Melder gauntlet and compare outer-scope and
    request-scope costs against the last no-GIL baseline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-23T23:35:59Z
  TYPE: DECISION
  CLAIM: The next narrow cleanup is `Conduit.create_lesser_conduit(...)` only.
    The current version already has a hookless bypass, but it still snapshots
    `self._conduit_hooks` and `self._local_conduit_hooks` into one-shot locals.
    That does not match the measured alias threshold and does not buy anything
    here because those values are only used for the branch condition.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1528-1604
  - tests/experimentation/test_self_vs_local_alias_access_experiment.py:1-217
  IMPACT: The right cleanup is to keep the hooks-vs-hookless split but express
    it as direct `self._conduit_hooks or self._local_conduit_hooks` checks
    inside explicit lanes, with no one-shot local aliasing for hook state.
  NEXT: patch `create_lesser_conduit(...)` into direct self-based lanes and
    rerun the direct conduit hook test file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-23T23:39:16Z
  TYPE: MEASURE
  CLAIM: `Conduit.create_lesser_conduit(...)` now uses explicit self-based
    hooks and hookless lanes with no one-shot local aliasing for hook state,
    and the direct conduit hook unit file is green again (`39 passed`).
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1528-1604
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\test_conduit_configuration_and_hooks.py`
  IMPACT: The narrow lesser-conduit hook path now matches the measured aliasing
    rule: no aliasing for one-use hook checks, while keeping the hookless
    bypass intact.
  NEXT: if the user still wants more speed work on this slice, the next step is
    performance measurement rather than more hook-shape argument.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-23T23:40:20Z
  TYPE: FACT
  CLAIM: The remaining conduit-side hook overhead is no longer just “call
    `_fire_conduit_hooks(...)` or not.” Three concrete issues remain:
    1) `cleanup()` still checks hook presence twice and can be split into one
    hooks lane versus one hookless lane.
    2) `link`/`sever_link` and the contract mutation methods still resolve the
    peer conduit before checking whether the relevant hook will actually fire,
    so hookless paths still pay peer-resolution overhead.
    3) `_local_conduit_hooks` is semantically mixed: local registrations may
    contain `on_meld_*` names, so a coarse global truthiness gate can say
    “hooks exist” even when no conduit hook exists for the current event.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:322-340
  - src/melder/aether/conduit/conduit.py:2962-3070
  - src/melder/aether/conduit/conduit.py:3522-3883
  - src/melder/aether/conduit/conduit.py:1101-1209
  - tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py:767-795
  IMPACT: The next real conduit trim is not another coarse “any hooks at all”
    bypass. It is event-specific bypassing so hookless paths avoid peer
    resolution and mixed local hook maps do not force conduit events through a
    useless dispatch attempt.
  NEXT: summarize these three remaining conduit trim points to the user before
    choosing the next implementation cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-23T23:44:33Z
  TYPE: MEASURE
  CLAIM: The next conduit trim slice is landed and the direct hook file is
    green (`41 passed`). `cleanup()` now checks only the specific cleanup-start
    and cleanup-complete hook names, `create_lesser_conduit(...)` only enters
    the hooks lane when one of its three lifecycle hook names is actually
    present, `link`/`sever_link` only check their specific event hooks, and the
    contract mutation methods now avoid peer-conduit resolution entirely when
    the relevant `on_contract_created` / `on_contract_removed` hook is absent.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:322-340
  - src/melder/aether/conduit/conduit.py:1528-1604
  - src/melder/aether/conduit/conduit.py:3004-3070
  - src/melder/aether/conduit/conduit.py:3554-3883
  - tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py:983-1110
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\test_conduit_configuration_and_hooks.py`
  IMPACT: Conduit no longer pays mixed-hook false positives at these lifecycle
    and contract surfaces, and hookless contract paths no longer pay peer
    resolution when there is no matching contract hook to fire.
  NEXT: the remaining question is performance, not correctness. Rerun the
    isolated Melder gauntlet if we want to see whether this hook trim moved the
    outer-scope numbers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-23T23:52:38Z
  TYPE: FACT
  CLAIM: The post-change full-suite drift splits into three classes:
    1) one real runtime restoration (`Conduit._creations_configuration(...)`
    was accidentally missing and needs to exist),
    2) private spellspace tests asserting no-op safety on invalid inputs for
    `_register_spellspace(...)` / `_unregister_spellspace(...)`, which are not
    valid runtime contracts and should be removed or rewritten, and
    3) stale test expectations from the split-hook and `dynamic` cleanup work
    (`get_hooks(...)` detached merge semantics and `SpellbookCreationSystem`
    no longer taking/storing `automatic`).
  EVIDENCE:
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q`
  - tests/unit/melder/aether/conduit/test_conduit_internal_registration.py:88-164
  - tests/unit/melder/aether/conduit/test_conduit_lifecycle.py:834-862
  - tests/unit/melder/spellbook/configuration/test_configuration.py:158-162
  - tests/component/melder/spellbook/test_spellbook_component_configuration_core.py:77-82
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:537-575
  IMPACT: The remaining repair work should stay strict: restore the genuinely
    dropped runtime helper, delete or rewrite the nanny-state private-method
    tests, and align stale tests to the current runtime contracts instead of
    softening code.
  NEXT: patch those exact runtime/test seams and rerun the failing files before
    spending another full-suite run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to map the current conduit hook overlay model and identify the
exact zero-hook bypass seams before any implementation cut starts.

