# Epic: OCE - Package Root and Document Surfaces (EXEMPLAR)

## Metadata
- Epic ID: EPIC-2026-07-19-oce-package-root
- Parent: EPIC-2026-07-19-object-contract-enrichment-program
- Status: ready
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-19T01:15:00Z
- Updated: 2026-07-19T01:15:00Z
- Stories:
  - STORY-2026-07-19-oce-root-document-surfaces (S1)

## LAW: NO CODEGEN FOR DOCUMENTATION (owner ruling 2026-07-20, non-negotiable)

Inherited from the program epic and binding on every story and task under this
epic.

- Docstrings and comments are AUTHORED CONTENT. Write them BY HAND, one method
  at a time, after reading that method's body.
- FORBIDDEN: scripts, codemods, loops, or generated passes that insert or
  bulk-apply docstring text across multiple methods or files - including
  hand-written strings applied by a script, because the application step is what
  removes the read-before-write discipline.
- FORBIDDEN: mass edits to move a completion counter.
- REQUIRED: targeted single-file edits; on tool failure, fall back to a
  single-file targeted write against THAT ONE FILE only.
- Scripts stay allowed for READ-ONLY verification afterwards (stripped-AST diff,
  trapped-line scan, counting). Never for producing the text.

## Problem / Opportunity
The package root is where an agent lands first and it is the thinnest surface in the repo:
2 classes, 1 of which (`StaticSystemDocument`) is already the exemplar for the whole program
and the other of which (`MelderRegistrationGuard`) is the guard itself. Three of the four
packaged hardcopy document modules still carry PLACEHOLDER payloads, so an agent that queries
`melder.__graph_network__` gets the string
`"placeholder: packaged Melder graph network hardcopy"` back.

This epic is deliberately smallest-first: it produces the reference diff every other child
epic copies.

## Subsystem Context Brief (read this, not the C-docs)
The package root is not a subsystem - it is the FRONT DOOR. Four things live here:

- `system_document.py:StaticSystemDocument` - immutable carrier for one packaged hardcopy
  document. Validates that the minified JSON contains string key `m`, then exposes
  `render_json()` and `render_markdown()`. Already Rank 4-5 with `__agent_purpose__` and
  `__ast_helper_access__`. THIS IS THE TEMPLATE.
- `__architecture__.py`, `__components__.py`, `__graph_network__.py`, `__graph_details__.py` -
  four module-level `StaticSystemDocument` instances. Their whole purpose is that an agent can
  query system structure WITHOUT conjuring a conduit (arch:260). They are import-time,
  immutable, and define no cleanup contract.
- `__melder_registration_guard__.py:MelderRegistrationGuard` - the eager singleton whose
  sentinel every other class in this program is about to adopt. Constructed at module import;
  `__init__.py` re-asserts it at package scope. DO NOT MODIFY the guard's construction or the
  `__init__.py` line that publishes it - owner ruling 2026-07-19.
- `__init__.py` - the entrypoint. OUT OF SCOPE for this epic.

Where this sits in the system: before everything. The guard sentinel must be importable
before any internal class body is evaluated, and the hardcopy documents must answer before
`Aether()` boots. Nothing here participates in the runtime graph.

## MRP Alignment
The front door has to be right the first time: it is the one surface an agent touches before
it knows anything else about the system. A placeholder answer here teaches an agent that the
document surface is not worth querying.

## Ticket Contract
- ENTRY_GATE: parent program epic accepted by owner; contract section read.
- EXECUTION_BOUNDARY: `src/melder/system_document.py`,
  `src/melder/__architecture__.py`, `src/melder/__components__.py`,
  `src/melder/__graph_network__.py`, `src/melder/__graph_details__.py`.
  EXPLICITLY EXCLUDED: `src/melder/__init__.py` and
  `src/melder/__melder_registration_guard__.py` - the guard and the entrypoint are not
  touched by this program.
- DEPENDENCIES: THE OBJECT CONTRACT in the parent program epic.
- EXIT_GATE: both root classes satisfy all five contract items; owner rules on whether the
  three placeholder hardcopies get real payloads in this epic or a separate lane.
- FAILURE_ESCALATION: DECISION_REQUEST if closing a placeholder requires generating real
  system-document content (that is a content lane, not a contract lane).

## Goals
- `StaticSystemDocument` and `MelderRegistrationGuard` reach full contract compliance.
- The four hardcopy modules carry accurate `__agent_purpose__` strings describing what an
  agent can actually ask them.
- The resulting diff becomes the reference every other child epic mirrors.

## Non-Goals
- Populating the placeholder hardcopy payloads with real architecture content.
- Any change to `__init__.py` export policy or the guard's construction.

## Scope Boundaries
- In scope: class attributes and docstrings on the two root classes; module docstrings and
  `agent_purpose` arguments on the four hardcopy modules.
- Out of scope: the entrypoint, the guard module, hardcopy payload content.
- Guard exclusions: NONE. Both root classes are Melder internals and both get the sentinel.

## Requirements
- Functional: `Spellbook.bind(StaticSystemDocument)` raises `InternalRegistrationError`.
- Non-functional: `StaticSystemDocument` uses `__slots__`; the sentinel is a ClassVar and must
  not disturb it.

