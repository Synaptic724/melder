# EPIC-2026-07-19-oce-nexus

- Completed: 2026-07-19T23:10:00Z
- Summary: All 114 classes under `src/melder/nexus/**` raised to 3+ canonical docstring
  headers with subsystem and system context - the entire AR surface (Nexus root, Rift, the
  three room postures, viewer/command/workstation, the codegen engine, the ACL family,
  descriptors, and projections). No behaviour changes. Owner 3.14t pytest OUTSTANDING.

- Status: done_pending_owner_run
- Created: 2026-07-19T21:45:00Z
- Updated: 2026-07-19T23:10:00Z
- Owner: cowork
- Agent Name: melder_0
- Parent: tickets/epics/2026-07-19_object_contract_enrichment_program_epic.md

## Problem / Opportunity
Nexus is the PUBLIC AR surface - the layer agents and users actually reach - yet 101 of its
114 classes were thin (<=2 canonical headers). The ACL family in particular encodes the
system's entire permission model across three independently versioned chains, and none of
that reasoning was written down where a reader would find it.

## Context (why now, relationship to architecture)
`Nexus` is the public singleton AR root over the hidden `Aether` substrate:
Nexus -> Rift -> RiftSpace, with `FrameDescriptorManager` (visibility),
`FrameACLManager` (permissions), `NexusFrameManager` (authoring/topology), and
`RiftGateController` (admission) beneath it. Evidence: `system_docs/src_architecture.md`
(Nexus and Rift Responsibilities, ACL selection model) and `src_components.md`
(AR Runtime Surface, Codegen Internal Engine, Nexus Descriptor And ACL Managers).

## MRP alignment
MRP: this is the public-facing surface of a public library, so its contracts must be right
the first time. Docstrings here are the API.

## Ticket Contract
- ENTRY_GATE: parent program epic active; conduit and aetheric_frame child epics complete.
- EXECUTION_BOUNDARY: `src/melder/nexus/**` ONLY. Docstrings and comments; zero behaviour
  changes, zero signature changes.
- DEPENDENCIES: THE OBJECT CONTRACT + THE COMPREHENSION LAW; the mandatory 5-check
  validation set; the INJECTION-SEAM TEST from the conduit epic.
- EXIT_GATE: 114/114 at 3+ canonical headers; 5-check validation passes; owner 3.14t green.
- FAILURE_ESCALATION: any behaviour-changing find becomes a DECISION_REQUEST.

## Goals / Non-goals
Goals: Rank 4+ class docstrings on all 114 classes; adjudicate the three MRO-risk bases.
Non-goals: no behaviour changes, no guard additions (nexus was already 113/114 guarded).

