# Task: Describe the notch's borrower updates as the feature they are in the system docs

## Metadata
- Task ID: TASK-2026-10-15-describe_notch_borrower_follow_as_feature
- Story: none - standalone; owner-directed documentation correction (chat 2026-10-15)
- Status: done
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-15T02:07:39Z
- Updated: 2026-10-15T10:47:22Z

- Completed: 2026-10-15T09:05:45Z
- Summary: Docs only (no notch): `src_architecture` opens with "What Melder Is (Read This First)" - not a DI
  container but a runtime agents live and build in - and the three "known limitation" passages describe
  borrowers following a notch as the feature it is; indexes, assets and bundles are current; unit_top,
  unit_build and unit_llm pass with the GIL off and on.

## Objective
Three system-document passages call the way a notch reaches borrowers a "known limitation" (a missing fan-out):
`src_architecture` Architecture Summary and Sequence: SpellIndex Mutation Entry step 6, and the `src_components`
SpellIndex Mutation Surface. The owner (chat 2026-10-15): "its not a limitation its a feature" - versions coexist by
design (MutationResearch records them, compositions pin them, several `unique` objects can live at once, one per
version), a notch moves which version is active, borrowers follow it and rebuild, and agents iterating on one object
converge on the version they want over many versions. Rewrite the three passages to describe what the code does, in
those terms. Docs only: no `src/` change, no notch.

## Ticket Contract
- ENTRY_GATE: the board row routes this task; the code path is read and recorded in Notes before any doc edit.
- EXECUTION_BOUNDARY: the three passages in src_architecture.md and src_components.md, their indexes, one packaging
  line in the running release note, the asset and bundle rebuild and checks. No `src/`, no tests.
- DEPENDENCIES: none.
- EXIT_GATE: the passages match the code; indexes, assets and bundles current (checks OK); the owner's direction
  recorded.
- FAILURE_ESCALATION: CONFLICT and stop if the code does not match the owner's description.

## Scope Boundaries
- In scope: the three passages, indexes, the release-note packaging line, the rebuild.
- Out of scope: any change to notch, contracts or MutationResearch behaviour.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner directed the correction (chat 2026-10-15: "its not a limitation its a feature").
- from_state: in_progress
- to_state: done
- transition_reason: exit gate met - the passages match the notch code, the owner's direction (the feature
  reading, the top section) is recorded, indexes, assets and bundles are current with checks OK, and the
  document, asset and bundle suites pass with the GIL off and on; routine owner-directed docs work, closed by
  its assigned agent; the commit stays the owner's.

## Steps / Checklist
- [x] Read the notch path (Conduit.notch_spell, Conduit._deactivate_borrowed_spell, ConduitWard._emit_index_notch).
- [x] Rewrite the three passages; regenerate the two indexes.
- [x] Add the packaging line; rebuild assets and bundles last; both checks OK.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- Corrected passages in src_architecture and src_components; current indexes, assets and bundles.

## Files / Paths Impacted
- context_compass/system_docs/src_architecture.md (+ src_architecture_index.md)
- context_compass/system_docs/src_components.md (+ src_components_index.md)
- release_docs/next_version_release.md (packaging line)
- src/melder/_build_assets/ manifests and payloads, llm_support/ bundles (regenerated)

## Validation
- Index checks: src_architecture (61 sections over 4250 lines) and src_components (149 over 11167) current.
- Asset check and bundle check (`--include-untracked`): three OK lines each
  (artifacts/slotted_lifetime_fixes_20261014/runs/rebuild_2026_10_15_closure.txt).
- unit_top 145, unit_build 116 and unit_llm 28 passed with the GIL off and on
  (artifacts/slotted_lifetime_fixes_20261014/runs/docs_2026_10_15_final_gil0.txt and _gil1.txt).
- Not run: the rest of the tree; nothing it reads changed.
- Recommended commands:
  - python src/melder/_build_assets/_build_asset_runner.py --check
  - python llm_support/_builder.py --check --include-untracked

## Risks / Rollback Notes
- Docs only; revert the passages and rebuild.

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
  - artifacts/slotted_lifetime_fixes_20261014/landing/notch_borrower_docs_2026_10_15.py
  - artifacts/slotted_lifetime_fixes_20261014/landing/what_melder_is_2026_10_15.py
  - artifacts/slotted_lifetime_fixes_20261014/landing/close_notch_borrower_docs_2026_10_15.py
  - artifacts/slotted_lifetime_fixes_20261014/runs/rebuild_2026_10_15_what_melder_is.txt
  - artifacts/slotted_lifetime_fixes_20261014/runs/rebuild_2026_10_15_closure.txt
  - artifacts/slotted_lifetime_fixes_20261014/runs/docs_2026_10_15_gil0.txt
  - artifacts/slotted_lifetime_fixes_20261014/runs/docs_2026_10_15_final_gil0.txt
  - artifacts/slotted_lifetime_fixes_20261014/runs/docs_2026_10_15_final_gil1.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none - kept in the slotted lane's evidence folder, which is rowed under its epic

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - how a notch reaches borrowers, and why versions coexist
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose; the whole ticket; initial revision 2026-10-15T02:07:39Z;
  the design and the direction are the owner's; Notes and closure revisions 2026-10-15T08:56:47Z-2026-10-15T09:05:45Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none

