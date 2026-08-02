

# Task: Stop context maps citing Context Compass paths that do not travel with them

## Metadata
- Task ID: TASK-2026-08-02-context-map-self-citation
- Story: STORY-2026-08-02-context-map-portability
- Status: draft
- Owner:
- Agent Name: <unassigned - handoff from melder_private>
- Priority: p2
- Created: 2026-08-02T00:00:00Z
- Updated: 2026-08-02T00:00:00Z

## Objective

Make the generated/authored context maps portable: a consumer reading
`src_architecture.md` or `src_components.md` outside the source repository must
never be pointed at a `context_compass/...` path that does not exist for them.

The document is about the SOURCE PACKAGE. It should cite the source package.

## Originating Evidence

Found while ingesting the context maps into the `melder` wheel. `melder`
captures `src_architecture.md`, `src_components.md` and `src_graph.md` into
generated Python modules at build time, so an installed `melder` can serve its
own documentation in-process. `context_compass/` is excluded from that wheel -
that exclusion is the entire reason the ingestion exists.

The documents travel. Their citations do not.

A consumer running `pip install melder` and reading `melder.__architecture__`
is currently told, in the document's own `Indexing` section:

```bash
python context_compass/tools/system_documents/index_document.py \
    --doc context_compass/system_docs/src_architecture.md
```

That tool is not installed. That path does not exist. Nothing in the document
signals that the instruction was addressed to someone else.

## Two Distinct Classes - They Need Different Fixes

The 18 affected lines are NOT one problem. Fixing them the same way would be
wrong.

### Class A - maintenance instructions addressed to the doc's author (13 lines)

Regeneration and verification commands, living in the `## Indexing` section.
These are correct, useful, and belong to whoever maintains the document IN the
repository. They are meaningless to a downstream reader.

- `src_architecture.md:39-40, 46-47, 67, 91-92`
- `src_components.md:28-29, 35-36, 42-43, 80`

**Recommended fix:** keep the content, move it out of the document body. Options
worth weighing in Context Compass:

1. Emit it into the `*_index.md` companion instead - the index is already the
   generated artifact and is already where the staleness proof lives. Nothing
   downstream ingests the index as prose.
2. Keep it in the document but inside a marked, strippable region (the same
   `<!-- BEGIN USER-DEFINED -->` convention the templates already use), so an
   ingesting build can drop it cleanly.
3. Rewrite the commands to be repo-root-relative and tool-agnostic, with an
   explicit "this applies when working in the source repository" preamble.

Option 1 is the cleanest - it puts author-facing instructions on the
author-facing artifact - but option 2 is the least disruptive to existing docs.

### Class B - cross-references between context maps (5 lines)

Real content. A reader genuinely wants these. The path is simply wrong for a
reader outside the repo.

- `src_components.md:13` - points at `context_compass/system_docs/src_architecture.md`
- `src_components.md:8178, 8180, 8182` - `Information Sources` block, pointing at
  `src_architecture.md`, `tests_components.md`, `patches/active/`

**Recommended fix:** re-address, do not remove. The referenced document is
usually published under a name the consumer actually has. In melder's case
`context_compass/system_docs/src_architecture.md` is served as
`melder.__architecture__`. A citation convention that survives ingestion needs
either:

- a logical document id (`src_architecture`) that a consumer resolves through
  whatever mechanism they have, rather than a filesystem path, or
- a documented rewrite hook the ingesting build can apply.

The second is more work for every consumer. The first is a one-line convention
change in the authoring skill and costs nothing.

## Ticket Contract
- ENTRY_GATE: Board row exists; this handoff read in full.
- EXECUTION_BOUNDARY: Context Compass skills and templates governing context-map
  authoring. Specifically the skills that tell an author to write the `Indexing`
  section and the `Information Sources` section. No changes to melder.
- DEPENDENCIES: None blocking. Independent of the melder-side ingestion, which
  already ships and does not need this to function.
- EXIT_GATE: Skills updated; a newly authored context map contains no
  `context_compass/` path in prose that a downstream reader would follow.
- FAILURE_ESCALATION: If Class B cannot be solved without a consumer-side
  rewrite hook, record a DECISION_REQUEST rather than shipping paths that
  dangle.

## Scope Boundaries
- In scope:
  - The authoring skills that produce `## Indexing` and `## Information Sources`.
  - `system_orientation.md` and `src_graph_usage.md`, which model the citation
    convention agents copy.
  - Template guidance, if the templates carry example citations.
  - A note in the doc-generation skill that context maps may be INGESTED, and
    what that implies for anything written in them.
- Out of scope:
  - Retro-editing existing `src_*.md` in consuming repositories. Those get fixed
    on their next authoring pass.
  - `src_graph.md` - it is fully generated and cites nothing. Zero occurrences.
    Whatever its generator does is already correct and is the model to copy.

