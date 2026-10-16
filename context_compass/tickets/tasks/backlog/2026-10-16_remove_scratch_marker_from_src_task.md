# Task: remove_scratch_marker_from_src - delete the leftover scratch marker module that ships in the wheel

## Metadata
- Task ID: TASK-2026-10-16-remove_scratch_marker_from_src
- Story: none (standalone backlog task; found during EPIC-2026-10-14-managed_spell_quantity S7)
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p3
- Created: 2026-10-16T00:52:02Z
- Updated: 2026-10-16T00:52:02Z

## Objective
Delete `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/
generalized_cache_runtime_rows_SCRATCH.py` (35 bytes: `# scratch marker - replaced below`). Nothing imports it, but
it is tracked under `src/`, so it ships in the wheel and the generated documents list it as a module.

## Ticket Contract
- ENTRY_GATE: an active board row; the file's git history read to confirm nothing needs it.
- EXECUTION_BOUNDARY: that file; its graph descriptor; src_components' inventory row and index; the generated build
  assets (rebuilt, never edited); the release note's packaging section.
- DEPENDENCIES: none.
- EXIT_GATE: the file removed; graph re-extracted and assembled; src_components updated with its index; notch and
  release-note line; both rebuild checks print only OK.
- FAILURE_ESCALATION: BLOCKER if anything imports the module or loads it by path.

## Scope Boundaries
- In scope: the one file and the documents and assets that list it.
- Out of scope: any other generated-asset cleanup.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: found in EPIC-2026-10-14-managed_spell_quantity S7 and evidenced below; parked in the backlog at
  the owner's direction ("if you found more bugs just add tickets", 2026-10-16).

## Steps / Checklist
- [ ] Confirm no import, path load or packaging rule needs the file.
- [ ] Delete it (needs delete permission on the folder); re-extract and assemble the graph; update src_components.
- [ ] Notch, the release-note packaging line, the rebuild last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The file gone from `src/` and the wheel; documents and assets current.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_cache_runtime_rows_SCRATCH.py
- context_compass/system_docs/graph/ (its descriptor), src_graph.md, src_graph_index.md
- context_compass/system_docs/src_components.md and src_components_index.md
- release_docs/next_version_release.md

## Validation
- Not run.
- Recommended commands:
  - `python -X gil=0 -m pytest tests/unit -q` (in shards)
  - `python src/melder/_build_assets/_build_asset_runner.py --check`
  - `python llm_support/_builder.py --check --include-untracked`

## Risks / Rollback Notes
- None expected; restore the file from git if anything turns out to load it by name.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
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
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; created 2026-10-16T00:52:02Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-16T00:52:02Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The module holds one comment line and nothing imports it; only generated documents name it (the graph adjacency
    manifest, the system-documents index, src_components' inventory and the graph payload).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_cache_runtime_rows_SCRATCH.py:1-1
  - src/melder/_build_assets/_system_documents/manifest/graph_adjacency_manifest.py:401-401
  - src/melder/_build_assets/_system_documents/manifest/system_documents_index.py:426-426
  - src/melder/_build_assets/_system_documents/payloads/src_components_payload.py:9401-9401
  IMPACT: A dead module ships to every user and is described as part of the package.
  NEXT: Read the file's git history, then delete it with its listings.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
- Scope: delete one leftover module and its listings. State: ready, unassigned, parked in the backlog.
- Next: an assigned agent opens a board row and reads the file's history.

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
