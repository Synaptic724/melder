# Story: book_teardown_leaves_parked_versions_uncleaned - a Book's teardown retires its parked versions too

- Completed: 2026-10-19T01:32:05Z
- Summary: landed and notched 0.2.8260 - a Spellbook's teardown retires every parked version with the local
  teardown `cleanup_spell`'s parked branch runs and cleans every index only parked versions hold
  (`_cleanup_spells`), so no version of a dead Book reads live or refuses its own cleanup. S7 tests green with
  the GIL off and on, the whole tree as the MEASURE note records; release note section "A Spellbook's teardown
  cleans its parked versions too"; system documents and graph; rebuilt last. Turned in after the landing, on
  the owner's word on the edit (2026-10-19).

## Metadata
- Story ID: STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned
- Epic: EPIC-2026-10-17-correctness_defects
- Status: done
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p3
- Created: 2026-10-17T21:13:35Z
- Updated: 2026-10-19T01:36:42Z

## User Narrative
As an agent who staged and separated versions in a Book and then tore the Book down, I want every version the Book
owned - the parked ones and an index only they hold included - retired with it, so that no version of a dead Book
still reads as live or refuses its own cleanup.

## Value / MRP Alignment
Melder's infrastructure cleans up its own state (owner ruling, src_architecture "Runtime Model"); a Spell and its
SpellIndex are Melder's records of a version. Today the parked versions of a torn-down Book stay uncleaned, and
`Spell.cleanup()` on one raises "Spellbook has already been cleaned." - a record that reads as live and can never be
retired.

## Ticket Contract
- ENTRY_GATE: the owner schedules the story and assigns an agent; melder_1 has released spellbook.py (its rule-2
  hold); an active board row; a component patch for the Book teardown.
- EXECUTION_BOUNDARY: `Spellbook._cleanup_spells` (or the step of `_cleanup_components` that clears
  `_inactive_spells`): the local teardown of every parked version, as the parked branch of `_dispose_spell` runs it
  (`_spellbook_cleanup` set, then `Spell.cleanup()`), and `SpellIndex.cleanup()` of every index only parked versions
  hold, best-effort and logged like the active loop; regression tests; the system documents (the cleanup sequence,
  the Spellbook Core component) with their indexes and the graph; the release note; one notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links); melder_1's release of
  spellbook.py (TASK-2026-10-16-recheck_contract_consumers_when_provider_changes).
- EXIT_GATE: probe T2 and T3 show French and the minted index cleaned after teardown and `French.cleanup()` returning;
  T1, T4 and T5 unchanged; regression tests pass with the GIL off and on; docs, notch and the rebuild with both
  checks OK.
- FAILURE_ESCALATION: CONFLICT while spellbook.py is held; DECISION_REQUEST if retiring a parked version turns out to
  need more than its local teardown.

## Requirements (Functional)
- Book teardown cleans every version the Book owns, active and parked, and every SpellIndex it owns, including an
  index only parked versions hold.
- A parked version's teardown is local: it is on no resolution map, in no lineage registration and in no frame lookup
  of its own, so only `Spell.cleanup()` (with `_spellbook_cleanup` set) and its index's cleanup run.
- After the teardown, `Spell.cleanup()` on any of the Book's versions returns without raising.

## Requirements (Non-Functional)
- The lock order stays: spell locks are taken under the Book lock, as the active loop takes them; nothing new runs
  user code.

## Scope Boundaries
- In scope: parked versions and parked-only indexes at Book teardown.
- Out of scope: frame claims (the two signature stories), borrowers' copies (the ward's teardown), the record (it
  already evicts the Book's custody in both locations and its index crystals).

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: landed at 0.2.8260 and turned in after the landing (the owner's word on the edit, DECISION
  note of 2026-10-19T01:00:17Z; closure is routine once criteria and tests are met). Before that: ready ->
  in_progress when the owner scheduled the story for melder_1 (chat 2026-10-18 and 2026-10-19; DECISION
  note).

## Dependencies / Related Work
- STORY-2026-10-17-notch_moves_signature_by_incoming_key_only: the same probe's case T4 (a claim that outlives the
  Book) belongs there.

