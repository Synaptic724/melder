# Task: Scaffold Caching System Utility

## Metadata
- Task ID: TASK-2026-06-07-scaffold-caching-system-utility
- Story: none
- Epic: EPIC-2026-06-06-define-compiler-phase-artifact-directory-cache
- Status: in_progress
- Owner: codex
- Agent Name: compiler_1
- Priority: p0
- Created: 2026-06-07T09:09:55Z
- Updated: 2026-06-07T09:29:13Z

## Objective
Build the first real `CachingSystem` utility under
`src/melder/utilities/caching_system/`, have Spellbook lazily own one instance
when Aether root caching is enabled, and provide the initial add/remove/transfer
and flush-to-disk mechanics around one conduit cache file.

## Ticket Contract
- ENTRY_GATE: the cache epic is active, the Aether root config bit/path exist,
  and the user explicitly approved building the utility object under
  `src/melder/utilities/caching_system/`.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/caching_system/`
  - `src/melder/aether/spellbook/spellbook.py`
  - `tests/unit/melder/utilities/`
  - `tests/component/melder/spellbook/`
  - `codex/context_compass/tickets/tasks/2026-06-07_scaffold_caching_system_utility_task.md`
  - `codex/context_compass/tickets/epics/2026-06-06_define_compiler_phase_artifact_directory_cache_epic.md`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-06-06_define_compiler_phase_artifact_directory_cache_epic.md`
  - `tickets/tasks/2026-06-06_add_aether_configuration_system_caching_flag_task.md`
  - `tickets/tasks/2026-06-06_experiment_phase11_cache_rehydration_dynamic_task.md`
- EXIT_GATE:
  - `CachingSystem` exists as a utility object
  - Spellbook can lazily create it only when Aether root caching is enabled
  - the utility supports add/remove/transfer and file flush placeholders
  - focused tests prove the utility and Spellbook lazy-init seam
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the utility cannot stay
  bounded and immediately requires wiring deep compiler/runtime cache payload
  emission.

## Scope Boundaries
- In scope:
  - `CachingSystem` utility scaffold
  - one in-memory dict mirror plus one file flush path
  - Spellbook lazy-init seam
  - add/remove/transfer core methods
  - focused tests
- Out of scope:
  - full bind/transfer ownership-cache emission wiring
  - compiler payload serialization details
  - broad conduit/runtime cache consumers

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested the utility object and the
  Spellbook lazy-init seam as the next cache-lane implementation slice.

## Deliverables
- `CachingSystem` utility object
- Spellbook lazy-init hook
- focused unit/component coverage

## Validation
- Ran:
  - `.venv_new\\Scripts\\python.exe -m pytest -q tests/unit/melder/utilities/test_caching_system.py tests/component/melder/spellbook/test_spellbook_component_caching_system.py`
- Result:
  - `39 unit passed, 1 warning`
  - `10 component passed, 1 warning`
  - `49 total passed, 1 warning`
- Recommended commands:
  - `.venv_new\\Scripts\\python.exe -m pytest -q tests/unit/melder/utilities/test_caching_system.py tests/component/melder/spellbook/test_spellbook_component_caching_system.py`