## Acceptance Criteria
- [ ] `StaticSystemDocument` carries `__melder_internal__` (it currently does NOT) plus its
      existing `__agent_purpose__` / `__ast_helper_access__`, and gains Subsystem Context and
      System Context sections in its class docstring.
- [ ] `MelderRegistrationGuard` carries all five contract items. Note the irony to resolve
      explicitly: the guard defines the sentinel and does not currently tag itself.
- [ ] All four hardcopy modules have `agent_purpose` strings that state what question the
      document answers, not what the document is named.
- [ ] Regression proving both root classes are refused by `bind(...)`.

## Risks / Mitigations
- Tagging `MelderRegistrationGuard` with its own sentinel could look circular -> it is not:
  the sentinel is a plain identity object created at class definition; tagging the guard only
  means the guard itself cannot be bound as a spell, which is correct and desirable.
- `StaticSystemDocument.__slots__` is a list, not a tuple -> ClassVar assignment is unaffected;
  verify no instance-level assignment is introduced.

## Validation Plan
- AST sweep: 2/2 root classes carry all three attributes.
- Guard regression: `bind(StaticSystemDocument)` and `bind(MelderRegistrationGuard)` both
  raise `InternalRegistrationError`.
- Not run by agent. Owner runs on 3.14t.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: scope is 2 classes and 4 modules, well inside one task under the chunking
  law; exemplar status makes it the correct first execution.

## Milestones
- [ ] S1 landed and reviewed as the reference diff.

## Applicable Anti-Patterns
- [ ] No edits to `__init__.py` or the guard module from this epic.
- [ ] No filling placeholder payloads with invented architecture content.
- [ ] No claiming DONE with fewer than all five contract items.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
- Epic notes: reference-diff decisions that other child epics must copy.

## Notes
- DATETIME: 2026-07-19T01:15:00Z
  TYPE: FACT
  CLAIM: `StaticSystemDocument` already carries `__agent_purpose__` and `__ast_helper_access__`
    but NOT `__melder_internal__` - so the file held up as the exemplar is itself bindable as
    a spell today. Three of the four hardcopy modules
    (`__graph_network__`, `__graph_details__`, and per the components doc
    `__architecture__`/`__components__`) carry placeholder payloads; comp:261-262 records this
    honestly as "placeholder markdown/json carriers, not live regenerated architecture
    snapshots".
  EVIDENCE:
  - src/melder/system_document.py:26-35
  - src/melder/__graph_network__.py:8-15
  IMPACT: Fixes the exemplar before it is copied 540 times, and separates the contract lane
    from the hardcopy-content lane so the second does not block the first.
  NEXT: Owner ruling on whether placeholder payloads are in scope here or a separate lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-21T22:36:00Z
  TYPE: FACT
  CLAIM: Exemplar is ALREADY contract-complete in source; the 2026-07-19 note above is stale.
    `StaticSystemDocument` now carries `__melder_internal__ = _mrg.sentinel`, both
    `__agent_purpose__`/`__ast_helper_access__`, a Rank-5 class docstring with all nine
    canonical headers (incl. Subsystem + System Context), and rich docstrings on every public
    method. The four hardcopy modules carry question-shaped `agent_purpose` strings plus
    Subsystem/System Context module docstrings. `MelderRegistrationGuard` is richly documented
    with per-method docstrings. No documentation edit is warranted - authoring redundant
    docstrings on a correct public-library file would violate No-Drive-By-Refactors.
  EVIDENCE:
  - src/melder/system_document.py:78-84
  - src/melder/system_document.py:13-76
  - src/melder/__architecture__.py:1-39
  - src/melder/__graph_details__.py:16-24
  - src/melder/__melder_registration_guard__.py:14-96
  IMPACT: The contract lane for oce-package-root is DONE in code; only ticket reconciliation
    plus the owner 3.14t validation run remain.
  NEXT: Raise the two stale acceptance criteria (below) to the owner before any closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-21T22:36:00Z
  TYPE: DECISION_REQUEST
  CLAIM: Two acceptance criteria contradict the resolved design and cannot both stand as
    written. (AC2) "MelderRegistrationGuard carries all five contract items" - the guard is
    DELIBERATELY UNGUARDED (no `__melder_internal__`), which is correct per the MRO law it
    documents; item-1 (guard classification) is satisfied as "unguarded, reasoned", not as a
    sentinel. (AC4) "Regression proving BOTH root classes are refused by bind(...)" is wrong:
    an unguarded guard is not bind-refused, so the refusal regression must be scoped to
    `StaticSystemDocument` ONLY.
  EVIDENCE:
  - src/melder/__melder_registration_guard__.py:50-89
  - src/melder/system_document.py:78
  IMPACT: If AC2/AC4 stand as written, "done" is unreachable and a future agent could wrongly
    tag the guard, poisoning every user subclass through the MRO.
  NEXT: Owner ruling - accept the unguarded-guard resolution and rescope AC4 to
    `StaticSystemDocument` only; then this epic is closure-ready pending the owner 3.14t run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Smallest child epic and the program's reference diff: 2 classes, 4 hardcopy modules, one
story. Establishes what "all five contract items" looks like in a real file before the
pattern is replicated across the other nine subsystems. Open question for the owner: whether
populating the three placeholder hardcopy payloads belongs here or in its own content lane.
