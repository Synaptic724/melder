# Task: public_notch_target_for_staged_versions - a public way to notch to a staged version

- Completed: 2026-10-16T16:06:21Z
- Summary: notched 0.2.8249 - `Conduit.notch_spell`, `add_to_spell_index` and `remove_from_spell_index` take
  `spell_id=` (the spell_id `bind` or `bind_inactive` returned) beside `spell=`, and a notch checks its target
  before and inside its transaction; the README loop and the docs run on public calls. Release-note section
  "`notch_spell`, `add_to_spell_index` and `remove_from_spell_index` take a `spell_id`; a notch checks its
  target". Targeted suites green with the GIL off and on; the whole tree not run; rebuilt last, both checks OK.

## Metadata
- Task ID: TASK-2026-10-16-public_notch_target_for_staged_versions
- Story: none (standalone backlog task; found during S8 of EPIC-2026-10-14-managed_spell_quantity)
- Status: done
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-16T11:42:41Z
- Updated: 2026-10-16T16:11:42Z

## Objective
Make the stage -> notch -> meld loop work on public API. `Conduit.notch_spell(spell_index=..., spell=...)` needs the
staged version's Spell object, and no public call returns a parked version's Spell: `Spellbook.find_spell_by_id` and
`Conduit.get_spell_by_id` answer a parked id with the index's live spell, and only the internal
`Spellbook._get_owned_spell` returns the parked one. The README's stage-notch-meld sketch passes `spell_v2` (and
`spell_v1` for the revert), which nothing public produces; docs/expert/governed-change.md stops its lesson before the
notch for that reason, and the 0.2.8248 release note shows the notch as a comment. Outcome: the owner picks the shape,
it is built, and the README and docs examples run as written.

## Ticket Contract
- ENTRY_GATE: the shape is chosen - option A, by the owner on 2026-10-16 (DECISION note below). Still required before
  the first `src/` edit: the active board row, the patch lane public_notch_target_2026_10_16 linked here, and the
  mapping note.
- EXECUTION_BOUNDARY: `Conduit.notch_spell` in src/melder/aether/conduit/conduit.py - the `spell_id=` keyword, its
  resolution through the Book's `_get_owned_spell` and the target checks before the transaction; README's
  stage-notch-meld sketch; docs/expert/governed-change.md; new unit and integration tests; system docs with their
  indexes and the graph; the release note; one notch; the rebuild last. spellbook.py is read, not edited.
  Extended by the owner (2026-10-16): `Conduit.add_to_spell_index` and `Conduit.remove_from_spell_index` take
  `spell_id=` too, resolved the same way, with their docstrings; the lane's text says spell_id, not "version id".
- DEPENDENCIES: none. 0.2.8248 (S8) already wires versions staged before conjure, so the loop also works for them.
- EXIT_GATE: a probe runs the README loop as written (stage, notch, meld, revert) on public calls only; tests green
  with the GIL off and on; docs, release note, notch and both rebuild checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST if the chosen shape changes the meaning of an existing argument; CONFLICT if the
  notch transaction's metadata (it reads `spell.spell_id` and `spell._key` before admission) cannot be built from an
  id alone without a new lookup. The keyword reached `add_to_spell_index` and `remove_from_spell_index` on the
  owner's word (DECISION note 2026-10-16T15:04:47Z), not before it.

## Scope Boundaries
- In scope: one public way to name the notch target; the README and docs examples; tests and docs; on the owner's
  extension (2026-10-16), the same `spell_id=` on `add_to_spell_index` / `remove_from_spell_index` and spell_id
  wording in the lane's text.
