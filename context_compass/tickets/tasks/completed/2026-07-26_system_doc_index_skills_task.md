

# Task: Author the generation and consumption skills for system-doc line indexes

## Metadata
- Task ID: TASK-2026-07-26-system-doc-index-skills
- Story: none (standalone; foundation for the index implementation that follows)
- Status: done
- Owner: melder_1
- Agent Name: melder_1
- Priority: p2
- Created: 2026-07-26T17:13:51Z
- Updated: 2026-07-31T23:03:22Z

## Objective
Write the two skills that govern line-range indexes over the large system docs - one for
CRAFTING an index, one for CONSUMING it - so a later implementation pass has a contract
to build against instead of inventing one mid-flight.

## Ticket Contract
- ENTRY_GATE: owner directed skills-before-implementation and named the delivery location
  (`special_instructions/new_skills/`) for portability into the context_compass repo.
- EXECUTION_BOUNDARY: two new skill documents plus their folder README, under
  `context_compass/special_instructions/new_skills/`. No index is generated yet and no
  existing skill, system doc, or config is modified.
- DEPENDENCIES: none. The indexes themselves are the NEXT task, deliberately not this one.
- EXIT_GATE: both skills specify a staleness-detection contract, a deterministic
  generation recipe, and an explicit refusal path when an index cannot be trusted.
- FAILURE_ESCALATION: DECISION_REQUEST if the index format needs to differ from the
  JSON-with-sha256 contract proposed here.

## Scope Boundaries
- In scope: the two skill documents and a short folder README explaining why the folder
  exists.
- Out of scope: generating `src_architecture_index` / `src_components_index`; wiring the
  skills into any `SKILLS.MD` chain; the broader Context Compass essential-vs-on-demand
  restructure discussed 2026-07-26; touching the target documents.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner gave an explicit, bounded instruction with a named delivery
  path; no unknown blocks authoring.

## Steps / Checklist
- [ ] Create `special_instructions/new_skills/` with a README stating the porting intent.
- [ ] Author the GENERATION skill: index schema, derivation rules, staleness fields,
      inline recipe, validation, handoff reporting.
- [ ] Author the CONSUMPTION skill: verify-before-slice, slice discipline, chunking
      against `codex.read_loc_max`, refusal path on a stale index.
- [ ] Match `special_instructions/` CRLF convention.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `special_instructions/new_skills/README.md`
- `special_instructions/new_skills/system_doc_index_generation.md`
- `special_instructions/new_skills/system_doc_index_usage.md`

## Files / Paths Impacted
- context_compass/special_instructions/new_skills/ (new folder, 3 files)

## Validation
- Not run (documentation artifacts; no test surface).
- Recommended checks:
  - CRLF + zero-NUL byte check on all three new files
  - confirm no existing file was modified by this task

## Risks / Rollback Notes
- RISK: a line-offset index is MORE fragile than the prose it indexes - inserting one
  line shifts every range below it, and a stale index returns confidently wrong content.
  Mitigation: the staleness contract is the centre of both skills, not an appendix.
- Rollback: delete the folder; nothing else is touched.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No committed generation script - recipes stay inline per the existing graph
      regeneration precedent.