## Notes
- DATETIME: 2026-10-15T02:07:39Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The notch reaches borrowers in the code, so the three "known limitation" passages are stale. After its
    transaction ends, `Conduit.notch_spell` calls `_deactivate_borrowed_spell(outgoing_id)`, which walks the
    conduit's links and has every peer's Spellbook park its contracted copy of the outgoing version
    (`_inactivate_contract_spell`, a no-op where the peer does not hold it), then `ConduitWard._emit_index_notch`,
    which for every index-link contract covering the index moves the subscription head to the new version
    (`IndexDetail.update_selected`) and has the receiver park the old copy and activate the new one
    (`_ensure_contracted_active` mints the contracted copy when the receiver never had it). The notch itself parks
    the outgoing member and gates the index for a rebuild at the next meld. Nothing is destroyed: old versions stay
    parked and their objects stay alive. I called this a defect from the stale doc line without reading the code;
    the owner corrected it (chat 2026-10-15).
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5461-5549
  - src/melder/aether/conduit/conduit.py:5746-5775
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2316-2380
  - context_compass/system_docs/src_architecture.md:510-520
  - context_compass/system_docs/src_architecture.md:858-871
  - context_compass/system_docs/src_components.md:5815-5826
  IMPACT: The passages taught a missing-feature reading of a deliberate design; correcting them keeps the next agent
    from repeating it.
  NEXT: Rewrite the three passages, regenerate both indexes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T08:56:47Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner widened the task (chat 2026-10-15): put what Melder is for "front and center at the top of
    SRC_Architecture", because the beginner docs make it look like a DI container - "this is NOT a di container".
    Done before the compaction, docs only: `src_architecture` opens with "What Melder Is (Read This First)" - a
    runtime agents live and build in, where many agents iterate on the same objects through versions, borrowers
    follow a notch, versions coexist (MutationResearch, compositions, one `unique` object per version) and agents
    build the subsystem they are in - with the Runtime Model moved under it and a closing rule not to judge the
    code by DI-container rules. The three passages describe the feature (Architecture Summary, SpellIndex Mutation
    Entry step 6, the src_components SpellIndex Mutation Surface); both documents carry handoff entries and the
    running release note two packaging lines. No `src/` change, so no notch.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:3-54
  - context_compass/system_docs/src_architecture.md:565-579
  - context_compass/system_docs/src_architecture.md:897-910
  - context_compass/system_docs/src_architecture.md:3788-3798
  - context_compass/system_docs/src_components.md:5823-5830
  - context_compass/system_docs/src_components.md:10691-10693
  - release_docs/next_version_release.md:333-342
  IMPACT: The packaged architecture tells every reader first that Melder is a runtime, not a container, so notch,
    transfer and pending objects are no longer judged by DI-container rules.
  NEXT: Record the validation already run, then correct the src_components metadata date.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T08:56:47Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Validation run before the compaction, on the live repo: both indexes regenerated and current
    (src_architecture 61 sections over 4250 lines, generated 02:09:57Z; src_components 149 sections over 11167
    lines, generated 02:08:23Z); asset build and check (three OK lines at v0.2.8240) and bundle build and check
    with `--include-untracked` (three OK lines) at 02:10:15Z; unit_top (test_system_documents,
    test_system_document_view and the package metadata tests) with the GIL off: 145 passed in two runs. Not run
    yet: unit_top with the GIL on, unit_build, unit_llm.
  EVIDENCE:
  - context_compass/system_docs/src_architecture_index.md:9-19
  - context_compass/system_docs/src_components_index.md:9-19
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/rebuild_2026_10_15_what_melder_is.txt:1-21
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/docs_2026_10_15_gil0.txt:1-2
  IMPACT: The docs change builds into the packaged documents and passes the document tests on the free-threaded
    build; the GIL-on run and the build-asset and bundle suites remain.
  NEXT: Correct the src_components metadata date, re-index, rebuild, then run the three suites with the GIL off and on.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-15T08:56:47Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: src_components' Metadata still reads `Updated: 2026-10-14`, but the 2026-10-15 correction changed a
    behaviour description (the SpellIndex Mutation Surface bullet); src_architecture already reads 2026-10-15, and
    the documentation standard moves the date with such a change. Plan, inside this task's boundary: set it to
    2026-10-15, regenerate the src_components index, rebuild the assets and bundles with both checks, then run
    unit_top, unit_build and unit_llm with the GIL off and on. Closing touches only tickets and boards, which the
    assets (the `melder` sources and `context_compass/system_docs`) and the bundles (`context_compass/` excluded)
    do not read; both checks are rerun after the closure to prove it.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:3-8
  - context_compass/system_docs/src_architecture.md:55-61
  - context_compass/agent_onboarding/default/engineer/skills/documentation_standards.md:92-95
  - src/melder/_build_assets/_system_documents/_builder.py:105-119
  - src/melder/_build_assets/_agent_documentation/_builder.py:181-194
  - llm_support/_builder.py:90-91
  IMPACT: Without it the packaged component map carries a stale Updated date for a change it describes.
  NEXT: Set the date, re-index src_components, rebuild and check.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-15T08:59:38Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: src_components' Metadata reads `Updated: 2026-10-15`; its index is regenerated (149 sections over 11167
    lines, generated 08:57:07Z) and both index checks print OK (src_architecture unchanged: 61 sections over 4250
    lines). The asset build and check print three OK lines at v0.2.8240; the bundle build rewrote the src bundle
    (the packaged component map moved) and its check prints three OK lines with `--include-untracked`.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:3-8
  - context_compass/system_docs/src_components_index.md:9-19
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/rebuild_2026_10_15_closure.txt:1-21
  IMPACT: The packaged documents and bundles carry the final text; only the test runs remain before closure.
  NEXT: Run unit_top, unit_build and unit_llm on the live repo with the GIL off and on.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-10-15T09:03:21Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: On the live repo after the final rebuild, Python 3.14t, GIL off and on: unit_top (test_system_documents,
    test_system_document_view and the package metadata tests) 145 passed each time; unit_build (the build-asset
    suite) 116 passed each time; unit_llm (the bundle suite) 28 passed each time. Not run: the rest of the tree,
    because nothing outside the documents, their indexes, the release note and the generated assets and bundles
    changed.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/docs_2026_10_15_final_gil0.txt:1-3
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/docs_2026_10_15_final_gil1.txt:1-3
  IMPACT: The exit gate is met: the passages match the code, the indexes, assets and bundles are current, and the
    suites that read them pass on both builds.
  NEXT: Close the task and sync the boards, then rerun both checks.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-15T09:05:45Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Closed: the exit gate is met. Re-read after the compaction, the notch code still matches the
    corrected passages - `notch_spell` ends its transaction, then `_deactivate_borrowed_spell` has each linked
    peer park its copy of the outgoing version and `_emit_index_notch` moves each index-link contract to the
    new version (park old, activate or mint new on the receiver); nothing is destroyed. The owner's direction
    is recorded, and the indexes, assets and bundles are current with the document, asset and bundle suites
    passing on both builds. Routine owner-directed docs work, closed by its assigned agent; no independent
    review was asked for. Not part of this task and not started: a matching "not a DI container" note in
    the beginner docs or README, which is the owner's call.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5461-5549
  - src/melder/aether/conduit/conduit.py:5746-5775
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2316-2380
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/docs_2026_10_15_final_gil0.txt:1-3
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/docs_2026_10_15_final_gil1.txt:1-3
  IMPACT: The lane is turned in; the board no longer routes it.
  NEXT: Rerun both checks after the board sync; then nothing until the owner directs.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-15T10:47:22Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner ruling (chat 2026-10-15, after the closure): the beginner docs onboard users through Melder as a DI
    container on purpose and introduce the deeper concepts step by step ("beginners are onboarded as a di
    container, then slowly introduced into more complex concepts"). My closing offer to add a "not a DI
    container" note to the beginner docs or README went against that design and is withdrawn; nothing was
    started. The beginner path, the README and the examples stay as the owner wrote them; no file outside
    context_compass was touched for this ruling.
  EVIDENCE:
  - docs/beginner/index.md:1-28
  IMPACT: The DI-first beginner path is the deliberate on-ramp (beginner, then intermediate and beyond); no agent
    should reshape the beginner docs, README or examples to lead with "not a DI container".
  NEXT: None; the src_architecture top section changes only if the owner asks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Done (2026-10-15T09:05:45Z). Docs only, no notch, at the owner's direction (chat 2026-10-15): `src_architecture` opens
with "What Melder Is (Read This First)" - not a DI container but a runtime agents live and build in - with
the Runtime Model under it, and the Architecture Summary, SpellIndex Mutation Entry step 6 and the
src_components SpellIndex Mutation Surface describe borrowers following a notch while older versions stay
alive. Indexes, assets and bundles are current (checks OK); unit_top, unit_build and unit_llm pass with the
GIL off and on. The beginner docs, README and examples stay DI-first on purpose (owner ruling, last Note);
nothing is open. Next: none.

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
