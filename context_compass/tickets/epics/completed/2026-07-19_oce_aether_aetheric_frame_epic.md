# EPIC-2026-07-19-oce-aether-aetheric-frame

- Completed: 2026-07-19T21:40:00Z
- Summary: All 60 classes under `src/melder/aether/aetheric_frame/**` raised to 3+ canonical
  docstring headers with subsystem and system context. No behaviour changes. Owner 3.14t
  pytest OUTSTANDING.

- Status: done_pending_owner_run
- Created: 2026-07-19T19:00:00Z
- Updated: 2026-07-19T21:40:00Z
- Owner: cowork
- Agent Name: melder_0
- Parent: tickets/epics/2026-07-19_object_contract_enrichment_program_epic.md

## Problem / Opportunity
The frame layer carries the runtime's ISOLATION BOUNDARY and its entire control plane -
60 classes, of which 46 were thin (<=2 canonical headers) and 5 carried none at all. The
control plane is the least self-explaining part of the system precisely where correctness
reasoning matters most: admission, claim modes, validity, and risk.

## Context (why now, relationship to architecture)
Layer 2 of the runtime: Aether -> AETHERIC_FRAME -> Spellbook -> Conduit -> Meld ->
Creations. Frames come BEFORE books in the canonical boot order because the frame owns the
dynamic gate that conjure's `check_system_state` reads. Evidence:
`system_docs/src_architecture.md` (Aetheric Frame Responsibilities, Transaction Admission
Plane) and `src_components.md` (DevOps Control Plane).

## MRP alignment
MRP: docstrings ARE the API for a public library, so partial or guessed contracts are worse
than none - they get trusted.

## Ticket Contract
- ENTRY_GATE: parent program epic active; conduit child epic complete.
- EXECUTION_BOUNDARY: `src/melder/aether/aetheric_frame/**` ONLY. Docstrings and comments
  only - zero behaviour changes, zero signature changes.
- DEPENDENCIES: THE OBJECT CONTRACT + THE COMPREHENSION LAW from the parent epic; the
  mandatory 5-check codemod validation set.
- EXIT_GATE: 60/60 at 3+ canonical headers; 5-check validation passes; owner 3.14t green.
- FAILURE_ESCALATION: any behaviour-changing find becomes a DECISION_REQUEST; never
  self-applied.

## Goals / Non-goals
Goals: Rank 4+ class docstrings on all 60 classes with subsystem and system context.
Non-goals: no behaviour changes, no renames, no guard reclassification (this package was
already correctly classified).

