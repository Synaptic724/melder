Completed: 2026-06-12T12:29:40Z
Summary: Closed as a stale tranche ticket after the older graph-population lane
was superseded by a fresh documentation-drift investigation epic.

# Task: Populate Src Graph For Aether Second Tranche

## Metadata
- Task ID: TASK-2026-04-19-populate-src-graph-for-aether-second-tranche
- Story: STORY-2026-04-19-populate-src-graph-for-aether-directory
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T20:03:32Z
- Updated: 2026-06-12T12:29:40Z

## Objective
Continue the `aether` graph lane by populating the deeper record, contract, and
ACL-leaf objects that support the already-modeled runtime and AR root layers.

## Ticket Contract
- ENTRY_GATE: the first `aether` tranche is in review and the story still has
  deeper `aether` objects that matter structurally.
- EXECUTION_BOUNDARY:
  - deeper `src/melder/aether/**` record, contract, and ACL-leaf objects
  - `codex/context_compass/system_docs/src_graph.json`
  - patch-lane expanded graph working copy for the active `aether` story
- DEPENDENCIES:
  - `tickets/tasks/2026-04-19_populate_src_graph_for_aether_first_tranche_task.md`
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - `codex/context_compass/system_docs/graph_details_document.md`
- EXIT_GATE: the second `aether` tranche lands the next high-value record,
  contract, and ACL-leaf nodes and edges with JSON validation still green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the second tranche starts to
  devolve into low-signal leaf inventory instead of meaningful structure.

## Scope Boundaries
- In scope:
  - descriptor records and payload-supporting aether-side record objects
  - conduit contract objects and lineage-supporting leaf objects
  - deeper ACL leaf objects only when they materially clarify the `aether`
    ownership model
- Out of scope:
  - `tests/**`
  - utilities-wide infrastructure
  - spellbook-owned graph-build internals

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the first `aether` tranche is coherent enough to hand off
  and the story still has a deeper leaf/object layer worth graphing.

## Steps / Checklist
- [ ] Choose the next high-value `aether` record/contract/ACL leaf set from
      source evidence.
- [ ] Read the selected files in compliant chunks where needed.
- [ ] Record the next meaningful finding in `## Notes` before graph edits.
- [ ] Patch the expanded graph working copy.
- [ ] Recompress and validate the canonical graph.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- second `aether` graph tranche
- updated `src_graph.json`
- validation record and tranche notes

