# Story: managed_bind_options - the four managed keywords on every bind path, the Spell fields and the record

- Completed: 2026-10-15T12:32:07Z
- Summary: landed 0.2.8242 - `ManagedSpellMode`; the four `managed_spell_*` bind options on Spellbook,
  Conduit, SpellBinder and scan_bind with their refusals; the Spell fields; the managed-only id part; the
  crystal capture and restore/graft replay (RecordVersion 4.2.0). Release-note section
  "`Existence.managed_spell_quantity`: objects leased from a root-owned pool and released back" extended.

## Metadata
- Story ID: STORY-2026-10-15-managed_bind_options
- Epic: EPIC-2026-10-14-managed_spell_quantity (tickets/epics/2026-10-14_managed_spell_quantity_epic.md); story 2 of 7
- Status: done
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-15T09:29:51Z
- Updated: 2026-10-15T12:32:07Z

## User Narrative
As an agent, I want to bind a class as `Existence.managed_spell_quantity` with its mode, limit, queue timeout and
reset methods, so that the Spell carries everything its pool needs and the crystallizer records and restores it.

## Value / MRP Alignment
The owner's ruling keeps every managed requirement on the Spell as bind options (no settings object). Validation at
bind gives an agent a precise error before anything compiles, and the managed-only fingerprint part keeps every
existing spell id byte-identical.

## Ticket Contract
- ENTRY_GATE: S1 closed; system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_bind_options.md
  written and linked; the mapping note recorded; U1 and U2 (epic B5) answered from source.
- EXECUTION_BOUNDARY: src/melder/aether/spellbook/existence/managed_spell_mode.py (new),
  src/melder/aether/spellbook/spellbook.py (`bind`, `bind_inactive`), src/melder/aether/spellbook/bind/bind.py
  (`_bind_logic`, `sha256_profile`), src/melder/aether/spellbook/spell.py (fields, properties),
  src/melder/aether/spellbook/spellbinder.py, src/melder/aether/spellbook/bind/scan.py, the Conduit bind facades if
  any, src/melder/crystallizer/crystals/spell_crystal.py, the restore engine and graft runner bind replay,
  src/melder/crystallizer/persistence/record_version.py; their tests.
- DEPENDENCIES: S1 (the member).
- EXIT_GATE: its tests green under `-X gil=0` and `-X gil=1`; the touched modules' existing suites green; one notch
  taken from `__version__` at landing with the running release note's managed section extended; the epic's Build
  Specification updated with what this story settled; story closed (completed folder, board sync)
- FAILURE_ESCALATION: DECISION_REQUEST if a change would alter an existing member's behaviour, an existing spell id or
  record, or the frame -> conduit -> Book lock order; CONFLICT when the source contradicts the epic's Build
  Specification (fix the spec first); BLOCKER when a gate cannot be met

## Requirements (Functional)
- `ManagedSpellMode` (elastic, limited_quantity, queue); bind accepts the member or its name.
- `managed_spell_mode`, `managed_spell_limit`, `managed_spell_timeout_seconds`, `managed_spell_reset_methods` on
  `Spellbook.bind`, `Spellbook.bind_inactive`, SpellBinder and `scan_bind` (target options; refused as metadata keys),
  plus any Conduit bind facade (U1).
- Bind refuses every case listed in the epic's B1 with a message that says what to change.
- Normalized values on the Spell behind read-only properties; non-managed spells read None / None / None / ().
- Elastic defaults: limit 256 (the idle cap), baseline min(20, limit); limited_quantity and queue require a limit >=
  1; queue requires a positive timeout.
- Fingerprint: `managed:<mode>:<limit>:<timeout>:<reset names>` appended only for managed bindings.
- SpellCrystal records the four values; restore and graft replay them through bind; RecordVersion 4.2.0.

## Requirements (Non-Functional)
- Every existing spell id byte-identical (tested for all six members and the resolvable variants).
- Validation runs once at bind; no meld path reads the options.

