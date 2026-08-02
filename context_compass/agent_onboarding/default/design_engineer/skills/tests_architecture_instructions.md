

# tests_architecture_instructions

## Purpose
- Define the exact build protocol for
  `context_compass/system_docs/tests_architecture.md`.
- Turn test-architecture docs from placeholder state into evidence-led C4
  system context.

## Canonical Output
- `context_compass/system_docs/tests_architecture.md`

## Example Documents (Required Read)
- `context_compass/examples/example_architecture/tests_architecture.md`
- `context_compass/examples/example_architecture/src_architecture.md`
- `context_compass/examples/example_components/tests_components.md`
- `context_compass/examples/example_components/src_components.md`

Read the two architecture examples as a pair. They share a section contract on
purpose: one maps the runtime, the other maps how the runtime is verified. If
your output makes the test map structurally different from the source map, the
divergence is the defect.

The canonical output does not ship with the package. `system_docs/` is empty in
a fresh install, so on first run you are creating this document, not editing
one. The examples above are the shape reference; this repository is the source
of truth for the content.

## Required Inputs (Read First)
- `context_compass/system_docs/tests_components.md`
- `context_compass/system_docs/src_architecture.md`
- `context_compass/system_docs/src_components.md`
- `context_compass/system_docs/src_graph.md`
- `context_compass/agent_onboarding/default/design_engineer/skills/tests_components_instructions.md`
- Active ticket and `context_compass/attention_board.md` route

## Indexing Contract (Non-Negotiable)

This document is AUTHORED. Nothing generates its prose. The only generated
artifact is its index, and the index is only as useful as the heading structure
you give it.

Regenerate the index in the SAME pass that edits the document:

```bash
python context_compass/tools/system_documents/index_document.py \
    --doc context_compass/system_docs/tests_architecture.md
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
  believing they sliced one section. On a production `src_components.md` that
  mistake costs 37% of the document in a single slice.

Consume the index by slicing, never by reading the document whole:

```bash
python context_compass/tools/system_documents/index_document.py \
    --doc context_compass/system_docs/tests_architecture.md --slice "<section name>"
```

It verifies the index before returning anything, refuses on a stale index, and
lists candidates rather than guessing when a name is ambiguous. Section names
are therefore the query - keep them unique and descriptive.

Verify before trusting any range:

```bash
python context_compass/tools/system_documents/index_document.py \
    --doc context_compass/system_docs/tests_architecture.md --check
```

An index records `line_count`, `content_sha256`, and `line_ending`. Insert one
line near the top and every range below it is wrong while still parsing and
still returning content - the WRONG content, confidently. On mismatch: STOP,
regenerate, do not eyeball an offset.

Full format specification:
`agent_onboarding/default/engineer/skills/system_document_build.md`

## Unknowns Gate (Non-Negotiable)
- Start unknown-heavy and explicit.
- Promote to `FACT` only when direct evidence is captured.
- If evidence is incomplete, keep `UNKNOWN` and list investigation targets.

## Required Section Contract
`tests_architecture.md` must contain these sections in order:
1. `## Metadata`
2. `## Scope and Intent`
3. `## Indexing`
4. `## DO NOT ASSUME / Unknowns Gate`
5. `## Unknowns`
6. `## System Context (C4)`
7. `## External Interfaces and Entry Points`
8. `## Core Responsibilities`
9. `## Data Flows and Lifecycle`
10. `## Invariants and Guarantees`
11. `## C1 Code Map (Key Paths)`
12. `## Diagrams`
13. `## Information Sources`
14. `## Context / Handoff Summary`

### Sections not in the contract

The contract is a **minimum in a fixed relative order**, not a whitelist. Other
sections are permitted and are common: real documents run 44 H2 sections against
a 17-section contract. Read literally as "only these sections", a recomposition
deletes roughly 1,200 lines per document.

If material genuinely does not belong here, it is **moved, never deleted**:

- relocate it to a named target - the patch lane
  (`system_docs/patches/active/<patch_id>/`) is the conventional destination
- name that target in `## Context / Handoff Summary`
- state plainly that until it is re-absorbed it lives in neither canonical
  document

"Delete it because the contract does not list it" is never the right answer.

## C1 Code Map Contract
Each C1 key-path entry must include:
- `path`
- `start_line`
- `end_line`
- `loc`
- `verified_at` (UTC DateTime `YYYY-MM-DDTHH:MM:SSZ`)

**Directories are not valid C1 entries.** A directory has no line range, and the
join to `src_graph.md` is keyed by source file, so a directory citation can never
resolve. Expand it into its constituent non-`__init__` modules and measure each.
Do not write `UNKNOWN` for a directory: `UNKNOWN` means "not yet verified and
here is the investigation target", and a directory is unverifiable in principle -
the marker would sit there forever with nothing to resolve it.

Ranges are measured, never estimated. If the exact range is not verified, keep
the claim `UNKNOWN` and add an investigation target in `## Unknowns` rather than
writing a plausible number.

