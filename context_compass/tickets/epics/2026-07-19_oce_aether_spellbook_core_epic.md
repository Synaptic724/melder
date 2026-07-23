# Epic: OCE - Aether Spellbook Core (user-facing binding surface)

## Metadata
- Epic ID: EPIC-2026-07-19-oce-aether-spellbook
- Parent: EPIC-2026-07-19-object-contract-enrichment-program
- Status: in_progress
- Owner: cowork
- Agent Name: melder_1, melder_0
- Priority: p1
- Created: 2026-07-22T23:15:00Z
- Updated: 2026-07-22T23:15:00Z
- Stories:
  - (lean epic; the remaining gap is 3 classes, tracked directly in Notes as a split)

## LAW: NO CODEGEN FOR DOCUMENTATION (owner ruling 2026-07-20, non-negotiable)
Inherited from the program epic and binding here. Docstrings are AUTHORED CONTENT:
written BY HAND, one class at a time, after reading the class body. No script,
codemod, or generated pass may produce or bulk-apply docstring text. Read-only
verification scripts (stripped-AST diff, trapped-line scan, coverage counting)
remain allowed AFTER the fact - never to produce the text.

## Scope confirmation (owner ruling 2026-07-22)
`aether/spellbook/spell_compiler/**` is OUT of the program (compiler internals are
not user-facing). Owner reconfirmed 2026-07-22: "you can ignore spell compiler its
not user facing its fine." This epic covers ONLY the core spellbook binding surface,
NOT the compiler.

## Problem / Opportunity
The core `aether/spellbook` package - the primary user-facing binding/conjure surface
(`Spellbook.bind`, `Spellbook.conjure`, `SpellBinder`, `Spell`, `SpellIndex`,
`Existence`, `SpellType`, `SpellbookConfiguration`) - was the last in-scope subsystem
without a child epic. A read-only structural scan (melder_1, 2026-07-22) over
`aether/spellbook/**` EXCLUDING `spell_compiler/**` shows 13 classes, of which
**10 are already at bar** and **3 carry the agent pair + sentinel but are missing the
three canonical context headers** (`Registration:` / `Subsystem Context:` /
`System Context:`) in their class docstrings:
- `Spell` (spell.py) - the per-binding runtime record.
- `Spellbook` (spellbook.py) - the primary bind/conjure surface (~6k LOC).
- `SpellbookCreationSystem` (spellbook_creation_system.py) - the conjure orchestration gate.

The gap is depth/context on three docstrings, not presence: each already has a rich
Rank-4/5 docstring, the agent pair (`__agent_purpose__` + `__ast_helper_access__`),
and the guard sentinel. Only the three subsystem/system context headers are absent.

## Subsystem Context Brief (read this, not the C-docs)
`aether/spellbook` (excluding the compiler) is the DGR's BINDING SURFACE - the layer a
user actually holds. `Spellbook` is the primary front door: it owns the local spell
registries + O(1) spell-id maps, runs the SpellCompiler phase pipeline through
`PhaseScheduler`, and conjures exactly ONE `Conduit` per instance. `Bind` reflects a
user object into a `SpellIndex` (stable ULID identity + active selected spell) plus a
`Spell` (the bind-time metadata record: existence, permissions, spellframe, hooks,
profile). `SpellbookCreationSystem` is the conjure-only orchestration helper Spellbook
delegates to (hook flow, the `check_system_state` policy/posture gate, conduit-ownership
stamping). `Existence`/`SpellType`/`SpellbookConfiguration`/`ResolutionStyleMatrix` are
the value/policy surfaces.

Where this sits: the Spellbook layer of the canonical boot order
`Aether|AetherUtilitySystem -> Crystallizer -> MutationResearch -> Nexus ->
AethericFrame -> Spellbook -> Conduit|Ward`. Everything here runs AFTER a frame exists
and BEFORE/DURING conjure; the `Spell` is the unit of currency every downstream layer
(SpellCompiler phases 1-11, SpellSystemStates validity, ChangeControl dirty-roots, Meld
resolution) keys on.

## The split (owner directive 2026-07-22: split evenly with melder_0)
- melder_1: `Spell` + `SpellbookCreationSystem` (this session).
- melder_0: `Spellbook` (the ~6k-LOC front door) - handed off via mailbox.

## Scope Boundaries
- IN: `src/melder/aether/spellbook/**` EXCLUDING `spell_compiler/**`.
- OUT: `spell_compiler/**` (owner-confirmed out of program), `__init__.py` export policy.
- Class attributes already present on all three; the ONLY change is adding the three
  canonical context headers to each class docstring. No behavior change, no method-doc
  churn on already-rich methods (No-Drive-By-Refactors).

## Guard Classification (already applied in source; recorded here for the docstrings)
- `Spell` - MELDER KERNEL, guarded (sentinel present); access=public because agents
  RECEIVE spells from bind()/viewer surfaces and read them, but never construct or bind
  one (binding a Spell is the category error the sentinel refuses).
- `Spellbook` - MELDER KERNEL, guarded; the user drives it via its public API but cannot
  bind() it.
- `SpellbookCreationSystem` - MELDER KERNEL, guarded; access=internal conjure machinery.

## Acceptance Criteria
- [ ] `Spell`, `Spellbook`, `SpellbookCreationSystem` each carry `Registration:` +
      `Subsystem Context:` + `System Context:` in their class docstring.
- [ ] No base class tagged; no method-doc churn; stripped-AST diff = docstring-only.
- [ ] Owner-run 3.14t suite green (agent reports "Not run." until then).