## Scope Boundaries
- In scope: options, validation, Spell fields, fingerprint, record and replay.
- Out of scope: pools (S3), dispensing (S5).

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: acceptance criteria met with red-then-green tests in both GIL modes and the touched unit,
  component and integration suites green; notched 0.2.8242 (delegated routine closure under the owner's go-ahead).

## Dependencies / Related Work
- EPIC-2026-10-14-managed_spell_quantity Build Specification B1, B5; S3 composes pools from these fields.

## Tasks (Implementation Checklist)
- [x] Read the bind chain whole (Spellbook.bind/bind_inactive, Bind._bind_logic, sha256_profile, Spell.__init__,
      SpellBinder, scan_bind) and the crystal record and replay sites (U2); find any Conduit bind facade (U1).
- [x] Component patch and mapping note.
- [x] Red tests: options, refusals, id byte-identity, record round trip.
- [x] Implement; green in both GIL modes; the bind, scan and crystallizer suites.
- [x] Notch, release note, epic spec update, close, board sync.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- Every B1 refusal raises the documented type and text.
- A managed spell's id changes with each option; every non-managed id is byte-identical.
- Record and restore (and graft) round-trip the options; RecordVersion reads 4.2.0.

## Validation / Test Plan
- Unit tests beside the existing bind, scan and SpellBinder tests; crystallizer record/restore tests; both GIL modes.

## UX / API / Data Notes
- Public keywords as listed; `ManagedSpellMode` at the package root lands with S4's export set.

## Risks / Mitigations
- A keyword collides with `**kwargs` metadata -> scan_bind refuses the names as metadata keys; bind's native-key list
  gains them.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.
- [x] No `src/` edit before the component patch and the mapping note exist.

## Open Questions
- None. U1 and U2 were answered from source (Notes, FACT of 2026-10-15T10:28:32Z; epic B5).

## Decision Log
- 2026-10-15 (melder_0): four keywords; elastic baseline fixed at min(20, limit) (epic Decision Log).
- 2026-10-15 (melder_0): `ManagedSpellMode` is imported at runtime beside `Existence` in every bind module, so the
  bind verbs' VALUE-format signatures and type hints keep resolving (Notes, DECISION of 2026-10-15T11:04:20Z).
  WITHDRAWN the same day by owner ruling: TYPE_CHECKING import; the parity test reads with FORWARDREF (Notes,
  DECISION of 2026-10-15T12:45:20Z).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/architecture_patch.md
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_bind_options.md
  - artifacts/managed_spell_quantity_20261015/ (this story's runs and scripts)
- DISPOSITION: promote_to_documentation (patch docs); retain_as_reference (artifacts)
- CLEANUP_TRIGGER: patch docs promoted and archived at S7; artifacts retained

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - managed bind options, validation, fingerprint and record
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose, design, implementation and tests of this story;
  created 2026-10-15T09:29:51Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-15T09:29:51Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Opened ready behind S1. Seams on 0.2.8240: Spellbook.bind 5392-5694, bind_inactive 5093-5321,
    Bind._bind_logic 571-820, Bind.sha256_profile 911-1022, Spell.__init__ 302-551, SpellBinder (spellbinder.py:14),
    scan_bind (scan.py:405), RecordVersion CURRENT (record_version.py:84).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:5093-5694
  - src/melder/aether/spellbook/bind/bind.py:571-1022
  - src/melder/aether/spellbook/spell.py:302-551
  - src/melder/crystallizer/persistence/record_version.py:84-84
  IMPACT: Names the read set for U1/U2 and the patch.
  NEXT: Start after S1 closes: read the bind chain whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T10:28:32Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The bind chain and the record sites, read whole on 0.2.8241. (1) `Spellbook.bind` / `bind_inactive` convert
    existence and permissions, then call `Bind.bind`, which forwards to `_bind_logic`: guard, Protocol rule, spellframe
    kind, profile, disposal names (class profiles only), `sha256_profile` (parts joined by "::"; the existence name and
    the disposal names come last), the existing-object and callable rules (`_validate_binding`, ValueError), then
    `Spell(...)` with leftover kwargs as metadata. (2) U1: `Conduit.bind` (3884-3984) and `Conduit.bind_inactive`
    (3986-4078) are facades that forward their own keywords plus **kwargs to the Spellbook. (3) SpellBinder stages
    existence and passthrough kwargs and `finalize` sends `**self._kwargs` to `Spellbook.bind`. (4) `scan_bind` stores a
    frozen `ScanBindMetadata`, `scan_module` replays its native options into `Spellbook.bind`, and
    `RESERVED_SPELL_METADATA_KEYS` lists the 24 native names. (5) U2: `SpellCrystal.__init__` captures the bind
    signature (296-337), `describe()` emits it, and the replays read the payload by key: RestoreEngine
    `_bind_one_active` (Spellbook.bind) and `_bind_one_staged` (conduit.bind_inactive), GraftRunner `_bind_selected`,
    `_park_members` and `_merge_members`; absent keys default. RecordVersion CURRENT is 4.1.0. (6) Spell's slots
    append new names last (hot fast-door offsets); `_resolvable` is read through a check_cleaned property and deleted
    at cleanup. The crystal test double `DummySpell` has no managed fields and an existence named "present".
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:5093-5321
  - src/melder/aether/spellbook/spellbook.py:5392-5694
  - src/melder/aether/spellbook/bind/bind.py:433-818
  - src/melder/aether/spellbook/bind/bind.py:911-1022
  - src/melder/aether/conduit/conduit.py:3884-4078
  - src/melder/aether/spellbook/spellbinder.py:290-870
  - src/melder/aether/spellbook/bind/scan.py:132-755
  - src/melder/crystallizer/crystals/spell_crystal.py:153-446
  - src/melder/crystallizer/crystals/spell_crystal.py:1240-1343
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2142-2264
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:374-572
  - src/melder/crystallizer/persistence/record_version.py:76-85
  - src/melder/aether/spellbook/spell.py:250-693
  - tests/mocks/crystallizer/spell_crystal_harness.py:18-42
  IMPACT: The four options thread Spellbook/Conduit -> Bind.bind -> _bind_logic -> fingerprint and Spell; SpellBinder
    and scan replay ride existing passthroughs; the crystal must read the options only for managed spells (keeps
    every other record and the test double unchanged); five replay calls gain the options from the payload.
  NEXT: Write component_patch_bind_options.md and the mapping note, then the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T10:30:08Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch-section -> implementation -> validation mapping (component_patch_bind_options.md, read after the
    architecture patch). Keywords -> the four keyword-only options on Spellbook.bind / bind_inactive, Conduit.bind /
    bind_inactive, Bind.bind / _bind_logic / spell_id_inspector and scan_bind -> forwarding unit tests and a real
    Spellbook bind. Normalization -> new static `Bind._normalize_managed_options` (after the profile, before the
    fingerprint; also in spell_id_inspector) -> the refusal and default table. Fingerprint -> `sha256_profile`
    keywords, part appended only with a mode -> literal ids pinned on 0.2.8241 for the six members x resolvable
    (runs/s2_golden_ids_pre.txt) plus one changed id per option. Spell -> four slots appended last, read-only
    properties, deleted at cleanup -> Spell unit tests. scan -> ScanBindMetadata slots, repr, replay, reserved keys
    24 -> 28 -> scan unit tests. SpellCrystal -> capture for managed only, describe keys, `managed_spell_options`,
    static `managed_bind_options` -> crystal unit tests (the DummySpell double stays valid). Replay -> five bind calls
    pass the payload's options -> loader unit tests with doubles and a record/restore integration test.
    RecordVersion -> 4.2.0 -> unit. ManagedSpellMode -> new module -> unit. Red first, both GIL modes.
  EVIDENCE:
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/architecture_patch.md:1-106
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_bind_options.md:1-76
  IMPACT: The patch gate for S2 is met: the patch exists, is linked from the story and the epic, and every section
    maps to a code step and a test.
  NEXT: Write the red tests (unit file for the options, Spell, scan, crystal, loaders; integration round trip).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T10:40:39Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Red on 0.2.8241 (GIL off). The seven new test files failed to collect without `ManagedSpellMode`. With only
    the new enum module in place, the Bind file ran 53 failed / 19 passed: every normalization, refusal, managed
    fingerprint, forwarding and inspector test fails; the 15 literal-id tests pass, which proves the pinned ids are
    the pre-change ids (they must stay green after the change). Four other passes are vacuous before the change
    (a tuple of reset names and three equal-id or passthrough checks) and become real checks after it.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_red_gil0.txt:1-80
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_red_bind_after_mode_gil0.txt:1-400
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_golden_ids_pre.txt:1-17
  IMPACT: The byte-identity guard is anchored on real pre-change values; implementation can start.
  NEXT: Implement Bind (normalizer, fingerprint part, forwarding), then Spell, the bind surfaces, scan, crystal,
    replays and RecordVersion; green in both GIL modes.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T10:56:53Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S2 implemented on the 0.2.8241 tree, as the component patch states. New `ManagedSpellMode`. Bind: the four
    keyword-only options on `bind`, `_bind_logic` and `spell_id_inspector`; `_normalize_managed_options` (and its mode,
    limit, timeout and reset helpers) runs after the disposal names and before the fingerprint; `sha256_profile`
    appends `managed:<mode>:<limit>:<timeout>:<names>` only with a mode. Spell: four slots appended last, read-only
    properties, deleted at cleanup. Spellbook / Conduit bind and bind_inactive forward the options;
    `SpellBinder.as_managed_spell_quantity`; scan_bind stores and replays them (reserved keys 24 -> 28). SpellCrystal
    captures them only for `managed_spell_quantity` (`managed_spell_options`, static `managed_bind_options`, the four
    describe keys); the five restore/graft replays pass `**SpellCrystal.managed_bind_options(crystal)`; RecordVersion
    4.2.0. Every added line is within 120 characters; nothing was run against it yet.
  EVIDENCE:
  - src/melder/aether/spellbook/existence/managed_spell_mode.py:4-89
  - src/melder/aether/spellbook/bind/bind.py:466-1150
  - src/melder/aether/spellbook/bind/bind.py:1216-1518
  - src/melder/aether/spellbook/spell.py:310-857
  - src/melder/aether/spellbook/spellbook.py:5095-5743
  - src/melder/aether/conduit/conduit.py:3885-4124
  - src/melder/aether/spellbook/spellbinder.py:550-602
  - src/melder/aether/spellbook/bind/scan.py:103-636
  - src/melder/aether/spellbook/bind/scan.py:771-852
  - src/melder/crystallizer/crystals/spell_crystal.py:160-472
  - src/melder/crystallizer/crystals/spell_crystal.py:865-927
  - src/melder/crystallizer/crystals/spell_crystal.py:1330-1441
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2142-2269
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:375-579
  - src/melder/crystallizer/persistence/record_version.py:76-87
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s2_apply_crystal.py:1-269
  IMPACT: Every patch section has its code; validation decides whether S2 lands.
  NEXT: Run the seven new test files under `-X gil=0` and `-X gil=1`, then the touched modules' existing suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T11:04:20Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Validation found one regression of my own and one test error. (1) The seven new files: 115 passed, 1 failed
    under `-X gil=0` (its log was overwritten by the green rerun) - the graft test expected `members_bound == 2`,
    but `GraftRunner.run` reports the selected member as bound and the rest as parked; the test now asserts bound
    1, parked 1 (the code is right). (2) The spellbook
    unit tree: 2473 passed, 1 failed - `test_reserved_metadata_keys_are_exactly_the_native_bind_parameters` reads
    `inspect.signature(scan_bind)` in the default VALUE format, and `ManagedSpellMode`, imported only under
    TYPE_CHECKING, raises NameError there. The same probe shows Spellbook.bind / bind_inactive, Conduit.bind /
    bind_inactive, Spell.__init__, ScanBindMetadata.__init__ and SpellBinder.as_managed_spell_quantity now raise
    NameError in VALUE format, with ManagedSpellMode their only unresolved name - all resolved at 0.2.8241. Decision:
    import ManagedSpellMode at runtime beside Existence in those five modules (bind.py already does): it is a
    dependency-free enum sibling of Existence, which each module imports at runtime for the same parameter, so no
    cycle or import cost is added and agents can keep introspecting the bind verbs. The parity test stays unchanged.
  EVIDENCE:
  - tests/integration/melder/crystallizer/test_managed_spell_options_record_integration.py:170-175
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_unit_spellbook_gil0.txt:37-100
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:230-330
  - tests/unit/melder/spellbook/test_scan_bind_option_parity.py:294-312
  - src/melder/aether/spellbook/bind/scan.py:1-13
  - src/melder/aether/spellbook/existence/managed_spell_mode.py:1-4
  IMPACT: The bind verbs keep their 0.2.8241 introspection behaviour; a hidden public-surface regression is closed.
  NEXT: Move the five TYPE_CHECKING imports to runtime imports, then rerun the new files and the spellbook unit tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T12:29:41Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Green in both GIL modes on the S2 tree (runtime ManagedSpellMode import in place). New: the S2 unit files
    plus the new 14-test VALUE-signature guard run inside the spellbook unit tree (2488 passed), the crystal file
    inside the crystallizer unit tree (607), the two integration files (9). Existing, both modes: unit aether 4228
    (after `test_bind_forwards_to_spellbook_for_normal_conduit` learned the four forwarded None options), top-level
    unit 145, mutation_research + utilities 1098 (2 skipped, 7 xfailed), component spellbook 819, component rest
    1545 (23 skipped, 1 xfailed), integration spellbook + conduit + mutation_research + live_sim 988 (GIL on; 619 +
    369 GIL off), integration aether 785 (5 xfailed), multithreading 54, and the whole crystallizer integration tree
    in shards (restore 46 with 3 xfailed, ordered disposal 23, named lessers 28, per-frame and spellframe kind 8,
    the rest 171). Unit build_assets + llm_support + architecture 162 (GIL off). The bind-guard scan counts 624
    classes (623 + ManagedSpellMode). Density: about 130 new tests over roughly 350 new code lines.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_unit_spellbook_gil0.txt:1-36
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_unit_spellbook_gil1.txt:1-44
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_unit_crystallizer_gil0.txt:1-10
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_unit_crystallizer_gil1.txt:1-18
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_green_integration_gil0.txt:1-2
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_green_integration_gil1.txt:1-10
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_unit_aether_gil0.txt:1-60
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_unit_aether_gil1.txt:1-68
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_unit_toplevel_gil0.txt:1-4
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_unit_toplevel_gil1.txt:1-12
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_unit_mr_utilities_gil0.txt:1-18
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_unit_mr_utilities_gil1.txt:1-26
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_unit_assets_docs_gil0.txt:1-4
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_component_spellbook_gil0.txt:1-13
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_component_spellbook_gil1.txt:1-21
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_component_rest_gil0.txt:1-23
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_component_rest_gil1.txt:1-31
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_integration_spellbook_gil0.txt:1-10
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_integration_conduit_mr_live_gil0.txt:1-7
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_integration_spellbook_conduit_mr_live_gil1.txt:1-23
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_integration_aether_gil0.txt:1-12
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_integration_aether_gil1.txt:1-20
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_integration_multithreading_gil0.txt:1-2
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_integration_multithreading_gil1.txt:1-10
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_integration_restore_p0_gil0.txt:1-2
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_integration_restore_p0_gil1.txt:1-10
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_integration_crystallizer_rest_gil1.txt:1-12
  IMPACT: Every EXIT_GATE test condition is met; S2 can land.
  NEXT: Notch to 0.2.8242, extend the release note's managed section, update the epic, close, rebuild last.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T12:45:20Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Correction inside 0.2.8242 by owner ruling ("use TYPECHECKING"; the test was wrong, not prod): the DECISION of
    2026-10-15T11:04:20Z is withdrawn. `ManagedSpellMode` is back under TYPE_CHECKING in spellbook.py, conduit.py,
    spell.py, scan.py and spellbinder.py; the extra signature test file is deleted; the scan_bind parity test reads the
    signature with FORWARDREF, as the typing policy says (src_architecture, Failure Modes); the release-note sentence
    about signatures is gone. Green after the correction: spellbook unit tree 2474 (both modes), unit aether plus the
    annotation integrity guard 4238 (both modes). Assets and bundles rebuilt again for 0.2.8242.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s2_revert_runtime_mode_import.py:1-30
  - tests/unit/melder/spellbook/test_scan_bind_option_parity.py:294-315
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_fix_unit_spellbook_gil0.txt:1-36
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_fix_unit_spellbook_gil1.txt:1-44
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_fix_unit_aether_annotation_gil0.txt:1-60
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_fix_unit_aether_annotation_gil1.txt:1-68
  IMPACT: S2 matches the typing policy; prod was never broken.
  NEXT: S3.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user (in the lane's report to the owner)
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: S2 - options, validation, fields, fingerprint, record (component_patch_bind_options.md). Done: landed
  0.2.8242.
- Evidence: Notes (FACT, PLAN mapping, MEASURE red, FACT implementation, DECISION, MEASURE green); runs and apply
  scripts in artifacts/managed_spell_quantity_20261015/.
- Not run: hosted CI (the owner's).
- Next: S3 (tickets/stories/2026-10-15_managed_quantity_pool_story.md).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