## Diagram Contract
- Include one ASCII flow diagram.
- Include one Mermaid flow diagram.
- Keep labels operational (surface, flow, boundary), not decorative.
- Keep diagram terms aligned with section terminology.
- Diagram the verification path, not the runtime path. If this diagram could be
  dropped into `src_architecture.md` unchanged, it is describing the wrong
  system.

## Build Sequence (Discovery-First, Required)
2a. Unwrap any heading spanning more than one physical line. A reflowed
    heading parses as several sections; the first wins "narrowest match"
    and `--slice` returns a stub. `index_document.py` warns on unclosed
    brackets, which is the usual tell, but it cannot catch every wrap -
    scan the heading list once before you trust it.

1. Confirm active ticket route and test-system scope.
2. Read required example documents and extract reusable C4 section patterns.
3. Inventory test entry surfaces (`tests/`, runner config, fixtures).
4. Capture unknowns before promoting any architecture claims.
5. Define C4 boundaries and external interfaces.
6. Document lifecycle flow (setup, execution, teardown) with evidence.
7. Capture invariants and failure paths observed in sources.
8. Build C1 key-path map with ranges, LOC, and verification timestamps.
9. Add ASCII + Mermaid diagrams per the Diagram Contract.
10. If patch lane is active, confirm the architecture patch has not moved a
    boundary this document still describes the old way.
11. Refresh `Information Sources` and `Context / Handoff Summary`.

Do not skip sequence order. If blocked, write a `BLOCKER` note in the active
ticket before expanding scope. If a test-architecture claim conflicts with
`src_architecture.md`, log `CONFLICT` in ticket notes and escalate before
proceeding - the mismatch is the finding, and resolving it silently in either
direction destroys it.

## Content Preservation Gate (Non-Negotiable)

**Structural checks cannot see content loss.** Every check in the Quality Gate
below is structural - sections present, fields present, ranges present. A
recomposition can pass all of them while having silently destroyed text.

This is not hypothetical. A real recomposition of a 2,249-line architecture
document lost ~170 lines to a regex that captured only the description text on
the same physical line as the path: fifteen wrapped descriptions truncated, two
destroyed outright, and a previous `## Context / Handoff Summary` overwritten,
taking a record of decisions in force with it. All six structural checks passed
the entire time. It was caught by a human noticing the file had shrunk.

So, before the first transform:

1. Capture a **multiset** of the document's non-blank, whitespace-normalised
   lines. Counts, not a set - a set cannot see that a line appearing three times
   now appears once.
2. Do the work.
3. Re-capture and compare. Every line from the baseline must appear either in
   the resulting document or in a **named migration target** you can point at.

```bash
# before
grep -v '^[[:space:]]*$' DOC.md | sed 's/[[:space:]]\+/ /g' | sort | uniq -c > /tmp/before.txt
# after
grep -v '^[[:space:]]*$' DOC.md | sed 's/[[:space:]]\+/ /g' | sort | uniq -c > /tmp/after.txt
diff /tmp/before.txt /tmp/after.txt
```

**The baseline must be captured BEFORE the first edit.** Captured afterwards it
proves nothing - it describes the document you already built, which is the exact
trap that makes "I verified it" feel true while content is gone.

A line legitimately removed is fine. A line you cannot account for is a defect,
and this gate fails until you can name where it went.

## Quality Gate (Pass/Fail)
Pass only when all checks are true:
- [ ] Content Preservation Gate satisfied: every baseline line is present
      in this document or in a named migration target.
- [ ] Required section order exists and is complete.
- [ ] Unknowns are explicit and tied to investigation targets.
- [ ] Interfaces, lifecycle, and invariants are evidence-backed.
- [ ] C1 map entries include path, range, LOC, and verified_at.
- [ ] Diagrams and narrative use consistent terms.

## Validation Commands
- `rg -n '^#{1,6} .*[([][^)\]]*$' context_compass/system_docs/tests_architecture.md` - headings with an unclosed bracket, the usual sign of a wrap
- `rg -n "^## " context_compass/system_docs/tests_architecture.md`
- `rg -n "UNKNOWN|System Context|Data Flows|C1 Code Map|Information Sources" context_compass/system_docs/tests_architecture.md`
- `rg -n "path|start_line|end_line|loc|verified_at" context_compass/system_docs/tests_architecture.md`

## Staleness Triggers (When Update Is Mandatory)
- Test runner/configuration behavior changed.
- Fixture lifecycle behavior changed.
- Test boundary/interfaces changed.
- C1 ranges became stale from test-file edits.
- `tests_components.md` introduces term/boundary changes.
- `src_architecture.md` changed a boundary this document verifies. The source
  map moving without the test map moving is the most common way these two drift.
- `src_graph.md` changed because documented source wiring or ownership
  relationships changed.
- `src_graph_index.md` changed because canonical object relationships or
  ownership moved.
- Active `architecture_patch.md` changed for the same patch id.

## Anti-Patterns (Reject)
- Generic "tests do X" statements without evidence.
- Missing unknown inventory in partially mapped docs.
- C1 map entries without verification fields.
- Copying src architecture claims into tests architecture without proof.

## Handoff Rule
- End with `Context / Handoff Summary` covering:
  - evidence-backed state,
  - unresolved unknowns,
  - next discovery target.

