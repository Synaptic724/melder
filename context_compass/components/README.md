# Components Docs (C3/C2/C1)

## Purpose
Define components and subcomponents for `src/` and `tests/` using a consistent, durable structure.
This is the detailed view that sits **under** the C4 architecture docs.

If you’re onboarding (or you’re an AI agent dropped into the repo mid-stream), the intent is:
- **C4** tells you “what the system *is*” and where the boundaries are.
- **C3/C2/C1** tells you “who owns what”, “how it works internally”, and “where the code lives”.

## Where to Start (Agent-Friendly)
1. `architecture/src_architecture.md` (C4): system boundaries, boot sequence, invariants.
2. `components/src_components.md` (C3/C2/C1): component responsibilities, wiring, call flows, code map.
3. `WORKFLOW.md`: how tickets and handoffs are tracked over time.
4. `documentation_standards.md`: the rules for adding/changing docs without degrading quality.

## Mapping
- **C3:** Components (major subsystems)
- **C2:** Subcomponents (internal building blocks)
- **C1:** Code (key files, entry points, symbol-level references)

## Examples
See `context_compass/examples/example_components/` for reference structure and tone.

## How to Gather Component Information (Practical Steps)
1. Enumerate major directories and modules in `src/` and `tests/`.
2. Identify **component boundaries** (ownership, responsibilities, lifecycle, cleanup).
3. For each component, list subcomponents and their **contracts**.
4. Record **data structures**, **concurrency primitives**, and **cleanup rules**.
5. Map key files and public entry points (C1) — prefer `path:Class.method` precision.
6. Capture **risks**, **invariants**, **failure modes**, and **error paths**.
7. Keep diagrams updated when you change flows (ASCII + Mermaid).

## DO NOT ASSUME / Unknowns Gate
Rule: No Unverified Claims.
Any statement that is not directly supported by evidence must be treated as UNKNOWN.

Evidence means at least one of:
- A specific source file reference with line location (preferred: file + symbol/method/class name + line number).
- A citation to an explicit, already-verified artifact (e.g., a prior approved doc section).

If not evidenced => UNKNOWN.

UNKNOWN items must be explicitly labeled UNKNOWN (or added to an Unknowns section).
UNKNOWN items must be investigated by reading the relevant source(s).
If investigation cannot be completed (missing source access, ambiguity, or time),
the item must remain UNKNOWN and must not be promoted to fact.

No reasonable assumptions.
Do not infer behavior from naming, patterns, conventions, or typical frameworks.
Only the code/docs count.

When unsure:
- Mark it UNKNOWN.
- Identify the most likely evidence target (file + symbol).
- Investigate, then update the doc (or leave it UNKNOWN).

## Documents
- `architecture/src_architecture.md` - C4 architecture for src.
- `components/src_components.md` - components for src.
- `components/tests_components.md` - components for tests.

## Diagram Guidance
Each components doc includes two baseline diagrams:
- **ASCII Diagram:** fast scanning in plain text; keep it readable in a terminal.
- **Mermaid Diagram:** higher fidelity for visualization; keep node names stable.

Optional but recommended diagrams for complex systems:
- A boot/configuration sequence diagram.
- A cleanup/teardown sequence diagram.
- A work/request execution path diagram (task vs deployment, etc.).

## Maintenance Checklist (Lightweight)
When you edit a doc:
- Update any **Metadata → Updated** fields (if present).
- Keep the **Table of Contents** in sync.
- Update **Information Sources** when new code files are used as evidence.
- If you add a new claim that you can’t verify yet, add it to **Unknowns**.
