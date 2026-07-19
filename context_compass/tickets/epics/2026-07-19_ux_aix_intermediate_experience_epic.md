# Epic: UX/AIX Intermediate experience exploration

## Metadata
- Epic ID: EPIC-2026-07-19-ux-aix-intermediate
- Status: in_progress
- Owner: cowork
- Agent Name: helper_f
- Priority: p2
- Created: 2026-07-19T12:52:00Z
- Updated: 2026-07-19T12:52:00Z

## Objective
The working developer's tier: SpellBinder fluent binding, spellframes and contracts (SpellMap/SpellContract), SpellSpace scoped resolution, spellbook and aether configuration (+builders), conduit linking and the ConduitCloud, SpellIndex membership verbs, crystallizer activation + first checkpoint.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-19 ("explore all the ways a user might use the
  library beginner -> intermediate -> expert -> Master... so we can properly explore
  what we need in init"). Examples live in UX_and_AIX_experiences/02_intermediate/.
- EXECUTION_BOUNDARY: UX_and_AIX_experiences/02_intermediate/ examples + findings notes ONLY.
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
- DATETIME: 2026-07-19T16:10:00Z
  TYPE: DECISION
  CLAIM: Owner ruling: PERMISSIONS ARE LINKING VOCABULARY - read/create/block
    govern what LINKED conduits may do in dynamic worlds, and that is their ONLY
    purpose; they are not a local-meld concept. ALL permissions teaching moved out
    of beginner: 28 -> intermediate/11_permissions_linking_vocabulary (reframed);
    permissions= kwargs stripped from beginner 03/07/18/33/37/40 (defaults apply);
    37's cheatsheet row is now a tier-02 pointer ("linking policy for shared
    worlds"); beginner backfilled with 28_real_objects_no_wrappers (identity law:
    melder hands back the real instance, no proxies). Beginner grep-verified
    permissions-free (39's namespace inventory + 37's pointer row exempt).
    Beginner holds 40; intermediate 11.
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/11_permissions_linking_vocabulary.py:1-15
  - UX_and_AIX_experiences/01_beginner/28_real_objects_no_wrappers.py:1-25
  IMPACT: Hour one shrinks to pure local-world concepts; permissions debut beside
    link(), where they mean something.
  NEXT: Permissions example should grow a LIVE demo (linked borrower blocked/read-
    limited) once the linking lessons expand - verification-gated.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T15:58:00Z
  TYPE: MEASURE
  CLAIM: Dynamic-mode arc opened (owner-directed). AUTHORED: 10_dynamic_named_worlds
    (canonical owner/borrower pattern LIFTED FROM the component suite - dynamic
    named roots + link()=True + static-vs-dynamic framing) and
    test_intermediate_probes.py (3 rows: dynamic pattern outside the component
    suite; crystallizer ACQUISITION-PATH probe - prints which public doors exist on
    Aether, because the user path to the live crystallizer in a dynamic no-Nexus
    world is NOT yet verified and the crystallizer lessons wait on this print;
    config-before-bind law - the crystallizer-off EXEMPTION pinned now, the
    active-crystallizer refusal (error text captured verbatim from a live run-2
    traceback) lands once acquisition is known). Tier stands at 10 examples.
    NEXT LESSONS QUEUED (verification-gated): crystallizer configure/activate in a
    dynamic no-Nexus world, config-before-bind demonstrated live, first
    checkpoint, CrystallizerBootstrap; then Nexus-static contrast when the expert
    tier opens AR.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_cluster.py:780-800
  - UX_and_AIX_experiences/pytest_examples/test_intermediate_probes.py:1-80
  IMPACT: Dynamic mode enters the curriculum on canon, not guesses; the
    crystallizer arc has its truth-gathering probe in place.
  NEXT: Owner runs the intermediate probes; their prints unlock the crystallizer
    lessons next wave.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8


## Context / Handoff Summary
Method: every example imports melder as md ONLY - a deep-path import in an example
IS the finding. Examples are runnable scripts with honest asserts; they ride the
owner's 3.14t runs (device VM cannot import the runtime).
