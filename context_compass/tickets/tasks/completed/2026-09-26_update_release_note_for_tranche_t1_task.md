# Task: Update the release note for 0.2.56 with tranche T1 (override rename, live payloads, determinism, phase 8)

- Completed: 2026-09-26T13:38:26Z
- Summary: Release note headed 0.2.56 (matching HEAD's `__version__`) with four tranche-T1 sections: the
  `override` rename (breaking), live override payload values by identity, faster conjure (phase-8 digest) and
  process-stable creation-cache signatures; packaging bullets updated. Owner accepted ("yeah all done").

## Metadata
- Task ID: TASK-2026-09-26-update-release-note-for-tranche-t1
- Story: none (release hygiene for the closed signature-determinism story)
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p2
- Created: 2026-09-26T13:29:26Z
- Updated: 2026-09-26T13:38:26Z

## Objective
Make `release_docs/next_version_release.md` name the committed `__version__` (0.2.56) and describe tranche T1 for
users: the `override` keyword replacing `spell_override` on `SpellMap`/`SpellContract`, override values of any
type delivered by identity (also after a cache hit), `SpellMap.override` now applied, faster conjure (phase-8 pool
digest), and process-stable creation-cache signatures for object payloads.

## Ticket Contract
- ENTRY_GATE: Owner direction 2026-09-26 ("update the release"); the T1 story is closed and accepted.
- EXECUTION_BOUNDARY: `release_docs/next_version_release.md` only. `src/melder/__version__.py` already reads
  0.2.56 at HEAD (f344028e2) and is not edited. No asset or LLM-bundle rebuild here (owner-run on 3.14), no
  commit, tag or publish; other lanes' release sections are not rewritten.
- DEPENDENCIES: tickets/stories/completed/2026-09-26_signature_determinism_and_phase8_digest_story.md and its
  five tasks; the descriptor docstrings (`spell_contract.py`, `spell_map.py`) for the shipped contract.
- EXIT_GATE: header and `__version__` agree (0.2.56); the T1 sections are at the top of the note (newest first),
  in the note's voice, with the breaking rename called out; packaging bullets updated; owner reviews.
- FAILURE_ESCALATION: DECISION_REQUEST if the target version is ambiguous; CONFLICT if another lane edits the
  note concurrently (re-read before writing).

## Scope Boundaries
- In scope: the release header, the new T1 sections, the packaging bullets.
- Out of scope: version literal (already notched), asset/LLM rebuild, commits, other agents' sections.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner directed the release update (2026-09-26T13:29:26Z); target version established from HEAD.
- from_state: in_progress
- to_state: review
- transition_reason: Header, four T1 sections and packaging bullets written and re-read (2026-09-26T13:33:47Z); owner review.
- from_state: review
- to_state: done
- transition_reason: Owner accepted ("yeah all done", 2026-09-26T13:38:26Z); board synced.

## Steps / Checklist
- [x] R1: establish the target version (HEAD `__version__` vs the note header) and the section order.
- [x] R2: write the T1 sections (rename; live payload values; SpellMap payloads; conjure speed; stable signatures).
- [x] R3: update the header and the packaging bullets; re-read the note; record the result; owner review.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `release_docs/next_version_release.md` headed 0.2.56 with the tranche T1 sections.

## Files / Paths Impacted
- release_docs/next_version_release.md

## Validation
- Not run (documentation only; assets deliberately not rebuilt).

## Risks / Rollback Notes
- Until the owner rebuilds, the packaged assets and LLM bundles still carry 0.2.55; the packaging line for
  0.2.56 holds only after that rebuild.
- Rollback: restore the note from git.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No hand edit of a generated asset.
- [x] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: none
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Release note for 0.2.56 (tranche T1).
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T13:29:26Z
  TYPE: FACT
  CLAIM: Target version is 0.2.56: HEAD (f344028e2, committed 2026-09-26T13:22:08Z) carries `__version__ =
    "0.2.56"` while the committed note is still headed "Melder 0.2.55 / Unreleased" (the 0.2.55 header was
    melder_1's, whose task recorded the earlier owner-side notch to 0.2.55 the same way). The note holds every
    change since the published 0.2.50, newest features first, then fixes, then "Packaging and documentation"
    (whose LLM/agent-docs line reads 0.2.55). Nothing in it mentions the descriptor rename, live payload values
    or the conjure speed-up. The public `Conduit.meld(..., override=...)` keyword already read `override`
    (conduit.py:4417-4425), so the descriptor rename makes the two agree - that is the user-facing framing.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-3
  - release_docs/next_version_release.md:242-250
  - src/melder/aether/conduit/conduit.py:4417-4425
  - src/melder/aether/conduit/meld/contracts/spell_contract.py:158-172
  IMPACT: Only the header, new sections and packaging bullets change; the literal is left as is.
  NEXT: R2 - write the sections at the top of the note; then R3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T13:33:47Z
  TYPE: FACT
  CLAIM: Release note updated (LF kept; new lines within the note's existing 108-column maximum). Header now
    "Melder 0.2.56". Four sections inserted at the top, newest first: "`override` replaces `spell_override` on
    `SpellMap` and `SpellContract`" (breaking rename, TypeError on the old keyword, `meld(override=...)` and
    precedence unchanged); "Override payload values reach the provider as the objects you gave" (any object,
    by identity, in-process and after a cache hit; SpellMap payloads applied; cache stores no objects; scalar
    books keep their cache; one caveat: a meld passing its own override still renders descriptor payload values
    into generated code until that executor is replaced - pass such values at meld); "Faster conjure on large
    books" (phase-8 rows hashed once per conjure; -34% at 300 spells, noise at 29; no cache invalidation);
    "Creation-cache signatures are the same in every process" (address-free rendering; stable books keep their
    bytes). Packaging bullets name the descriptor keyword, live payloads and the single signature
    implementation; the LLM/agent-docs line reads 0.2.56 and holds only after the owner's asset rebuild.
    `__version__` untouched (already 0.2.56 at HEAD). The override-path caveat is melder_0's to retire when S3a
    ships (their M0-25 says S3a already routes the override runtime through the live resolution on the device
    tree; NOTICE F0-14 sent).
  EVIDENCE:
  - release_docs/next_version_release.md:1-68
  - release_docs/next_version_release.md:306-315
  - src/melder/__version__.py:12-12
  IMPACT: Version and release note agree; the note carries tranche T1 for users; ready for owner review.
  NEXT: Owner reviews the note and runs the asset/LLM rebuild on 3.14
    (`python src/melder/_build_assets/_build_asset_runner.py` then `python llm_support/_builder.py`); close on
    acceptance.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-09-26T13:29:26Z: IN_PROGRESS. R1 done (target 0.2.56); writing the T1 sections next (R2), then header and
packaging bullets (R3); task -> review for the owner.
STATE 2026-09-26T13:33:47Z: REVIEW. Note headed 0.2.56 with four T1 sections and updated packaging bullets; __version__ untouched.
Owner reviews; asset/LLM rebuild is owner-run on 3.14; close on acceptance.
STATE 2026-09-26T13:38:26Z: DONE. Owner accepted the 0.2.56 note; ticket closed. Asset/LLM rebuild and graph regeneration are
owner-run on 3.14 (commands in the closure report).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
