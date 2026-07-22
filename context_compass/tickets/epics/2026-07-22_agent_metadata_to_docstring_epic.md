# Epic: Move agent metadata attrs to docstring level, discover via inspect

## Metadata
- Epic ID: EPIC-2026-07-22-agent-metadata-to-docstring
- Status: active (investigation; NOT designed)
- Owner: UNASSIGNED
- Agent Name: -
- Priority: p3
- Created: 2026-07-22T10:44:00Z
- Updated: 2026-07-22T10:44:00Z

## Objective
Owner directive (2026-07-22): move the agent-facing class metadata attrs -
example:
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Pure-data digital twin of one AethericFrame's "
        "configured surface. Melder kernel machinery: read it to understand "
        "the runtime, do not drive it directly."
    )
- DOWN TO DOCSTRING LEVEL, and discover them with `inspect` (read the
docstring/source at need-time) instead of creating live attributes on every
class, "because it slows down the entire fucken system." The metadata's
CONTENT and intent stay exactly as-is; only the carrier changes: from
runtime class attributes (paid at import, held in memory forever, on every
class) to docstring convention (paid only when a reader actually asks).

## Current State (measured 2026-07-22, filesystem-verified)
- `__ast_helper_access__`: 330 definition sites across 318 files in
  `src/melder`.
- `__agent_purpose__`: 345 occurrences.
- RUNTIME READERS FOUND: ZERO - a getattr-consumer sweep across src/melder,
  tests, tools, scripts, and context_compass matched nothing. If confirmed
  by the deeper sweep (Lane A), every one of these attributes is pure
  import-time and memory cost with no live consumer: the intended readers
  are agents and AST tooling, which read SOURCE - and source-level
  (docstring) carriers serve an AST reader identically with zero runtime
  footprint.
- Sibling epic: EPIC-2026-07-22-internal-bind-guard-replacement (the
  `__melder_internal__` sentinel, 329 files) - same disease, same cure
  direction: stop stamping runtime attributes for policies/metadata that
  one central mechanism can own. The two sweeps likely share migration
  tooling and should coordinate.

## Investigation Lanes (questions to answer, not designs to follow)
LANE A - find EVERY reader, then prove zero-or-few:
- Raw attribute access (`.__ast_helper_access__` / `.__agent_purpose__`),
  string-key reads, AST/tooling readers (readable_src_graph generation,
  graph-doc pipelines, protocol crafter, spell examiner profiles, Rift
  rooms/workstation), tests pinning the attrs (e.g. probes asserting
  __agent_purpose__ content), and anything OUTSIDE the repo that consumes
  the packaged hardcopy docs. The migration story depends entirely on this
  inventory.
LANE B - docstring convention design:
- The house docstring style already carries structured sections (Purpose /
  Contract / Registration / Subsystem Context...). Define ONE standard
  section (e.g. "Access:" line + "Agent:" paragraph, exact grammar TBD)
  that carries access level + agent purpose, parseable by BOTH a live
  `inspect.getdoc` reader and a pure-AST reader (no import needed).
- Caching: a lazy, cached need-time reader (parse once per class per
  process WHEN ASKED) so the cost moves from every-import to actual-use.
- Classes with __slots__ and generated/synthetic classes: confirm the
  docstring carrier works everywhere the attrs exist today.
LANE B2 - BIND GUARD UNIFICATION (owner extension, 2026-07-22): the same
  docstring section could carry the internal-bind marker the sibling
  sentinel-replacement epic needs (its Lane A2) - the grammar must then be
  designed for TWO consumers: offline agents/AST tooling AND a live,
  cache-able bind-time check. If this wins, one sweep retires BOTH attr
  families (__melder_internal__ + __ast_helper_access__/__agent_purpose__)
  and the access line becomes load-bearing policy, not just documentation -
  which raises the bar: -OO docstring stripping, non-inheriting __doc__,
  and marker-grammar ambiguity all become guard-correctness questions, not
  cosmetic ones.
LANE C - the perf claim, measured:
- Benchmark import time + memory (330+ class-dict entries and interned
  strings) before/after on the owner's 3.14t; benchmark the inspect-based
  read path for the tooling that actually consumes the metadata. The
  premise (attrs slow the whole system) gets numbers, not vibes.
LANE D - migration mechanics:
- Scripted sweep (attrs -> docstring section) across ~318 files with
  CRLF/120-col discipline; docstring collision handling (classes whose
  docstrings already carry the same prose); verification that no attr
  remains; suite green; hardcopy/graph doc regeneration if those pipelines
  embed the metadata.

## Exit Shape (what done looks like)
- Reader inventory published with EVIDENCE (file:line per consumer, or a
  proven "zero live readers" claim).
- DECISION doc: docstring grammar chosen, reader utility chosen (inspect
  vs AST vs both), measurements attached.
- If chosen: attrs removed across the tree, docstring sections in place,
  need-time reader landed for the real consumers, full suite green,
  import/memory delta reported.

## Ticket Contract
- ENTRY_GATE: picked up explicitly; Lanes A-C answered with evidence BEFORE
  any sweep.
- EXECUTION_BOUNDARY: investigation touches no runtime code; the sweep is
  its own story set after the DECISION.
- DEPENDENCIES: house docstring standard; AST helper tooling; packaged
  hardcopy doc generation; sibling sentinel-replacement epic (shared
  tooling, coordinated sweeps).
- EXIT_GATE: see Exit Shape.
- FAILURE_ESCALATION: DECISION_REQUEST to owner on the docstring grammar
  and on any consumer that genuinely needs a LIVE attribute.

## Notes
- DATETIME: 2026-07-22T10:44:00Z
  TYPE: MEASURE
  CLAIM: Epic captured from owner directive. Counts measured this session
    (330 defs / 318 files; 345 __agent_purpose__ occurrences; zero getattr
    readers found in the first sweep). UNASSIGNED; active for pickup.
  EVIDENCE:
  - grep counts, 2026-07-22 session
  - example carrier: src/melder/aether/conduit/meld/contracts/spell_contract.py
    (__ast_helper_access__ + __agent_purpose__ block)
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## Context / Handoff Summary
Investigation epic. The metadata CONTENT stays; the carrier moves from live
class attributes to docstring convention discovered at need-time via
inspect/AST. Prove the reader inventory first - the whole migration hangs
on Lane A.