## Tasks (Implementation Checklist)
- [x] Task: patch docs for the Book teardown (linked; PLAN note); the owner's approval (DECISION note).
- [x] Task: the fix with symptom-named regression tests (red on 0.2.8259, green at 0.2.8260; MEASURE notes),
  docs, notch and the rebuild last (the rebuild follows this closure, as the contribution guide orders).
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- After its root's teardown, a Book's parked version (on a shared index, or alone in a minted one) reads cleaned,
  its parked-only index reads cleaned, and `cleanup()` on the version returns.
- An active-only Book and a Book with managed versions tear down as today.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_book_teardown_cleans_its_parked_versions` and
  `test_book_teardown_cleans_an_index_only_parked_versions_hold`; GIL off and on; the probe re-run.

## UX / API / Data Notes
- No public signature changes. Visible today: `spell.cleaned` is False for a parked version of a torn-down Book, and
  `spell.cleanup()` raises RuntimeError "Spellbook has already been cleaned.".

## Risks / Mitigations
- Cleaning a parked Spell drops its factory and any compiled artifact; nothing can meld it once its Book is gone, so
  nothing is lost.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- none.

## Decision Log
- 2026-10-17T21:13:35Z: filed under EPIC-2026-10-17-correctness_defects from sweep A7 (Notes).
- 2026-10-19T00:51:08Z: scheduled for melder_1 on the owner's order, after S4 (DECISION note).
- 2026-10-19T01:00:17Z: the owner's word on the edit, "Go ahead" (DECISION note).
- 2026-10-19T01:32:05Z: landed at 0.2.8260 and turned in (MEASURE and FACT notes).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_book_teardown_parked.py (cases T1-T3, T5)
  - artifacts/correctness_defects_20261017/runs/probe_book_teardown_parked_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_book_teardown_parked_gil1.txt
  - artifacts/book_teardown_parked_20261019/ (melder_1's lane: re-runs, scripts, notes)
  - system_docs/patches/completed/book_teardown_parked_2026_10_19/ (architecture and Spellbook component patch;
    promoted at landing, archived at turn-in)
- DISPOSITION: retain_as_reference (the probe, its runs and the lane folder); promote_to_documentation (the
  patch)
- CLEANUP_TRIGGER: the probe was re-run at the fix and is kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - parked versions and parked-only indexes at Book teardown
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probe); filed 2026-10-17T21:13:35Z.
- Contributions: melder_1 (synaptic_python_developer) - the re-verification on 0.2.8259, edits A-C and their
  prototype, the patch docs book_teardown_parked_2026_10_19, the regression tests, the system documents, the
  graph prose and the release note (2026-10-19; Notes).
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none (self-checks only; closure on the owner's word on the edit, DECISION note of
  2026-10-19T01:00:17Z)

## Notes
- DATETIME: 2026-10-17T21:13:35Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect, read whole and proven on 0.2.8252. `Spellbook._cleanup_spells` walks `_spells` - the active
    version of each index - unregistering, cleaning each Spell and its index; `_cleanup_components` then clears
    `_inactive_spells` without cleaning one of them, and an index only parked versions hold is never reached. The
    parked branch of `_dispose_spell` shows the teardown a parked version needs (`_spellbook_cleanup` set, then
    `Spell.cleanup()`). Afterwards a direct `Spell.cleanup()` routes to the Book (`_direct_removal_route`,
    `cleanup_and_remove_spell`), which raises "Spellbook has already been cleaned.". Probe T2: after the root's
    teardown English is cleaned and French, parked on its index, is not; `French.cleanup()` raises. T3: French
    separated into its own minted index - neither French nor that index is cleaned. T1 (active only) and T5 (the
    pools of an active and a parked managed version, both unregistered) are right. Identical with the GIL off and on.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:405-556
  - src/melder/aether/spellbook/spellbook.py:557-600
  - src/melder/aether/spellbook/spellbook.py:602-748
  - src/melder/aether/spellbook/spellbook.py:4422-4563
  - src/melder/aether/spellbook/spell.py:581-723
  - src/melder/aether/spellbook/spell.py:725-763
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_book_teardown_parked.py:1-231
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_book_teardown_parked_gil0.txt:1-30
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_book_teardown_parked_gil1.txt:1-30
  IMPACT: A dead Book's parked versions read as live and can never be retired.
  NEXT: The owner's scheduling, after melder_1 releases spellbook.py; then patch docs for the Book teardown.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T00:51:08Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's order puts this story with melder_1 now. Of the correctness fixes he gave melder_1 (chat
    2026-10-18: "do the ones without open questions please" - S9, S4 and S7 - with "go over them again before you
    make changes and let him know"), S9 landed at 0.2.8256 and S4 at 0.2.8259; on S4's report he said "lets move on"
    (chat 2026-10-19). S8 stays on his hold. So S7 is re-verified on 0.2.8259 and its teardown path re-read whole
    before any change; the patch (a component patch for the Book teardown) and the exact edits go to the owner
    before the first src edit; spellbook.py is claimed from melder_0 by message (M1-43), nothing edited before his
    answer. S4 touched the same teardown (the root's teardown now unregisters parked versions' indexes), so the
    probe is re-read against it.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:908-928
  - context_compass/tickets/stories/completed/2026-10-17_minted_index_missing_from_frame_registry_story.md:1-12
  - src/melder/aether/spellbook/spellbook.py:2695-2736
  IMPACT: The ENTRY_GATE's scheduling and assignment are met; the board row exists; the patch, the owner's word
    on the edits and the file claim remain before any src edit.
  NEXT: Re-run probe T1-T5 on 0.2.8259 with the GIL off and on; re-read Spellbook teardown whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T00:58:59Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The defect holds on 0.2.8259, re-verified before any change as the owner asked. melder_0's probe, copied
    with the 0.2.8253 rename (`find_spell_by_id` -> `find_spell_by_spell_id`) and T5's parked version made its own
    class (one object is one spell since 0.2.8257), ran on Python 3.14.7t; with the GIL on the output equals the
    GIL-off run apart from the GIL-mode warning. T2: after the root's teardown English and the shared index are
    cleaned, French (parked on it) is not, and `French.cleanup()` raises "Spellbook has already been cleaned.". T3:
    French alone in the index `remove_from_spell_index` minted - neither French nor that index is cleaned. T1
    (active only) and T5 (both managed versions' pools unregistered) are right; T4 belongs to the notch-signature
    story and is unchanged. S4's teardown edit (0.2.8259) changed none of it.
  EVIDENCE:
  - context_compass/artifacts/book_teardown_parked_20261019/probes/probe_book_teardown_parked_0_2_8259.py:1-242
  - context_compass/artifacts/book_teardown_parked_20261019/runs/probe_book_teardown_parked_0_2_8259_gil0.txt:1-30
  - context_compass/artifacts/book_teardown_parked_20261019/runs/probe_book_teardown_parked_0_2_8259_gil1.txt:1-34
  IMPACT: The acceptance criteria stand as written.
  NEXT: Read the Book teardown whole (FACT note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T00:58:59Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The Book teardown, read whole on 0.2.8259. `Spellbook.cleanup` runs `_cleanup_components` under the Book
    lock: Bind's retirement, the risk-manager entry, the phase scheduler, the record's eviction of the whole Book,
    Nexus, then `_cleanup_spells`, which walks `_spells` (index -> active Spell) - unregister the index from
    SpellSystemStates, set `_spellbook_cleanup`, `Spell.cleanup()`, `SpellIndex.cleanup()` - and then
    `_inactive_spells` is cleared, never cleaned. A parked version's retirement is local, as the parked branch of
    `_dispose_spell` shows (`_spellbook_cleanup` set, then `Spell.cleanup()`): `Spell.cleanup` with that flag set skips
    `_direct_removal_route` and tears down only the spell's own fields (it never touches the index object), and
    `SpellIndex.cleanup` is idempotent and lock-guarded. A parked version holds no lineage registration (only active
    selections are registered), no resolution-map entry and no frame lookup of its own, and since 0.2.8259 the root's
    teardown unregisters its index from the frame before the Book is cleaned. So the fix is one loop after the
    active one: retire each parked version locally and clean each index no active member holds.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:370-397
  - src/melder/aether/spellbook/spellbook.py:405-555
  - src/melder/aether/spellbook/spellbook.py:557-600
  - src/melder/aether/spellbook/spellbook.py:4503-4651
  - src/melder/aether/spellbook/spellbook.py:2695-2736
  - src/melder/aether/spellbook/spell.py:614-762
  - src/melder/aether/spellbook/spell.py:764-801
  - src/melder/aether/spellbook/bind/spell_index.py:118-137
  IMPACT: The change is one module (spellbook.py), no new lock edge (spell and index locks under the Book lock, as the
    active loop takes them), no persisted or cached shape.
  NEXT: The patch docs, the red tests and a prototype in a /tmp mirror (MEASURE note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T00:58:59Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch book_teardown_parked_2026_10_19 (architecture and a Spellbook component patch; no code-description
    patch - no state machine, gate or rollback semantics change) mapped to steps and tests. Edit (apply_s7.py, one
    module): (A) `_cleanup_spells`' docstring names the parked loop and its threading; (B) after the active loop,
    each parked version's index is read while the version is live and noted when no active member holds it, the
    version is retired locally (`_spellbook_cleanup`, `Spell.cleanup()`), then each noted index is cleaned - every
    step best-effort and logged; (C) `_cleanup_components`' docstring names them. Tests (new integration file, 8
    cases): six regressions red on 0.2.8259 - a parked version on a shared index and alone in its own index, with the
    frame kept and collapsed, a version parked before conjure under a direct `Spellbook.cleanup()`, a parked managed
    version's Spell - and two controls (active only; a parked version disposed first). In a /tmp mirror with the
    edit (preview 72 lines): 8 passed, the GIL off and on; probe T2 and T3 fixed, T1, T4 and T5 unchanged. Then the
    whole tree, docs, graph, the release note, the next notch (0.2.8260 unless someone notches first), closure and
    the rebuild last. No src edit before the owner's word.
  EVIDENCE:
  - context_compass/system_docs/patches/active/book_teardown_parked_2026_10_19/architecture_patch.md:1-44
  - context_compass/system_docs/patches/active/book_teardown_parked_2026_10_19/component_patch_spellbook_book_teardown.md:1-30
  - context_compass/artifacts/book_teardown_parked_20261019/scripts/apply_s7.py:1-141
  - context_compass/artifacts/book_teardown_parked_20261019/runs/s7_preview_0_2_8259.diff:1-72
  - tests/integration/melder/spellbook/test_book_teardown_retires_parked_versions_integration.py:1-330
  - context_compass/artifacts/book_teardown_parked_20261019/runs/red_s7_0_2_8259_gil0.txt:1-32
  - context_compass/artifacts/book_teardown_parked_20261019/runs/green_s7_mirror_gil0.txt:1-2
  - context_compass/artifacts/book_teardown_parked_20261019/runs/green_s7_mirror_gil1.txt:1-10
  - context_compass/artifacts/book_teardown_parked_20261019/runs/prototype_s7_probe_book_teardown_parked_gil0.txt:1-30
  IMPACT: The patch gate's mapping is recorded; the edit waits for the owner's word only (melder_0 holds no src file,
    M0-207).
  NEXT: The owner's word on the edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T00:58:59Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-207 from melder_0 (2026-10-19T00:49:20Z, re M1-42), consumed. EPIC-2026-10-18-spell_identity_is_the_code
    is turned in on the owner's word (S1 and S2 landed; S3-S5 parked in the backlog beside S6, its S4 taking M4b and
    M5b); melder_0 edits neither spellbook.py nor spell.py and names S7 as melder_1's next, so S7's file claim (M1-43)
    is met. Its note that `_system_documents` was stale after melder_2's wording fix (M2-27) is settled: melder_1
    rebuilt in the repository before staging the commit, and both checks read OK.
  EVIDENCE: context_compass/artifacts/spell_identity_20261018/runs/turn_in/asset_check_after_wording.txt:1-8
  IMPACT: Nothing but the owner's word stands between the patch and the edit.
  NEXT: The owner's word on the edit.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-19T01:00:17Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's word (chat 2026-10-19): asked "Go ahead with S7's fix as described (one extra cleanup loop at
    the end of a Spellbook's teardown, in spellbook.py)?", he chose "Go ahead". The edit lands as the PLAN note maps
    it (apply_s7.py, edits A-C) at the next notch, 0.2.8260, then the whole tree, the documents, the graph, the
    release note, the notch, the closure and the rebuild last.
  EVIDENCE: context_compass/artifacts/book_teardown_parked_20261019/runs/s7_preview_0_2_8259.diff:1-72
  IMPACT: The ENTRY_GATE is met in full; the src edit is authorized.
  NEXT: Apply A-C to the repository and run the S7 tests there, the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T01:16:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-208 from melder_0 (2026-10-19T01:07:36Z, ACK of M1-43), consumed. spellbook.py and spell.py are
    melder_1's for S7; melder_0 holds no edit in either and has no src/ lane open. conduit.py,
    spellbook_validation_error.py and change_control_manager.py stay with melder_0 while S8 is on hold (a claim by
    mailbox first if S7 needed one; it needs none). spellbook.py and spell.py go back to melder_0 when S7 turns in.
  EVIDENCE: context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:1053-1071
  IMPACT: The file claim behind the 0.2.8260 edit is confirmed in writing; S7's closure hands both files back.
  NEXT: Record the landing's validation (MEASURE note), then the system documents.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-19T01:17:45Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The edit is in the repository as the PLAN note maps it (apply_s7.py, edits A-C, notch text 0.2.8260;
    spellbook.py 7858 -> 7903 lines; `__version__` stays 0.2.8259 until the turn-in's notch). The S7 tests pass there,
    8 passed with the GIL off and on. The whole tree in the VM mirror, seven shards with the GIL off and on: every
    test passes except S8's 18 red tests, held with the story (7 in test_spellbook_validation_error_preface.py, 11 in
    test_notch_refused_at_commit_integration.py), failing as on 0.2.8259; integration/spellbook reads 678 passed.
    Probe T1-T5 on the landed tree is byte-equal to the prototype's run: T2 and T3 fixed (French, the shared index
    and the minted index cleaned; `French.cleanup()` returns), T1, T4 and T5 unchanged.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:405-422
  - src/melder/aether/spellbook/spellbook.py:559-645
  - context_compass/artifacts/book_teardown_parked_20261019/runs/apply_s7_repo_0_2_8260.txt:1-2
  - context_compass/artifacts/book_teardown_parked_20261019/runs/green_s7_repo_0_2_8260_gil0.txt:1-2
  - context_compass/artifacts/book_teardown_parked_20261019/runs/green_s7_repo_0_2_8260_gil1.txt:1-10
  - context_compass/artifacts/book_teardown_parked_20261019/runs/full_tree_0_2_8260/unit_gil0.txt:1-168
  - context_compass/artifacts/book_teardown_parked_20261019/runs/full_tree_0_2_8260/integ_aether_gil0.txt:1-71
  - context_compass/artifacts/book_teardown_parked_20261019/runs/full_tree_0_2_8260/integ_spellbook_gil0.txt:1-11
  - context_compass/artifacts/book_teardown_parked_20261019/runs/landed_0_2_8260_probe_book_teardown_parked_gil0.txt:1-30
  - context_compass/artifacts/book_teardown_parked_20261019/runs/landed_0_2_8260_probe_book_teardown_parked_gil1.txt:1-34
  IMPACT: The EXIT_GATE's probe and test conditions are met; the documents, the graph, the notch, the release note,
    the closure and the rebuild remain.
  NEXT: The system documents (citation remap first, then the anchored edits and the indexes).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T01:28:16Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The documents and the graph carry S7. Citations: every numeric `spellbook.py:N` past the edit moved 45 lines
    and was remapped line by line against the pre-edit copy (11 lines in src_architecture, 14 in src_components;
    handoff history left as written). src_architecture: the cleanup sequence, a new operational invariant, a fixed
    failure mode, the 0.2.8256 invariant's "Not changed", the code map (7903 lines) and a handoff entry;
    src_components: Spellbook Core's cleanup line, a new invariant, the 0.2.8256 invariant's teardown sentence, the
    code map and a handoff entry; tests_components: the Spellbook Integration Cluster's new module (8 tests), a key
    file and its code-map record, counts recounted (integration 177 of 184, spellbook tree 54, 858 test modules,
    key-file union 274 = code-map records); tests_architecture: the inventory and a handoff entry. The four indexes
    are regenerated and their checks read OK; the citation check reports only the two bare file names in
    src_components' handoff history, as at 0.2.8259. The graph: extract --strict (593 descriptors, none skipped),
    Spellbook's 27 responsibilities re-read against the edited source and one added (the teardown's parked loop),
    accepted, assembled (28191 lines) and checked OK. The release note's example runs as written, GIL off and on.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1094-1095
  - context_compass/system_docs/src_architecture.md:1159-1177
  - context_compass/system_docs/src_architecture.md:2412-2418
  - context_compass/system_docs/src_components.md:746-759
  - context_compass/system_docs/tests_components.md:1793-1800
  - context_compass/system_docs/src_graph.md:15888-15888
  - context_compass/artifacts/book_teardown_parked_20261019/runs/remap_s7_citations_apply.txt:1-79
  - context_compass/artifacts/book_teardown_parked_20261019/runs/land_s7_docs_apply.txt:1-5
  - context_compass/artifacts/book_teardown_parked_20261019/runs/citation_check_0_2_8260.txt:1-4
  - context_compass/artifacts/book_teardown_parked_20261019/runs/graph_extract_0_2_8260.txt:1-46
  - context_compass/artifacts/book_teardown_parked_20261019/runs/graph_assemble_check_0_2_8260.txt:1-4
  - context_compass/artifacts/book_teardown_parked_20261019/runs/release_note_probe_0_2_8260_gil1.txt:1-5
  IMPACT: The documents describe the landed behaviour; the notch, the release-note entry, the closure and the
    rebuild remain, in that order.
  NEXT: Notch 0.2.8259 -> 0.2.8260 (read at that moment), then the release-note section.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T01:30:28Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Notched 0.2.8259 -> 0.2.8260, read at that moment (no other lane had notched). The running release note's
    header reads 0.2.8260; its new section "A Spellbook's teardown cleans its parked versions too" stands before
    "Packaging and documentation", its example byte-equal to the probe that ran as written with the GIL off and on;
    the packaging list gains the system documents' bullet and its rebuild line names 0.2.8260.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-1
  - release_docs/next_version_release.md:1049-1082
  - release_docs/next_version_release.md:1214-1217
  - context_compass/artifacts/book_teardown_parked_20261019/probes/probe_release_note_s7.py:1-25
  - context_compass/artifacts/book_teardown_parked_20261019/runs/release_note_probe_0_2_8260_gil0.txt:1-1
  IMPACT: The turn-in's notch and release-note steps are done; the closure and the rebuild remain.
  NEXT: The closure (story to completed/, board and artifact sync, the patch archived), then the rebuild last.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-19T01:36:42Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rebuilt last for 0.2.8260. rebuild_s4_assets.py ran the asset runner in a /tmp mirror (the agent
    documentation, bind-guard and system-documents manifests at v0.2.8260, 630 bind-guard entries) and copied the
    eight changed files back byte-equal; the mirror's src/ and documents equal the repository's. In the repository:
    the runner's --check OK for all three assets; llm_support/_builder.py --include-untracked rewrote src (585
    files), tests (1140) and other (409), and its --check OK for all three; the runner's --check OK again. No
    .git/index.lock. M1-44 sent to melder_0 (the notch, the files back).
  EVIDENCE:
  - context_compass/artifacts/book_teardown_parked_20261019/runs/rebuild_assets_0_2_8260_mirror.txt:1-13
  - context_compass/artifacts/book_teardown_parked_20261019/runs/rebuild_asset_check_0_2_8260.txt:1-3
  - context_compass/artifacts/book_teardown_parked_20261019/runs/rebuild_llm_0_2_8260.txt:1-4
  - context_compass/artifacts/book_teardown_parked_20261019/runs/rebuild_llm_check_0_2_8260.txt:1-3
  - context_compass/artifacts/book_teardown_parked_20261019/runs/rebuild_asset_check_after_llm_0_2_8260.txt:1-3
  IMPACT: S7 is landed, documented, notched and rebuilt; nothing is owed but the owner's signed commit.
  NEXT: none for S7; S8 waits for the owner's word.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Closure Confirmation
- [x] Work walkthrough shared with user (the landing report, chat 2026-10-19, sent with this turn-in)
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: a Spellbook's teardown retires its parked versions and the indexes only they hold (Requirements).
  Defect proven on 0.2.8252 and re-verified on 0.2.8259 (Notes); probe and runs in Artifact Links.
- State: done (melder_1; turned in 2026-10-19T01:32:05Z). Landed at 0.2.8260: edits A-C in spellbook.py
  (PLAN and MEASURE notes); the S7 tests green with the GIL off and on and the whole tree as the MEASURE note
  records; the system documents with their indexes and the graph, the notch and the release-note section
  (MEASURE and FACT notes); the rebuild follows this closure.
- Open elsewhere: the claim a notch leaves on an outgoing key outlives the Book (probe T4,
  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only); S8 on the owner's hold.
- Next: none here; spellbook.py and spell.py go back to melder_0 (M1-44).

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
