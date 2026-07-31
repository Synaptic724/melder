

# Task: Diagnose readable_src_graph.json consumption cost and rule on an index

## Metadata
- Task ID: TASK-2026-07-29-readable-src-graph-consumption-index
- Story: none (standalone task)
- Status: in_progress
- Owner: cowork
- Agent Name: helper_f1
- Priority: p1
- Created: 2026-07-29T22:41:09Z
- Updated: 2026-07-29T22:41:09Z

## Objective
Establish with measured evidence WHY `system_docs/readable_src_graph.json` has become
unreadable in a single onboarding pass, separate spec-mandated size from actual drift,
and bring the owner one `DECISION_REQUEST` on the fix direction. Diagnosis only; no
graph edits and no regeneration in this task.

## Ticket Contract
- ENTRY_GATE: active `attention_board.md` row routes to this task; owner ruling on record
  that `readable_src_graph.json` + `src_graph.json` are SKIPPED as onboarding reads for
  the 2026-07-29 cycle.
- EXECUTION_BOUNDARY: read-only measurement over `system_docs/src_graph.json` and
  `system_docs/readable_src_graph.json` (aggregate statistics only, no content dump);
  read-only reference to `graph_details_document.md`,
  `agent_onboarding/default/engineer/skills/graph_details_usage.md`,
  `agent_onboarding/default/engineer/skills/graph_details_readable_generation.md`,
  `special_instructions/new_skills/system_doc_index_generation.md`,
  `special_instructions/new_skills/system_doc_index_usage.md`.
  Writes limited to this ticket, `attention_board.md`, `mailbox_board.md`.
- DEPENDENCIES: `TASK-2026-07-26-system-doc-index-skills` (melder_1) authored the index
  generation/usage contract this task evaluates for JSON reuse; that task is still open
  in `review`.
- EXIT_GATE: measured field/size distribution recorded in `## Notes` with evidence; the
  spec-mandated vs drift split stated as FACT or left UNKNOWN; one `DECISION_REQUEST`
  posted for the owner; no graph bytes modified.
- FAILURE_ESCALATION: raise `BLOCKER` if the graph cannot be measured without a full
  content read; raise `CONFLICT` if measurement contradicts `graph_details_document.md`
  coverage or schema rules.

## Scope Boundaries
- In scope:
  - aggregate measurement of node/edge counts and per-field string lengths
  - reconciling measured size against the coverage + schema mandates in the spec
  - assessing whether the existing index skill pair can be applied to a JSON artifact
  - one owner decision ask on fix direction
- Out of scope:
  - editing `src_graph.json` or regenerating `readable_src_graph.json`
  - generating an actual index file (that is the follow-on lane, if approved)
  - trimming node/edge semantics (the spec mandates them; not an agent call)
  - porting the `new_skills/` index skills into the role chain

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner assigned the graph size question directly and certified
  `helper_f1` this cycle; first finding is already evidenced, so the lane is active
  rather than merely planned.

## Steps / Checklist
- [x] Establish that the readable view is a faithful reflow, not a bloated re-render
- [ ] Measure node count, edge count, and per-field string-length distribution
- [ ] Split measured size into spec-mandated cost vs prose drift (or mark UNKNOWN)
- [ ] Check whether any `readable_src_graph_index.json` precedent exists
- [ ] Post one `DECISION_REQUEST`: index the graph vs shard it vs leave as-is
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Measured size/field distribution recorded in this ticket's `## Notes`
- An evidence-backed statement of what is spec-mandated vs what is drift
- One `DECISION_REQUEST` for the owner on fix direction

## Files / Paths Impacted
- `context_compass/tickets/tasks/2026-07-29_readable_src_graph_consumption_index_task.md`
- `context_compass/attention_board.md`
- `context_compass/mailbox_board.md`

## Validation
- Not run.
- Recommended commands (owner-run, once a fix direction is chosen):
  - `python -c "import json;json.load(open('context_compass/system_docs/readable_src_graph.json'))"`
  - `pytest tests/unit/melder -q`

## Risks / Rollback Notes
- Measurement is read-only, so there is nothing to roll back in this task.
- RISK: proposing any reduction of node/edge semantics would violate
  `graph_details_document.md` and turn the graph into the import-graph noise that doc
  explicitly rejects. The fix direction must not be "make the graph smaller".
