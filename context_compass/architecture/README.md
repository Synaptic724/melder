# Architecture Docs (C4 Mapping)

## Purpose
This folder is the **system-level map** (C4) for the repo.
It exists so a human or AI agent can:
- re-orient from a blank slate,
- rebuild the *correct* initialization + lifecycle ordering,
- and avoid inventing behavior during refactors.

These docs are intended to survive context compaction and handoffs.

## Where to Start (Agent-Friendly)
If you’re dropped into the repo with no context:
1. `architecture/src_architecture.md` — **C4** system boundaries, boot sequence, invariants, failure modes.
2. `components/src_components.md` — **C3/C2/C1** ownership map, wiring tables, call flows, code map.
3. `WORKFLOW.md` — how work is tracked (epic/story/task) and handed off.
4. `documentation_standards.md` — the hard rules for editing docs without degrading accuracy.

## Reader Map
Use this as a “jump list” instead of reading everything linearly.

### If you are trying to…
- **Bootstrap the runtime / bring the system up**
    - Read: `src_architecture.md → Entrypoints and Runtime Guardrails`
    - Then: `src_architecture.md → Boot and Configuration Sequence`
    - Then: `src_components.md → Method-Level Call Flows (C1)`

- **Find the real entrypoint and global singletons**
    - Read: `src_architecture.md → Entrypoints and Runtime Guardrails`
    - Then: `src_components.md → Public API + Spectrum Root`

- **Understand lifecycle + cleanup (what owns what)**
    - Read: `src_architecture.md → Ownership, Lifecycle, and Cleanup`
    - Then: `src_components.md → Lifecycle/Cleanup per component`

- **Debug why something “won’t run”**
    - Read: `src_architecture.md → Failure Modes and Error Paths`
    - Then: `src_components.md → Runtime Guardrails`

- **Change / add a subsystem**
    - Read: `src_architecture.md → System Boundary` + `Extension Points`
    - Then: `src_components.md → Component Catalog` + `Wiring Tables`

## Agent Rebuild Playbook (High-Level)
This is the minimum *procedural* sequence an agent should follow to rebuild or simulate the runtime shape.

**Important:** exact API names / signatures must be verified in code (Unknowns Gate). The safest anchors are:
- `components/src_components.md → Method-Level Call Flows (C1)`
- `components/src_components.md → C1 Code Map (Core)`

### 1) Confirm runtime guardrails (don’t fight the runtime)
Before doing anything else, find and read the runtime checks in the public entrypoint module(s).
Typical checks include:
- Python version gating
- free-threaded / nogil gating

### 2) Import the package and locate the root singleton (if any)
Most systems define a root object responsible for configuration + singleton publication.
If a global is created at import time, treat it as the boot boundary.

### 3) Configure once (freeze config, publish singletons)
- Build the configuration object(s).
- Call the one-time configure pipeline.
- Ensure singletons/resources/builders are published **only after** configuration completes.

### 4) Create the primary orchestration node(s)
Create the “top-level runtime container” (whatever owns groups/registries).
This typically allocates registries and maintenance/default sub-scopes.

### 5) Create a working scope and workers
Within a scope (group/project/session):
- create pools,
- create agents/workers,
- register jobs/tools/actions,
- then submit work.

### 6) Validate teardown order
Rebuild isn’t “done” unless teardown works.
Verify cleanup is ordered and idempotent:
- stop/disable processing first,
- detach/restore patches last,
- clear registries,
- then tear down logging.

## C4 Mapping (User-Defined)
- **C4:** Architecture (system-level view)
- **C3:** Components (major subsystems)
- **C2:** Subcomponents (internal building blocks)
- **C1:** Code (key files and entry points)

## Documents
- `architecture/src_architecture.md` — system architecture for `src/`.
- `architecture/tests_architecture.md` — system architecture for `tests/`.
- `components/src_components.md` — component map for `src/`.
- `components/tests_components.md` — component map for `tests/`.

## How to Gather Architecture Information
Use this sequence and record sources in the docs:
1. Read project goals and constraints in `context_compass/README.md` and `context_compass/AGENTS.MD`.
2. Identify entry points and public APIs (look for package `__init__`, CLI, or top-level modules).
3. Scan folder structure for major subsystems (`src/` and `tests/`).
4. Use `rg` to map key domains, names, and dependencies (search for class names, registries, or factory patterns).
5. Identify data flows: inputs, outputs, persistence, and side effects.
6. Identify lifecycle boundaries (init, cleanup, worker ownership, resource management).
7. Capture invariants and error paths that define the architecture.

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

## Update Cadence
Update architecture docs when:
- A new subsystem is introduced.
- Major ownership or lifecycle changes occur.
- Public API shape or boundaries shift.

## Diagram Guidance
Each architecture doc should include:
- **ASCII Diagram:** fast scanning in plain text.
- **Mermaid Diagram:** higher fidelity visualization.

Keep diagrams honest:
- show ownership and lifecycle edges ("creates", "owns", "cleans up"),
- mark optional subsystems clearly,
- and prefer clarity over completeness.

## Examples
See `context_compass/examples/example_architecture/` for reference structure.
