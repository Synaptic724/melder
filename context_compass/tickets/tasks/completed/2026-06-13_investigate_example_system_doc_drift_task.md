<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner hope_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Task: Investigate Example System Doc Drift

## Metadata
- Task ID: TASK-2026-06-13-investigate-example-system-doc-drift
- Story: none
- Epic: none
- Status: in_progress
- Owner: codex
- Agent Name: hope_0
- Priority: p1
- Created: 2026-06-13T20:41:02Z
- Updated: 2026-06-13T22:49:36Z

## Objective
Explore the example architecture/components/graph docs under
`codex/context_compass/examples/` and produce an evidence-backed inventory of
current drift relative to the upgraded canonical documentation standards.

## Ticket Contract
- ENTRY_GATE: the local-evidence source-doc and tests-doc lanes are already
  deep-cleaned, and the user explicitly directed continued documentation work.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/examples/example_architecture/src_architecture.md`
  - `codex/context_compass/examples/example_components/src_components.md`
  - `codex/context_compass/examples/example_components/tests_components.md`
  - `codex/context_compass/examples/example_graph_details/graph_details_document.md`
  - `codex/context_compass/examples/example_graph_details/src_graph.json`
  - `codex/context_compass/examples/example_graph_details/readable_src_graph.json`
  - `codex/context_compass/examples/repo_overview.md`
  - `codex/context_compass/examples/eng_task_flow.md`
  - `codex/context_compass/examples/design_task_flow.md`
  - supporting canonical docs when needed for comparison:
    `codex/context_compass/system_docs/src_architecture.md`
    `codex/context_compass/system_docs/src_components.md`
    `codex/context_compass/system_docs/tests_components.md`
    `codex/context_compass/system_docs/graph_details_document.md`
  - `codex/context_compass/attention_board.md`
  - this task
- DEPENDENCIES:
  - `codex/context_compass/examples/example_architecture/src_architecture.md`
  - `codex/context_compass/examples/example_components/src_components.md`
  - `codex/context_compass/examples/example_components/tests_components.md`
  - `codex/context_compass/examples/example_graph_details/graph_details_document.md`
  - `codex/context_compass/examples/repo_overview.md`
  - `codex/context_compass/system_docs/graph_details_document.md`
- EXIT_GATE:
  - at least one concrete example-doc drift finding exists with evidence
  - the next bounded patch slice is explicit
  - no silent widening back into live source/test doc lanes
- FAILURE_ESCALATION: raise `DECISION_REQUEST`, `CONFLICT`, or `BLOCKER` if
  example-doc drift cannot be bounded without changing the purpose of the
  examples themselves.

## Scope Boundaries
- In scope:
  - example architecture/components/graph doc drift
  - evidence gathering from example docs and canonical comparison docs
  - identifying the next bounded example-doc refresh slice
- Out of scope:
  - live source/test documentation already covered by sibling tasks
  - mutation-research doc investigation
  - broad example rewrite before drift is evidenced

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly directed continued documentation work
  after the live source-doc and tests-doc local-evidence lanes were exhausted.

## Steps / Checklist
- [ ] Re-read the key example docs and note likely drift seams.
- [ ] Verify likely seams against the current canonical docs.
- [ ] Record the first concrete drift findings in `## Notes`.
- [ ] Define the first bounded patch slice from those findings.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.

## Deliverables
- evidence-backed example-doc drift inventory
- explicit next patch slice

