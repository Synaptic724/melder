

# src_components_instructions

## Purpose
- Define the exact build protocol for
  `context_compass/system_docs/src_components.md`.
- Produce a bottom-up component contract map (C3/C2/C1) that stays aligned to
  architecture boundaries.

## Canonical Output
- `context_compass/system_docs/src_components.md`

## Example Documents (Required Read)
- `context_compass/examples/example_components/src_components.md`
- `context_compass/examples/example_components/tests_components.md`
- `context_compass/examples/example_architecture/src_architecture.md`
- `context_compass/examples/example_architecture/tests_architecture.md`
- `context_compass/system_docs/src_components.md` (active baseline)

## Required Inputs (Read First)
- `context_compass/system_docs/src_architecture.md`
- `context_compass/system_docs/src_graph.md`
- `context_compass/system_docs/src_graph_index.md`
- `context_compass/system_docs/tests_components.md`
- `context_compass/system_docs/tests_architecture.md`
- `context_compass/system_docs/patches/active/<patch_id>/component_patch_<component>.md`
  (when patch lane is active)
- `context_compass/system_docs/patches/active/<patch_id>/code_description_patch_<component>.md`
  (when complexity trigger applies)
- `context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md`
- `context_compass/agent_onboarding/default/design_engineer/skills/patch_framework_design.md`
- `context_compass/agent_onboarding/default/design_engineer/skills/component_patch_contracts.md`
- `context_compass/agent_onboarding/default/design_engineer/skills/code_description_patch_contracts.md`
- Active ticket and `context_compass/attention_board.md` route

## Indexing Contract (Non-Negotiable)

This document is AUTHORED. Nothing generates its prose. The only generated
artifact is its index, and the index is only as useful as the heading structure
you give it.

Regenerate the index in the SAME pass that edits the document:

```bash
python context_compass/tools/system_documents/index_document.py \
    --doc context_compass/system_docs/src_components.md
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
  document believing they sliced it.

Consume the index by slicing, never by reading the document whole:

```bash
python context_compass/tools/system_documents/index_document.py \
    --doc context_compass/system_docs/src_components.md --slice "<section name>"
```

It verifies the index before returning anything, refuses on a stale index, and
lists candidates rather than guessing when a name is ambiguous. Section names
are therefore the query - keep them unique and descriptive.

Verify before trusting any range:

```bash
python context_compass/tools/system_documents/index_document.py \
    --doc context_compass/system_docs/src_components.md --check
```

An index records `line_count`, `content_sha256`, and `line_ending`. Insert one
line near the top and every range below it is wrong while still parsing and
still returning content - the WRONG content, confidently. On mismatch: STOP,
regenerate, do not eyeball an offset.

Full format specification:
`agent_onboarding/default/engineer/skills/system_document_build.md`

## Unknowns Gate (Non-Negotiable)
- Default to `UNKNOWN` for unevidenced component claims.
- Promote to `FACT` only with direct evidence.
- No behavior inference from naming or folder shape.

## Required Section Contract
`src_components.md` must contain these sections in order:
1. `## Metadata`
2. `## Scope`
3. `## Indexing`
4. `## DO NOT ASSUME / Unknowns Gate`
5. `## Unknowns`
6. `## C3 Components Catalog`
7. `## C2 Subcomponents Catalog`
8. `## Method-Level Call Flows (C1)`
9. `## C1 Code Map (Core)`
10. `## Diagrams`
11. `## Information Sources`
12. `## Context / Handoff Summary`

## Component Entry Contract (C3 Minimum)
Each C3 component entry must include:
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

## C1 Flow/Map Contract
- Method-level call flows must include concrete method/function names.
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
1. Confirm active ticket route and component scope.
2. Read required example documents and note reusable structure patterns.
3. Re-read architecture boundaries and terms.
4. Draft/refresh `Metadata`, `Scope`, `Unknowns Gate`, and `Unknowns`.
5. Build C3 component catalog using the entry contract.
6. Build C2 subcomponent catalog with ownership and wiring.
7. Capture method-level C1 call flows for core paths.
8. Build C1 map entries with ranges, LOC, and verification timestamps.
9. Add/refresh diagrams aligned to catalog terminology.
10. If patch lane is active, verify component/code-description patch updates
    are complete and linked in tickets.
11. Refresh `Information Sources` and `Context / Handoff Summary`.

If a component claim conflicts with architecture, log `CONFLICT` in ticket
notes and escalate before proceeding.

## Quality Gate (Pass/Fail)
Pass only when all checks are true:
- [ ] Required section order exists and is complete.
- [ ] Every C3 entry includes the minimum contract fields.
- [ ] C1 call flows use concrete method/function names.
- [ ] C1 map entries include path, range, LOC, and verified_at.
- [ ] Architecture terminology and boundaries are consistent.
- [ ] Information Sources support all promoted FACT claims.

## Validation Commands
- `rg -n "^## " context_compass/system_docs/src_components.md`
- `rg -n "C3 Components Catalog|C2 Subcomponents Catalog|Method-Level Call Flows|C1 Code Map" context_compass/system_docs/src_components.md`
- `rg -n "path|start_line|end_line|loc|verified_at" context_compass/system_docs/src_components.md`

## Staleness Triggers (When Update Is Mandatory)
- Component ownership/wiring changed.
- Lifecycle/cleanup ordering changed.
- Core method-level flows changed.
- Architecture boundaries/terms changed.
- `src_graph.md` changed because documented source wiring or
  ownership relationships changed.
- `src_graph_index.md` changed because canonical object relationships or ownership
  moved.
- C1 ranges became stale from code edits.
- Active component/code-description patch docs changed for the same patch id.

## Anti-Patterns (Reject)
- Component summaries without ownership/lifecycle details.
- C1 call flows without concrete methods.
- C1 map entries missing verification fields.
- Architecture mismatch left undocumented.

## Handoff Rule
- End with a concise `Context / Handoff Summary` that states:
  - what component contracts changed,
  - what is still unknown,
  - which subsystem should be verified next.
