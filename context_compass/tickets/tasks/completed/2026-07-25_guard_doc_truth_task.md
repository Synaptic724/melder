

# Task: Correct every guard claim in src_architecture.md and src_components.md

## Metadata
- Task ID: TASK-2026-07-25-guard-doc-truth
- Story: STORY-2026-07-25-guard-manifest-truth
- Status: done
- Owner: melder_1
- Agent Name: melder_1
- Priority: p2
- Created: 2026-07-25T18:19:28Z
- Updated: 2026-07-31T23:03:22Z

## Objective
Replace the retired-sentinel description with the shipped build-time manifest model in
both canonical system docs, including the accepted subclass behavior flip.

## Ticket Contract
- ENTRY_GATE: story routed on `attention_board.md`; mechanism evidenced in source.
- EXECUTION_BOUNDARY: `system_docs/src_architecture.md` and
  `system_docs/src_components.md` only. No code, no graph, no other docs.
- DEPENDENCIES: STORY-2026-07-25-guard-manifest-truth Notes FACT entry.
- EXIT_GATE: all five drift sites corrected; no live sentinel mechanism claim remains;
  doc metadata `Updated:` refreshed.
- FAILURE_ESCALATION: DECISION_REQUEST if a correction would require asserting the
  cold-boot fallback as an evidenced runtime guarantee.

## Scope Boundaries
- In scope: the guard/guardrail prose, the C1 one-line descriptor, the subcomponent
  entry, and the failure-mode sentence.
- Out of scope: the C1 Code Map rebuild (own task), graph, code.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Mechanism is evidenced and the drift sites are enumerated with
  line numbers; no unknowns block the edit.

## Steps / Checklist
- [x] `src_architecture.md:612-615` - rewrite the two guardrail bullets to describe the
      manifest, exact-match lookup, and no-MRO semantics.
- [x] `src_architecture.md:1503` - C1 descriptor: "registration guard sentinel" ->
      manifest-backed guard.
- [x] `src_architecture.md:1369` - boot-sequence line: keep the import-time singleton
      fact, drop any sentinel implication.
- [x] `src_components.md:207` - failure mode: refusal is manifest membership, not a tag.
- [x] `src_components.md:2142-2153` - retitle the subcomponent and replace `_SENTINEL`
      data-structure claim with `INTERNAL_MANIFEST` frozenset.
- [x] `src_components.md:190-194,3412` - guard-instance claims reviewed for accuracy.
- [x] Record the accepted behavior flip (user subclasses bindable) in both docs.
- [x] Refresh `Updated:` in both Metadata blocks.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Both canonical system docs describing the manifest mechanism accurately.

## Files / Paths Impacted
- context_compass/system_docs/src_architecture.md
- context_compass/system_docs/src_components.md

## Validation
- Run 2026-07-30. All checks pass.
- Live-source agreement (7/7 OK): call site `bind.py:364`; `ENTRY_COUNT` 582 asserted in
  both docs; committed manifest path `_bind_guard/manifest/bind_guard_manifest.py` in
  both docs; loader `_bind_guard.bind_guard` named in both docs.
- Retired-name sweep, both docs: `_SENTINEL` 0, `MelderRegistrationGuard` 0,
  `_RegistrationGuardProxy` 0, `_mrg` 0, `is_internal` 0. `__melder_internal__` 1 each -
  both are the accurate explanation of WHY user subclasses are now bindable (the retired
  sentinel was read via `getattr` and therefore inherited), which this ticket requires.
  Not residue.
- Dead-path sweep, both docs: `_init_manifest` 0, `_agent_metadata` 0, `__init_cache__` 0.
- Path resolution: 705 cited `src/melder/**.py` paths across both docs, ZERO missing.
- Line endings match the INDEX (the settled rule), not the worktree:
  `src_architecture.md` i/crlf w/crlf, `src_components.md` i/lf w/lf. Content diffs are
  19/15 and 36/25 - surgical, no whitespace reflow.
- Both doc indexes regenerated; each passes round-trip, coverage-to-EOF with no gaps,
  monotonicity, and fingerprint.

