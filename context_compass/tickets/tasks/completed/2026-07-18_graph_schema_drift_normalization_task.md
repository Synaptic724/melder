

# Task: Normalize graph schema drift to the canonical vocabulary

- Completed: 2026-07-19T00:05:00Z
- Summary: All required-field gaps and off-vocabulary values removed from the canonical graph.
  69 field-level corrections across 5 rules; topology untouched at 537 nodes / 1002 edges.
  Full authoring-contract quality gate now passes.

## Metadata
- Task ID: TASK-2026-07-18-graph-schema-drift-normalization
- Story: none (standalone task)
- Status: done
- Owner: cowork
- Agent Name: melder_0
- Priority: p2
- Created: 2026-07-18T23:58:00Z
- Updated: 2026-07-18T23:58:00Z

## Objective
Bring every node and edge in the canonical graph onto the required-field and canonical-
vocabulary contract. Serialization and graph topology stay unchanged: 537 nodes, 1002 edges.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-18 ("go fucken do the problems you gotta do"); drift
  inventory measured and recorded below with counts.
- EXECUTION_BOUNDARY: `system_docs/src_graph.json`, `system_docs/readable_src_graph.json`,
  and one expand-edit-compress patch lane. No node/edge additions or removals.
- DEPENDENCIES: `agent_onboarding/default/design_engineer/skills/graph_details_instructions.md`
  (required fields, canonical vocabulary, expand-edit-compress workflow).
- EXIT_GATE: zero nodes missing `owns_state`; zero edges missing `cardinality`/`phase`/
  `strength`; `strength` and `cardinality` inside canonical vocabulary; `phase` uniformly
  list-typed; node/edge counts unchanged.
- FAILURE_ESCALATION: DECISION_REQUEST if any normalization would change a documented
  relationship's meaning rather than its encoding.

## Scope Boundaries
- In scope: field encoding and vocabulary normalization only.
- Out of scope: adding/removing nodes or edges; re-deriving relationships from source.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: drift is measured, not hypothesised; each rule below is backed either by
  source or by the dominant existing convention in the same relation class.

## Normalization Rules (each with its basis)
1. `strength: strong` -> `hard` (12 edges). Basis: dominant convention within the same
   relations - `owns_lifecycle_of` 200 hard vs 5 strong, `specializes` 158 vs 2,
   `creates` 135 vs 5. `strong` is a minority synonym from one mutation_research pass.
2. `phase: "runtime"` (str) -> `["runtime"]` (15 edges). Basis: 976 edges already list-typed.
3. `cardinality: "1"` -> `one_to_one` (11 edges); `"N"` -> `one_to_many` (4 edges). Basis:
   canonical vocabulary is one_to_one / one_to_many / many_to_one; these are shorthand.
4. 11 edges missing `cardinality`/`phase`/`strength` entirely: `phase` -> `["runtime"]`;
   `strength` derived per relation from dominant convention (`creates` -> hard,
   `uses`/`borrows`/`delegates_to` -> borrowed); `cardinality` -> `one_to_one`.
   WEAKEST INFERENCE IN THIS PASS: `cardinality` here is read from each edge naming a single
   collaborator, not from source cardinality analysis. Flagged rather than hidden.
5. 5 nodes missing `owns_state`: populated from each class's `__slots__` in source. Three
   are stateless strategies inheriting only the base `__slots__` and correctly get `[]`.

## Deliverables
- Canonical graph with zero required-field gaps and zero off-vocabulary values.

## Files / Paths Impacted
- `context_compass/system_docs/src_graph.json`
- `context_compass/system_docs/readable_src_graph.json`

## Validation
- Not run (`pytest` - this change touches no Python).
- Gate checks recorded in `## Notes`.

## Risks / Rollback Notes
- Pre-change backups from the predecessor lane remain at
  `outputs/graph_backup_2026-07-18/` (pre-serialization-repair state).
- Rule 4's `cardinality` assignment is the one inference that could be wrong per-edge; it is
  encoding-level and correctable without touching topology.

## Applicable Anti-Patterns
- [ ] No editing compressed storage directly - edits go through the patch-lane expanded copy.
- [ ] No inventing new edge verbs or vocabulary values.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Validation status recorded
- [x] Board sync completed

- DATETIME: 2026-07-19T00:05:00Z
  TYPE: MEASURE
  CLAIM: Normalization applied and gate-verified. 69 corrections: 12 `strong`->`hard`,
    15 `phase` str->list, 11 `"1"`->`one_to_one`, 4 `"N"`->`one_to_many`, 11 edges each
    backfilled with cardinality/phase/strength, 5 nodes given `owns_state` from source
    `__slots__`. Final state: nodes missing required fields NONE; edges missing required
    fields NONE; strength {hard 522, borrowed 455, soft 25}; cardinality {one_to_one 668,
    one_to_many 189, many_to_one 145}; phase list-typed on all 1002 edges. Topology
    unchanged at 537/1002, storage == readable, readable 4,284 lines with 19
    spec-sanctioned over-220 tokens.
  EVIDENCE:
  - context_compass/system_docs/src_graph.json:1-1
  - context_compass/system_docs/readable_src_graph.json:1-4284
  - src/melder/mutation_research/group_diff/group_diff_engine.py:1-40
  IMPACT: The graph now satisfies every check in the authoring contract's quality gate.
    Consumers filtering on `strength == "hard"` no longer miss 12 ownership edges, and
    `phase` can be treated as a list unconditionally.
  NEXT: none - lane closed.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T00:06:00Z
  TYPE: RISK
  CLAIM: Residual inference to revisit if graph accuracy is ever questioned: the
    `cardinality: one_to_one` assigned to the 11 previously-empty edges (rule 4) was read
    from each edge naming a single collaborator, NOT from source cardinality analysis. All
    other 68 corrections are backed by source or by dominant in-graph convention.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-07-18_graph_schema_drift_normalization_task.md:44-50
  IMPACT: If any of those 11 relationships is genuinely one-to-many, the encoding is wrong
    while the relationship itself remains correct. Encoding-level, cheaply correctable.
  NEXT: none - recorded for a future graph-accuracy pass.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.

## Notes
- DATETIME: 2026-07-18T23:58:00Z
  TYPE: FACT
  CLAIM: Drift inventory before normalization: `strength` {hard 507, borrowed 447, soft 25,
    strong 12, null 11}; `cardinality` {one_to_one 646, one_to_many 185, many_to_one 145,
    "1" 11, "N" 4, null 11}; `phase` types {list 976, str 15, null 11}; 5 nodes without
    `owns_state`. The off-vocabulary values cluster in mutation_research, indicating one
    authoring pass that used its own shorthand.
  EVIDENCE:
  - context_compass/agent_onboarding/default/design_engineer/skills/graph_details_instructions.md:60-77
  - context_compass/system_docs/src_graph.json:1-1
  IMPACT: Consumers filtering on `strength == "hard"` silently miss 12 hard-ownership edges;
    consumers treating `phase` as a list break on 15 edges.
  NEXT: Apply the five normalization rules through the patch lane.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Encoding-only normalization pass over the canonical graph. Topology untouched.