## Scope boundaries
IN: aetheric_frame.py, aetheric_frame_configuration.py, conduit_cloud.py, dev_ops/**
(spell_system_states, change_control_manager + transaction/embargo/conflict managers and
the transaction strategy family, risk_manager, incident_manager,
devops_information_registry + the information strategy family).
OUT: everything else under `src/melder`.

## Requirements
Functional: every class carries the canonical headers appropriate to its kind, with each
behavioural claim verified against source before being written.
Non-functional: no `# noqa`, no `type: ignore`, no PEP 604 unions, no wildcard imports
(`skills/python/banned_patterns.md:57-71`); never delete a comment or docstring
(`skills/python/comments.md:17-19`).

## Acceptance criteria
- [x] 60/60 classes at 3+ canonical headers.
- [x] py_compile clean across the package.
- [x] 0 trapped lines, 0 unbound `_mrg`, 0 duplicate sentinels.
- [x] 0 comment/docstring loss vs HEAD.
- [ ] Owner 3.14t pytest green.

## Risks / Mitigations
- RISK: batch docstring insertion producing malformed spacing. OCCURRED and was repaired -
  82 files had a canonical header landing directly against a preceding bullet with no
  blank line; detected and fixed in-pass. Cosmetic only, never a syntax issue.
- RISK: documenting a contract the code does not honour. MITIGATION: read the
  implementation first; every claim below traces to source.

## Validation plan
py_compile over the package; AST audits for trapped lines, name binding, duplicate
sentinels, and comment/docstring preservation. Owner runs pytest on 3.14t - the sandbox is
3.10 and cannot execute this package.

## Decision Log
- 2026-07-19: aetheric_frame taken after conduit, following the parent epic's
  user-facing-first ordering down the runtime layers.

## State Transition Event
- from_state: in_progress
- to_state: done_pending_owner_run
- transition_reason: 60/60 landed and statically validated; only the owner's 3.14t run
  remains.

## Milestones
- [x] M1 survey (60 classes measured)
- [x] M2 frame core (AethericFrame, ConduitCloud, AethericFrameConfiguration)
- [x] M3 validity model (SpellSystemStates, SpellSystemState, ConduitResolutionState,
      SpellValidity, SpellState, SpellStateChangeReason)
- [x] M4 admission plane (TransactionStrategy family, embargo/conflict managers,
      ChangeControlTransactionManager)
- [x] M5 DevOps services (DevOpsManager, RiskManager, IncidentManager + vocabulary,
      DevopsInformationRegistry + the information strategy family)
- [x] M6 validation (5-check set)
- [ ] M7 owner 3.14t pytest

## Applicable Anti-Patterns
- Documenting from naming rather than implementation (Unknowns Gate).
- Claiming tests ran when they did not.
- Batch-editing docstrings without re-verifying spacing and structure afterwards.

## Artifact Links (Optional)
None.

## Context Management
CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
Epic-level: cross-tranche direction and the contract facts recovered per tranche.

## Notes

- TYPE: MEASURE
  DATETIME: 2026-07-19T21:40:00Z
  AGENT: melder_0
  CLAIM: 60/60 at 3+ canonical headers (14 at epic open). Five subsystems of the OCE
    program are now complete: aetheric_frame 60/60, conduit 30/30, crystallizer 62/62,
    mutation_research 23/23, utilities 47/48 - 222 of 223 classes.
  VALIDATION: py_compile ALL CLEAN, 0 trapped lines, 0 unbound `_mrg`, 0 duplicate
    sentinels, 0 comment/docstring loss. Not run: pytest (needs 3.14t; sandbox is 3.10).
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1-120
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1-95
  IMPACT: The control plane is now self-explaining at the point of use.
  NEXT: Owner 3.14t run; then oce-nexus-rift (53 classes).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- TYPE: FACT
  DATETIME: 2026-07-19T21:40:00Z
  AGENT: melder_0
  CLAIM: THE FOUR CONTRACT FACTS WORTH CARRYING FORWARD from this package, each recovered
    by reading implementation rather than inferred from naming:
    1. SCOPE CLAIMS EXCLUDE OTHER TRANSACTIONS ONLY. A meld-side reader holds no claim yet
       holds its gate ticket across the whole executor, so scope claims alone cannot make
       it wait. `NotchTransactionStrategy` and
       `UnelectConduitClusterLeaderTransactionStrategy` therefore drain lineage gates
       before their swap and reopen on EVERY exit path. Transaction claims serialize
       STRUCTURE; gates serialize RUNTIME; an operation racing runtime readers needs both.
    2. ELECT/UNELECT ASYMMETRY IS PRINCIPLED, not an oversight. Election runs
       inert -> active and the cluster door hard-errors while inert, so no meld can be
       mid-create and a light atomic envelope is provably sufficient. Unelection runs
       active -> inert where a reader may be in flight, so it needs the full freeze.
    3. REGISTRY ASYMMETRY IS EVIDENCE, NOT DRIFT. If the plane's claim ("transactions
       write the registry through commit deltas while scopes are held") holds, forward and
       reverse mirrors cannot disagree - they are written together under one claim. So
       `RegistryConsistencyAuditStrategy` is a falsification test for the core invariant,
       and any finding means a write bypassed the plane or a delta applied partially.
    4. CLUSTER JOIN/LEAVE SELF-CONFLICT IS A HANG, NOT AN ERROR. An in-window share that
       opens its own `cluster_link` runs under a CONDUIT identity while the enclosing seal
       runs under a CLUSTER identity, so the embargo sees a different owner, blocks, and
       times out.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py:1-90
  - src/melder/aether/aetheric_frame/dev_ops/information_strategies/registry_consistency_audit_strategy.py:1-60
  IMPACT: These four are cross-cutting laws, not local details; they belong in any future
    reader's model of the control plane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Child epic of the OCE program covering `src/melder/aether/aetheric_frame/**` (60 classes),
complete at 60/60 and statically validated. Only the owner's 3.14t pytest run remains
before formal closure. Five OCE child epics are now landed; `oce-nexus-rift` (53) is next.
