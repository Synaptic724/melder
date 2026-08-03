# Epic: UX/AIX Expert experience exploration

## Metadata
- Epic ID: EPIC-2026-07-19-ux-aix-expert
- Status: pending
- Owner: cowork
- Agent Name: examples_0
- Priority: p2
- Created: 2026-07-19T12:52:00Z
- Updated: 2026-08-01T10:41:33Z

## Objective
The operator's tier: CrystallizerBootstrap pod restart, external persistence meshes (user DB callables), profile/checkpoint operations, group composition and campaign evolution, synthesis previews, class_wraps-built custom decorators over bound spells, multi-frame orchestration.

## Notes

- DATETIME: 2026-08-02T22:15:00Z
  TYPE: MEASURE
  CLAIM: EXPERT TIER OPENED - 6 LESSONS, 20 PROBE ROWS, AND THE PUBLIC ROOT
    IS NOW FULLY TAUGHT. Coverage went 49/63 -> 60/63; the three remaining
    are `__author__`, `__description__`, `__license__`, which beginner 12
    already covers as module reads. 103 lessons across four tiers
    (41 / 37 / 19 / 6).
    LESSONS: 01 pod boot ("the ORDER is the product"), 02 the external mesh,
    03 research sets / lanes / residency, 04 diffs are derived never stored,
    05 ProtocolCrafter (the one tool that writes), 06 two knobs and a
    terminator per rung.
    NEW HARNESS FILES: pytest_examples/test_expert_examples.py (runner) and
    test_expert_probes.py (20 rows). The probe fixture adds
    MutationResearch to the singleton reset - expert is the first tier to
    touch it, so all five now reset per row.
  EVIDENCE: scripted `md.<Name>` sweep over
    `UX_and_AIX_experiences/**/[0-9]*.py` against `melder.__all__`, and
    py_compile over every new file.
  IMPACT: The four-tier ladder now covers every public name melder exports.
    PROCESS NOTE, because it is the fix that actually held: access markers
    and property-vs-method were checked BEFORE authoring each lesson this
    time, not after a red run. That is the correction from the withdrawn
    Scan lesson, applied rather than merely recorded.
  NEXT: UNRUN. Rides the owner's 3.14t like every other tier.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-08-02T22:00:00Z
  TYPE: DECISION
  CLAIM: THE CRYSTALLIZER MACHINERY SHOULD NOT BE EXPORTED. The tier-split
    ruling of 2026-08-01 said expert gets "crystallizer loading features and
    saving, synthetic modules", which read as though `RestoreEngine`,
    `LoadPlan`, `LoadAdmission`, `GraftRunner`, `CrystalLoaderSystem` and
    `SyntheticModule` needed to reach the public root. THEY DO NOT.
    Owner 2026-08-02: "don't you just use crystallizer for that shit?" -
    correct, and the facade already carries it.
  EVIDENCE: `Crystallizer` exposes 25 verbs covering the whole scope line:
    SAVING      create_checkpoint, flush_checkpoint, save_formation
    LOADING     load_checkpoint, reload_cached_checkpoint,
                reload_profile_from_cache, reload_profile_from_external,
                reload_formations_from_external
    FORMATIONS  restore_formation, list_formations, analyze_formation,
                delete_formation
    GRAFTS      capture_index_graft, graft_index,
                store_index_graft_external, fetch/list variants
    The machinery it delegates to is referenced across 9-18 src files each -
    internal wiring, not user surface.
  IMPACT: This is the FOURTH instance of one pattern in a single session:
    a capable internal collaborator behind a facade that is the real API.
      Scan            -> `Spellbook.scan(module)` is the door (withdrawn lesson)
      SpellOverrider  -> the override PAYLOAD dict is the door (expert-adjacent)
      SpellExaminer   -> curated OFF the root this session
      crystal loaders -> `Crystallizer` is the door
    The rule that keeps falling out: IF A FACADE COVERS IT, THE COLLABORATOR
    IS NOT USER SURFACE. Export is not the test - the presence of a working
    door is.
  NEXT: no export work. Expert teaches the facade, which lessons 01-06
    already do.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-08-02T22:00:00Z
  TYPE: DECISION
  CLAIM: `SyntheticModule` STAYS UNEXPORTED, and for a different reason than
    the loaders. It is not merely behind a facade - IT HAS NO AUTHORING PATH
    AT ALL. Its constructor demands `spell_crystal_id`, `source_sha256` and
    `binding_signature`, all of which only exist once a spell has already
    been harvested, and its only construction site is the restore lane.
    Owner: "synthetic module is for agents not really sure where to go from
    there because a lot of this shit is new."
  EVIDENCE: EPIC-2026-08-02-agent-authored-synthetic-modules, filed this
    session, which documents the closed lifecycle in full.
  IMPACT: Exporting it today would ship HALF A FEATURE - a public class an
    agent cannot originate - which is exactly the mistake SpellExaminer was
    curated off the root for (public class, public extension point, private
    instance). The honest order is: give it an authoring path FIRST, then
    export, then teach. Not the reverse.
  NEXT: gated on EPIC-2026-08-02-agent-authored-synthetic-modules. No expert
    lesson until an agent can actually author one.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-19 ("explore all the ways a user might use the
  library beginner -> intermediate -> expert -> Master... so we can properly explore
  what we need in init"). Examples live in UX_and_AIX_experiences/04_expert/.
- EXECUTION_BOUNDARY: UX_and_AIX_experiences/04_master/ examples + findings notes ONLY.
- DEPENDENCIES: init composition story (the 66-name root is the surface under test);
  prior tiers' findings.
- EXIT_GATE: every example runs green on the owner's 3.14t; every discovered
  init-surface gap either landed on the init story or recorded as a rejected
  curation call with reasons; owner walkthrough of the tier.
- FAILURE_ESCALATION: DECISION_REQUEST on any gap whose fix would widen the public
  surface beyond the ConduitWard law.

## Noting Behavior
- MEASURE per authoring wave (examples written, surfaces exercised, gaps found).
- DECISION for every init-surface change the tier proposes.

## Notes

## DECISION - 2026-07-25 19:23 UTC - tier renamed to EXPERT (README ladder match)
  RULING: owner (2026-07-22) - the ladder is Beginner/Intermediate/Advanced/
    Expert per the shipped README. This epic (formerly "Master", folder
    04_master) is now the EXPERT tier: AR rooms, transactions, checkpoints,
    governed mutation, external DB meshes. Folder renamed 04_master ->
    04_expert. Historical notes below keep their original wording.
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

- DATETIME: 2026-08-01T10:41:33Z
  TYPE: DECISION
  CLAIM: Ownership reassigned helper_f -> examples_0 under owner directive this session. ONLY the
    `Agent Name` field changed. `Owner: cowork` is deliberately unchanged: `owner` is the
    executor/runtime identity and `agent_name` is the assignment identity - different fields.
    No status, scope, acceptance criterion, or prior note was altered.
  EVIDENCE:
    - agent_onboarding/default/general/skills/agent_identity.md:21-24
    - tickets/epics/2026-07-19_ux_aix_expert_experience_epic.md:5-10
  IMPACT: Tier stays `pending` and is the thinnest of the four (46 lines) - it carries the ladder
    ruling and little else, so it needs the most authoring once the lower tiers land.
  NEXT: Blocked behind beginner/intermediate/advanced; no expert authoring until the ladder below
    it is owner-accepted.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## State Transition Event - 2026-08-01T10:41:33Z
- from_state: assigned helper_f
- to_state: assigned examples_0
- transition_reason: owner directive this session (claim the four UX/AIX epics, remove helper_f
  from ownership). Status stays `pending` - assignment changed, lifecycle did not.

## Context / Handoff Summary
Method: every example imports melder as md ONLY - a deep-path import in an example
IS the finding. Examples are runnable scripts with honest asserts; they ride the
owner's 3.14t runs (device VM cannot import the runtime).