## Notes
- DATETIME: 2026-06-07T09:09:55Z
  TYPE: PLAN
  CLAIM: The first utility slice should stay narrow. One Spellbook-owned
    `CachingSystem` should represent one root conduit cache file, load the file
    once, keep the dict in memory, flush on mutation, and expose only the
    minimal operations we already agreed on: add, remove, transfer, and file
    persistence. Spellbook should lazily create it only when the Aether root
    configuration is activated and `system_caching_enabled` is true.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/aether_configuration.py:142-182
  - src/melder/aether/aether.py:503-613
  - src/melder/aether/spellbook/spellbook.py:3052-3646
  IMPACT: This gives the cache lane a real owned utility object without forcing
    premature compiler payload wiring.
  NEXT: implement the utility class, wire Spellbook lazy init, and add focused
    tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-07T09:18:50Z
  TYPE: FACT
  CLAIM: The utility slice is now implemented. `CachingSystem` exists under
    `src/melder/utilities/caching_system/` and owns one conduit cache file,
    an in-memory dict mirror, bundle-level SHA stamping, immediate flush on
    add/remove, and best-effort transfer to another cache utility. Spellbook
    now lazily creates one owned cache utility only when the Aether root config
    is activated and `system_caching_enabled` is true.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:16-430
  - src/melder/aether/spellbook/spellbook.py:672-730
  IMPACT: The cache lane now has a real owned utility seam instead of only
    config bits and experiments.
  NEXT: record the focused test result and choose whether the next slice should
    wire bind/transfer/conjure call sites into this utility.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-07T09:18:50Z
  TYPE: MEASURE
  CLAIM: The focused utility/component validation ring is green. Running
    `.venv_new\\Scripts\\python.exe -m pytest -q tests/unit/melder/utilities/test_caching_system.py tests/component/melder/spellbook/test_spellbook_component_caching_system.py`
    passed `4` tests with one existing pytest cache warning. The tests prove:
    - add/remove/reload round-trip
    - source->target transfer
    - Spellbook lazy creation when root caching is enabled
    - Spellbook no-op when root caching is disabled
  EVIDENCE:
  - tests/unit/melder/utilities/test_caching_system.py:1-125
  - tests/component/melder/spellbook/test_spellbook_component_caching_system.py:1-158
  IMPACT: The first `CachingSystem` scaffold is stable enough to start wiring
    real cache emission call sites.
  NEXT: choose the first live mutation path that should call into the utility:
    bind-after-conjure, transfer of ownership, or conjure-time bundle emit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-07T09:21:40Z
  TYPE: PLAN
  CLAIM: The next bounded slice is test expansion, not new runtime behavior.
    The cache utility now has enough stable seams to justify a larger unit and
    component matrix. The unit layer should cover constructor validation,
    default/load semantics, rollback-on-flush-failure behavior, transfer edge
    cases, and cleaned-state guards. The component layer should cover the
    Spellbook lazy-init gate under multiple Aether root-config and conduit
    lifecycle postures.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:16-430
  - src/melder/aether/spellbook/spellbook.py:672-730
  - tests/unit/melder/utilities/test_caching_system.py:1-125
  - tests/component/melder/spellbook/test_spellbook_component_caching_system.py:1-158
  IMPACT: A broader test ring will let us wire live bind/transfer/conjure
    callers into the utility later without relying on only the two original
    happy-path tests.
  NEXT: expand to at least 30 unit tests and 10 component tests for the cache
    seam, then rerun the focused ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-07T09:23:35Z
  TYPE: FACT
  CLAIM: The expanded cache test matrix is nearly green. The current run
    reached `48 passed` before one rollback-oriented unit case failed. The
    failure is not a cache-behavior defect; it is a test seam issue caused by
    trying to monkeypatch a slotted instance method (`upsert_spell_payload`) on
    `CachingSystem`. Because the utility is slotted, instance attribute
    replacement is read-only there. The right fix is to patch the class method
    conditionally or patch a lower write seam instead of assigning onto the
    instance.
  EVIDENCE:
  - tests/unit/melder/utilities/test_caching_system.py:553-586
  - src/melder/utilities/caching_system/caching_system.py:44-54
  IMPACT: The utility code itself is not blocked; only one rollback test seam
    needs to be corrected before the expanded matrix can go green.
  NEXT: change the rollback test to patch the class-level method conditionally
    and rerun the focused cache test ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-07T09:29:13Z
  TYPE: MEASURE
  CLAIM: The requested cache test expansion is now complete and green:
    - `tests/unit/melder/utilities/test_caching_system.py` runs `39` unit tests
    - `tests/component/melder/spellbook/test_spellbook_component_caching_system.py`
      runs `10` component tests
    - combined focused ring: `49 passed, 1 warning`
    The unit matrix now covers constructor validation, default/load behavior,
    read-only views, missing spell behavior, replace/remove flows, invalid
    spell-id inputs, bundle serialization, invalid bundle recovery,
    rollback-on-write-failure behavior, transfer edge cases, and cleaned-state
    guards. The component matrix now covers the Spellbook cache gate, lazy
    creation, custom conduit/frame paths, same-instance reuse, field storage,
    cleanup, and relative cache-root fragment behavior.
  EVIDENCE:
  - tests/unit/melder/utilities/test_caching_system.py:1-622
  - tests/component/melder/spellbook/test_spellbook_component_caching_system.py:1-324
  IMPACT: The cache utility seam now has the requested broader safety net
    before live bind/transfer/conjure emission wiring begins.
  NEXT: choose the first live cache-emission path to wire into
    `CachingSystem`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-07T10:34:37Z
  TYPE: PLAN
  CLAIM: The next cache-lane investigation is no longer about utility wiring.
    It is about proving the exact runtime boundary of cached `CreationContext`:
    which pre-execution checks happen before the context is used, which spell
    fields the context/executors read directly, and therefore which earlier
    compiler/control-plane outputs a pure cached `CreationContext` does or does
    not replace.
  EVIDENCE:
  - user_instruction
  IMPACT: This will let us answer the cache-boundary question from current code
    instead of from guesses about phases.
  NEXT: read meld call sites, spell-owned context factory/build paths, and the
    generated creation-context executor code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-07T11:17:01Z
  TYPE: PLAN
  CLAIM: The next implementation slice is the conjure branch itself. The user
    wants three cache paths inside `SpellbookCreationSystem`:
    1. full cache hit: spell set matches cache, so conjure can use cached
       runtime payloads in full after the conduit/runtime environment exists
    2. mixed run: likely dynamic-mode only, where cached spells stop after the
       structural/foundational baseline and uncached spells finish live plan
       resolution and then emit cache
    3. full miss: current live conjure path, followed by cache emit
    The next investigation step is to map those three paths onto the current
    `conjure -> prepare_spellbook -> prepare_resolution -> build_conduit ->
    activate_conjured_conduit` flow and the available compiler entrypoints.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spellbook_creation_system.py:152-215
  - src/melder/utilities/caching_system/caching_system.py:16-453
  IMPACT: This narrows the next code change to one orchestration seam instead
    of scattering cache decisions across Spellbook, Conduit, and compiler code.
  NEXT: identify the exact point where cached spells can skip live `8-11`
    while misses still run and emit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-07T12:00:31Z
  TYPE: FACT
  CLAIM: The spell-owned cache gate bit is now landed. `Spell` now owns
    `_caching_enabled`, that field defaults to `False`, and conduit ownership
    stamping now sets it from the current root cache posture during:
    - normal conjure ownership stamping
    - bind-after-conjure ownership stamping
    - transfer-of-ownership restamping
    The ownership-stamp seam treats missing root Aether cache config as
    `False`, while the stricter Spellbook cache getter still assumes cache is
    actually enabled before a caller requests the utility.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:195-242
  - src/melder/aether/spellbook/spell.py:995-1019
  - src/melder/aether/spellbook/spellbook_creation_system.py:571-593
  - src/melder/aether/spellbook/spellbook.py:2865-2883
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1408-1420
  IMPACT: Later JIT/conjure emit paths can branch on spell-owned runtime state
    instead of re-reading root config from `CreationContext`.
  NEXT: wire the first real emit path to use `spell._caching_enabled`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-07T12:00:31Z
  TYPE: MEASURE
  CLAIM: The spell-owned cache-gate slice is green across the directly affected
    runtime/test surfaces. Running
    `.venv_new\\Scripts\\python.exe -m pytest -q`
    against:
    - `tests/component/melder/spellbook/test_spellbook_component_spell.py`
    - `tests/component/melder/spellbook/test_spellbook_component_caching_system.py`
    - `tests/unit/melder/spellbook/test_spell.py`
    - `tests/unit/melder/spellbook/test_spellbook.py`
    - `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py`
    - `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py`
    passed `396` tests with one existing pytest cache warning.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_caching_system.py:1-324
  - tests/component/melder/spellbook/test_spellbook_component_spell.py:268-290
  - tests/unit/melder/spellbook/test_spell.py:13-27
  - tests/unit/melder/spellbook/test_spell.py:751-761
  - tests/unit/melder/spellbook/test_spell.py:1214-1224
  - tests/unit/melder/spellbook/test_spellbook.py:263-294
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:489-520
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py:457-484
  IMPACT: The cache bit did not destabilize Spell, Spellbook conjure wiring, or
    ownership transfer behavior.
  NEXT: implement the first emit path instead of widening the cache object
    further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-07T12:57:43Z
  TYPE: FACT
  CLAIM: The first real emit slice is now implemented. `Spell.emit_cache()`
    is a public delegate that returns early when `_caching_enabled` is false
    and otherwise routes through `Spellbook._emit_spell_cache(...)`. Spellbook
    now builds the payload from current spell/compiler state using the new
    production helper
    `utilities/caching_system/spell_cache_payload_builder.py`, then upserts it
    into `CachingSystem`. The first emitted payload shape is the proven
    no-overrides creation-context-facing package:
    route metadata, no-overrides step rows, transient schema, emitted source,
    and marshaled code object bytes.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:641-695
  - src/melder/aether/spellbook/spellbook.py:721-752
  - src/melder/utilities/caching_system/spell_cache_payload_builder.py:1-136
  IMPACT: We now have one real spell-facing cache emission entrypoint instead
    of only a utility object and a cache-policy bit.
  NEXT: choose whether the first live caller of `emit_cache()` should be the
    JIT meld success path or the conjure batch path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-07T12:57:43Z
  TYPE: MEASURE
  CLAIM: The focused emit-entrypoint ring is green. Running
    `.venv_new\\Scripts\\python.exe -m pytest -q tests/unit/melder/spellbook/test_spell.py tests/component/melder/spellbook/test_spellbook_component_caching_system.py`
    passed `108` tests with one existing pytest cache warning.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spell.py:765-810
  - tests/component/melder/spellbook/test_spellbook_component_caching_system.py:302-324
  IMPACT: The public `Spell.emit_cache()` delegate and Spellbook payload
    emission seam are stable enough to wire into one live runtime path next.
  NEXT: wire one real caller into `emit_cache()`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the first real utility object for the cache lane: one
Spellbook-owned `CachingSystem` that represents one conduit cache file and
handles the local add/remove/transfer/flush mechanics.
