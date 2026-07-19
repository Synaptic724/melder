# Task: Define Graph Details Document And Agent Workflow
- Completed: 2026-04-24T01:03:27Z
- Summary: Closed during the 2026-04-24 cleanup after the graph workflow contract landed and later work moved on from graph-details setup.

## Metadata
- Task ID: TASK-2026-04-19-define-graph-details-document-and-agent-workflow
- Story:
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T19:19:24Z
- Updated: 2026-04-24T01:03:27Z

## Objective
Define one canonical graph-details document contract for machine-first system
relationship mapping, add the authoring/maintenance/read workflow to the
agent skill chain, and seed the canonical/example files that demonstrate the
expand-edit-compress storage model.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a real graph-details system,
  machine-first storage workflow, and skill/doc integration for
  design-engineer and engineer roles.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/system_docs/graph_details_document.md`
  - `codex/context_compass/system_docs/src_graph.json`
  - `codex/context_compass/system_docs/src_graph_details.md`
  - `codex/context_compass/system_docs/src_graph_network.md`
  - `codex/context_compass/agent_onboarding/default/design_engineer/`
  - `codex/context_compass/agent_onboarding/default/engineer/`
  - `codex/context_compass/examples/example_graph_details/`
  - ticket/board/artifact sync for this lane
- DEPENDENCIES:
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - `codex/context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md`
  - `codex/context_compass/agent_onboarding/default/design_engineer/skills/src_components_instructions.md`
  - `codex/context_compass/agent_onboarding/default/engineer/skills/context_protocol.md`
  - `codex/context_compass/system_docs/patches/active/graph_details_document_workflow/architecture_patch.md`
  - `codex/context_compass/system_docs/patches/active/graph_details_document_workflow/component_patch_system_docs.md`
  - `codex/context_compass/system_docs/patches/active/graph_details_document_workflow/component_patch_design_engineer.md`
  - `codex/context_compass/system_docs/patches/active/graph_details_document_workflow/component_patch_engineer.md`
  - `codex/context_compass/system_docs/patches/active/graph_details_document_workflow/code_description_patch_graph_document_workflow.md`
- EXIT_GATE: the canonical graph-details schema and storage workflow are
  documented, design-engineer and engineer skills are updated, the example
  folder demonstrates the workflow, and the graph package includes compressed
  storage plus a readable JSON consumption artifact.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the graph schema must widen
  beyond one canonical file or if the architecture/components doc split proves
  incompatible with the graph-details workflow.

## Scope Boundaries
- In scope:
  - one canonical graph-details schema
  - compressed-storage and expanded-patch editing workflow
  - design-engineer authoring/maintenance guidance
  - engineer reading/usage guidance
  - canonical example files
- Out of scope:
  - full-repo graph population
  - runtime code changes in `src/`
  - CI automation for graph generation

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the canonical graph-details docs, skills, examples, and
  compressed graph storage file are implemented and the JSON files validate.

## Steps / Checklist
- [x] Stage and consume patch docs for the graph-details workflow lane.
- [x] Define the canonical graph-details schema and compressed storage model.
- [x] Add canonical system docs for graph-details authoring and maintenance.
- [x] Add design-engineer and engineer skill docs for creation/maintenance/read flows.
- [x] Add example graph-details files under the examples folder.
- [x] Validate JSON/doc integrity and summarize the workflow.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- canonical graph-details documentation
- canonical compressed `src_graph.json`
- required readable `readable_src_graph.json`
- design-engineer and engineer skill updates
- example graph-details workflow files

## Files / Paths Impacted
- codex/context_compass/system_docs/
- codex/context_compass/agent_onboarding/default/design_engineer/
- codex/context_compass/agent_onboarding/default/engineer/
- codex/context_compass/examples/example_graph_details/
- codex/context_compass/tickets/tasks/2026-04-19_define_graph_details_document_and_agent_workflow_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- JSON validation only.
- Recommended commands:
  - `Get-Content codex/context_compass/system_docs/src_graph.json -Raw | ConvertFrom-Json | Out-Null`
  - `Get-Content codex/context_compass/system_docs/readable_src_graph.json -Raw | ConvertFrom-Json | Out-Null`
  - `Get-Content codex/context_compass/examples/example_graph_details/src_graph.json -Raw | ConvertFrom-Json | Out-Null`
  - `Get-Content codex/context_compass/examples/example_graph_details/readable_src_graph.json -Raw | ConvertFrom-Json | Out-Null`
  - `Get-Content codex/context_compass/examples/example_graph_details/src_graph.expanded.json -Raw | ConvertFrom-Json | Out-Null`

## Risks / Rollback Notes
- Risk: the graph doc duplicates architecture/components prose and becomes
  another drifting narrative layer.
  Rollback: keep the graph file structural and relationship-focused, with
  architecture/components remaining the canonical long-form explanation layer.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/graph_details_document_workflow/architecture_patch.md
  - system_docs/patches/active/graph_details_document_workflow/component_patch_system_docs.md
  - system_docs/patches/active/graph_details_document_workflow/component_patch_design_engineer.md
  - system_docs/patches/active/graph_details_document_workflow/component_patch_engineer.md
  - system_docs/patches/active/graph_details_document_workflow/code_description_patch_graph_document_workflow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the graph-details contract is merged into the
  canonical doc/skill chain and intentionally superseded.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-19T19:19:24Z
  TYPE: PLAN
  CLAIM: The graph-details lane should not produce two parallel graph docs or
    another prose-heavy architecture duplicate. The user wants one machine-first
    relationship map with a compressed-storage workflow, plus explicit skill
    guidance for authoring, maintenance, and reading.
  EVIDENCE:
  - codex/context_compass/system_docs/src_graph_details.md:1-10
  - codex/context_compass/system_docs/src_graph_network.md:1-10
  - user_instruction: "the goal is literally just to show relationships and what something is"
  - user_instruction: "it must uncompress the data and save it as a patch file the whole document edit it then resave it compressed in storage"
  IMPACT: The implementation should converge on one canonical `src_graph.json`
    plus one companion workflow doc and matching skill-chain instructions.
  NEXT: stage the patch docs and then patch the canonical docs/skills/examples
    around that single-file workflow.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:24:40Z
  TYPE: FACT
  CLAIM: The lane landed one canonical graph workflow instead of two competing
    graph docs. The system docs now include:
    - `graph_details_document.md` as the schema + workflow contract
    - `src_graph.json` as the compressed canonical graph store
    - redirect stubs in `src_graph_details.md` and `src_graph_network.md`
    The skill chain now includes:
    - `design_engineer/skills/graph_details_instructions.md`
    - `engineer/skills/graph_details_usage.md`
    and the examples folder now includes a full expanded/compressed example pair
    under `examples/example_graph_details/`.
  EVIDENCE:
  - codex/context_compass/system_docs/graph_details_document.md:1-171
  - codex/context_compass/system_docs/src_graph.json:1-1
  - codex/context_compass/system_docs/src_graph_details.md:1-9
  - codex/context_compass/system_docs/src_graph_network.md:1-9
  - codex/context_compass/agent_onboarding/default/design_engineer/skills/graph_details_instructions.md:1-78
  - codex/context_compass/agent_onboarding/default/engineer/skills/graph_details_usage.md:1-58
  - codex/context_compass/examples/example_graph_details/graph_details_document.md:1-13
  IMPACT: Agents now have one stable graph-details workflow and do not need to
    guess how to author, store, read, or patch the graph manifest.
  NEXT: review the canonical workflow and decide whether to accept this as the
    new graph-details contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:24:40Z
  TYPE: MEASURE
  CLAIM: The canonical and example graph files validate as JSON after the
    compressed-storage workflow landed.
  EVIDENCE:
  - validation_result: `Get-Content codex/context_compass/system_docs/src_graph.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_CANONICAL_GRAPH`
  - validation_result: `Get-Content codex/context_compass/examples/example_graph_details/src_graph.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_EXAMPLE_COMPRESSED`
  - validation_result: `Get-Content codex/context_compass/examples/example_graph_details/src_graph.expanded.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_EXAMPLE_EXPANDED`
  IMPACT: The graph workflow is not just documented; the canonical and example
    storage/editing artifacts are structurally valid.
  NEXT: return the graph-details workflow for review and acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:32:20Z
  TYPE: FACT
  CLAIM: The first cut of the graph workflow did not explicitly state that
    `__init__.py` files must be excluded from graph nodes. That gap is now
    patched in the canonical workflow doc, the design-engineer authoring skill,
    and the example workflow doc so package marker files do not get promoted
    into the graph as system-significant objects.
  EVIDENCE:
  - codex/context_compass/system_docs/graph_details_document.md:116-126
  - codex/context_compass/agent_onboarding/default/design_engineer/skills/graph_details_instructions.md:27-34
  - codex/context_compass/examples/example_graph_details/graph_details_document.md:8-13
  IMPACT: The graph contract now explicitly excludes `__init__.py` noise and
    is safer for manual population.
  NEXT: review the graph workflow with the explicit `__init__.py` exclusion in place.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T19:32:42Z
  TYPE: FACT
  CLAIM: The first cut of the graph workflow also left the source/test boundary
    implicit. That is now patched explicitly: `src_graph.json` is source-only
    and must not include `tests/` objects. Test-side relationships stay in the
    existing tests architecture/components docs unless a separate test graph is
    intentionally introduced later.
  EVIDENCE:
  - codex/context_compass/system_docs/graph_details_document.md:34-46
  - codex/context_compass/agent_onboarding/default/design_engineer/skills/graph_details_instructions.md:12-21
  - codex/context_compass/agent_onboarding/default/engineer/skills/graph_details_usage.md:9-16
  IMPACT: The canonical graph contract is now scoped cleanly to `src/` and is
    less likely to drift into mixed runtime/test topology noise.
  NEXT: review the graph workflow with both the `src/`-only scope and the
    `__init__.py` exclusion in place.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T21:15:48Z
  TYPE: FACT
  CLAIM: The initial graph workflow still left a gap between compressed
    storage and honest line-based reading. That gap is now closed by making
    `readable_src_graph.json` a required end-state artifact: the compressed
    canonical graph remains storage, the readable JSON view becomes the
    primary reading surface, and the expanded patch copy remains the edit
    surface.
  EVIDENCE:
  - codex/context_compass/system_docs/readable_src_graph.json:1-632
  - user_instruction: "a patch document requires the end state for the src_graph to be the readable_src_graph"
  IMPACT: The graph workflow now has one honest storage/read/edit split
    instead of pretending the compressed storage file is the normal reading
    surface.
  NEXT: review the updated graph workflow with the readable JSON consumption
    artifact included as part of the required graph package.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T21:15:48Z
  TYPE: MEASURE
  CLAIM: The main and example readable graph artifacts now exist, parse as
    JSON, and satisfy the `220`-character line-width contract.
  EVIDENCE:
  - validation_result: `Get-Content codex/context_compass/system_docs/readable_src_graph.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_MAIN_READABLE_JSON`
  - validation_result: main readable max line length -> `220`
  - validation_result: `Get-Content codex/context_compass/examples/example_graph_details/readable_src_graph.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_EXAMPLE_READABLE_JSON`
  - validation_result: example readable max line length -> `220`
  IMPACT: The graph workflow now has a real readable consumption artifact for
    both the canonical and example graph package, not just a documented idea.
  NEXT: review the updated graph contract with storage, readable, and expanded
    artifact roles all present.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T22:58:18Z
  TYPE: FACT
  CLAIM: The onboarding and skill-chain routing for architecture/components
    work now explicitly includes `readable_src_graph.json` alongside
    `src_architecture.md` and `src_components.md`. The read requirement is now
    enforced in engineer context protocol, design-engineer instruction docs,
    tests-architecture/tests-components instruction docs, system-orientation
    guidance, compaction/workflow policy, and AR read-first onboarding.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/default/engineer/skills/context_protocol.md:10-24
  - codex/context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md:20-27
  - codex/context_compass/agent_onboarding/default/design_engineer/skills/src_components_instructions.md:20-28
  - codex/context_compass/agent_onboarding/default/design_engineer/skills/tests_architecture_instructions.md:20-25
  - codex/context_compass/agent_onboarding/default/design_engineer/skills/tests_components_instructions.md:20-25
  - codex/context_compass/agent_onboarding/default/general/skills/context_compaction.md:39-50
  - codex/context_compass/system_docs/ar_onboarding_read_first.md:9-19
  IMPACT: Agents that already know to re-read architecture/components docs on
    demand now also have an explicit requirement to read the readable graph
    surface instead of guessing from compressed storage or skipping graph
    context entirely.
  NEXT: keep the readable graph synchronized whenever architecture/components
    work changes documented source wiring or ownership.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the graph-details document contract, the compressed-storage
workflow, the skill-chain updates, and the example files that demonstrate the
workflow.