- RISK: a line-offset index over a regenerated artifact goes stale instantly; any index
  must carry `line_count` + `content_sha256` + `line_ending` per the index contract.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No treating the compressed canonical file as a line-based read surface.
- [ ] No hand-editing the compressed canonical graph.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: not applicable while no artifacts exist

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
- DATETIME: 2026-07-29T22:41:09Z
  TYPE: FACT
  CLAIM: The readable view is a faithful raw-text reflow, so the generation step is NOT
    the cause of the size. `src_graph.json` is 767,788 bytes; `readable_src_graph.json`
    is 776,314 bytes over 4,263 lines. The delta is 8,526 bytes, which equals
    4,262 x 2 - exactly the CRLF terminators inserted by the reflow. Mean line length is
    ~182 chars, inside the 220-char contract. Nobody pretty-printed or reshaped it.
  EVIDENCE:
  - context_compass/system_docs/graph_details_document.md:277-289
  - context_compass/agent_onboarding/default/engineer/skills/graph_details_readable_generation.md:14-39
  IMPACT: Rules out the regeneration recipe as the defect and relocates the question to
    the canonical graph payload itself, so no time is spent auditing the reflow.
  NEXT: Measure node count, edge count, and per-field string-length distribution over
    `src_graph.json` using aggregates only (no content dump).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-29T22:41:09Z
  TYPE: HYPOTHESIS
  CLAIM: The ~767 KB canonical size is mostly SPEC-MANDATED rather than rot. The spec
    requires exhaustive coverage of every non-`__init__.py` file under `src/melder/**`
    (scaffold-only files still get a `module` node) AND four semantic fields per node
    plus four per edge. Exhaustive coverage multiplied by mandated per-object semantics
    produces roughly 1.4 KB per node by construction. If so, "why did it get so big" has
    a boring answer: it was specified to.
  EVIDENCE:
  - context_compass/system_docs/graph_details_document.md:88-134
  - context_compass/system_docs/graph_details_document.md:135-172
  - context_compass/system_docs/graph_details_document.md:205-225
  IMPACT: Decides the fix direction. If size is mandated, shrinking the graph is the
    wrong move and would violate the doc's own anti-pattern list; the problem is then a
    CONSUMPTION gap, not a content gap.
  NEXT: Falsify or confirm with a per-field length histogram; a long tail of
    paragraph-length `role`/`why` strings would indicate drift on top of the mandate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-29T22:41:09Z
  TYPE: UNKNOWN
  CLAIM: Whether individual `role`, `responsibilities`, `owns_state`, or edge `why`
    strings have drifted into long-form prose ON TOP OF the mandated richness is not yet
    evidenced. The spec rejects "duplicating long-form architecture/components prose
    into the graph", but no measurement has been taken, so no drift claim is justified.
  EVIDENCE:
  - context_compass/system_docs/graph_details_document.md:423-437
  IMPACT: This is the only part of the size question that could represent a real defect.
    It must not be asserted without a histogram.
  NEXT: Run the aggregate field-length measurement and record the distribution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-07-29T22:41:09Z
  TYPE: FACT
  CLAIM: The largest artifact in `system_docs/` is the only large one with no line-range
    index. `src_architecture_index.json` (72 sections, line_count 2079) and
    `src_components_index.json` (156 sections, line_count 5176) both exist; there is no
    `readable_src_graph_index.json`. Meanwhile `graph_details_usage.md` designates the
    readable graph the PRIMARY consumption surface and says to read it in bounded
    chunks - which at `codex.read_loc_max` 500 is nine sequential reads of
    undifferentiated JSON with no way to know which chunk holds a given subsystem.
  EVIDENCE:
  - context_compass/agent_onboarding/default/engineer/skills/graph_details_usage.md:34-38
  - context_compass/special_instructions/new_skills/system_doc_index_generation.md:47-67
  - context_compass/config/context_compass_config.yaml:138-140
  IMPACT: Reframes the lane from "the graph is too big" to "the graph has no addressing
    scheme". An index over the graph could key on fully-qualified node ids, giving
    subsystem-to-line-range lookup that is strictly more precise than heading
    breadcrumbs over markdown.
  NEXT: Post the `DECISION_REQUEST` on fix direction once the histogram lands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-29T22:52:40Z
  TYPE: MEASURE
  CLAIM: Measured aggregate over `src_graph.json`: 535 nodes, 997 edges, schema_version 1
    (node count matches the board's post-fix claim, so the board is accurate). Node
    objects total 317,509 B (593/node); edge objects total 399,205 B (400/edge); payload
    716,714 B. Method: `json.dumps(separators=(",",":"))` per object, aggregates only, no
    content dumped.
  EVIDENCE:
  - context_compass/system_docs/src_graph.json:1-1
  - context_compass/attention_board.md:87-87
  IMPACT: Establishes the denominator for every share claim below and confirms edges, not
    nodes, are the larger half of the payload (56% vs 44%).
  NEXT: Attribute payload to identity fields vs semantic fields.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-29T22:52:40Z
  TYPE: FACT
  CLAIM: HYPOTHESIS ABOVE IS PARTLY WRONG - the mandated SEMANTICS are not the cost
    driver. IDENTITY REPETITION is. Fully-qualified dotted paths total 269,874 chars
    (37.7% of payload): node `id` 47,897 + node `file` 42,657 + edge `from` 92,839 +
    edge `to` 86,481. All mandated semantic fields together total 246,900 chars (34.4%):
    `role` 33,772 + `responsibilities` 87,912 + `owns_state` 20,913 + `phases` 7,171 +
    edge `why` 97,132. Identity outweighs meaning. Worst concentration is in edges, where
    `from`+`to` are 179,320 of 399,205 B = 45% of all edge payload while `why` is only
    24%. Mean id is 90 chars (max 186) and every edge stores two of them verbatim.
    Additionally the nodes map is KEYED by id while each node object also carries an `id`
    field, so all 47,897 chars of node ids are stored twice - mandated by the node
    contract, which requires `id` even though it duplicates the key.
  EVIDENCE:
  - context_compass/system_docs/graph_details_document.md:88-134
  - context_compass/system_docs/graph_details_document.md:135-172
  IMPACT: Decisive for fix direction. Every semantic field could be deleted and the file
    would still be ~450 KB, so trimming meaning cannot solve this and would violate
    `graph_details_document.md:433`. Interning node ids behind short aliases in edge
    endpoints would cut roughly 130-180 KB while preserving 100% of the semantics - the
    owner's "the structure is the point" holds, and the structure is not what costs.
  NEXT: Post the DECISION_REQUEST; interning changes the schema and is owner authority.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-29T22:52:40Z
  TYPE: FACT
  CLAIM: Prose drift is REAL but narrow and subsystem-localised, not systemic. `role`
    median 56 / p90 83 but max 451 and p99 335; `responsibilities` (joined) median 156 /
    p90 251 but max 3,347 with 16 items against a median of 3; edge `why` median 94 /
    p90 127 but max 470. Seven of the ten longest `role` strings and five of the ten
    longest `why` strings belong to `melder.mutation_research.*` surfaces. The
    distribution is tight everywhere else.
  EVIDENCE:
  - context_compass/system_docs/graph_details_document.md:423-437
  IMPACT: Promotes the earlier UNKNOWN to FACT and bounds it: this is one subsystem's
    authoring voice, plausibly a single lane, not a repo-wide rot. A targeted pass over
    `mutation_research.*` nodes/edges plus the one 3,347-char blob is surgical and cheap.
    It is NOT the size fix - the whole long tail is worth only tens of KB.
  NEXT: Fold into the DECISION_REQUEST as a separate, smaller ask.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-29T22:52:40Z
  TYPE: CONFLICT
  CLAIM: The live graph violates its own controlled vocabularies in two places, which
    means the spec's stated validation was never enforced. (1) `kind` is restricted to
    `class` | `component` | `interface` | `module`, but 3 nodes carry `kind: package`.
    Also zero nodes use `component` despite it being allowed. (2) `relation` is
    restricted to a 15-value list, but 5 edges use `owns` (the legal value is
    `owns_lifecycle_of`) and 2 use `delegates_to` - 7 out-of-vocabulary edges. The doc
    calls inventing ad hoc labels a reject-level anti-pattern and lists "relation values
    stay inside the allowed vocabulary" as a required validation.
  EVIDENCE:
  - context_compass/system_docs/graph_details_document.md:112-118
  - context_compass/system_docs/graph_details_document.md:173-203
  - context_compass/system_docs/graph_details_document.md:402-411
  - context_compass/system_docs/graph_details_document.md:423-437
  IMPACT: Independent of size, and arguably more serious: a consumer applying the
    documented interpretation rules in `graph_details_usage.md:70-83` has no meaning for
    `owns`, `delegates_to`, or `package`, so those 7 edges and 3 nodes are silently
    unreadable to any agent following the contract. `owns` vs `owns_lifecycle_of` is the
    exact hard-ownership distinction the graph exists to carry.
  NEXT: Include in the DECISION_REQUEST - either widen the vocabulary deliberately (the
    doc permits intentional schema revision) or normalise the 10 offenders. Not an agent
    call either way.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-29T23:04:00Z
  TYPE: MEASURE
  CLAIM: The graph is NOT over-described; its size tracks repo size almost exactly.
    `src/melder` holds 560 non-`__init__.py` files against 535 graph nodes = 0.96 nodes
    per eligible file, so node count is pinned 1:1 to file count by the exhaustive
    coverage rule, not by authoring choice. Source is 259,068 LOC / 10,385,201 B; the
    graph is 767,788 B = 7.4% of source, or 3.0 bytes of graph per LOC. Description
    budget per node is ~1.5 sentences (mean `role` 63 chars, mean `responsibilities` 164)
    for a file averaging 463 LOC - roughly 30:1 compression. The tree contains 589
    top-level classes and 6,354 `def` statements, and the graph carries NO function-level
    detail at all.
  EVIDENCE:
  - context_compass/system_docs/graph_details_document.md:205-225
  IMPACT: Kills "the graph is bloated" as a framing - per-object density is already
    frugal and cannot be meaningfully reduced without breaching the schema mandate. The
    cost is structural: size multiplied by TREE DEPTH, since ids are fully-qualified
    dotted paths (mean 90 chars) stored twice per edge. A shallow tree of 560 files would
    produce a far smaller graph.
  NEXT: Add sharding to the DECISION_REQUEST as a fourth option alongside interning.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-29T23:04:00Z
  TYPE: TRADEOFF
  CLAIM: Subsystem sharding is a viable alternative to indexing and may dominate it. File
    distribution is heavily lopsided: aether 295 (53%), nexus 122 (22%), crystallizer 59
    (11%), utilities 44 (8%), mutation_research 20 (4%), _build_assets 10 (2%). aether +
    nexus alone are 75% of the tree. Sharding on those boundaries means a crystallizer
    lane loads ~11% of the graph rather than 100%, with NO index machinery to maintain
    and no `content_sha256` staleness contract to enforce. Cost: cross-subsystem edges
    need an owning shard or a separate cross-edge file; at 1.86 edges per node the
    cross-boundary set should be modest, but it is UNMEASURED.
  EVIDENCE:
  - context_compass/agent_onboarding/default/engineer/skills/graph_details_usage.md:34-38
  - context_compass/special_instructions/new_skills/system_doc_index_usage.md:29-51
  IMPACT: An index over a regenerated artifact goes stale on every regeneration and must
    carry line_count + content_sha256 + line_ending to be safe; a shard boundary does
    not, because it is semantic rather than positional. Sharding is the lower-maintenance
    answer if cross-edge count is genuinely low.
  NEXT: If the owner favours sharding, measure the cross-subsystem edge count first -
    that single number decides whether sharding is clean or messy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Owner (2026-07-29) skipped `readable_src_graph.json` and `src_graph.json` as onboarding
reads and assigned `helper_f1` the question of why the artifact grew unreadable. First
finding is settled: the reflow generator is not at fault, the delta between canonical and
readable is exactly the inserted CRLFs. Working position, still a HYPOTHESIS, is that the
size is spec-mandated by exhaustive coverage plus mandated per-node/per-edge semantics,
which would make "shrink the graph" the wrong fix and a spec violation. The one confirmed
gap is addressing: both big markdown docs got line-range indexes on 2026-07-26 and the
776 KB graph did not. Next concrete step is the aggregate field-length histogram to
separate mandate from drift, then a single owner `DECISION_REQUEST` on direction. No graph
bytes have been touched and none will be in this task.