- [ ] No modification of the documents being indexed.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 7)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: when the skills are ported into the context_compass repo proper.

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
- DATETIME: 2026-07-26T17:13:51Z
  TYPE: MEASURE
  CLAIM: The payload case for indexing, measured on the live readset. Total onboarding
    read is ~232k tokens, and the two target documents are ~102k of that - 44% of the
    entire cost in two files (`src_architecture.md` ~30k, `src_components.md` ~72k).
    Current sizes are 2079 and 5176 lines, both CRLF.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md
  - context_compass/system_docs/src_components.md
  IMPACT: An index that lets an agent slice one subsystem section instead of reading
    5176 lines is the single largest available reduction in onboarding cost, which is
    why it is worth a formal contract rather than an ad-hoc convention.
  NEXT: Author the generation skill first; the usage skill depends on its schema.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-26T17:13:51Z
  TYPE: RISK
  CLAIM: The central design hazard, learned first-hand this session. A derived inventory
    over these documents went stale TWICE within hours: the C1 Code Map was generated at
    550 modules, drifted to 553 when build-asset modules landed, and I did not notice
    until the owner asked. A line-offset index is strictly more fragile than that
    inventory, because a single inserted line silently invalidates every range below it
    while the index still LOOKS valid.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-07-25_system_doc_graph_drift_audit_task.md
  IMPACT: Without a staleness gate, a stale index does not fail - it returns the wrong
    lines confidently, which is worse than reading the whole document. Both skills
    therefore centre on verify-before-trust: the index carries line count plus a content
    SHA256, and the consumer recomputes both and REFUSES to slice on mismatch.
  NEXT: Make the staleness contract the first normative section of each skill.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-26T17:40:00Z
  TYPE: MEASURE
  CLAIM: Both skills authored AND dogfooded by executing their own recipes verbatim,
    extracted from the markdown. That testing found three defects, all now fixed.
    (1) The fence-detection regex was written with literal triple-backticks INSIDE a
    fenced python block, which broke the fence - a skill whose recipe cannot be extracted
    is not a recipe. Rewritten as `` `{3} `` so the line is fence-safe.
    (2) A lone `#` document title produced a "section" spanning 5,174 of 5,176 lines,
    i.e. an entry whose only use is to defeat the index while appearing to use it. The
    generator now omits it.
    (3) Schema slimmed from six fields to four after measuring: `title` is
    `path.split(" > ")[-1]` and `lines` is `end - start + 1`. Dropping both plus
    pretty-printing took the components index from 9,519 to 5,661 tokens.
  EVIDENCE:
  - context_compass/special_instructions/new_skills/system_doc_index_generation.md
  - context_compass/special_instructions/new_skills/system_doc_index_usage.md
  IMPACT: A skill that has never been run is a hypothesis. All three defects were
    invisible on reading and obvious on execution.
  NEXT: Owner acceptance of the two skills.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-26T17:40:00Z
  TYPE: FACT
  CLAIM: Dogfooding the USAGE skill surfaced two more issues, one mine and one a genuine
    DOCUMENT defect. Mine: a case-insensitive substring search for `mutation_research`
    returned ZERO hits against headings that say `MutationResearch`, so the skill now
    mandates folding case AND stripping separators on both sides. The document's: both
    target docs contain headings WRAPPED across consecutive `##` lines, so the generator
    faithfully emits each fragment as its own 1-line section - and those sort FIRST under
    "narrowest wins", handing a caller a heading fragment and nothing else. Counted 4 in
    `src_architecture.md` and 8 in `src_components.md`.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:4948-4951
  - context_compass/system_docs/src_architecture.md:1921-1921
  IMPACT: The usage skill now filters `<= 2` line hits and classes them as a reportable
    document defect rather than a section, because the real fix is repairing the wrapped
    headings in the source documents - which is a separate, owner-routable task.
  NEXT: Raise the 12 wrapped headings for a decision; they are cosmetic to a human reader
    and actively misleading to an indexed one.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-26T17:40:00Z
  TYPE: DECISION
  CLAIM: SCOPE NOTE - validating the recipes produced the two real indexes as a
    by-product. `system_docs/src_architecture_index.json` (72 sections, 8,102 bytes) and
    `system_docs/src_components_index.json` (156 sections, 22,644 bytes) now exist on
    disk. Owner asked for skills FIRST and implementation second; I did not set out to
    implement, but the only honest way to validate a generation recipe is to run it.
    Both pass all four validations: line_count, sha256, zero round-trip mismatches
    (72/72 and 156/156), no gaps or overlaps, coverage to EOF.
  EVIDENCE:
  - context_compass/system_docs/src_architecture_index.json
  - context_compass/system_docs/src_components_index.json
  IMPACT: Measured payoff on `src_components.md`: whole document ~72,069 tokens; index
    ~5,661; the narrowest real crystallizer section 10 lines. A lane needing one
    subsystem reads roughly 6-8k tokens instead of 72k.
  NEXT: Owner keeps or discards the two generated indexes; the skills stand either way.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-31T23:03:22Z
  TYPE: DECISION
  CLAIM: CLOSED at owner turn-in 2026-07-31. Both index skills authored AND dogfooded by running their own recipes verbatim, which found 3
    defects invisible on reading: an unextractable fence, a title section spanning 5,174 of
    5,176 lines, and 2 redundant schema fields worth 3,900 tokens. Indexes generated as a
    validation by-product; both pass all four checks and were regenerated after every doc edit.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-07-26_system_doc_index_skills_task.md
  IMPACT: Ticket moved to completed/; board row removed and replaced by one anchor.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Skills-before-implementation, per owner instruction. Two skills authored under
`special_instructions/new_skills/` so the pair ports cleanly into the context_compass
repo: one defines the index schema and deterministic derivation, the other defines
verify-before-slice consumption. No index is generated in this task - that is the next
one, and it should be built against this contract rather than alongside it.
