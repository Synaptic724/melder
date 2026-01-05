# Analyst Example: Analysis Brief

Context
- The user asks for a concise analysis of a change impact.
- Inputs include a short description of the change and affected modules.

Example brief (sample)
Title: Impact Brief — Scan Registry Refactor

Scope
- Affected modules: scan registry writer, query registry, scan store tests.

Findings
- The refactor reduces JSON usage and enforces relational schemas.
- Test coverage should be updated to reflect new payload shapes.

Risks
- Migration gaps if legacy JSON readers remain.
- Schema mismatches in multi-table query scripts.

Recommendations
- Add regression tests for query payloads.
- Verify action registry entries cover the new scripts.