## Files / Paths Impacted
- src/melder/aether/
- codex/context_compass/system_docs/src_graph.json
- codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json
- codex/context_compass/tickets/tasks/2026-04-19_populate_src_graph_for_aether_second_tranche_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/system_docs/src_graph.json -Raw | ConvertFrom-Json | Out-Null`

## Risks / Rollback Notes
- Risk: the second tranche widens into low-signal leaf coverage.
  Rollback: stop at the next meaningful structural boundary and hand the story
  off once the graph stops getting denser in useful ways.

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
  - system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the active `aether` story is complete or the
  working copy is replaced by a later patch-lane artifact.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-19T20:03:32Z
  TYPE: PLAN
  CLAIM: The second `aether` tranche should not reopen the already-modeled
    root/frame/runtime objects. It should focus on the next high-value leaf
    layer: records, contracts, and ACL-related objects that materially sharpen
    the existing graph without turning into noise.
  EVIDENCE:
  - tickets/tasks/2026-04-19_populate_src_graph_for_aether_first_tranche_task.md: current note stack
  - codex/context_compass/system_docs/src_graph.json: current graph shape
  IMPACT: The story can continue without making the first tranche unmanageably
    broad.
  NEXT: choose the next high-value `aether` leaf/object set from source
    evidence before patching the graph.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:12:34Z
  TYPE: FACT
  CLAIM: The next best leaf layer is the descriptor-record and contract-detail
    layer. The current graph explains who owns the managers, wards, and
    projections, but it still underexplains the concrete record/detail objects
    those parents actually own:
    - `FrameRecord`
    - `ConduitRecord`
    - `SpellRecord`
    - their descriptor payload objects
    - `Contract`
    - `Detail`
    Those objects are structurally meaningful because they are the owned units
    of publication and contracting, not just passive data noise.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:11-47
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:11-47
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:12-58
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor_payload.py:11-38
  - src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py:10-38
  - src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py:27-93
  - src/melder/aether/conduit/conduit_ward/contract/contract.py:13-31
  - src/melder/aether/conduit/conduit_ward/contract/details.py:13-31
  IMPACT: The second tranche should deepen the graph at the record/detail level
    before drifting into lower-value enum or helper coverage.
  NEXT: patch the expanded graph with the record/detail nodes and the ownership
    edges that connect them to `FrameDescriptorManager`, `FrameDescriptor`, and
    `ConduitWard`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:13:59Z
  TYPE: FACT
  CLAIM: The second `aether` tranche now includes the descriptor-record and
    contract-detail layer. The graph adds:
    - `FrameRecord`
    - `ConduitRecord`
    - `SpellRecord`
    - `FrameDescriptorPayload`
    - `ConduitDescriptorPayload`
    - `SpellDescriptorPayload`
    - `Contract`
    - `Detail`
    and the matching ownership edges from `FrameDescriptor` to its records,
    from each record to its payload, and from `ConduitWard` to `Contract` to
    `Detail`.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:11-47
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:11-47
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:12-58
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor_payload.py:11-38
  - src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py:10-38
  - src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py:27-93
  - src/melder/aether/conduit/conduit_ward/contract/contract.py:13-31
  - src/melder/aether/conduit/conduit_ward/contract/details.py:13-31
  - codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json:1-1110
  IMPACT: The graph now explains not just who owns the managers and wards, but
    the concrete publication and contract units those owners actually manage.
  NEXT: choose the next high-value `aether` leaf set from source evidence
    rather than widening blindly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:13:59Z
  TYPE: MEASURE
  CLAIM: The expanded and canonical graph both still validate as JSON after the
    record/detail patch and recompression.
  EVIDENCE:
  - validation_result: `Get-Content codex/context_compass/system_docs/src_graph.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_CANONICAL_GRAPH_AFTER_RECORD_PATCH`
  - validation_result: `Get-Content codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_EXPANDED_GRAPH_AFTER_RECORD_PATCH`
  IMPACT: The graph remains structurally sound while the second tranche deepens
    the publication and contract model.
  NEXT: decide the next `aether` leaf set from evidence instead of adding more
    leaf objects by habit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:13:59Z
  TYPE: DECISION
  CLAIM: The next `aether` leaf set should be the ACL runtime core, not enum or
    helper noise. `FrameACLManager` is already in the graph, but without
    `FrameACLContainer`, `FrameACLConfiguration`, `FrameACLCompiler`,
    `CompiledFrameACLAccessSurface`, `FrameACLValidator`, and
    `FrameACLSetCompatibilityValidator`, the graph still cannot explain what the
    ACL manager actually owns or what the projections are built from.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_container.py:29-58
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:24-71
  - src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py:9-38
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:44-83
  - src/melder/aether/nexus/acl/validator/frame_acl_validator.py:52-85
  - src/melder/aether/nexus/acl/validator/compatibility/frame_acl_set_compatibility_validator.py:25-54
  IMPACT: One more targeted patch will make the `aether` graph materially more
    honest about the ACL and projection substrate before we consider handing
    the story off.
  NEXT: patch the graph with the ACL core nodes and the manager/container/
    compiler/validator relationships.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T20:16:31Z
  TYPE: DECISION
  CLAIM: The `aether` graph is now coherent enough to stop widening for now.
    Between the first and second tranches it covers:
    - substrate roots
    - frame-local services
    - conduit/dev-ops runtime ownership
    - AR projection/viewer flow
    - room-mode specialization
    - descriptor record ownership
    - contract/detail ownership
    - ACL container/compiler/validator relationships
    Continuing deeper in `aether` right now would mostly add lower-value chain
    and enum noise instead of materially improving the system map.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json:1-1267
  - validation_result: `Get-Content codex/context_compass/system_docs/src_graph.json -Raw | ConvertFrom-Json | Out-Null` -> `OK_CANONICAL_GRAPH_AFTER_ACL_PATCH`
  IMPACT: The next honest move is to shift active population to the
    `spellbook` story instead of inflating the `aether` story.
  NEXT: activate the first `spellbook` tranche and start with the top-level
    spellbook and spell crafter root objects.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the second active `aether` graph-population tranche.
