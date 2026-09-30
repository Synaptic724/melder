

# Task: Promote the host read surface into the system documents and remap the citations it shifted

## Metadata
- Task ID: TASK-2026-09-29-promote-host-read-surface-into-system-docs
- Story: none; follow-up of EPIC-2026-09-29-host-integration-read-surface (closed by owner turn-in)
- Status: draft
- Owner: user
- Agent Name: melder_0
- Priority: p2
- Created: 2026-09-29T22:27:07Z
- Updated: 2026-09-29T22:27:07Z

## Objective
Parked at the owner's turn-in of the host read surface lane (chat, 2026-09-29: "add the details to the new release
and keep the version update then turn in your shit don't rebuild assets"). The source, tests, release note and the
0.2.8208 wheel landed; the canonical documents did not. This task brings them current when the owner schedules
it: describe `Aether.find_frame` / `get_frame` / `list_frame_names` and the read accessors in src_architecture,
src_components and tests_components; add the scopes.md paragraph; update the graph; and fix the 13 `path:line`
citations that the lane's insertions moved.

## Ticket Contract
- ENTRY_GATE: owner schedules it; board row; preservation baselines RE-CAPTURED at the start of the pass (the ones in
  artifacts/host_read_surface_20260929/docs/preservation/ describe the documents as of 2026-09-29T22:00Z).
- EXECUTION_BOUNDARY: context_compass/system_docs (the three documents, their indexes, the graph descriptors of the
  five touched nodes, the assembled graph), docs/intermediate/scopes.md, then assets and LLM bundles last.
- DEPENDENCIES: system_docs/patches/completed/host_read_surface_2026_09_29/ (the contracts to promote, archived
  without promotion); tickets/tasks/completed/2026-09-29_implement_frame_lookups_and_read_accessors_task.md.
- EXIT_GATE: the three documents describe the new calls; the 13 citations resolve to the same code as before the
  insertions; C1 entries of the five files remeasured; indexes current; both portability checks empty;
  preservation diff explained; graph assembled with the touched nodes read and accepted; assets and LLM bundles
  rebuilt with both checks OK.
- FAILURE_ESCALATION: CONFLICT if a document contradicts the landed source; BLOCKER if the graph tooling refuses.

## Scope Boundaries
- In scope: the objective above.
- Out of scope: source changes; the parked atomic-retirement story.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Created parked at the owner's turn-in; awaits scheduling.

## Steps / Checklist
- [ ] Re-capture preservation baselines; read the three authoring instructions again.
- [ ] Remap the 13 shifted citations (list below), each checked at its new line.
- [ ] src_architecture: System Boundary list, Operational Invariants (noncreating, no lease, no lock), Failure
      Modes (get_frame ValueError, TypeError), a Frame Lookups diagram, C1 remeasure, Information Sources, handoff.
- [ ] src_components: Aether Singleton responsibilities/invariants/failure modes, Subcomponent: Aether Frame
      Registry, AethericFrame Services (shared configuration, posture `frozen`), Spellbook Configuration (`frozen`,
      `aether_frame`), Conduit Runtime (`spellbook`), a lookup call flow, C1 entries, handoff.
- [ ] tests_components: the two new test files (component list, C1 entries, sources, handoff).
- [ ] scopes.md paragraph; graph extract (--strict), author, accept, assemble.
- [ ] Indexes, portability checks, preservation report; assets and LLM bundles last.

## Citations shifted by the 0.2.8208 insertions (old -> new; each checked 2026-09-29T22:08Z)
- src_architecture.md:425-427 conduit.py 5280->5309, 5352->5381, 5370->5399, 5425->5454, 5448->5477, 5496->5525
- src_architecture.md:864 and src_components.md:2543 conduit.py 5229-5231 -> 5258-5260 (link isinstance check)
- src_architecture.md:1271 aetheric_frame.py 691-752 -> 726-787 (bind_frame_configuration unfrozen branch)
- src_components.md:469 conduit.py 5329, 5405, 5485 -> 5358, 5434, 5514 (transaction mediator reads)
- src_components.md:984 spellbook_configuration.py 277-343 -> 329-395 (freeze)
- src_components.md:1227 aetheric_frame_configuration.py 1984 -> 2008 (SafeGuard pair)
- src_components.md:1267 aetheric_frame.py 759-770 -> 794-805 (conflicting posture warning)
- src_components.md:5185, 5188, 5191 conduit.py 5352, 5425, 5496 -> 5381, 5454, 5525
- src_components.md:5204 conduit.py 5280, 5370, 5448 -> 5309, 5399, 5477
- src_components.md:9478 aetheric_frame.py 867 -> 902 (find_index_for_spell)
- Offsets: aether.py +149 from 1687; aetheric_frame.py +35 from 591; aetheric_frame_configuration.py +24 from 1500;
  spellbook_configuration.py +52 from 219; conduit.py +29 from 1910. File lengths now 2839, 1180, 2074, 1479, 7131.
  Document line numbers above are as of 2026-09-29T22:00Z and move with any edit.

## Deliverables
- The three documents, their indexes, scopes.md and the graph current for 0.2.8208; assets and bundles rebuilt.

## Validation
- Not run.

## Risks / Rollback Notes
- Until this runs, the packaged system documents do not mention the new calls, and the 13 citations above point
  24 to 52 lines away from the code they name.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No graph acceptance without reading the node's source against its prose.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/completed/host_read_surface_2026_09_29/
  - artifacts/host_read_surface_20260929/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: task closure

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
- DATETIME: 2026-09-29T22:27:07Z
  TYPE: DECISION
  CLAIM: Parked at the owner's turn-in (chat, 2026-09-29) of the host read surface lane: release note written,
    version kept at 0.2.8208, asset rebuild waived, canonical documents not yet promoted. The shifted-citation
    list above was verified line by line on 2026-09-29.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-09-29_implement_frame_lookups_and_read_accessors_task.md
  - context_compass/system_docs/patches/completed/host_read_surface_2026_09_29/architecture_patch.md:1-75
  IMPACT: The documentation gap stays visible instead of living only in chat.
  NEXT: Wait for the owner to schedule it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Parked 2026-09-29T22:27:07Z. Start with the Entry Gate (fresh baselines), then the citation list, then the
three documents.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
