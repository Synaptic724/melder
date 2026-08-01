

# src_architecture_instructions

## Purpose
- Define the exact build protocol for
  `context_compass/system_docs/src_architecture.md`.
- Produce a durable C4 architecture document that is re-entry safe after
  compaction.

## Canonical Output
- `context_compass/system_docs/src_architecture.md`

## Example Documents (Required Read)
- `context_compass/examples/example_architecture/src_architecture.md`
- `context_compass/examples/example_architecture/tests_architecture.md`
- `context_compass/examples/example_components/src_components.md`
- `context_compass/examples/example_components/tests_components.md`
- `context_compass/system_docs/src_architecture.md` (active baseline)

## Required Inputs (Read First)
- `context_compass/system_docs/src_components.md`
- `context_compass/system_docs/src_graph.md`
- `context_compass/system_docs/src_graph_index.md`
- `context_compass/system_docs/tests_architecture.md`
- `context_compass/system_docs/tests_components.md`
- `context_compass/system_docs/patches/active/<patch_id>/architecture_patch.md`
  (when patch lane is active)
- `context_compass/agent_onboarding/default/design_engineer/skills/src_components_instructions.md`
- `context_compass/agent_onboarding/default/design_engineer/skills/patch_framework_design.md`
- `context_compass/agent_onboarding/default/design_engineer/skills/architecture_patch_contracts.md`
- Active ticket and `context_compass/attention_board.md` route

## Indexing Contract (Non-Negotiable)

This document is AUTHORED. Nothing generates its prose. The only generated
artifact is its index, and the index is only as useful as the heading structure
you give it.

Regenerate the index in the SAME pass that edits the document:

```bash
python context_compass/tools/system_documents/index_document.py \
    --doc context_compass/system_docs/src_architecture.md
```

Heading discipline the index depends on:
- **Exactly one H1.** A second one and the indexer cannot identify the document
  title, so it stops omitting it and emits a section spanning the whole file.
- **The navigable unit is H2 `## <Concern>`.** Consistent depth, never mixed.
- **Names unique and stable.** Index rows are selected on name; two sections
  sharing a name are indistinguishable to a consumer.
- **No container headings in this document.** Every H2 is a selectable concern,
  so there is no wrapper heading to select by mistake. Keep it that way: the
  moment an H2 exists only to group other headings, it indexes as a range
  covering all of them, and a reader selecting it loads that whole span
  believing they sliced one section. On a production `src_components.md` - not
  the starter shipped here - that mistake costs 37% of the document in a single
  slice.

Consume the index by slicing, never by reading the document whole:

```bash
python context_compass/tools/system_documents/index_document.py \
    --doc context_compass/system_docs/src_architecture.md --slice "<section name>"
```

It verifies the index before returning anything, refuses on a stale index, and
lists candidates rather than guessing when a name is ambiguous. Section names
are therefore the query - keep them unique and descriptive.

Verify before trusting any range:

```bash
python context_compass/tools/system_documents/index_document.py \
    --doc context_compass/system_docs/src_architecture.md --check
```

An index records `line_count`, `content_sha256`, and `line_ending`. Insert one
line near the top and every range below it is wrong while still parsing and
still returning content - the WRONG content, confidently. On mismatch: STOP,
regenerate, do not eyeball an offset.

Full format specification:
`agent_onboarding/default/engineer/skills/system_document_build.md`

## Unknowns Gate (Non-Negotiable)
- New claims start as `UNKNOWN`.
- Promote to `FACT` only with direct evidence.
- Evidence must be concrete code/doc references, not naming inference.

## Required Section Contract
`src_architecture.md` must contain these sections in order:
1. `## Metadata`
2. `## Scope and Intent`
3. `## Indexing`
4. `## DO NOT ASSUME / Unknowns Gate`
5. `## Unknowns`
6. `## System Context (C4)`
7. `## System Boundary and External Interfaces`
8. `## Architecture Summary (C4)`
9. `## Entrypoints and Runtime Guardrails`
10. `## Boot and Configuration Sequence`
11. `## Data Flows and Sequences`
12. `## Operational Invariants`
13. `## Failure Modes and Error Paths`
14. `## C1 Code Map (Core Only)`
15. `## Diagrams`
16. `## Information Sources`
17. `## Context / Handoff Summary`

## C1 Code Map Contract
Every C1 entry must include:
- `path`
- `start_line`
- `end_line`
- `loc`
- `verified_at` (UTC DateTime `YYYY-MM-DDTHH:MM:SSZ`)

Ranges are measured, never estimated. If the exact range is not verified, keep
the claim `UNKNOWN` and add an investigation target in `## Unknowns` rather than
writing a plausible number.

## Diagram Contract
- Include one ASCII architecture diagram.
- Include one Mermaid architecture diagram.
- Keep labels operational (ownership, flow, boundary), not decorative.
- Keep diagram terms aligned with section terminology.

## Build Sequence (Top-Down, Required)
1. Confirm active ticket route and architecture scope.
2. Read required example documents and note formatting patterns to preserve.
3. Re-read companion component/test docs for boundary alignment.
4. Draft/refresh `Metadata`, `Scope and Intent`, and Unknowns sections.
5. Define system boundary, interfaces, and high-level runtime summary.
6. Write entrypoints and boot/configuration sequence.
7. Write data-flow sequences (normal path and failure path).
8. Capture invariants and failure modes with source evidence.
9. Build C1 core map with line ranges, LOC, and verification timestamps.
10. Refresh diagrams to match narrative and naming.
11. If patch lane is active, verify architecture patch updates are complete and
    linked in tickets.
12. Refresh `Information Sources` and `Context / Handoff Summary`.

Do not skip sequence order. If blocked, write a `BLOCKER` note in the active
ticket before expanding scope.

## Quality Gate (Pass/Fail)
Pass only when all checks are true:
- [ ] Required section order exists and is complete.
- [ ] Unknowns are explicit and carry investigation targets.
- [ ] Boundary/interfaces and boot sequence are concrete and testable.
- [ ] C1 entries include path, range, LOC, and verified_at.
- [ ] Diagrams match written flow and use aligned terminology.
- [ ] Information Sources cover every promoted FACT.

## Validation Commands
- `rg -n "^## " context_compass/system_docs/src_architecture.md`
- `rg -n "UNKNOWN|C1 Code Map|Information Sources|Context / Handoff Summary" context_compass/system_docs/src_architecture.md`
- `rg -n "path|start_line|end_line|loc|verified_at" context_compass/system_docs/src_architecture.md`

## Staleness Triggers (When Update Is Mandatory)
- Boundary or integration contracts changed.
- Boot/configuration ordering changed.
- Invariants/failure modes changed.
- C1 line ranges became stale from code edits.
- `src_components.md` introduces term/boundary changes.
- `src_graph.md` changed because documented source wiring or
  ownership relationships changed.
- `src_graph_index.md` changed because canonical object relationships or ownership
  moved.
- Active `architecture_patch.md` changed for the same patch id.

## Anti-Patterns (Reject)
- Placeholder claims without evidence.
- C1 map entries without ranges/LOC/verified_at.
- Diagrams that do not match section content.
- Mixing component-level deep dives into architecture sections.

## Handoff Rule
- End with a concise `Context / Handoff Summary` that states:
  - what changed,
  - what remains unknown,
  - where the next reader should start.