## Scope boundaries
IN: nexus.py, nexus_frame_manager/builder/configuration, frame_descriptor/**,
configuration/**, acl/** (configurations, profiles, rules, validators, compiler,
container, chain), rift/** (rift, rift_space + 3 room types, command_system + 3 postures,
frame_viewer + helpers, workstation, gates, frame_link, projections, memory/event systems,
codegen_system/**).
OUT: everything else under `src/melder`.

## Requirements
Functional: every class carries canonical headers with each behavioural claim verified
against source. Non-functional: no `# noqa`, no `type: ignore`, no PEP 604 unions
(`banned_patterns.md:57-71`); never delete a comment or docstring (`comments.md:17-19`).

## Acceptance criteria
- [x] 114/114 classes at 3+ canonical headers.
- [x] Three MRO-risk bases adjudicated with the injection-seam test.
- [x] py_compile clean; 0 trapped lines; 0 unbound `_mrg`; 0 duplicate sentinels.
- [x] 0 comment/docstring loss vs HEAD.
- [ ] Owner 3.14t pytest green.

## Risks / Mitigations
- RISK: single-line docstrings breaking a batch inserter. OCCURRED on
  `_NamedCleanableProfile`; the `ast.parse` write-gate refused the write and nothing was
  corrupted. Inserter now expands single-line docstrings to multi-line before appending.
- RISK: documenting a contract the code does not honour. MITIGATION: every class docstring
  was read before its block was written.

## Validation plan
py_compile plus AST audits for trapped lines, name binding, duplicate sentinels, and
comment/docstring preservation. Owner runs pytest on 3.14t; the sandbox is 3.10 and cannot
execute this package.

## Decision Log
- 2026-07-19: nexus taken after aetheric_frame, completing the public-facing surfaces
  before the remaining aether internals (spellbook core, spell_compiler is out of scope).

## State Transition Event
- from_state: in_progress
- to_state: done_pending_owner_run
- transition_reason: 114/114 landed and statically validated; only the owner's 3.14t run
  remains.

## Milestones
- [x] M1 survey + MRO adjudication
- [x] M2 AR spine (Nexus, Rift, RiftSpace, CommandSystem, FrameViewer)
- [x] M3 room ladder + postures + workstation + gates + frame-link
- [x] M4 managers, builders, configuration vocabulary, descriptors, projections
- [x] M5 ACL family (configurations, profiles, presets, rules, chain, container,
      compiler, validators)
- [x] M6 codegen engine (transaction, validation chain, namespace strategies, execution,
      observability)
- [x] M7 validation (5-check set)
- [ ] M8 owner 3.14t pytest

## Applicable Anti-Patterns
- Documenting from naming rather than implementation (Unknowns Gate).
- Batch-inserting into docstrings without handling the single-line form.
- Claiming tests ran when they did not.

## Artifact Links (Optional)
None.

## Context Management
CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
Epic-level: cross-tranche direction and the contract facts recovered per tranche.

## Notes

- TYPE: DECISION
  DATETIME: 2026-07-19T23:10:00Z
  AGENT: melder_0
  CLAIM: MRO ADJUDICATION - all three nexus risk entries are REDUNDANT, NOT DEFECTIVE, and
    their sentinels STAY. `RiftSpace` (base of StaticRiftSpace/CapabilityRiftSpace/
    CodegenRiftSpace), `CommandSystem` (base of the three postures), and `FrameViewer`
    (base of StaticFrameViewer) are all guarded bases whose every subclass is
    melder-internal: rooms are constructed only inside `Rift` from `space_type`
    (rift.py:917-933) and each room builds its own command system. A repo-wide grep for
    injection kwargs (`*_class`, `*_factory`, room/command/viewer parameters) returns no
    user seam. The inherited sentinel therefore cannot reach a user-written class.
    The reasoning is now written INLINE on each of the three bases so a future auditor does
    not "fix" the MRO law by stripping a correct sentinel.
    This closes 3 of the 14 repo-wide MRO risk entries. Remaining in-scope: none.
    `PersistenceAnalysisStrategy` (crystallizer) stays the ONLY confirmed defect, because it
    alone has a real injection seam (`PersistenceAnalyzer(strategies=...)`).
  EVIDENCE:
  - src/melder/nexus/rift/rift.py:917-933
  - src/melder/nexus/rift/rift_space/rift_space.py:26-26
  IMPACT: The injection-seam test is now validated across two subsystems and 5 bases;
    it should be the standard adjudication for the remaining child epics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- TYPE: FACT
  DATETIME: 2026-07-19T23:10:00Z
  AGENT: melder_0
  CLAIM: THE CONTRACT FACTS WORTH CARRYING FORWARD from the AR surface:
    1. THE ROOM LADDER IS PROTECTIVE, NOT ADDITIVE. `codegen` is deliberately NOT
       `capability` plus more - it keeps a SLIMMER manual surface precisely because it can
       generate and execute code. Weak-vs-strong workstation defaults follow the same
       logic: a static room observing the world must not extend the lifetime of what it
       observes.
    2. STATIC DOES NOT DENY `meld()` - IT NEVER INHERITS IT. Inheriting a dangerous method
       and refusing it leaves it on the object, in introspection, and defended at every
       call site. Never inheriting makes the narrow surface HONEST, which matters because
       agents enumerate `list_supported_command_methods`.
    3. VALIDATE BEFORE BUILD is the codegen engine's central ordering. The live namespace is
       constructed only AFTER validation is accepted, so no execution environment is ever
       materialized for code about to be rejected. `CodegenNameResolutionStrategy` validates
       against the namespace CONFIGURATION rather than a live namespace precisely to
       preserve that ordering.
    4. CONTROL SURFACES COME IN STATIC/RUNTIME PAIRS. Builtins: static
       `CodegenBuiltinPolicyStrategy` + runtime `CodegenBuiltinsStrategy` withholding the
       name. Recursion: static `CodegenRecursiveControlStrategy` + runtime
       `CodegenControlSurface` applying the permission. Neither half suffices alone -
       static analysis of Python is not exhaustive, and a name present at runtime is
       reachable indirectly.
    5. `CodegenControlSurface` EXISTS SO THE RAW ENGINE NEVER LEAKS. Exposing
       `CodegenSystem` directly would hand generated code the validator, compiler, and
       executor as attributes - an escape hatch around every gate.
    6. PROJECTIONS SWAP AS ONE UNIT. `FrameProjectionSet` bundles view/command/codegen with
       a generation marker so a room can never run view answers from one ACL revision
       against command answers from another.
    7. ACL SEPARATES REUSABLE FROM APPLIED. Profiles are shared library postures; applied
       configurations own DETACHED rulesets so a later profile edit cannot retroactively
       rewrite what a committed revision granted.
  EVIDENCE:
  - src/melder/nexus/rift/rift_space/rift_space.py:26-120
  - src/melder/nexus/rift/codegen_system/namespace/codegen_control_surface.py:1-60
  IMPACT: These are cross-cutting AR laws; they belong in any reader's model of the layer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- TYPE: MEASURE
  DATETIME: 2026-07-19T23:10:00Z
  AGENT: melder_0
  CLAIM: OCE PROGRAM STATUS after this epic: 347/577 classes repo-wide (60%).
    COMPLETE: nexus 114/114, crystallizer 62/62, mutation_research 23/23,
    utilities 47/48 (Package parked as dead code). REMAINING: aether 100/328 - of which
    aetheric_frame (60) and conduit (30) are done, so the outstanding work is spellbook
    core plus `spell_compiler`, and the owner ruled spell_compiler OUT OF SCOPE
    ("the goal is user facing assets").
  VALIDATION: 5-check set PASSES on nexus - compile ALL CLEAN, 0 trapped lines,
    0 unbound `_mrg`, 0 duplicate sentinels, 0 comment/docstring loss.
    Not run: pytest (needs 3.14t; sandbox is 3.10).
  NEXT: oce-aether-spellbook-core, then the program epic closes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Child epic of the OCE program covering `src/melder/nexus/**` (114 classes), complete at
114/114 and statically validated. Six OCE child epics are now landed (package-root,
utilities, mutation-research, crystallizer, conduit, aetheric-frame, nexus). The program
sits at 347/577 repo-wide; the remaining in-scope work is spellbook core, since
`spell_compiler` is owner-ruled out of scope. Only the owner's 3.14t pytest run stands
between this epic and formal closure.