## Validation Plan
- Per class: read the body, hand-write the headers, `py_compile` + the read-only
  coverage scan (GAP -> 0) + a stripped-AST/diff check that the change is docstring-only.
- Not run by agent beyond py_compile + scans; owner runs 3.14t.

## Ticket Contract
- ENTRY_GATE: program contract + MRO law re-read (melder_1 REONBOARD 2026-07-22); scan
  identifying the exact 3-class gap complete.
- EXECUTION_BOUNDARY: the three named files under `aether/spellbook/` (compiler excluded).
- EXIT_GATE: all three carry the three context headers; owner 3.14t run.
- FAILURE_ESCALATION: DECISION_REQUEST on anything requiring a behavior change.

## Applicable Anti-Patterns
- [ ] No behavior change smuggled into a docstring pass.
- [ ] No touching spell_compiler (out of scope).
- [ ] No rewriting the existing rich docstrings/methods (drive-by).

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
- Epic notes: the split, per-class landings, and any cross-agent coordination.

## Notes
- DATETIME: 2026-07-22T23:15:00Z
  TYPE: FACT
  CLAIM: Read-only structural scan over `aether/spellbook/**` (compiler excluded) = 13
    classes; 10 at bar, 3 GAPS missing only the three context headers (Spell, Spellbook,
    SpellbookCreationSystem). All 3 already carry `__agent_purpose__` +
    `__ast_helper_access__` + the guard sentinel. This is the last unstarted in-scope lane.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:61-209
  - src/melder/aether/spellbook/spellbook_creation_system.py:44-72
  IMPACT: The remaining in-scope OCE docstring work is exactly 3 class docstrings.
  NEXT: melder_1 documents Spell + SpellbookCreationSystem this session; Spellbook handed
    to melder_0 via mailbox.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-22T23:20:00Z
  TYPE: FACT
  CLAIM: melder_0 landed the Spellbook handoff. Added the three canonical context headers
    (Registration / Subsystem Context / System Context) to the `Spellbook` class docstring
    (spellbook.py), hand-written from this epic's Subsystem Context Brief + Guard
    Classification. Registration = MELDER KERNEL guarded (user drives via public API, cannot
    bind() the Spellbook). Subsystem = front door of the binding surface (owns spell
    registries + O(1) id maps, runs SpellCompiler via PhaseScheduler, exactly one Conduit per
    instance, delegates conjure orchestration to SpellbookCreationSystem). System = the
    Spellbook layer of the canonical boot order; runs after a frame exists and before/during
    conjure; frame-join is a real coupling; the Spell is the downstream unit of currency.
    Docstring-only, no method churn; stripped-AST diff = 0 (outputs/verify_docstring_only.py).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:57-155
  IMPACT: Spellbook GAP -> 0. Acceptance Criteria #1 met for Spellbook pending owner run.
  NEXT: owner 3.14t run (agent reports "Not run.") -> close epic when all 3 landed.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-22T23:22:00Z
  TYPE: FACT
  CLAIM: melder_1 landed both split classes BY HAND. Added the three canonical context
    headers (Registration / Subsystem Context / System Context) to `Spell` (spell.py) and
    `SpellbookCreationSystem` (spellbook_creation_system.py), written from each class body +
    the re-read src_architecture/src_components. Spell = MELDER KERNEL guarded but
    access=public (agents RECEIVE spells from bind()/viewer surfaces, never construct/bind
    them); it is the spellbook subsystem's unit of currency (Bind produces it, Spellbook
    registers it, SpellCompiler keys phase artifacts on it, Meld resolves it).
    SpellbookCreationSystem = MELDER KERNEL guarded / internal: the conjure-only
    orchestration helper Spellbook delegates to (hook flow, the check_system_state
    posture/policy gate, define_conduit_into_spells ownership stamping). check_system_state
    behavior VERIFIED at spellbook_creation_system.py:1104 BEFORE writing the claim (static;
    raises on missing frame posture; non-dynamic admits only Policies.default).
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:205-225
  - src/melder/aether/spellbook/spellbook_creation_system.py:66-92
  - src/melder/aether/spellbook/spellbook_creation_system.py:1104-1151
  MEASURE: py_compile green on both; read-only stripped-AST diff vs HEAD = docstring-only
    (True/True); coverage scan = all 3 target classes OK. NO CODEGEN - hand-written
    single-file Edits after reading each body; scripts were read-only verification only.
    3.14t suite NOT run by agent (sandbox is 3.10; owner runs the definitive validation).
  IMPACT: All 3 in-scope spellbook-core gaps closed (melder_1: Spell + SpellbookCreationSystem;
    melder_0: Spellbook). AC #1 fully met pending owner run; the last in-scope OCE lane is done.
  NEXT: owner 3.14t run -> close this epic; the whole in-scope OCE program is then
    closure-ready (spell_compiler excluded by owner).
  REREAD: OPTIONAL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Lean child epic created 2026-07-22 (melder_1) for the last in-scope OCE lane: the three core
spellbook classes that were missing the Registration/Subsystem/System Context headers. DONE
2026-07-22 via an owner-directed split - melder_1 landed `Spell` + `SpellbookCreationSystem`,
melder_0 landed `Spellbook` - all docstring-only (stripped-AST diff vs HEAD = 0), py_compile
green, coverage scan 3/3 OK. Class attributes were already present; only the three context
headers were added. Compiler is out of scope (owner-confirmed 2026-07-22). Sole remaining
item: the owner's 3.14t validation run, after which this epic and the in-scope program close.
