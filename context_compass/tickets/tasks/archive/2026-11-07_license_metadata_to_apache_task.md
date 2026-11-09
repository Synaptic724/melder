> **Moved to GitHub Issues on 2026-11-07:** https://github.com/Synaptic724/melder/issues/244
> This file is read-only history; the Issue is the live record.



# Task: license_metadata_to_apache - every license statement agrees with the owner's Apache-2.0 LICENSE

## Metadata
- Task ID: TASK-2026-11-07-license_metadata_to_apache
- Story: none - a standalone task on the owner's word
- Status: in_progress
- Owner: Mark (owner)
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-11-07T15:16:05Z
- Updated: 2026-11-07T15:16:05Z

## Objective
The owner replaced LICENSE (AGPL-3.0-or-later) with the Apache License 2.0 and asked for a check before the asset
rebuild (chat 2026-11-07: "there my license is in and you can check it b4 you rebuild assets"). Every other license
statement in the repository says AGPL; on his choice "Update all" each is brought to Apache-2.0, landed as one source
change with its notch, release-note line and the rebuild last.

## Ticket Contract
- ENTRY_GATE: the owner's LICENSE in the working tree; his "Update all" (chat 2026-11-07); a board row routes here.
- EXECUTION_BOUNDARY: NOTICE (its license paragraphs; the trademark and third-party sections keep their substance),
  pyproject.toml's `license`, src/melder/__license__.py, tests/unit/melder/test_package_license_metadata.py,
  README.md's license section, architecture_and_design/README.md's license line, the source-graph descriptor of
  __license__.py, the running release note, `__version__`; the rebuild last.
- DEPENDENCIES: special_instructions/agent_contribution_guide.md (notch, release note, rebuild).
- EXIT_GATE: no tracked file outside history (tickets, artifacts, cut release notes, generated bundles) states AGPL;
  the license tests pass the GIL off and on; the graph check and both rebuild `--check` runs print only OK.
- FAILURE_ESCALATION: DECISION_REQUEST for any legal wording beyond swapping the license (the trademark paragraph,
  the copyright years).

