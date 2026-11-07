

# Task: class_annotation_selects_only_bare_spells - framing hides the concrete class in injection, as in the meld door

## Metadata
- Task ID: TASK-2026-11-07-class_annotation_selects_only_bare_spells
- Story: none - an epic-level task of EPIC-2026-11-07-spellframe_hides_the_concrete_class
- Status: draft
- Owner: Mark (owner)
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-11-07T10:03:26Z
- Updated: 2026-11-07T10:03:26Z

## Objective
A class annotation, a string naming a class and `list[Class]` select only spells bound bare; a spell bound under a
spellframe is reached only through that frame. Land it as one change set: source, tests, docs, release note, notch,
rebuild.

## Ticket Contract
- ENTRY_GATE: T1 done; its edge cases decided by the owner; a board row routes here.
- EXECUTION_BOUNDARY: the matchers T1 lists (Phase 3 first); the S1 regression file
  tests/component/melder/aether/conduit/test_conduit_component_waiting_consumer_wakes_for_its_provider.py rewritten
  to this contract; the tests, docs and examples T1 lists; src_architecture/src_components and their indexes;
  release_docs/next_version_release.md; __version__; the asset and llm_support rebuild last.
- DEPENDENCIES: TASK-2026-11-07-inventory_class_resolution_of_framed_spells.
- EXIT_GATE: the regressions assert this contract and pass, the GIL off and on; the full suite run and reported;
  the S1 matrix re-run shows no key-split MISS; release note (Breaking), notch and both `--check` runs green.
- FAILURE_ESCALATION: DECISION_REQUEST when a converted test encodes intent the owner may want kept; CONFLICT if
  another lane holds the files.

## Scope Boundaries
- In scope: type-key matching; every caller T1 lists; the creation-cache generation if T1 says replay keeps old rows.
- Out of scope: meld doors, Bind, addresses, contract/definition/label matching, the Phase 4/6 check (T3).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: filed with the epic (chat 2026-11-07); waits for T1 and the owner's edge-case decisions.

## Steps / Checklist
- [ ] Change the type-key matching to admit only spells with no spellframe (index and scan paths alike).
- [ ] Rewrite the S1 regression file: class consumers never resolve a framed provider, waiting or fresh; Protocol,
      label and SpellMap consumers do; the late-twin preconditions follow the new contract.
- [ ] Convert or remove each test, doc and example from T1's list.
- [ ] Docstrings of every touched symbol; src_architecture and src_components entries with their indexes.
- [ ] Creation-cache generation bump if T1 requires it.
- [ ] Release note section leading with **Breaking change:** and the upgrade path; notch; rebuild and `--check` last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The strict model in src with tests and docs; the release-note section; the notch; green checks.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py (and what T1 adds)
- tests/component/melder/aether/conduit/test_conduit_component_waiting_consumer_wakes_for_its_provider.py
- context_compass/system_docs/src_architecture.md, src_components.md and their indexes
- release_docs/next_version_release.md, src/melder/__version__.py

## Validation
- Not run.
- Recommended commands:
  - `.venv_new/Scripts/python.exe -X gil=0 -m pytest tests -q` and the same with `-X gil=1`
  - `bash context_compass/artifacts/dependency_watchers_20261107/probes/run_probe_watcher_announcer_matrix.sh`
  - `python src/melder/_build_assets/_build_asset_runner.py` then `--check`; `python llm_support/_builder.py` then `--check`

## Risks / Rollback Notes
- Breaking for class consumers of framed spells; rollback is the revert of the change set (no record format moves).

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

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/dependency_watchers_20261107/ (the matrix and interface checks to re-run)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the before/after runs land beside the 0.2.8277 ones

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - the strict class-resolution contract
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; filed 2026-11-07T10:03:26Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-11-07T10:03:26Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The change is the type row of Phase 3's matching table - a class annotation compares the spell's type key
    whatever its frame - applied identically in the scan and index paths; the 14 strict xfails in the S1 regression
    file were written for the other option and become assertions that a class consumer stays unresolved.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:349-386
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:545-574
  IMPACT: One rule for injection and the meld door; the key split cannot occur.
  NEXT: Wait for T1's inventory and the owner's edge-case decisions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

## Context / Handoff Summary
- Scope: land the strict model end to end. State: draft, melder_0; blocked on T1 and the edge-case decisions.
- Next: (1) T1; (2) the change with tests and docs; (3) release note, notch, rebuild.

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