## Steps / Checklist
- [ ] Confirm the two classes above hold against other Context Compass installs,
      not just melder. The counts here are from one repository.
- [ ] Decide Class A placement (index companion vs strippable region vs
      preamble). Record as a DECISION note.
- [ ] Decide Class B addressing (logical id vs rewrite hook). Record as DECISION.
- [ ] Update the authoring skills to state the rule and show a compliant example.
- [ ] Add the rule to `system_orientation.md` core references, since that is
      where agents learn what a context map is for.
- [ ] Verify: author a fresh context map from the updated skills and grep it for
      `context_compass/`. Expect zero prose hits.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Updated authoring skill(s) carrying an explicit portability rule.
- A worked compliant example of both an `Indexing` section and an
  `Information Sources` block.

## Files / Paths Impacted
- `agent_onboarding/default/engineer/skills/` - the context-map authoring skills
- `agent_onboarding/default/engineer/skills/system_orientation.md`
- `agent_onboarding/default/engineer/skills/src_graph_usage.md` (citation convention)
- Possibly `templates/` if examples there carry repo-rooted paths

## Validation
- Not run.
- Recommended commands:
  - `grep -rn "context_compass/" <repo>/context_compass/system_docs/src_*.md`
    Expect: hits only inside a marked strippable region, or none.
  - Re-run the melder ingestion afterwards and confirm the refusal gate still
    passes - this change alters document bytes, so every `*_index.md` must be
    regenerated in the same pass or the staleness proof will correctly refuse.

## Risks / Rollback Notes
- **Editing a document without regenerating its index will break the staleness
  proof.** `line_count` and `content_sha256` both move. Any consumer enforcing
  the gate will refuse the pair - which is the gate working, but it will look
  like a regression. Regenerate in the same pass.
- Class A content is genuinely useful to maintainers. Deleting rather than
  relocating it would trade one problem for another.
- Low blast radius otherwise: prose-only, no tooling depends on these lines.

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
- [ ] Notes quality maintained
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Notes
- DATETIME: 2026-08-02T00:00:00Z
  TYPE: FACT
  CLAIM: Context maps cite Context Compass paths in prose, and those documents
    are now ingested into a wheel that excludes Context Compass.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:39-40
  - context_compass/system_docs/src_architecture.md:46-47
  - context_compass/system_docs/src_architecture.md:67
  - context_compass/system_docs/src_architecture.md:91-92
  - context_compass/system_docs/src_components.md:13
  - context_compass/system_docs/src_components.md:28-29
  - context_compass/system_docs/src_components.md:35-36
  - context_compass/system_docs/src_components.md:42-43
  - context_compass/system_docs/src_components.md:80
  - context_compass/system_docs/src_components.md:8178-8182
  IMPACT: A downstream reader is instructed to run a tool they do not have,
    against a path that does not exist, with nothing marking the instruction as
    addressed to someone else. Counts measured in `melder_private` on
    2026-08-02: 7 lines in `src_architecture.md`, 11 in `src_components.md`.
  NEXT: Decide Class A placement and Class B addressing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-02T00:00:00Z
  TYPE: FACT
  CLAIM: `src_graph.md` has ZERO context_compass citations and is the model.
  EVIDENCE:
  - `grep -c "context_compass" context_compass/system_docs/src_graph.md` -> 0
  IMPACT: The fully generated document is already portable. This is not a hard
    problem - it is a convention gap in the AUTHORED documents only. Whatever
    the graph generator does should be the rule for the rest.
  NEXT: Read the graph generator's output conventions before designing the fix.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-08-02T00:00:00Z
  TYPE: TRADEOFF
  CLAIM: Class B cannot be fixed by deletion without losing real content.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:13
  - context_compass/system_docs/src_components.md:8178-8182
  IMPACT: `src_components.md` explicitly defers to `src_architecture.md` for the
    C4 boundary. A reader who cannot follow that reference loses the layering
    that makes the two documents a pair. Removing the citation is worse than
    leaving it wrong.
  NEXT: Choose a logical document id convention over filesystem paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

## Context / Handoff Summary

Raised from `melder_private`, where the context maps are captured into generated
Python modules at build time so an installed `melder` can query its own
documentation without the repository present. The ingestion works and is not
blocked by this.

The finding is a Context Compass convention gap, not a melder bug: authored
context maps embed repo-rooted `context_compass/...` paths in their prose, and
those documents are designed to be consumed elsewhere. Eighteen lines across two
documents, splitting cleanly into author-facing maintenance instructions (13,
relocate) and genuine cross-document references (5, re-address). The fully
generated `src_graph.md` has none and shows the target state.

Fix belongs in the authoring skills so new documents are born portable.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