## Scope Boundaries
- In scope: the license identity everywhere it is stated; NOTICE's AGPL paragraphs replaced with Apache-2.0 wording.
- Out of scope: LICENSE itself (the owner's file), context_compass/LICENSE and NOTICE (Context Compass's own),
  historical records (tickets, artifacts, cut release notes), commit and push (the owner's, with his key).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner's "Update all" (chat 2026-11-07) after the review in Notes.

## Steps / Checklist
- [x] Review LICENSE against the canonical Apache-2.0 text and list every remaining AGPL statement (Notes).
- [ ] NOTICE, pyproject.toml, __license__.py and its test, README, architecture_and_design/README.md.
- [ ] Release-note line; notch; the graph descriptor of __license__.py refreshed.
- [ ] Validate: the license tests the GIL off and on; the graph check; then the rebuild and both `--check` runs.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- One consistent Apache-2.0 license statement across the repository; the release-note line; the notch.

## Files / Paths Impacted
- NOTICE, pyproject.toml, src/melder/__license__.py, tests/unit/melder/test_package_license_metadata.py
- README.md, architecture_and_design/README.md, release_docs/next_version_release.md, src/melder/__version__.py
- context_compass/system_docs/graph/melder/__license__.json (regenerated through the graph tooling)

## Validation
- Not run.
- Recommended commands:
  - `.venv_new/Scripts/python.exe -X gil=0 -m pytest tests/unit/melder/test_package_license_metadata.py -q`
  - `python src/melder/_build_assets/_build_asset_runner.py` then `--check`; `python llm_support/_builder.py` then `--check`

## Risks / Rollback Notes
- PyPI shows the `license` field of the next published release; rollback is reverting the change set.

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
  - the license identity across metadata and docs
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; filed 2026-11-07T15:16:05Z. LICENSE: the owner.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-11-07T15:16:05Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: LICENSE (the owner's) is the Apache License 2.0: its TERMS AND CONDITIONS (sections 1-9) equal, whitespace
    normalized, the canonical text installed with coverage 7.16.1; the appendix carries a filled notice "Copyright (C)
    2026 Mark Thomas Geleta" (NOTICE says 2025-2026; the owner's to align or not). Still AGPL: NOTICE (7 places: the
    trademark sentence, the license paragraphs, SPDX AGPL-3.0-or-later, the network-use paragraph), pyproject.toml
    `license = "AGPL-3.0-or-later"` (what PyPI publishes), src/melder/__license__.py (`__license__` and its header),
    tests/unit/melder/test_package_license_metadata.py (pins AGPL), README.md's license section, and
    architecture_and_design/README.md. The owner chose "Update all".
  EVIDENCE:
  - LICENSE:1-201
  - NOTICE:1-30
  - pyproject.toml:11-12
  - src/melder/__license__.py:1-29
  - tests/unit/melder/test_package_license_metadata.py:5-8
  IMPACT: Shipped metadata would contradict the LICENSE without this task; __license__.py is shipped source, so the
    task notches.
  NEXT: Edit the six files, the release note and the notch; then the graph descriptor; then validate and rebuild.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T15:17:55Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Landed in the working tree (uncommitted). NOTICE: the trademark sentence names the Apache License (and its
    section 6), the AGPL licence paragraphs and the network-use paragraph are replaced by the Apache-2.0 notice
    (SPDX Apache-2.0); the retention and third-party sections are unchanged. pyproject.toml `license = "Apache-2.0"`
    (no license classifiers exist). __license__.py: `__license__ = "Apache-2.0"`, the Apache header comment, the
    docstring recording the move. The license test pins Apache-2.0 (2 passed, the GIL off). README's license section
    and architecture_and_design/README.md state Apache-2.0 (the AGPL network-clause paragraph gone with the AGPL).
    Release note: the section "Melder is licensed under the Apache License 2.0"; notched 0.2.8279 (0.2.8278 was
    T2's). A sweep finds no AGPL statement left outside history and the board's routing text; system_docs hold none.
    The source-graph descriptors are being refreshed for __license__.py and __version__.py.
  EVIDENCE:
  - NOTICE:1-25
  - pyproject.toml:11-11
  - src/melder/__license__.py:1-31
  - README.md:1536-1545
  - release_docs/next_version_release.md:1-11
  IMPACT: Shipped metadata and every user-facing statement agree with the owner's LICENSE.
  NEXT: The graph refresh, then the shared rebuild and both `--check` runs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T15:32:00Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The source graph is refreshed (by subagent, src_graph_generation.md): `extract_graph.py --strict` re-extracted
    593 descriptors (0 skipped, none behind the tree); `melder.__license__`'s responsibility prose names Apache-2.0
    since 0.2.8279 and was accepted, `melder.__version__`'s accepted unchanged, SpellMap's re-accepted after T2's
    docstring fix (and spell_map.py's C1 extents remeasured, 382 lines, in both system docs with their indexes
    regenerated, both `--check` current); `assemble_graph.py --check` exit 0, all 593 ranges verified. Not this task's:
    `extract_graph.py --check --strict` still reports 355 stale nodes (143 unverified prose, 9 without semantics),
    all older than today's changes - the graph check this task's exit gate means is `assemble_graph.py --check`.
    Correction: this ticket's and the Dependabot ticket's creation stamps and this ticket's previous note were
    written as 15:31:12Z and 15:38:40Z without reading the clock; they are corrected to the files' write times
    (15:16:05Z, 15:16:07Z, 15:17:55Z).
  EVIDENCE:
  - context_compass/system_docs/graph/melder/__license__.json:1-1
  - context_compass/system_docs/src_graph_index.md:1-20
  IMPACT: The graph agrees with the source; only the shared rebuild remains for this task.
  NEXT: The shared rebuild with both `--check` runs once the Dependabot bump lands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
- Scope: bring every license statement to Apache-2.0 on the owner's "Update all"; LICENSE is his and is clean.
- State: in_progress, melder_0. Edits, release note, notch 0.2.8279 and graph refresh done and committed by the
  owner in 0733b3b65 (2026-11-07T15:25:35Z). The asset and llm_support rebuild is held on his word ("do not rebuild
  assets", chat 2026-11-07), so the committed build assets are still stamped 0.2.8278.
- Next: the rebuild with both `--check` runs when the owner lifts the hold; then closure.

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
