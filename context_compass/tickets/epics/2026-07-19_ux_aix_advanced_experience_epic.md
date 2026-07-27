# Epic: UX/AIX Advanced experience exploration

## Metadata
- Epic ID: EPIC-2026-07-19-ux-aix-advanced
- Status: pending
- Owner: cowork
- Agent Name: helper_f
- Priority: p2
- Created: 2026-07-19T12:52:00Z
- Updated: 2026-07-19T12:52:00Z

## Objective
The AR + research tier: Nexus enablement, rifts, rooms by RiftSpaceType, workstation binding canvases, frame viewers and the View* family, research sets with typed lanes, diff/impact/foresight reads, drift views.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-19 ("explore all the ways a user might use the
  library beginner -> intermediate -> expert -> Master... so we can properly explore
  what we need in init"). Examples live in UX_and_AIX_experiences/03_advanced/.
- EXECUTION_BOUNDARY: UX_and_AIX_experiences/03_expert/ examples + findings notes ONLY.
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

## DECISION - 2026-07-25 19:23 UTC - tier renamed to ADVANCED (README ladder match)
  RULING: owner (2026-07-22) - the ladder is Beginner/Intermediate/Advanced/
    Expert per the shipped README. This epic (formerly "Expert", folder
    03_expert) is now the ADVANCED tier: frames as worlds, static rooms,
    clusters, deep overrides. Folder renamed 03_expert -> 03_advanced; the two
    seeded lessons retiered in their headers (cluster declaration, deep
    override paths). Historical notes below keep their original wording.
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## MEASURE - 2026-07-26 17:13 UTC - advanced tier opens: owner syllabus wave 1 (lessons 03-05)
  WHAT: Owner syllabus for advanced: devops config, aetheric_frame config,
    frame management/layers of separation, utility-system logger, "static
    and compatibility mode", crystallizer basics LAST (owner adding epic
    items himself). Wave 1 authored after source verification:
    - 03_frames_as_worlds: categories arc ACT 3 - Spellbook(aetheric_frame=)
      births an isolated world; same class + name in two frames, zero
      collision; unique = singleton PER FRAME; per-frame reuse asserted.
    - 04_frame_posture_public_door: configure_aether_frame(system_state=
      "dynamic") pre-conjure -> plain conjures INHERIT and link (settle law
      driven from the config side); posture freezes at first conjure -
      reconfigure refuses (caught + printed).
    - 05_utility_system_logger: boots-silent law; attach_logger /
      enable_logging public doors; None detaches (BUG-278 retire law noted
      in source read).
    Harness: test_advanced_examples.py runner (sys.modules import law) +
    test_advanced_probes.py (4 rows: frame isolation pin, posture+freeze,
    devops-flag gate via seam, logger lifecycle).
  FINDINGS:
    - NO PUBLIC DOOR for frame devops flags (disable_*): component suite
      stages via PRIVATE book._aetheric_frame_configuration. Probe pins the
      gate through the seam; init/public-surface gap recorded for owner.
    - "compatibility mode" absent from src/melder - awaiting owner
      definition (concept map notes it).
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:366-1364 (verb sweep)
  - src/melder/aether/aether.py:502-560 (attach_logger contract, BUG-278)
  - src/melder/aether/spellbook/spellbook.py:203 (aetheric_frame ctor door)
  - grep: no public frame accessor on Aether; "compatibility" absent
  NEXT: Owner runs the harness (advanced rows now included); crystallizer
    lessons wait for the owner's epic additions + the acquisition-path
    probe's print.
  REREAD: REQUIRED
  SCORE_0_TO_10: -

## MEASURE - 2026-07-26 17:42 UTC - posture knob wave: lessons 06-07 + probes
  WHAT: 06 frame_caching_knob (system_caching_enabled via the public
    configure_aether_frame door). 07 frame_posture_cheatsheet - all 15
    AethericFrameConfiguration knobs mapped and explained in one runnable
    reference (mode / AR eligibility / sharing / caching / 7 devops brakes /
    transaction patience / 3 presets / freeze law), the advanced twin of
    beginner 37. Advanced probes now 5 rows (+caching door). Findings stand:
    no public staging door for devops brakes or cache_root_path.
  EVIDENCE:
  - UX_and_AIX_experiences/03_advanced/06-07_*.py
  - UX_and_AIX_experiences/pytest_examples/test_advanced_probes.py
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## Context / Handoff Summary
Method: every example imports melder as md ONLY - a deep-path import in an example
IS the finding. Examples are runnable scripts with honest asserts; they ride the
owner's 3.14t runs (device VM cannot import the runtime).
