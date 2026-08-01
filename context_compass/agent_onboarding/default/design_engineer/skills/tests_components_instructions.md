

# tests_components_instructions

## Purpose
- Define the exact build protocol for
  `context_compass/system_docs/tests_components.md`.
- Produce evidence-backed C3/C2/C1 test component mapping aligned to test
  architecture boundaries.

## Canonical Output
- `context_compass/system_docs/tests_components.md`

## Example Documents (Required Read)
- `context_compass/examples/example_components/tests_components.md`
- `context_compass/examples/example_components/src_components.md`
- `context_compass/examples/example_architecture/tests_architecture.md`
- `context_compass/examples/example_architecture/src_architecture.md`
- `context_compass/system_docs/tests_components.md` (active baseline)

## Required Inputs (Read First)
- `context_compass/system_docs/tests_architecture.md`
- `context_compass/system_docs/src_architecture.md`
- `context_compass/system_docs/src_components.md`
- `context_compass/system_docs/src_graph.md`
- `context_compass/agent_onboarding/default/design_engineer/skills/tests_architecture_instructions.md`
- Active ticket and `context_compass/attention_board.md` route

## Indexing Contract (Non-Negotiable)

This document is AUTHORED. Nothing generates its prose. The only generated
artifact is its index, and the index is only as useful as the heading structure
you give it.

Regenerate the index in the SAME pass that edits the document:

```bash
python context_compass/tools/system_documents/index_document.py \
    --doc context_compass/system_docs/tests_components.md
```

Heading discipline the index depends on:
- **Exactly one H1.** A second one and the indexer cannot identify the document
  title, so it stops omitting it and emits a section spanning the whole file.
- **The navigable unit is H3 `### Component: <Name>`.** Consistent depth, never mixed.
- **Names unique and stable.** Index rows are selected on name; two sections
  sharing a name are indistinguishable to a consumer.
- **Never leave a container heading as the read target.** `## C3 Components
  Catalog` wraps only other headings, so it indexes as a range covering every
  component beneath it. Select a component, never the catalog. Measured on a
  production `src_components.md` - not the starter shipped here - that catalog
  indexes as a **1,945-line** section, so a reader selecting it loads 37% of the
  document believing they sliced it. The same shape applies here.

Consume the index by slicing, never by reading the document whole:

```bash
python context_compass/tools/system_documents/index_document.py \
    --doc context_compass/system_docs/tests_components.md --slice "<section name>"
```

It verifies the index before returning anything, refuses on a stale index, and
lists candidates rather than guessing when a name is ambiguous. Section names
are therefore the query - keep them unique and descriptive.

Verify before trusting any range:

```bash
python context_compass/tools/system_documents/index_document.py \
    --doc context_compass/system_docs/tests_components.md --check
```

An index records `line_count`, `content_sha256`, and `line_ending`. Insert one
line near the top and every range below it is wrong while still parsing and
still returning content - the WRONG content, confidently. On mismatch: STOP,
regenerate, do not eyeball an offset.

Full format specification:
`agent_onboarding/default/engineer/skills/system_document_build.md`

## Unknowns Gate (Non-Negotiable)
- New component claims default to `UNKNOWN`.
- Promote to `FACT` only with concrete evidence.
- Preserve unresolved UNKNOWNs; do not normalize into assumptions.

## Required Section Contract
`tests_components.md` must contain these sections in order:
1. `## Metadata`
2. `## Scope`
3. `## Indexing`
4. `## DO NOT ASSUME / Unknowns Gate`
5. `## Unknowns`
6. `## C3 Components Catalog`
7. `## C2 Subcomponents Catalog`
8. `## Method-Level Call Flows (C1)`
9. `## C1 Code Map (Key Paths)`
10. `## Diagrams`
11. `## Information Sources`
12. `## Context / Handoff Summary`

## Component Entry Contract (C3 Minimum)
Each C3 test component must include:
- `Purpose`
- `Responsibilities`
- `Inputs`
- `Outputs`
- `Owned State`
- `Lifecycle/Cleanup`
- `Concurrency/Threading`
- `Invariants/Guarantees`
- `Failure Modes`
- `Observability`
- `Extension Points`
- `Key Files (C1)`

This is the same twelve-field minimum `src_components_instructions.md` requires.
Test components are components. If a field genuinely does not apply, say so in
the field rather than dropping it - a missing field and a deliberately empty one
look identical to a reader, and only one of them is a decision.

## C1 Flow/Map Contract
- Call-flow entries must include concrete test methods/functions/fixtures.
- C1 map entries must include:
  - `path`
  - `start_line`
  - `end_line`
  - `loc`
  - `verified_at` (UTC DateTime `YYYY-MM-DDTHH:MM:SSZ`)

Ranges are measured, never estimated. If the exact range is not verified, keep
the claim `UNKNOWN` and add an investigation target in `## Unknowns` rather than
writing a plausible number.

## Build Sequence (Bottom-Up, Required)
1. Confirm active ticket route and test component scope.
2. Read required example documents and extract reusable C3/C2/C1 patterns.
3. Re-read tests architecture boundaries and terminology.
4. Draft/refresh metadata, scope, unknowns gate, and unknowns inventory.
5. Build C3 test component catalog with entry-contract fields.
6. Build C2 subcomponents and wiring/dependency notes.
7. Capture method-level C1 flows (fixtures, harnesses, execution paths).
8. Build C1 key-path map with ranges, LOC, and verification timestamps.
9. Add diagrams aligned to terminology and flow.
10. If patch lane is active, confirm the component patch has not moved a
    boundary this document still describes the old way.
11. Refresh `Information Sources` and `Context / Handoff Summary`.

If a test component claim conflicts with `tests_architecture.md` or with the
component it verifies in `src_components.md`, log `CONFLICT` in ticket notes and
escalate before proceeding. The mismatch is the finding; resolving it silently
in either direction destroys it.

## Quality Gate (Pass/Fail)
Pass only when all checks are true:
- [ ] Required section order exists and is complete.
- [ ] Every C3 entry includes the minimum contract fields.
- [ ] C1 call flows include concrete methods/functions/fixtures.
- [ ] C1 map entries include path, range, LOC, and verified_at.
- [ ] Terminology aligns with `tests_architecture.md`.
- [ ] Information Sources support promoted FACT claims.

## Validation Commands
- `rg -n "^## " context_compass/system_docs/tests_components.md`
- `rg -n "C3 Components|C2 Subcomponents|Method-Level Call Flows|C1 Code Map" context_compass/system_docs/tests_components.md`
- `rg -n "path|start_line|end_line|loc|verified_at" context_compass/system_docs/tests_components.md`

## Staleness Triggers (When Update Is Mandatory)
- Test component ownership/wiring changed.
- Fixture or harness lifecycle changed.
- Method-level test flow changed.
- C1 ranges became stale from test-file edits.
- `tests_architecture.md` changed boundaries or terminology.
- `src_components.md` changed a component this document verifies. The source
  map moving without the test map moving is the most common way these two drift.
- `src_graph.md` changed because documented source wiring or ownership
  relationships changed.
- `src_graph_index.md` changed because canonical object relationships or
  ownership moved.
- Active component/code-description patch docs changed for the same patch id.

## Anti-Patterns (Reject)
- Test component entries without lifecycle/ownership detail.
- C1 call flows with generic statements and no concrete symbols.
- C1 map entries missing verification fields.
- Divergence from tests architecture terminology without escalation.

## Handoff Rule
- End with `Context / Handoff Summary` that states:
  - what component mapping is verified,
  - what remains unknown,
  - which test subsystem should be mapped next.