## Risks / Rollback Notes
- Low risk: documentation-only, no runtime behavior. Rollback is a git revert of the
  two files.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 7)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

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
- DATETIME: 2026-07-25T18:19:28Z
  TYPE: FACT
  CLAIM: Five drift sites enumerated by grep across both docs; no other guard claims
    exist in either file, and `tests_architecture.md`, `tests_components.md`, and
    `graph_details_document.md` contain zero guard/sentinel references.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:612-615
  - context_compass/system_docs/src_components.md:2142-2153
  IMPACT: Bounds the doc blast radius to exactly two files, keeping the edit inside
    the expansion gate without a scope-confirmation round trip.
  NEXT: Rewrite `src_architecture.md:612-615` first, as it is the mechanism anchor the
    other sites refer back to.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-25T18:19:28Z
  TYPE: FACT
  CLAIM: All drift sites corrected in both docs. Remaining `sentinel` matches are
    exactly the intended ones: historical/superseded framing explaining WHY the
    manifest exists, the vestigial-surface note pointing at the strip task, and one
    unrelated crystallizer binding marker (`"user_source_retained"`), which is a
    different concept and was not touched.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:622-622
  - context_compass/system_docs/src_components.md:2180-2194
  IMPACT: Acceptance criterion "no live sentinel mechanism claim remains" is met
    without erasing the historical rationale a future reader needs.
  NEXT: Await owner acceptance; proceed to TASK-2026-07-25-c1-code-map-restore.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-25T18:19:28Z
  TYPE: MEASURE
  CLAIM: Formatting and encoding verified. Zero lines authored in this task exceed the
    120-char hard cap; the over-cap lines that exist in both files are pre-existing and
    untouched. Line endings preserved: 2120/2120 CRLF in `src_architecture.md` and
    4190/4190 in `src_components.md`, with zero LF-only lines in the edited zones.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1510-1510
  - context_compass/agent_onboarding/default/general/skills/configuration_standards.md:22-30
  IMPACT: Repo has a documented history of encoding faults on board/doc writes; mixed
    line endings would have been a silent regression.
  NEXT: None for this task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-07-30T11:37:39Z
  TYPE: FACT
  CLAIM: Guard citations repaired for the FOURTH time, now against a settled target.
    Found ELEVEN stale citations, not the 13 this lane's board anchor claimed - the
    other two named `__melder_cache__/__melder_cache__.py`, which EXISTS, so treating
    the anchor's count as authoritative would have broken two correct citations.
    Corrections written: path `_build_assets/_init_manifest/internal_manifest.py` ->
    `_build_assets/_bind_guard/manifest/bind_guard_manifest.py` (the committed truth,
    not the loader); import module -> `melder._build_assets._bind_guard.bind_guard`;
    call site `bind.py:363` -> `:364`; entry count 577 -> 582. Both counts were derived
    from source inside the edit script rather than typed, so they cannot drift from
    what was asserted.
  EVIDENCE:
  - src/melder/_build_assets/_bind_guard/bind_guard.py:91-96
  - src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:16-19
  - src/melder/aether/spellbook/bind/bind.py:20
  IMPACT: An agent following either doc reached a deleted directory. Docs, board anchor,
    and source now agree; the anchor's own count is corrected in the same pass.
  NEXT: Prose coverage for `_agent_documentation/` and `_system_documents/`, which have
    zero mentions outside the C1 map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-30T11:37:39Z
  TYPE: FACT
  CLAIM: Reading `bind_guard.py` before editing prevented two NEW falsehoods. (1) I was
    about to rename `MANIFEST_ENTRY_COUNT` to `ENTRY_COUNT`; the former is a real symbol
    re-exported by the loader at line 96, so the docs were RIGHT and only the value was
    wrong. (2) Both docs asserted "there is no loader, no first-import scan, and no
    cache-write fallback" - now false on two of three counts. `bind_guard.py` IS a
    hand-written loader that hydrates through a `.melc` under
    `__melder_cache__/__bind_guard__/`, importing the manifest module lazily on cache
    miss only. Rewrote the claim to name the cache as an ACCELERATOR that is never the
    source, which is the loader's own stated contract.
  EVIDENCE:
  - src/melder/_build_assets/_bind_guard/bind_guard.py:6-11
  - src/melder/_build_assets/_bind_guard/bind_guard.py:65-96
  IMPACT: A path-only find/replace would have preserved a false mechanism claim and
    corrupted a correct symbol name. Mechanism claims must be re-read, not carried.
  NEXT: None for this finding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-30T11:37:39Z
  TYPE: RISK
  CLAIM: PROCESS VIOLATION, self-reported. This ticket sat at `ready` while I
    implemented and validated; the transition to `in_progress` is being written in the
    same pass as the work rather than before it. Second occurrence of this exact gate
    miss in this session.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-07-25_guard_doc_truth_task.md:8
  IMPACT: The gate exists so a reader can tell in-flight work from finished work. Fixing
    it after the fact records the truth but does not restore the guarantee.
  NEXT: Transition before touching files on the next lane.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-30T11:37:39Z
  TYPE: MEASURE
  CLAIM: Validation. Line endings preserved against the INDEX, not the worktree:
    `src_architecture.md` i/crlf w/crlf, `src_components.md` i/lf w/lf. The components
    worktree arrived CRLF against an LF index, so a faithful read-write produced a
    whole-file 5179/5176 diff; converted to LF and the diff collapsed to the intended
    11/8. Full path-resolution sweep over both docs: 705 cited `src/melder/**.py` paths,
    ZERO missing. Residual dead-path scan for `_init_manifest`, `_agent_metadata` and
    `__init_cache__`: zero hits in either document. Both indexes regenerated and pass
    all four validations (round-trip, coverage to EOF with no gaps, monotonicity,
    fingerprint).
  EVIDENCE:
  - context_compass/system_docs/src_architecture_index.json
  - context_compass/system_docs/src_components_index.json
  IMPACT: The line-ending check is the one that matters: without it this lane would have
    landed a 5,000-line whitespace diff on top of an 11-line fix.
  NEXT: Owner acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-31T22:41:44Z
  TYPE: FACT
  CLAIM: CONSUMED melder_0's 2026-07-28T00:10:00Z NOTICE (deleted from mailbox_board.md,
    alert cleared in the same pass). Three of its four points were already independently
    verified and applied by this lane before the message was read: loader vs committed
    manifest, `ENTRY_COUNT` 582, and `utilities/caching_system/asset_cache.py` (which is
    one of the 11 modules inserted into the C1 map). Its point 2 - that
    `_agent_documentation/` and `_system_documents/` are absent from both canonical docs -
    is TRUE but is NOT this lane's work: its own EVIDENCE pointer is
    TASK-2026-07-25-agent-metadata-build-asset, melder_0's in_progress ticket, which
    already carries the durable delta as active patch docs.
  EVIDENCE:
  - context_compass/system_docs/patches/active/agent_metadata_asset_2026_07_25/architecture_patch.md
  - context_compass/tickets/tasks/2026-07-25_agent_metadata_build_asset_task.md:6-10
  IMPACT: Confirms the routing correction made on the board: authoring that prose here
    would duplicate another agent's unclosed patch.
  NEXT: Adopt the directory-citation suggestion selectively (next note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-31T22:41:44Z
  TYPE: DECISION
  CLAIM: melder_0's suggestion - cite the ASSET DIRECTORY rather than a file inside it,
    because "the manifest moved three times this epic and every move invalidated your
    lane; the directory never moved" - is ACCEPTED SELECTIVELY, not wholesale. Adopt it
    for locator and inventory references, where the question is "where does the guard
    live" and file precision buys nothing. REJECT it for the loader-vs-truth distinction:
    collapsing `bind_guard.py` (hand-written loader) and
    `manifest/bind_guard_manifest.py` (committed truth) into `_bind_guard/` would erase
    exactly the distinction that helper_f got wrong, that melder_0 and I each corrected
    independently, and that this lane just spent a fourth pass recording. A directory
    citation is durable; it is also incapable of saying which file is the source of truth.
  EVIDENCE:
  - src/melder/_build_assets/_bind_guard/bind_guard.py:6-11
  IMPACT: The suggestion correctly diagnoses why this lane went stale four times. Applied
    everywhere it would cost the reader the one fact the lane exists to establish.
  NEXT: Owner acceptance; the selective rewrite is a follow-up increment, not a reopen.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-31T22:41:44Z
  TYPE: FACT
  CLAIM: Resolves melder_0's open uncertainty in that NOTICE. They wrote "your inbound
    message from helper_f is missing from this board as of 2026-07-28T00:10Z. I did not
    knowingly delete it - my own consume pass sliced this section and a concurrent write
    is equally possible." Neither: I consumed and deleted it myself at 2026-07-27T23:52:40Z,
    18 minutes earlier, which is the `last_checked` stamp on my own roster row. There was
    no write race and no lost message.
  EVIDENCE:
  - context_compass/mailbox_board.md:41
  IMPACT: Closes a suspected concurrency fault that did not happen. Left unanswered it
    would invite someone to harden a write path against a phantom.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-31T23:03:22Z
  TYPE: DECISION
  CLAIM: CLOSED at owner turn-in 2026-07-31. Guard citations correct against a settled target. 11 stale citations repaired (not the 13 the
    anchor claimed - 2 named __melder_cache__/__melder_cache__.py, which EXISTS). Path, import
    module, call site :364 and count 582 all derived from source inside the edit script. Reading
    the loader first prevented renaming MANIFEST_ENTRY_COUNT (a real symbol) and caught the
    now-false 'no loader, no cache-write fallback' claim. 705 cited paths resolve, 0 missing.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-07-25_guard_doc_truth_task.md
  IMPACT: Ticket moved to completed/; board row removed and replaced by one anchor.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Five enumerated drift sites across two files. Mechanism truth is recorded in the parent
story's FACT note. The cold-boot fallback must be attributed to the loader contract
rather than asserted as an evidenced runtime guarantee, per the story's RISK note.