- Out of scope: `find_spell_by_id`'s documented live-spell answer (other callers rely on it); `bind_inactive`'s
  return value (a spell id); new checks in the index-move seams (spellbook.py is melder_1's); "version id" wording
  outside this lane's text.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: every EXIT_GATE item but the rebuild checks is recorded in the Notes - the README loop on
  public calls and the tests green with the GIL off and on (13:28:26Z, 13:41:41Z, 15:23:08Z), the docs, system
  docs, graph and release note (14:15:44Z, 15:41:00Z, 15:53:41Z), the notch 0.2.8249 (14:23:00Z) - and the
  owner's extension landed in the same notch (15:04:47Z, 15:23:08Z). The rebuild runs last, after this closure,
  as the contribution guide orders, and its checks are recorded in a note below. Closed under the owner's
  standing direction to carry on ("continue onto the next stuff please"); no reserved decision is open.
- prior: draft -> in_progress (2026-10-16T12:33:09Z): the owner chose option A (chat 2026-10-16: "just use the
  private version if its inside the public call thats reasonable") and directed this task next ("continue onto
  the next stuff please"); melder_0 took it out of the backlog. Previous: draft -> draft at creation, from S8's
  finding, the owner's design choice first ("if you found more bugs just add tickets", 2026-10-16).

## Steps / Checklist
- [x] The owner picks the shape: option A (DECISION note, 2026-10-16).
- [x] Component patch and mapping note; red tests (the README loop on public calls only), the change, green in both
      GIL modes.
- [x] README sketch and docs/expert/governed-change.md run as written; system docs, graph, release note, notch,
      rebuild last.
- [x] Extension (owner, 2026-10-16): index-move component patch and mapping; red tests, `spell_id=` on
      `add_to_spell_index` / `remove_from_spell_index`, green in both GIL modes; spell_id wording; docs, system docs,
      graph and release note carry it; the lane archived again.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The chosen public notch target, its tests and a probe that runs the README loop.
- README and docs examples that run; system docs, release note, notch and rebuild.

## Files / Paths Impacted
- src/melder/aether/conduit/conduit.py (`Conduit.notch_spell`); src/melder/aether/spellbook/spellbook.py is read, not
  edited (`_get_owned_spell` already resolves an owned version, active or parked)
- src/melder/__version__.py (the notch); release_docs/next_version_release.md
- context_compass/system_docs/ (src_architecture, src_components, tests_architecture, tests_components, their
  indexes, conduit.py's graph descriptor and the assembled graph)
- README.md (the stage-notch-meld sketch); docs/expert/governed-change.md
- tests under tests/unit/melder/aether/conduit/ and tests/integration/melder/spellbook/

## Validation
- Run on Python 3.14.7t with the GIL off and on: the 52 tests of the four new files;
  tests/unit/melder/aether/conduit (1455 passed) and tests/integration/melder/aether/conduit (130 passed); the
  index-move callers (crystallizer membership and the find-by-id component test, 22 passed); GIL off, the
  crystallizer notch callers (5 passed, 3 xfailed as before); the notch callers listed in the 13:28:26Z note;
  the README-loop, release-note and today probes; expert lessons 17 and 26.
- Not run: the whole tree.

## Risks / Rollback Notes
- A second way to name the target must refuse both or neither given, so a notch never picks one silently.
- Rollback: revert the notch's files; the private path keeps working for internal callers.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/public_notch_target_20261016/ (scripts, probes, runs, notes)
  - system_docs/patches/completed/public_notch_target_2026_10_16/architecture_patch.md
  - system_docs/patches/completed/public_notch_target_2026_10_16/component_patch_conduit_notch_target.md
  - system_docs/patches/completed/public_notch_target_2026_10_16/code_description_patch_conduit_notch_target.md
  - system_docs/patches/completed/public_notch_target_2026_10_16/component_patch_conduit_index_move_target.md
  - S8's release-note probe shows the private notch the public loop replaces; it is rowed under the closed epic's
    evidence folder: artifacts/managed_spell_quantity_20261015/probes/probe_s8_release_note_example.py
- DISPOSITION: retain_as_reference (the folder); promote_to_documentation (the patch docs)
- CLEANUP_TRIGGER: done at closure (2026-10-16): the patch docs were promoted into the system docs and archived
  under system_docs/patches/completed/; the folder stays as the lane's evidence

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - the public notch target for a staged (parked) version
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; created 2026-10-16T11:42:41Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none (self-checks only; closed under the owner's standing direction)

## Notes
- DATETIME: 2026-10-16T11:42:41Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: No public call returns a staged (parked) version's Spell, and `notch_spell` needs one. `Conduit.notch_spell`
    builds its transaction metadata from `spell.spell_id` and `spell._key` and passes the object to the Book's
    notch; `Spellbook.find_spell_by_id` (and `Conduit.get_spell_by_id` through it) answers a parked id with the
    live spell of its index, by its documented contract; `Spellbook._get_owned_spell` - internal - returns the exact
    version. So the README's stage-notch-meld sketch cannot run as written (`spell_v2` and `spell_v1` come from
    nowhere public), docs/expert/governed-change.md stops its lesson before the notch, the S8 integration tests and
    probes notch through `_get_owned_spell`, and the 0.2.8248 release note shows the notch as a comment. A completed
    task recorded the same gap on 2026-09-05.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5622-5710
  - src/melder/aether/spellbook/spellbook.py:2029-2108
  - src/melder/aether/spellbook/spellbook.py:3290-3309
  - README.md:1068-1092
  - docs/expert/governed-change.md:16-25
  - release_docs/next_version_release.md:543-565
  - context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_bind_and_spell_task.md:185-191
  IMPACT: A user can stage a version but cannot promote it without private access; the documented loop is a sketch.
  NEXT: The owner answers the DECISION_REQUEST below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T11:42:41Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: Which public shape names the notch target? (A, recommended) `notch_spell(spell_index=..., spell=None, *,
    spell_id=None)` - exactly one of `spell` and `spell_id`, the id resolved to the exact owned version (active or
    parked) before the transaction starts; the smallest change, and it mirrors `meld(spell_id=...)`. (B) a public
    exact-version lookup beside `find_spell_by_id` (for example `find_version_by_id`, active or parked, None on a
    miss) that callers pass to `notch_spell` unchanged. (C) both. Either keeps `find_spell_by_id`'s live-spell
    answer, which other callers rely on.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5622-5710
  - src/melder/aether/spellbook/spellbook.py:2029-2108
  IMPACT: The choice fixes the public surface the README and docs examples will use.
  NEXT: Build the chosen shape after the owner answers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T12:33:09Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner chose option A (chat 2026-10-16: "just use the private version if its inside the public call thats
    reasonable"): `Conduit.notch_spell` takes `spell_id=` beside `spell=`, exactly one of the two, and resolves the id
    inside the public call through the Book's internal `_get_owned_spell` (the active or a parked version) before the
    transaction starts. `find_spell_by_id` keeps its live-spell answer and no public lookup is added. The same message
    accepted EPIC-2026-10-14-managed_spell_quantity and directed this task next ("continue onto the next stuff
    please").
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md:167-183
  - src/melder/aether/spellbook/spellbook.py:3290-3309
  IMPACT: The public shape is settled; the build follows the patch lane and the mapping note.
  NEXT: Probe what today's notch does with each way a caller can name its target.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T12:33:09Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Today's notch checks nothing about its target before it mutates (probe on the 0.2.8248 tree, Python 3.14.7t,
    GIL off and on, same results; no monkeypatches). C1: `find_spell_by_id(x2)` returns index X's live x1, so a notch
    to it is a silent no-op and `meld(spell_id=x2)` still raises KeyError. C2: the private `_get_owned_spell(x2)`
    notches both ways. C3: notching X to y2, a version parked in another index Y of the same Book, RETURNS and
    corrupts both indexes - X selects y2 with no active-map entry (a meld of x1 raises KeyError), Y keeps selecting y1
    while its active-map entry is y2, and a meld of y2 raises RuntimeError "Cannot build CreationContext before
    spell_codegen_creation exists". C4 (Y's active y1) and C5 (another Book's parked version) raise RuntimeError
    "Owned spell_id not parked for reactivation" after X's active version was already parked, so X has no active
    version (a meld of x1 raises KeyError) until a notch back to x1. Cause: `_apply_notch` parks the outgoing version
    first, and `_reactivate_owned_spell` files the incoming one under its own `spell.spell_index`, not the index
    passed.
  EVIDENCE:
  - context_compass/artifacts/public_notch_target_20261016/probes/probe_notch_target_today.py:1-132
  - context_compass/artifacts/public_notch_target_20261016/runs/probe_notch_target_today_gil0.txt:1-6
  - context_compass/artifacts/public_notch_target_20261016/runs/probe_notch_target_today_gil1.txt:5-10
  - src/melder/aether/conduit/conduit.py:5622-5710
  - src/melder/aether/spellbook/spellbook.py:3826-3967
  - src/melder/aether/spellbook/spellbook.py:1563-1621
  IMPACT: A `spell_id=` can name any version of the Book, so the id path must check its target before the
    transaction; the same checks close C3-C5 for `spell=`, which today corrupt the Book or leave an index without an
    active version.
  NEXT: Record the target-check decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T12:33:09Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: `notch_spell` resolves and checks its target before it starts the transaction, for both forms: (1) exactly one
    of `spell` and `spell_id` (ValueError otherwise, in the words `meld` and `managed_spell_meld` use) and a string id
    (TypeError); (2) the target is a version the conduit's Book owns - `spell_id` resolves through `_get_owned_spell`,
    and a `spell` must be the object `_get_owned_spell(spell.spell_id)` returns - else ValueError; (3) the target
    belongs to the index passed (`target.spell_index is spell_index`, the check `_apply_remove_from_index` makes),
    else ValueError naming the version and the remedy. A refused notch mutates nothing. Valid calls behave as before;
    the failing forms of C3-C5 raise ValueError up front instead of corrupting the Book or raising RuntimeError
    half-way.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4177-4262
  - src/melder/aether/conduit/conduit.py:5020-5021
  - src/melder/aether/conduit/conduit.py:5142-5145
  - context_compass/artifacts/public_notch_target_20261016/runs/probe_notch_target_today_gil0.txt:1-6
  IMPACT: The target is safe to name by id; the release note lists the new ValueErrors as a change for calls that were
    already broken.
  NEXT: Write the patch lane (architecture and Conduit component patch) and the mapping note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T12:33:09Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: File custody. EPIC-2026-10-14-managed_spell_quantity closed at 2026-10-16T12:17:31Z, so spellbook.py and
    transfer_of_ownership.py are released to melder_1 now (its TASK-2026-10-16-recheck_contract_consumers_when_provider_
    changes waits on that handoff); this task edits neither. conduit.py is held by this task until it lands: melder_1's
    D3 also edits `Conduit.notch_spell` (after the notch window), and its build has not started (it waits on the
    owner's approval). The change leaves the window and the fan-out lines of `notch_spell` as they are (the resolved
    target is rebound to `spell`), so melder_1's planned diff applies with at most a context shift; conduit.py is
    released at this task's closure. The Codex bridge does not connect (list_threads: "Cannot connect to Codex
    desktop") and melder_1 is a Claude session, so the owner relays this handoff.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:25-34
  - context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/architecture_patch.md:58-69
  - context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/architecture_patch.md:144-150
  IMPACT: melder_1's wait on spellbook.py is over; conduit.py keeps one writer.
  NEXT: The owner relays the handoff to melder_1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T12:33:09Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: Should `add_to_spell_index` and `remove_from_spell_index` take the same `spell_id=` keyword? Both move only a
    parked version (their seams refuse an active one), so with no public call returning a parked Spell neither can be
    called on public objects today - the gap this task closes for the notch. The keyword would resolve the id the
    same way (one shared resolver); their seams already check ownership and membership before they mutate.
    Recommended: yes, in this landing; without an answer by the landing they get a backlog task instead.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5712-5788
  - src/melder/aether/conduit/conduit.py:5790-5851
  - src/melder/aether/spellbook/spellbook.py:4002-4096
  - src/melder/aether/spellbook/spellbook.py:4177-4262
  IMPACT: The owner ruled on the notch; extending another public surface waits for his word.
  NEXT: Ask the owner in the report; build the notch meanwhile.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T12:43:41Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Two internal callers notch through the public facade and pass the checks the patch adds:
    `RestoreEngine._enforce_selections` and the graft runner's selection adoption both resolve their target with
    `_get_owned_spell` on the Book whose own conduit they notch through (`_conjure_for_book`, `_host_book.conduit`),
    and the target was staged on the index they pass (`bind_inactive(spell_index=anchor)` / the merge index). A
    cleaned Spell keeps `spell_id` and `_key` and loses `spell_index`, so the ownership check (first) refuses a stale
    object before the membership check reads `spell_index`.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2271-2321
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:553-578
  - src/melder/aether/spellbook/spell.py:581-723
  IMPACT: The checks need no caller change; the crystallizer suites are regression evidence for them.
  NEXT: Record the mapping note.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T12:43:41Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Mapping, patch section -> implementation -> validation (patch lane public_notch_target_2026_10_16, written
    before any src/ edit). (1) Invariants 1-2 and the component patch's two helpers -> `_resolve_notch_target` and
    `_refuse_foreign_notch_target` in conduit.py, called as `spell = self._resolve_notch_target(...)` after the Book
    check -> unit refusals with nothing started; integration C3-C5 refused with both indexes intact. (2) Invariant 3
    (the second check under the seal) -> one `_refuse_foreign_notch_target` line inside the window's `try`, before
    `_notch_spell` (so the custody note's "leaves the window lines as they are" gains that one line) -> a unit test
    that moves the target after the first check and sees the in-window refusal, the transaction ended failed and the
    seam not called. (3) Invariant 4 (valid calls unchanged) -> nothing else in `notch_spell` moves; the docstring is
    rewritten -> integration: the loop by id (staged after and before conjure), the revert, the no-op, an index-link
    borrower following a notch by id; the existing notch, index-link, S8 and crystallizer suites green in both GIL
    modes. (4) Invariant 5 (no new lock) -> review and the suites. Then the docs (README, governed-change, UX expert
    17 and 26, the concept map), the README-loop probe, system docs and graph, release note, notch, closure, rebuild.
  EVIDENCE:
  - context_compass/system_docs/patches/active/public_notch_target_2026_10_16/architecture_patch.md:1-109
  - context_compass/system_docs/patches/active/public_notch_target_2026_10_16/component_patch_conduit_notch_target.md:1-80
  - context_compass/system_docs/patches/active/public_notch_target_2026_10_16/code_description_patch_conduit_notch_target.md:1-67
  IMPACT: The entry gate is met: the board row routes the task, the patch lane is linked, the mapping is recorded.
  NEXT: Write the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T12:55:55Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Mailbox messaging is on again (owner, chat 2026-10-16: "talk to melder_0 in the mailbox please and
    switch the mailbox on in this context_compass yaml I'll tell melder_1" - melder_1 is meant, melder_0 being
    this agent; the yaml already read `agent_communication.backend: mailbox` at 12:54:10Z). Consumed the two
    messages addressed to melder_0: M1-18 (melder_1's rule-1 handoff questions, ACK requested) was closed by M1-19
    (rule 1 landed as 0.2.8247; the spellbook.py and transfer_of_ownership.py keywords and five test files
    returned), and S8 landed above it as 0.2.8248, so nothing in either is open. Sent melder_1 M0-175 (ACK of
    both) and M0-176 (HANDOFF: spellbook.py and transfer_of_ownership.py released; conduit.py held until this task
    lands; the seam backlog task), each with its alert line. The earlier DECISION note's ticket range is
    corrected to 167-183 (the Artifact Links edit moved it).
  EVIDENCE:
  - context_compass/config/context_compass_config.yaml:122-123
  - context_compass/tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md:255-274
  IMPACT: melder_1 can take spellbook.py; conduit.py keeps one writer until this task lands.
  NEXT: Rerun the crystallizer suites in smaller shards (the combined run hit the 175 s limit).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T13:28:26Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Built as patched: `Conduit.notch_spell` takes `spell_id=` (keyword-only, `spell` now defaulting to None),
    `_resolve_notch_target` does the argument checks and `_owned_notch_target` the resolution, ownership and
    membership checks (the patch called the second helper `_refuse_foreign_notch_target`; one helper now resolves and
    checks, so the refusal text lives in one place), called before admission and again inside the window's `try`;
    the docstring now says the conduit admits the transaction (the old one said the Spellbook did). Red then green:
    the 16 unit tests (15 failed before - the 16th, `spell=` with an owned member, passed before as it should) and 10
    integration tests (all failed before) pass with the GIL off and on. Regression, both GIL modes:
    tests/unit/melder/aether/conduit 1439 passed; tests/integration/melder/aether/conduit 120 passed (the new file,
    notch lifecycle, op guards, index-link follow and meld, the notch race); the notch callers - crystallizer restore
    43 passed + 3 xfailed (as before), ordered-disposal replay 23, membership, lifecycle, per-frame worlds, spellframe
    kind, managed options, bind-hook recording, the S8 parked tests, the managed conduit tests, non-resolvable replay
    and eight component files that notch - all passed (GIL off: the first ordered-disposal run hit the 175 s call limit
    after 22 passes; its last 12 then passed alone).
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5622-5859
  - tests/unit/melder/aether/conduit/test_conduit_notch_target.py:1-252
  - tests/integration/melder/aether/conduit/test_notch_spell_by_id_integration.py:1-271
  - context_compass/artifacts/public_notch_target_20261016/runs/red_unit_gil0.txt:1-297
  - context_compass/artifacts/public_notch_target_20261016/runs/green_new_tests_gil1.txt:1-2
  - context_compass/artifacts/public_notch_target_20261016/runs/shard_restore_b_gil1.txt:1-2
  IMPACT: The code side of the exit gate holds; the docs, the README-loop probe, the system docs, the release note,
    the notch and the rebuild remain.
  NEXT: The docs - README, docs/expert/governed-change.md, UX expert 17 and 26, the expert concept map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T13:40:45Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Re-onboarded after a context compaction (attestation 13:39Z, self-certified on the owner's standing
    instruction) and consumed M1-20, melder_1's ACK of M0-175 and M0-176 (no ACK requested). The owner approved
    melder_1's rule-2 patch; its build runs on a scratch copy of the tree over spellbook.py,
    spell_system_states.py, meld.py, the contract presence strategy, spellbook_validation_error.py and
    conduit_ward.py (docstring and comment), with tests - not transfer_of_ownership.py. conduit.py stays with
    this task until it lands; then melder_0 hands it over and names the notch it took, and melder_1's D3 lines
    follow one notch above. The seam task stays a backlog draft unless the owner adds it to melder_1's lane.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:686-747
  - context_compass/attention_board.md:185-185
  IMPACT: The closure NOTICE (M0-177) releases conduit.py and names the notch; melder_1's landing comes after
    this one and re-extracts its own files' graph descriptors and rebuilds then.
  NEXT: Land the docs and probes MEASURE note.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T13:41:41Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The user docs run on public calls (Python 3.14.7t, GIL off and on, same output). README's swap sketch names
    the versions by id (`id_v1 = index.selected_spell_id`, `notch_spell(spell_index=index, spell_id=id_v2)`, the
    revert by `id_v1`); the acceptance probe builds the sketch's preconditions on a dynamic root and execs its two
    blocks verbatim - loop and revert OK. docs/expert/governed-change.md says promotion is
    `notch_spell(spell_index=..., spell_id=...)` and that a wrong target is refused. UX expert 17 takes the swap by
    id - melds v2 (rate 250), notches back (rate 100); expert 26's comment points at that lesson; both run green.
    The expert concept map's lesson-17 entry and arc line carry the 2026-10-16 ruling, and its 2026-08-03
    retraction is marked SUPERSEDED with its history kept. The today-probe rerun on the changed tree: C3, C4 and C5
    raise ValueError naming the version and leave both indexes selecting, holding and melding as before; C1
    (notching to what `find_spell_by_id` returns) is still the documented no-op, its answer being the active
    member; C2 unchanged.
  EVIDENCE:
  - context_compass/artifacts/public_notch_target_20261016/probes/probe_readme_loop.py:1-76
  - context_compass/artifacts/public_notch_target_20261016/runs/probe_readme_loop_gil0.txt:1-4
  - context_compass/artifacts/public_notch_target_20261016/runs/probe_readme_loop_gil1.txt:1-4
  - context_compass/artifacts/public_notch_target_20261016/runs/ux17_gil1.txt:1-18
  - context_compass/artifacts/public_notch_target_20261016/runs/ux26_gil0.txt:1-20
  - context_compass/artifacts/public_notch_target_20261016/runs/probe_notch_target_after_gil0.txt:1-6
  - README.md:1063-1093
  - docs/expert/governed-change.md:16-27
  - UX_and_AIX_experiences/04_expert/17_notch_swapping_a_live_object.py:1-169
  - UX_and_AIX_experiences/04_expert/_concept_map.txt:348-389
  - UX_and_AIX_experiences/04_expert/_concept_map.txt:807-812
  IMPACT: The exit gate's README-loop probe holds; the system docs, graph, release note, notch and rebuild remain.
  NEXT: The system docs (src_architecture, src_components, the tests docs, their indexes) and the graph.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T14:15:44Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The patch lane is promoted into the four system documents and the graph, checked from disk.
    src_architecture (9 edits, plus 2 citation repoints in the rubric pass; 4665 lines, 62 sections), src_components
    (13 edits; 11641 lines, 153 sections), tests_components (14; 3549 lines, 69 sections) and tests_architecture
    (4; 972 lines, 32 sections): each index regenerated and `--check` OK; the content-preservation diff loses only
    deliberate replacements (18, 18, 4 and 3 lines - remeasured citations and extents, the corrected sequence step
    and seal mode, the recounted counts; 3 more in the rubric pass); no package or absolute path; every code-map and
    Key Files path resolves (src in the graph index, tests on disk) and every code-map extent equals its file today;
    the inventory recounted again in this pass (unit 509/506, component 168/166, integration 175/168, aether trees
    205 and 45; the two new files hold 16 and 10 tests). Graph: re-extracted with `--strict`, the Conduit node's
    responsibilities appended but not accepted (it was SEMANTICS_STALE before this lane), reassembled - 28067 lines,
    591 sections, 1227 nodes, 1415 edges, `--check` rc=0; walker census unchanged (AUTHORED 1074, SEMANTICS_STALE
    144, UNSEMANTIC 9, RETIRED 5). Stale text corrected on the way: the SpellIndex Mutation Entry's step 2 (it said
    the Spellbook starts the transaction; the Conduit does), src_components' verb citations (5419/5492/5563 ->
    5731/5916/5987) and `link`'s TypeError (5296-5298 -> 5571-5573), the notch seal described as spellbook INTENT
    (the strategy claims the Book EXCLUSIVE), and `check_system_state` cited at
    spellbook_creation_system.py:1253-1292 (it is at 1282-1329). Still wrong, in a file this lane does not edit:
    spellbook.py's `_notch_spell` and `_apply_notch` docstrings say the notch claims the Book INTENT.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:920-968
  - context_compass/system_docs/src_architecture.md:1061-1082
  - context_compass/system_docs/src_components.md:2742-2756
  - context_compass/system_docs/src_components.md:6058-6139
  - context_compass/system_docs/src_components.md:7930-7946
  - context_compass/system_docs/tests_components.md:1121-1128
  - context_compass/system_docs/tests_architecture.md:459-467
  - context_compass/artifacts/public_notch_target_20261016/runs/docs_checks_after_rubric.txt:1-9
  - context_compass/artifacts/public_notch_target_20261016/runs/graph_walker_after.txt:1-10
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py:239-269
  - src/melder/aether/spellbook/spellbook.py:3792-3796
  - src/melder/aether/spellbook/spellbook.py:3834-3838
  - src/melder/aether/spellbook/spellbook_creation_system.py:1281-1329
  IMPACT: The packaged system docs and graph describe the notch target and the corrected sequence; the closure
    NOTICE tells melder_1 about the INTENT docstrings in spellbook.py.
  NEXT: Record the rubric scores.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T14:15:45Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rubric scores, from disk after the index rebuilds (self-scored; no independent reviewer), unchanged from the
    0.2.8247 pass: src_architecture 83 (B) - fidelity 4, contract 5, depth 4, addressability 4, join 4, mirror 4;
    src_components 83 (B) - 4, 5, 4, 4, 4, 4; tests_architecture 83 (B) - 4, 5, 4, 4, 4, 4; tests_components 77
    (B) - 4, 4, 3, 4, 4, 4. Basis: src_architecture was re-read whole after this session's compaction; in the other
    three the sections this landing edited were re-read from disk and checked against the source (conduit.py
    5622-5859, the notch seal, the test counts), and their unchanged remainder keeps the 0.2.8247 judgment. The
    measurable half was rerun on all four: one H1 each, no duplicate indexed name, contracts complete and in order,
    no portability or absolute-path hit, 160 / 36 / 234 / 254 code-map records complete with every extent equal to
    its file today, every Key Files path resolving, every `path:line` of the src pair in bounds (the recipe's two
    misses are bare file names in the 0.2.8247 handoff prose). Why not 5: fidelity - both src meld-flow diagrams
    name "Phase12 Compiled Executors", which the Unknowns list as removed; some one-line failure modes and test
    invariants carry no citation; and the drifted `check_system_state` citation (repointed) shows carried-forward
    ranges can drift - eight more were spot-checked and hold; depth - those one-clause lines and four src_components
    entries with thin fields; addressability - container H2s that hold only sub-headings; join - 150 of 160, 36 of
    36, 225 of 234 and 242 of 254 verified_at stamps carried forward although every extent measured equal today;
    mirror - each pair shares its contract and adds different non-contract sections. tests_components contract 4: a
    Table of Contents and a Component Template sit among its sections; depth 3: its Mock Fixture Corpus entry has
    five thin fields.
  EVIDENCE:
  - context_compass/artifacts/public_notch_target_20261016/runs/rubric_checks_2026_10_16.txt:1-52
  - context_compass/artifacts/public_notch_target_20261016/scripts/rubric_checks_2026_10_16.py:1-176
  - context_compass/artifacts/public_notch_target_20261016/runs/citation_bounds_2026_10_16.txt:1-3
  - context_compass/system_docs/src_architecture.md:3943-3943
  - context_compass/system_docs/src_components.md:10862-10862
  - context_compass/system_docs/src_architecture.md:2329-2341
  - context_compass/system_docs/tests_architecture.md:419-428
  - context_compass/system_docs/src_components.md:5691-5764
  - context_compass/system_docs/src_architecture.md:735-736
  - context_compass/system_docs/tests_architecture.md:353-354
  - context_compass/system_docs/tests_components.md:156-172
  - context_compass/system_docs/tests_components.md:639-728
  IMPACT: All four documents stay in band B; the weak points are recorded for the next reader.
  NEXT: Notch `__version__` to 0.2.8249 and add the board's notch notice.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T14:23:00Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Notched and written up. `__version__` read 0.2.8248 just before the change, set to 0.2.8249; the
    board's notch notice names it ("notch above it if you land after"). The running release note is headed
    0.2.8249 and carries the
    section "`notch_spell` takes the version's id, and refuses a version that is not the index's" (the gap, a
    self-contained example, the exactly-one rule, the id resolution, both checks with their quoted messages, the
    C3-C5 history, the no-op, what stays the same); S8's example notches by id instead of a comment and S8's "What
    stays the same" no longer lists `notch_spell`; two packaging bullets (the README sketch, governed-change and
    lesson 17 by id; the packaged system docs and graph) and the rebuild line at 0.2.8249. A probe execs both
    examples from the note as written, each in a fresh interpreter, plus the refusals: both examples OK and every
    quoted message matches, with the GIL off and on. The patch lane's three docs say landed and promoted and moved
    to system_docs/patches/completed/; the artifact board's three active patch rows became one cleared row and the
    ticket's Artifact Links point at the completed folder. The owner asked (chat, 2026-10-16) what the add/remove
    question means; it was restated - whether `add_to_spell_index` / `remove_from_spell_index` also take
    `spell_id=` to name the owned, parked version they move (ids stay identities) - and the closure waits for the
    answer, so it can join this landing.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - context_compass/attention_board.md:297-299
  - release_docs/next_version_release.md:1-1
  - release_docs/next_version_release.md:560-578
  - release_docs/next_version_release.md:580-636
  - release_docs/next_version_release.md:637-711
  - context_compass/artifacts/public_notch_target_20261016/scripts/release_note.py:1-65
  - context_compass/artifacts/public_notch_target_20261016/probes/probe_release_note_examples.py:1-109
  - context_compass/artifacts/public_notch_target_20261016/runs/probe_release_note_examples_gil0.txt:1-11
  - context_compass/artifacts/public_notch_target_20261016/runs/probe_release_note_examples_gil1.txt:1-11
  - context_compass/system_docs/patches/completed/public_notch_target_2026_10_16/architecture_patch.md:1-117
  - context_compass/artifact_board.md:110-110
  IMPACT: The landing is complete but for the owner's add/remove answer, the closure and the rebuild; the assets and
    LLM bundles are stale until the rebuild.
  NEXT: On the owner's answer, either build the add/remove keyword in this landing or file it as a backlog task;
    then close with NOTICE M0-177 and rebuild last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T15:04:47Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner answered (chat, 2026-10-16: "yeah that makes sense sure, 1. not sure what a version id, spell_id
    is generated by bind, not sure what you mean by version_id, your not using codex your using mailbox turn off
    codex_mcp"). (1) `add_to_spell_index` and `remove_from_spell_index` take `spell_id=` beside `spell=` in this
    landing (0.2.8249): exactly one of the two, the spell_id resolved inside the call through the Book's
    `_get_owned_spell`, as `notch_spell` does; their seams keep checking ownership, the parked state and
    membership. (2) The identifier is `spell_id`, the id `bind` and `bind_inactive` generate: this lane's
    messages, docstrings, tests, docs and release note say spell_id, not "version id" ("version" stays the word
    for a spell in an index's lineage). (3) Codex MCP messaging is off: special_instructions/codex_mcp.md (not in
    version control) is rewritten to a short notice that the mailbox is the transport; its previous text is kept
    verbatim in this task's notes folder.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md:275-292
  - src/melder/aether/conduit/conduit.py:5861-5938
  - src/melder/aether/conduit/conduit.py:5939-6001
  - src/melder/aether/spellbook/spellbook.py:4002-4096
  - src/melder/aether/spellbook/spellbook.py:4177-4262
  - context_compass/special_instructions/codex_mcp.md:1-118
  - context_compass/config/context_compass_config.yaml:122-123
  IMPACT: The landing grows by the two keywords and a terminology pass; the patch lane reopens for them before any
    src/ edit; the closure follows after.
  NEXT: Rewrite codex_mcp.md, then reopen the patch lane with the index-move component patch and the mapping.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T15:10:41Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Mapping for the owner's extension, patch section -> implementation -> validation (lane reopened; written
    before the src/ edit). (1) Invariant 6 and the index-move component patch -> in conduit.py a shared
    `_check_spell_argument(verb, spell, spell_id)` (both / neither -> ValueError, non-str id / str spell ->
    TypeError, worded for the verb), `_owned_spell_by_id(verb, spell_id)` (`_get_owned_spell`, None -> ValueError)
    and `_resolve_spell_to_move`, called by `add_to_spell_index` and `remove_from_spell_index` after their Book check;
    `_resolve_notch_target` uses the shared argument check -> unit (new test_conduit_index_move_target.py): per verb,
    the refusals with nothing started, a resolved spell_id reaching the metadata and the Book's entry, `spell=`
    passed through without asking the Book; integration (new test_index_moves_by_spell_id_integration.py): add and
    remove by spell_id in a dynamic world, then a notch to the moved spell and a meld; an unknown id, both and
    neither refused with the indexes intact; an active spell_id refused by the seam, indexes intact. (2) Invariant
    7 -> the notch refusals reworded to spell_id -> one notch unit test asserts the new text; the lane's files
    searched for "version id". (3) The add and remove docstrings say the conduit admits the transaction and list the
    seams' refusals (remove: the active member and the only member are refused). (4) Regression, GIL off and on: the
    conduit unit tree, the notch-target tests, the index-move suites (index lifecycle and depth, index-link follow,
    notch lifecycle, op guards, crystallizer membership, the find-by-id component test). (5) Then the wording in the
    lane's docs, system docs and graph, the release note, the tests docs, the archive, closure and rebuild; the notch
    stays 0.2.8249.
  EVIDENCE:
  - context_compass/system_docs/patches/active/public_notch_target_2026_10_16/architecture_patch.md:1-150
  - context_compass/system_docs/patches/active/public_notch_target_2026_10_16/component_patch_conduit_index_move_target.md:1-76
  - src/melder/aether/conduit/conduit.py:5753-6001
  - src/melder/aether/spellbook/spellbook.py:3969-4096
  - src/melder/aether/spellbook/spellbook.py:4145-4262
  IMPACT: The entry gate is met again for the extension: the lane is reopened and linked, the mapping recorded.
  NEXT: Write the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T15:23:08Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The extension is built as patched. `add_to_spell_index` and `remove_from_spell_index` take `spell_id=`
    beside `spell=` (keyword-only, `spell` now defaulting to None) and call `_resolve_spell_to_move` after their
    Book check: the shared `_check_spell_argument` (both / neither -> ValueError, non-str spell_id / str spell ->
    TypeError, each message naming the verb), then `_owned_spell_by_id` for a spell_id (`_get_owned_spell`; None ->
    ValueError "<verb>: spell_id '<id>' is not owned by this conduit's Spellbook. ..."); a `spell` passes through to
    the seams' own checks. `_resolve_notch_target` uses the same argument check; the notch refusals now read
    "spell_id '<id>' ...". Both verbs' docstrings now say the conduit admits the transaction and list the seams'
    refusals; remove's old bullet (retiring the active member leaves the index selecting a non-member) is corrected -
    the seam refuses an active member. Red then green: 28 failed before (14 of 16 new unit tests - the two `spell=`
    pass-through tests passed, as they should -, the 4 reworded notch tests, all 10 new integration tests); after,
    the 52 targeted tests pass with the GIL off and on. Regression, both modes: tests/unit/melder/aether/conduit 1455
    passed; tests/integration/melder/aether/conduit 130 passed; the crystallizer membership and find-by-id component
    tests 22 passed; GIL off, the crystallizer notch callers (restore, lifecycle and per-frame worlds selected on
    selection/staged/notch/graft) 5 passed and 3 xfailed, as before. The release-note and README-loop probes rerun OK.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5753-5970
  - src/melder/aether/conduit/conduit.py:5971-6173
  - tests/unit/melder/aether/conduit/test_conduit_index_move_target.py:1-232
  - tests/integration/melder/aether/conduit/test_index_moves_by_spell_id_integration.py:1-226
  - tests/unit/melder/aether/conduit/test_conduit_notch_target.py:153-190
  - context_compass/artifacts/public_notch_target_20261016/scripts/apply_index_move_target.py:1-526
  - context_compass/artifacts/public_notch_target_20261016/runs/red_extension_gil0.txt:1-713
  - context_compass/artifacts/public_notch_target_20261016/runs/green_extension_gil0.txt:1-2
  - context_compass/artifacts/public_notch_target_20261016/runs/green_extension_gil1.txt:1-2
  - context_compass/artifacts/public_notch_target_20261016/runs/suite_unit_conduit_ext_gil1.txt:1-22
  - context_compass/artifacts/public_notch_target_20261016/runs/suite_integration_aether_conduit_ext_gil1.txt:1-3
  - context_compass/artifacts/public_notch_target_20261016/runs/shard_notch_callers_ext_gil0.txt:1-2
  IMPACT: The code side of the extension holds; conduit.py grew 172 lines (7784), so its citations and code-map
    extent in the system docs move; the wording pass, docs, release note and archive remain.
  NEXT: The spell_id wording in the lane's docs, then the system docs, graph and release note for the extension.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T15:41:00Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The spell_id wording and the release note carry the owner's extension. Reworded to spell_id and nothing
    else: UX expert 17 (docstring, comments and prints; two paragraphs rewrapped) and 26 (one comment), both rerun
    green with the GIL off and on; the expert concept map's lesson-17 entry, and its "DOCSTRINGS THAT LIE" block
    marked RESOLVED in 0.2.8249 with its history kept; the docstrings of the two notch test files (the 52 targeted
    tests still pass in both modes); two comment lines in conduit.py (no line moved). The release-note section is
    retitled "`notch_spell`, `add_to_spell_index` and `remove_from_spell_index` take a `spell_id`; a notch checks
    its target": its example also moves the parked version out and back by spell_id, new bullets give the index
    moves' refusals and the corrected docstrings, the quoted notch messages carry the spell_id text; the S8
    comment and two packaging bullets say spell_id. A new probe runs both note examples as written and compares
    the three quoted messages with what the calls raise: all three match, eleven refusals leave both indexes
    intact, the moves by spell_id work, GIL off and on. Left as written: "version id" in another lane's sections
    (the 0.2.8229 lookup, lines 46 and 656) and the docstrings of `_deactivate_borrowed_spell` and
    `Spellbook._get_owned_spell` ("Version id of ..."), code this lane does not change.
  EVIDENCE:
  - UX_and_AIX_experiences/04_expert/17_notch_swapping_a_live_object.py:1-171
  - UX_and_AIX_experiences/04_expert/26_codegen_create_modify_iterate.py:230-233
  - UX_and_AIX_experiences/04_expert/_concept_map.txt:348-388
  - UX_and_AIX_experiences/04_expert/_concept_map.txt:865-883
  - tests/integration/melder/aether/conduit/test_notch_spell_by_id_integration.py:1-10
  - release_docs/next_version_release.md:580-648
  - release_docs/next_version_release.md:714-721
  - context_compass/artifacts/public_notch_target_20261016/probes/probe_release_note_examples_ext.py:1-194
  - context_compass/artifacts/public_notch_target_20261016/runs/probe_release_note_ext_gil0.txt:1-20
  - context_compass/artifacts/public_notch_target_20261016/runs/probe_release_note_ext_gil1.txt:1-20
  - context_compass/artifacts/public_notch_target_20261016/runs/ux17_spell_id_gil0.txt:1-18
  - context_compass/artifacts/public_notch_target_20261016/runs/green_wording_gil1.txt:1-2
  IMPACT: The lane's user-facing text names spells by spell_id and the note's examples and messages are checked
    against the code; the system docs, their indexes, the graph and the tests docs remain.
  NEXT: Bring src_architecture and src_components to the extension, with remeasured conduit.py citations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T15:53:41Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The four system documents and the graph carry the owner's extension, checked from disk. src_architecture
    (4696 lines, 62 sections): the boundary bullet (all three verbs by spell_id; the add and remove docstrings
    fixed), the summary, the mutation sequence (step 1 and the seams' refusals in step 5), the notch invariant
    with the index moves appended, a fourth failure mode for the index moves and the notch messages in their
    spell_id text, the code map (conduit.py 7784) and the handoff. src_components (11695 lines, 154 sections): the
    Conduit Runtime's index-move paragraph, Inputs, Outputs, Responsibilities and Failure Modes; the SpellIndex
    Mutation Surface (both verbs resolve a spell_id, the docstring warning marked resolved, citations remeasured);
    a new flow "Conduit Index Moves by spell_id -> Spellbook Seams"; Spellbook Core's mediator citations
    (5708/6041/6148); the code map and the handoff. tests_components and tests_architecture: the two new files in
    the same clusters as the notch files (16 and 10 tests read from disk), key files, code-map records and sources;
    the counts recounted (unit 507 of 510, component 166 of 168, integration 169 of 176, aether trees 206 and 46;
    842 test modules). Every remeasured conduit.py citation lands on the line it names (5622, 5708, 5731, 5753,
    5791, 5846, 5897, 5932, 5971, 6041, 6061, 6084, 6148, 6159, 6228). Each index rebuilt and `--check` OK; the
    preservation diff loses only this pass's replacements (51, 38, 7 and 26 lines: rewording, remeasured
    citations and extents, recounts, rewraps, the resolved warning); the measurable rubric half clean on all four
    (one H1, no duplicate or wrapped headings, contracts in order, no portability or absolute-path hit, every C1
    extent equal to its file, every path resolving); the citation recipe's two misses are the 0.2.8247 handoff's
    bare file names, as before. Graph: re-extracted with `--strict` (rc 0), the Conduit node's notch line reworded
    to spell_id and the index-move line appended, not accepted; reassembled (28068 lines, 591 sections, 1227
    nodes, 1415 edges, `--check` rc 0); the walker census is unchanged (AUTHORED 1074, SEMANTICS_STALE 144,
    UNSEMANTIC 9, RETIRED 5). Rubric scores, self-scored from disk (no independent reviewer), unchanged from the
    14:15:45Z note: 83 / 83 / 83 / 77, band B; the edited sections were re-read against conduit.py 5622-6257 and
    spellbook.py 3969-4262, and the weak points recorded then stand.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:494-512
  - context_compass/system_docs/src_architecture.md:922-976
  - context_compass/system_docs/src_architecture.md:1069-1099
  - context_compass/system_docs/src_architecture.md:2029-2051
  - context_compass/system_docs/src_components.md:2759-2772
  - context_compass/system_docs/src_components.md:6080-6168
  - context_compass/system_docs/src_components.md:7977-7995
  - context_compass/system_docs/tests_components.md:1129-1135
  - context_compass/system_docs/tests_components.md:1600-1605
  - context_compass/system_docs/tests_architecture.md:461-467
  - context_compass/artifacts/public_notch_target_20261016/runs/docs_checks_extension.txt:1-4
  - context_compass/artifacts/public_notch_target_20261016/runs/preservation_extension.txt:1-125
  - context_compass/artifacts/public_notch_target_20261016/runs/rubric_checks_extension.txt:1-52
  - context_compass/artifacts/public_notch_target_20261016/runs/citation_bounds_extension.txt:1-3
  - context_compass/artifacts/public_notch_target_20261016/runs/graph_assemble_check_extension.txt:1-4
  - context_compass/artifacts/public_notch_target_20261016/runs/graph_walker_extension.txt:1-10
  - src/melder/aether/conduit/conduit.py:5622-6257
  IMPACT: The packaged docs and graph describe the landing as built; the patch lane can be archived and the
    task closed.
  NEXT: Archive the patch lane (status and handoff of the four patch docs, move to completed/, board rows).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T16:11:42Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Closed and rebuilt. Re-onboarded after a context compaction (attestation about 16:04Z, self-certified on
    the owner's standing instruction); no message was addressed to melder_0. The closure (16:06:21Z) moved this
    ticket to tasks/completed/, synced the attention board (row and detail removed, the notch_borrower_docs anchor
    dropped and this one added - 12 kept - and the 0.2.8249 notice worded for the extension) and the artifact
    board (the folder row and the four patch rows became two cleared rows), and sent melder_1 NOTICE M0-177 with
    its alert: conduit.py released, the INTENT docstrings in spellbook.py named. Then the rebuild, last, from the
    repository root on Python 3.14.7t: the build assets (agent documentation 468 entries, bind guard 628, system
    documents 4, all at v0.2.8249) with `--check` OK on all three; the LLM bundles with `--include-untracked` (src
    583, tests 1123, other 404 files) with `--check --include-untracked` OK on all three. No .git/index.lock left.
    This note and the board edits after the rebuild lie outside both builds' inputs (the LLM builder excludes
    context_compass/; the assets read src/ and the four system documents); both checks are rerun after them.
  EVIDENCE:
  - context_compass/artifacts/public_notch_target_20261016/scripts/close_task_extension.py:1-292
  - context_compass/artifacts/public_notch_target_20261016/runs/rebuild_assets_0_2_8249.txt:1-7
  - context_compass/artifacts/public_notch_target_20261016/runs/rebuild_assets_check_0_2_8249.txt:1-7
  - context_compass/artifacts/public_notch_target_20261016/runs/rebuild_llm_0_2_8249.txt:1-8
  - context_compass/artifacts/public_notch_target_20261016/runs/rebuild_llm_check_0_2_8249.txt:1-7
  - context_compass/attention_board.md:212-212
  - context_compass/attention_board.md:293-296
  - context_compass/mailbox_board.md:912-926
  - llm_support/_builder.py:90-91
  IMPACT: The EXIT_GATE's rebuild checks hold and the landing is complete; conduit.py is melder_1's.
  NEXT: None in this lane; melder_1 lands D3 above 0.2.8249.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
- Scope and outcome: done. `Conduit.notch_spell(spell_index=..., spell_id=...)` - option A, the owner's choice -
  runs the stage -> notch -> meld loop on public calls, its target checked before and inside the transaction; on
  the owner's extension `add_to_spell_index` and `remove_from_spell_index` take `spell_id=` too, and the lane's
  text says spell_id. Notched 0.2.8249; release-note section "`notch_spell`, `add_to_spell_index` and
  `remove_from_spell_index` take a `spell_id`; a notch checks its target".
- Evidence: Notes 11:42:41Z-16:11:42Z; the lane folder artifacts/public_notch_target_20261016/; the patch docs in
  system_docs/patches/completed/public_notch_target_2026_10_16/.
- Owners: conduit.py is released to melder_1 at this closure (NOTICE M0-177); spellbook.py and
  transfer_of_ownership.py are melder_1's.
- Limits: the whole tree was not run (the suites run are in the 13:28:26Z and 15:23:08Z notes). "version id" text
  outside this lane is left as written: the release note's 0.2.8229 lookup sections (lines 46 and 656) and the
  docstrings of `Spellbook._get_owned_spell` and `Conduit._deactivate_borrowed_spell`.
- Follow-ups: TASK-2026-10-16-notch_seam_checks_incoming_before_parking (backlog; the seam's park-first order, in
  spellbook.py); the INTENT wording in spellbook.py's `_notch_spell` / `_apply_notch` docstrings, told to melder_1.
- Next: none in this lane; the rebuild ran last and both checks are OK (Notes, 2026-10-16T16:11:30Z); melder_1 lands D3
  above 0.2.8249.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
