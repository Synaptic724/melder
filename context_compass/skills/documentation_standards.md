# Documentation Standards (Skill)

## Purpose
Architecture and components docs must be deep enough to reorient from a blank slate
without relying on memory.

## Core Rules
- No handwaving. Every claim must be grounded in source evidence or marked as unknown.
- Use explicit entrypoints, flows, and ownership boundaries.
- Record lifecycle and cleanup order for each core component.
- Capture invariants, failure modes, and concurrency constraints.
- Keep C4 (architecture) and C3/C2/C1 (components) consistent.
- Maintain ASCII and Mermaid diagrams for key flows.

## Required Sections (Architecture)
- Scope and Intent
- System Context and Boundaries
- Entrypoints and Boot Sequence
- Major component responsibilities and interactions
- Invariants, failure modes, and cleanup rules
- Evidence and information sources

## Required Sections (Components)
- C3 components with responsibilities and contracts
- C2 subcomponents with wiring and data structures
- C1 code map for entrypoints and core files
- Method-level call flows for core behaviors

## Evidence Discipline
- Cite concrete file paths for claims.
- Add "needs verification" for any assumption.
- Update info sources when new files are used.