## Files / Paths Impacted
- `codex/context_compass/examples/example_architecture/src_architecture.md`
- `codex/context_compass/examples/example_components/src_components.md`
- `codex/context_compass/examples/example_components/tests_components.md`
- `codex/context_compass/examples/example_graph_details/graph_details_document.md`
- `codex/context_compass/examples/repo_overview.md`
- `codex/context_compass/examples/eng_task_flow.md`
- `codex/context_compass/examples/design_task_flow.md`
- `codex/context_compass/tickets/tasks/2026-06-13_investigate_example_system_doc_drift_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: examples may intentionally lag canonical docs if they are meant to stay
  minimal rather than fully feature-complete.
- Rollback: keep this task investigation-first until one bounded example-doc
  patch is clearly justified.

## Applicable Anti-Patterns
- [ ] No example rewrite before concrete drift is recorded.
- [ ] No widening back into canonical live-doc maintenance without a new note.
- [ ] No assuming the examples should mirror every live feature unless the
      example purpose requires it.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 7)
- [ ] Board sync completed

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: none
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - example docs drift
  - architecture/components/graph example alignment
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-13T20:41:02Z
  TYPE: PLAN
  CLAIM: The next bounded docs lane is the example architecture/components/graph
    set. The live source-doc and tests-doc lanes are already locally cleaned,
    so continuing documentation work should move to the example/reference
    surfaces rather than forcing more churn into the canonical live docs.
  EVIDENCE:
  - user_instruction: `continue`
  - local state in sibling source-doc and tests-doc tasks
  IMPACT: This keeps documentation work moving while respecting the natural
    boundary of the already-cleaned live docs.
  NEXT: inspect the example graph/schema doc first for drift against the now
    updated canonical graph contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:43:59Z
  TYPE: FACT
  CLAIM: The first concrete example-doc drift seam is the example graph
    workflow doc. The canonical graph contract now documents node/edge schema,
    relation vocabulary, and the storage-vs-readable consumption split in much
    more detail, but the example graph doc still demonstrates only the older
    minimal workflow and no longer shows enough of the current contract to act
    as a good template.
  EVIDENCE:
  - codex/context_compass/examples/example_graph_details/graph_details_document.md:1-31
  - codex/context_compass/system_docs/graph_details_document.md:64-186
  IMPACT: The example graph doc now underspecifies the current graph contract
    and can mislead future doc authors toward a thinner graph workflow than the
    canonical doc actually requires.
  NEXT: patch the example graph details doc to include a compact schema,
    relation-vocabulary, and readable-vs-storage explanation while staying
    smaller than the canonical doc.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:45:54Z
  TYPE: FACT
  CLAIM: `example_components/tests_components.md` is now the odd one out among
    the example docs. The other example architecture/components surfaces are
    repo-grounded, but this example still anchors its C1 map and information
    sources to the `user_defined/synaptic_python_developer` overlay instead of
    current repo-level test support surfaces.
  EVIDENCE:
  - codex/context_compass/examples/example_components/tests_components.md:38-44
  - codex/context_compass/examples/example_architecture/src_architecture.md:48-73
  - codex/context_compass/examples/example_components/src_components.md:74-94
  IMPACT: The example tests-components template no longer matches the style of
    the other repo-grounded examples and can mislead future doc authors toward
    overlay-specific evidence choices.
  NEXT: patch the example tests-components C1 map and information sources to
    use small repo-grounded test support/example paths instead of the
    user-defined overlay.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:48:00Z
  TYPE: FACT
  CLAIM: The repo-grounded example architecture/components docs still carry old
    verification snapshots. Their `Last verified at` fields and C1 line-count
    entries still reflect February 2026 values even though the referenced live
    files have changed materially since then.
  EVIDENCE:
  - codex/context_compass/examples/example_architecture/src_architecture.md:3-6
  - codex/context_compass/examples/example_architecture/src_architecture.md:54-72
  - codex/context_compass/examples/example_components/src_components.md:3-6
  - codex/context_compass/examples/example_components/src_components.md:66-84
  - validation_result: `SKILLS.md 65`
  - validation_result: `config/context_compass_config.yaml 134`
  - validation_result: `attention_board.md 249`
  - validation_result: `artifact_board.md 124`
  - validation_result: `templates/task_template.md 91`
  - validation_result: `tickets/tasks/README.md 52`
  - validation_result: `examples/eng_task_flow.md 23`
  IMPACT: The example docs currently demonstrate stale verification habits
    instead of the current repo state, which undercuts their value as
    high-fidelity examples.
  NEXT: patch the example architecture/components metadata and C1 line-count
    snapshots to current values.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:49:34Z
  TYPE: FACT
  CLAIM: The example docs are still inconsistent about metadata richness.
    The repo-grounded example architecture/components docs now carry refreshed
    verification metadata, but `example_components/tests_components.md` still
    has only a one-line metadata marker and
    `example_graph_details/graph_details_document.md` still has no metadata
    block at all.
  EVIDENCE:
  - codex/context_compass/examples/example_architecture/src_architecture.md:1-7
  - codex/context_compass/examples/example_components/src_components.md:1-6
  - codex/context_compass/examples/example_components/tests_components.md:1-4
  - codex/context_compass/examples/example_graph_details/graph_details_document.md:1-4
  IMPACT: The example set no longer presents a consistent template standard for
    metadata and verification posture.
  NEXT: patch the example tests-components and example graph-details docs to
    carry compact metadata blocks aligned with the other repo-grounded examples.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:50:55Z
  TYPE: FACT
  CLAIM: `example_components/tests_components.md` now has one internal
    consistency seam left: its new metadata block says
    `Last verified at: 2026-06-13T20:49:34Z`, but the individual C1
    `verified_at` fields still lag at `2026-06-13T20:45:54Z`.
  EVIDENCE:
  - codex/context_compass/examples/example_components/tests_components.md:3-7
  - codex/context_compass/examples/example_components/tests_components.md:41-56
  IMPACT: The example doc would be internally inconsistent even though the
    referenced paths are correct.
  NEXT: patch the three C1 `verified_at` fields to match the refreshed metadata
    timestamp.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:52:35Z
  TYPE: FACT
  CLAIM: The example architecture/repo-overview surfaces still describe a
    pre-mailbox state model. They list `attention_board.md` and
    `artifact_board.md`, but still omit `mailbox_board.md` and
    `context_management/context_board.md`, which are now part of the current
    durable execution model.
  EVIDENCE:
  - codex/context_compass/examples/example_architecture/src_architecture.md:28-31
  - codex/context_compass/examples/repo_overview.md:14-20
  IMPACT: The example docs still teach an older narrower Context Compass state
    surface than the live repo now uses.
  NEXT: patch the example architecture and repo-overview docs to include the
    mailbox and context-board surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:54:12Z
  TYPE: FACT
  CLAIM: The example architecture doc now has one immediate consistency seam
    after that state-surface patch: it names `mailbox_board.md` and
    `context_management/context_board.md` in the boundary section, but its C1
    code map and information sources still omit those two surfaces.
  EVIDENCE:
  - codex/context_compass/examples/example_architecture/src_architecture.md:28-33
  - codex/context_compass/examples/example_architecture/src_architecture.md:58-86
  - codex/context_compass/examples/example_architecture/src_architecture.md:101-106
  IMPACT: The example architecture doc now claims a broader state model than
    its own evidence and code map demonstrate.
  NEXT: patch the example architecture C1 map and information sources to
    include mailbox and context-board surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T20:55:32Z
  TYPE: FACT
  CLAIM: `repo_overview.md` still has one immediate flow-order seam after the
    folder-map patch. It now lists `mailbox_board.md` and
    `context_management/context_board.md` in the repo surface map, but the
    “How To Read This Repo Fast” sequence still skips both of them.
  EVIDENCE:
  - codex/context_compass/examples/repo_overview.md:14-20
  - codex/context_compass/examples/repo_overview.md:31-36
  IMPACT: The same example doc now lists those surfaces as important but does
    not tell readers when to read them.
  NEXT: patch the read-order steps in `repo_overview.md` to include mailbox and
    context-board checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T22:11:25Z
  TYPE: FACT
  CLAIM: The example workflow docs now lag the rest of the refreshed example
    set. `repo_overview.md` and the example architecture doc already teach the
    mailbox/context-board state model, but `eng_task_flow.md` and
    `design_task_flow.md` still show the older lightweight flow and omit the
    current certification and active-route checks.
  EVIDENCE:
  - codex/context_compass/examples/eng_task_flow.md:8-31
  - codex/context_compass/examples/design_task_flow.md:7-35
  - codex/context_compass/examples/repo_overview.md:17-20
  - codex/context_compass/examples/repo_overview.md:39-41
  - codex/context_compass/attention_board.md:3-29
  IMPACT: The example set now disagrees internally about how real repo-based
    work starts and stays routed, which makes the workflow examples weaker than
    the refreshed overview and architecture templates.
  NEXT: patch the two workflow example docs so they include certification,
    attention-board/mailbox routing, optional context-board usage, and
    closeout sync expectations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T22:14:28Z
  TYPE: MEASURE
  CLAIM: The workflow-example patch is landed and locally validated. Both
    `eng_task_flow.md` and `design_task_flow.md` now expose certification,
    attention-board routing, mailbox checks, optional context-board usage, and
    closeout sync expectations.
  EVIDENCE:
  - codex/context_compass/examples/eng_task_flow.md:8-46
  - codex/context_compass/examples/design_task_flow.md:7-44
  - validation_result: `rg -n "AGENT_NAME|CERTIFY: APPROVED|attention_board|mailbox_board|context_management/context_board|Context / Handoff Summary" codex/context_compass/examples/eng_task_flow.md codex/context_compass/examples/design_task_flow.md`
  IMPACT: The example workflow pair now matches the repo-grounded operating
    model instead of the older lightweight flow.
  NEXT: inspect the example release-readiness epic/story/task against the live
    templates to find the next bounded schema drift seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T22:14:28Z
  TYPE: FACT
  CLAIM: The example release-readiness ticket chain now lags the live template
    schema. The current task, story, and epic examples still omit `Agent Name`
    metadata and `Context Management`, and the story/epic examples also miss
    several newer template sections that now shape durable ticket structure.
  EVIDENCE:
  - codex/context_compass/templates/task_template.md:5-110
  - codex/context_compass/templates/story_template.md:5-117
  - codex/context_compass/templates/epic_template.md:5-135
  - codex/context_compass/examples/example_tasks/2026-02-19_context_compass_release_readiness_pack_task.md:3-145
  - codex/context_compass/examples/example_stories/2026-02-19_context_compass_release_readiness_examples_story.md:3-119
  - codex/context_compass/examples/example_epics/2026-02-19_context_compass_release_readiness_example_pack_epic.md:3-127
  IMPACT: The example ticket chain no longer demonstrates the current template
    contract, so the refreshed workflow docs now point readers at examples that
    still underrepresent the modern ticket shape.
  NEXT: patch the example task/story/epic to add the current schema surfaces
    with repo-grounded values, starting with `Agent Name`, `Context Management`,
    and the missing section blocks each template now requires.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T22:16:48Z
  TYPE: MEASURE
  CLAIM: The example release-readiness ticket chain is now aligned to the live
    template schema. The task, story, and epic examples all carry `Agent Name`,
    `Context Management`, and the previously missing section blocks their
    current templates require.
  EVIDENCE:
  - codex/context_compass/examples/example_tasks/2026-02-19_context_compass_release_readiness_pack_task.md:3-127
  - codex/context_compass/examples/example_stories/2026-02-19_context_compass_release_readiness_examples_story.md:3-149
  - codex/context_compass/examples/example_epics/2026-02-19_context_compass_release_readiness_example_pack_epic.md:3-170
  - validation_result: `rg -n "Agent Name|## Context Management|## Noting Behavior|## Open Questions|## Decision Log|## Dependencies / Related Work|## Requirements \\(Functional \\+ Non-Functional\\)|## Constraints / Assumptions|## Rollout / Adoption Plan" codex/context_compass/examples/example_tasks/2026-02-19_context_compass_release_readiness_pack_task.md codex/context_compass/examples/example_stories/2026-02-19_context_compass_release_readiness_examples_story.md codex/context_compass/examples/example_epics/2026-02-19_context_compass_release_readiness_example_pack_epic.md`
  IMPACT: The example workflow docs now point at example tickets that match the
    current ticket contract instead of an older schema snapshot.
  NEXT: inspect `artifact_workflow.md` and `adr_example.md` against the current
    artifact and ADR examples to find the last top-level example drift seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T22:16:48Z
  TYPE: FACT
  CLAIM: The last obvious top-level example seams are `artifact_workflow.md`
    and `adr_example.md`. The artifact workflow still reduces the process to
    create/link/disposition only, and the ADR example still lacks the current
    options/tradeoffs/validation structure shown in the role-local design
    example.
  EVIDENCE:
  - codex/context_compass/examples/artifact_workflow.md:1-20
  - codex/context_compass/examples/adr_example.md:1-28
  - codex/context_compass/agent_onboarding/default/engineer/examples/artifact_workflow.md:1-78
  - codex/context_compass/agent_onboarding/default/design_engineer/examples/adr_example.md:1-28
  IMPACT: The top-level example set is close to converged, but these two
    reference docs still under-teach the current artifact/ADR discipline.
  NEXT: patch `artifact_workflow.md` and `adr_example.md` to match the current
    repo-grounded examples without widening back into canonical live-doc work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T22:19:47Z
  TYPE: MEASURE
  CLAIM: The top-level artifact and ADR examples are now aligned to the current
    repo-grounded references. `artifact_workflow.md` now teaches the
    ticket/artifact-board split, and `adr_example.md` now carries the fuller
    title/options/tradeoffs/validation/link structure used by the live design
    example.
  EVIDENCE:
  - codex/context_compass/examples/artifact_workflow.md:1-34
  - codex/context_compass/examples/adr_example.md:1-45
  - validation_result: `rg -n "artifact_board|Artifact Links|attention_board|Title|Status|Options considered|Tradeoffs|Validation|Links" codex/context_compass/examples/artifact_workflow.md codex/context_compass/examples/adr_example.md`
  IMPACT: The last thin top-level example references now match the current
    artifact and ADR discipline instead of teaching the older minimal forms.
  NEXT: run one broader example-only sweep and decide whether the bounded
    example-doc lane is locally exhausted.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T22:19:47Z
  TYPE: MEASURE
  CLAIM: The bounded example-doc sweep is now locally clean for the concrete
    seams investigated in this lane. Architecture/components/graph examples,
    repo overview, workflow examples, example ticket chain, artifact workflow,
    and ADR example all reflect the current repo-grounded model. Remaining
    example hits in the final grep sweep are historical note text, stable
    example IDs, or intentional placeholder references inside the example
    narrative itself rather than live drift.
  EVIDENCE:
  - validation_result: `rg -n "AGENT_NAME|CERTIFY: APPROVED|mailbox_board|context_management/context_board|artifact_board|Artifact Links \\(Optional\\)|Agent Name|Context Management|Noting Behavior|Context / Handoff Summary" codex/context_compass/examples -g "*.md"`
  - validation_result: `rg -n "user_defined/synaptic_python_developer|context_compass_release_readiness|old slugs|older lightweight flow|placeholder" codex/context_compass/examples -g "*.md"`
  IMPACT: The active example-doc lane no longer has an obvious next in-scope
    patch slice from this targeted audit.
  NEXT: decide whether to close the example-doc lane or open a new bounded docs
    lane elsewhere in Context Compass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T22:46:44Z
  TYPE: FACT
  CLAIM: A broader example-only sweep exposed one more bounded top-level seam
    inside the role-flow references. `platform_task_flow.md`, `qa_task_flow.md`,
    `security_review_flow.md`, and `researcher_task_flow.md` still use older
    lightweight layouts that diverge from both their role-local source examples
    and the refreshed repo-grounded engineer/design example style.
  EVIDENCE:
  - codex/context_compass/examples/platform_task_flow.md:1-26
  - codex/context_compass/examples/qa_task_flow.md:1-26
  - codex/context_compass/examples/security_review_flow.md:1-24
  - codex/context_compass/examples/researcher_task_flow.md:1-25
  - codex/context_compass/agent_onboarding/default/platform_engineer/examples/platform_task_flow.md:2-20
  - codex/context_compass/agent_onboarding/default/qa_engineer/examples/qa_task_flow.md:2-22
  - codex/context_compass/agent_onboarding/default/security_engineer/examples/security_review_flow.md:2-20
  - codex/context_compass/agent_onboarding/default/researcher/examples/researcher_task_flow.md:1-25
  IMPACT: The top-level example set is still inconsistent across role-flow
    references even though the core architecture, workflow, ticket, artifact,
    and ADR example surfaces are now aligned.
  NEXT: patch those four role-flow example docs into the same modern
    repo-grounded example shape used by the refreshed top-level examples.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T22:48:18Z
  TYPE: FACT
  CLAIM: The same drift pattern continues into the fiction/editor role-flow
    examples. `draft_writer_task_flow.md`,
    `developmental_editor_task_flow.md`, `line_copy_editor_task_flow.md`, and
    `proofreader_task_flow.md` still use older lightweight layouts and under-teach
    the gate/handoff/pass-condition shape shown in their role-local source
    examples.
  EVIDENCE:
  - codex/context_compass/examples/draft_writer_task_flow.md:1-17
  - codex/context_compass/examples/developmental_editor_task_flow.md:1-15
  - codex/context_compass/examples/line_copy_editor_task_flow.md:1-17
  - codex/context_compass/examples/proofreader_task_flow.md:1-17
  - codex/context_compass/agent_onboarding/default/draft_writer/examples/draft_writer_task_flow.md:1-18
  - codex/context_compass/agent_onboarding/default/developmental_editor/examples/developmental_editor_task_flow.md:1-17
  - codex/context_compass/agent_onboarding/default/line_copy_editor/examples/line_copy_editor_task_flow.md:1-17
  - codex/context_compass/agent_onboarding/default/proofreader/examples/proofreader_task_flow.md:1-17
  IMPACT: Even after the first role-flow batch, the top-level example set is
    still inconsistent across the fiction/editor surfaces.
  NEXT: patch those four fiction/editor role-flow examples into the same modern
    shape used by the refreshed top-level role-flow references.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-13T22:49:36Z
  TYPE: FACT
  CLAIM: The last untouched role-flow references show the same drift pattern.
    `continuity_fact_checker_task_flow.md`, `story_designer_task_flow.md`, and
    `story_novel_artist_task_flow.md` still use the older lightweight layout
    and underrepresent the fuller artifact/pass-condition shape shown in their
    role-local source examples.
  EVIDENCE:
  - codex/context_compass/examples/continuity_fact_checker_task_flow.md:1-17
  - codex/context_compass/examples/story_designer_task_flow.md:1-17
  - codex/context_compass/examples/story_novel_artist_task_flow.md:1-15
  - codex/context_compass/agent_onboarding/default/continuity_fact_checker/examples/continuity_fact_checker_task_flow.md:1-17
  - codex/context_compass/agent_onboarding/default/story_designer/examples/story_designer_task_flow.md:1-19
  - codex/context_compass/agent_onboarding/default/story_novel_artist/examples/story_novel_artist_task_flow.md:1-19
  IMPACT: After the earlier role-flow patches, these three are now the last
    obvious inconsistent top-level role-flow references in the example set.
  NEXT: patch those three role-flow docs and then rerun the example-only sweep
    to see whether the bounded example-doc lane is finally exhausted.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task continues the documentation program after the live source-doc and
tests-doc local-evidence passes converged. It is intentionally bounded to the
example docs as template/reference surfaces.
