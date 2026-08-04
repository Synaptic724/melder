# Task: Implement Spell Examiner Registry Rebuild
- Completed: 2026-04-05T19:35:48Z
- Summary: Rebuilt the SpellExaminer/profile lane onto the requested two-step
  `general` / `detailed` model, propagated default profile choice through the
  public bind/scan paths, removed the redundant `Spell.resolution_profile`
  mirror, and validated the focused runtime/test surfaces.

## Metadata
- Task ID: TASK-2026-04-05-implement-spell-examiner-registry-rebuild
- Story: STORY-2026-04-05-spell-examiner-registry-rebuild
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T13:45:00Z
- Updated: 2026-04-05T19:35:48Z

## Objective
Rebuild SpellExaminer to the currently requested model:
- registry-driven profile builders
- single `create_profile(...)` entrypoint
- `general` and `detailed` profile names instead of `binding` / `resolution` / `ai`
- `general` bundling binding + resolution
- `detailed` replacing the AI-facing naming
- no helper creation methods on `SpellExaminer`
- no explicit registry lock on `SpellExaminer`
- `Bind` owning one long-lived `SpellExaminer`

## Ticket Contract
- ENTRY_GATE: the current reverted checkout and the requested rebuild direction
  are both documented in notes.
- EXECUTION_BOUNDARY: SpellExaminer contract, Bind wiring, direct runtime/test
  consumers, patch docs, and focused validation only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-05_investigate_spell_examiner_registry_rebuild_task.md
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_examiner.py
  - src/melder/spellbook/bind/bind.py
- EXIT_GATE: SpellExaminer exposes only the requested `create_profile(...)`
  contract, bind owns one long-lived examiner on the new path, the stale
  middle-version API is gone, and focused validation passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the rebuild forces wider
  profile-storage changes than the safe slice is supposed to own.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the user approved moving on from the SpellExaminer lane,
  and the rebuilt two-step profile contract plus the focused validation slices
  are complete enough to leave active routing.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/spell_examiner_registry_rebuild/architecture_patch.md
  - system_docs/patches/active/spell_examiner_registry_rebuild/component_patch_spell_examiner.md
  - system_docs/patches/active/spell_examiner_registry_rebuild/component_patch_bind.md
  - system_docs/patches/active/spell_examiner_registry_rebuild/component_patch_spellbook_bind_scan.md
  - system_docs/patches/active/spell_examiner_registry_rebuild/component_patch_spell_profile_consumers.md
  - system_docs/patches/active/spell_examiner_registry_rebuild/code_description_patch_spell_examiner.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Validation
- Completed:
  - `python -m py_compile src/melder/spellbook/spell_crafter/spell_examiner/spell_examiner.py src/melder/spellbook/spell_crafter/spell_examiner/profiles/general_profile.py src/melder/spellbook/spell_crafter/spell_examiner/profiles/detailed_profile.py src/melder/spellbook/bind/bind.py src/melder/spellbook/spell.py src/melder/spellbook/spellbook_creation_system.py src/melder/spellbook/spell_crafter/validation/strategies/callable_profile_hygiene_strategy.py src/melder/spellbook/spell_crafter/validation/strategies/existing_creation_compatibility_strategy.py src/melder/aether/nexus/frame_descriptor_manager.py src/melder/aether/nexus/frame_descriptor/spell_record.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/test_spell_examiner.py tests/unit/melder/spellbook/bind/test_bind.py tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner.py tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner_inspection.py tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner_profiles.py tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner_profile_models.py tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner_strategies.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/profiles/test_ai_profile.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py tests/unit/melder/aether/test_aetheric_frame_descriptor.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/spell_examiner/test_spell_examiner.py tests/unit/melder/spellbook/bind/test_bind.py tests/component/melder/spellbook/spell_crafter/spell_examiner tests/unit/melder/spellbook/spell_crafter/spell_examiner/profiles/test_ai_profile.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py tests/unit/melder/aether/test_aetheric_frame_descriptor.py`
  - `python -m py_compile tests/unit/melder/spellbook/test_scan_bind.py tests/unit/melder/spellbook/test_spellbinder.py src/melder/spellbook/bind/scan.py src/melder/spellbook/spellbinder.py src/melder/spellbook/spellbook.py src/melder/aether/conduit/conduit.py src/melder/spellbook/bind/bind.py src/melder/utilities/interfaces/interfaces.py`
  - `python -m pytest -q tests/unit/melder/spellbook/bind/test_bind.py tests/unit/melder/spellbook/test_scan_bind.py tests/unit/melder/spellbook/test_spellbinder.py`
  - `python -m py_compile src/melder/utilities/interfaces/interfaces.py src/melder/spellbook/spell.py src/melder/spellbook/spell_crafter/spell_crafter.py src/melder/aether/nexus/frame_descriptor_manager.py src/melder/spellbook/spellbook_creation_system.py src/melder/spellbook/spell_crafter/validation/strategies/callable_profile_hygiene_strategy.py src/melder/spellbook/spell_crafter/validation/strategies/existing_creation_compatibility_strategy.py`
  - `python -m pytest -q tests/unit/melder/spellbook/test_spell.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py tests/unit/melder/spellbook/bind/test_bind.py tests/component/melder/spellbook/test_spellbook_component_bind.py tests/unit/melder/aether/conduit/test_conduit_facade.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/test_spell_examiner.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py`

## Notes
- DATETIME: 2026-04-05T19:13:53Z
  TYPE: MEASURE
  CLAIM: The `spell.resolution_profile` mirror field is now gone, and the
    remaining runtime readers normalize through `.profile` instead. `Spell`
    no longer stores or cleans a separate resolution-profile field, `Bind` no
    longer mirrors one onto the spell, Nexus publish reads resolution data
    directly from `general` / `detailed`, and `Spell._ensure_crafter()` now
    seeds `SpellCrafter` from the profile-held resolution payload. The
    normalization boundary now uses profile interfaces in
    `interfaces.py` instead of concrete profile imports in those runtime
    consumers. The focused runtime/test surface passed with `506 passed`.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:43-75
  - src/melder/spellbook/spell.py:1-22
  - src/melder/spellbook/spell.py:670-683
  - src/melder/spellbook/bind/bind.py:276-291
  - src/melder/spellbook/spell_crafter/spell_crafter.py:216-239
  - src/melder/spellbook/spell_crafter/spell_crafter.py:3234-3241
  - src/melder/aether/nexus/frame_descriptor_manager.py:403-432
  - src/melder/spellbook/spellbook_creation_system.py:451-457
  - src/melder/spellbook/spell_crafter/validation/strategies/callable_profile_hygiene_strategy.py:48-63
  - src/melder/spellbook/spell_crafter/validation/strategies/existing_creation_compatibility_strategy.py:71-82
  - command:python -m pytest -q tests/unit/melder/spellbook/test_spell.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py tests/unit/melder/spellbook/bind/test_bind.py tests/component/melder/spellbook/test_spellbook_component_bind.py tests/unit/melder/aether/conduit/test_conduit_facade.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/test_spell_examiner.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py
  IMPACT: The spell/profile contract is cleaner now: resolution data lives under
    the spell-owned profile where it belongs, and the downstream consumers no
    longer depend on a redundant mirror field on `Spell`.
  NEXT: review whether you want to keep pushing cleanup around file names/docs or
    move back to the next ACL/view lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T19:35:48Z
  TYPE: DECISION
  CLAIM: The SpellExaminer lane is complete enough to close. The user explicitly
    approved moving on and shifting focus back to ACL work after the two-step
    profile lifecycle, public bind/scan propagation, interface-based
    normalization, and resolution-profile field removal all landed and the
    focused validation surfaces were green.
  EVIDENCE:
  - user_instruction: "yeah continue"
  - user_instruction: "go ahead and close the tickets for the mods in spell and the spell examiner and I think its time to move on"
  - command:python -m pytest -q tests/unit/melder/spellbook/spell_crafter/spell_examiner/test_spell_examiner.py tests/unit/melder/spellbook/bind/test_bind.py tests/component/melder/spellbook/spell_crafter/spell_examiner tests/unit/melder/spellbook/spell_crafter/spell_examiner/profiles/test_ai_profile.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py tests/unit/melder/aether/test_aetheric_frame_descriptor.py
  - command:python -m pytest -q tests/unit/melder/spellbook/bind/test_bind.py tests/unit/melder/spellbook/test_scan_bind.py tests/unit/melder/spellbook/test_spellbinder.py
  - command:python -m pytest -q tests/unit/melder/spellbook/test_spell.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py tests/unit/melder/spellbook/bind/test_bind.py tests/component/melder/spellbook/test_spellbook_component_bind.py tests/unit/melder/aether/conduit/test_conduit_facade.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/test_spell_examiner.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py
  IMPACT: This task can leave active routing and its retained patch docs can now
    serve as reference material while ACL work resumes.
  NEXT: move this task to `tickets/tasks/completed/` and route attention back
    to the ACL design lane.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T19:13:53Z
  TYPE: FACT
  CLAIM: The only remaining red integration expectation from this lane is old
    SpellCrafter Phase 2 behavior. There is exactly one integration test still
    asserting that `run_phase_symbolic_graph()` must raise before an explicit
    Phase 1 call. That is now stale because newly bound spells already seed
    Phase 1 requirements through the profile-held resolution payload when the
    crafter is created. So the runtime behavior is coherent with the new model;
    the integration test needs to be updated to the seeded-profile contract.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_spellbook_integration_spell_crafter.py:424-457
  - src/melder/spellbook/spell.py:675-683
  - src/melder/spellbook/spell_crafter/spell_crafter.py:230-233
  - src/melder/spellbook/spell_crafter/spell_crafter.py:3248-3249
  IMPACT: We should not reintroduce the old Phase 2 guard just to satisfy one
    stale integration test. The test should instead lock the new seeded-profile
    behavior.
  NEXT: patch the integration test to assert Phase 2 can run directly on a
    newly bound spell because Phase 1 requirements are already seeded.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T19:01:52Z
  TYPE: MEASURE
  CLAIM: The public bind/scan propagation boundary is now aligned with the new
    profile model. `Spellbook.bind(...)`, `Conduit.bind(...)`, and
    `Bind.bind(...)` all accept `profile` with default `general`.
    `scan_bind` metadata now stores `profile`, `Scan.scan_module(...)` forwards
    it, and `SpellBinder` now carries and forwards profile choice through
    `finalize()`. The focused bind/scan/binder unit surface passed with
    `264 passed`.
  EVIDENCE:
  - src/melder/spellbook/bind/bind.py:73-141
  - src/melder/spellbook/spellbook.py:2371-2485
  - src/melder/aether/conduit/conduit.py:2041-2135
  - src/melder/spellbook/bind/scan.py:41-245
  - src/melder/spellbook/spellbinder.py:47-175
  - src/melder/spellbook/spellbinder.py:223-275
  - src/melder/spellbook/spellbinder.py:625-637
  - src/melder/utilities/interfaces/interfaces.py:1301-1310
  - src/melder/utilities/interfaces/interfaces.py:2436-2446
  - src/melder/utilities/interfaces/interfaces.py:3941-3950
  - tests/unit/melder/spellbook/test_scan_bind.py:63-186
  - tests/unit/melder/spellbook/test_spellbinder.py:41-176
  - command:python -m pytest -q tests/unit/melder/spellbook/bind/test_bind.py tests/unit/melder/spellbook/test_scan_bind.py tests/unit/melder/spellbook/test_spellbinder.py
  IMPACT: The default profile choice is now a real public binding option instead
    of an internal-only behavior, and scan/fluent binding stay coherent with the
    downstream SpellExaminer model.
  NEXT: review whether you want another cleanup pass on naming/doc artifacts or
    move back to the next ACL/view lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T19:01:52Z
  TYPE: FACT
  CLAIM: The next red tests are contract-drift tests, not a new runtime design
    break. The component bind tests still assert that `spell.profile` is a raw
    `ClassBindingProfile` / `CallableBindingProfile` / `InstanceBindingProfile`,
    but the new contract is that bind stores `SpellGeneralProfile` on
    `.profile` and the binding artifact now lives under
    `spell.profile.binding_profile`. The conduit facade test is failing for the
    same reason on the public propagation boundary: it still expects the old
    forwarded kwargs and does not account for the new default
    `profile='general'` kwarg.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_bind.py:58-88
  - tests/component/melder/spellbook/test_spellbook_component_bind.py:140-206
  - tests/unit/melder/aether/conduit/test_conduit_facade.py:119-157
  IMPACT: We only need to align the stale assertions to the new public bind
    contract; there is no evidence here that the runtime model itself is wrong.
  NEXT: patch the bind and conduit facade tests to assert `SpellGeneralProfile`
    and the forwarded `profile='general'` kwarg, then rerun the focused test
    slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T19:01:52Z
  TYPE: FACT
  CLAIM: `spell.resolution_profile` is now just a mirror field, not a real
    owning contract. The live runtime writes it in `Bind` after the general
    profile completes, `Spell.cleanup()` clears it, and `FrameDescriptorManager`
    still reads it first before falling back to `.profile`. `SpellCrafter`
    itself does not read `spell.resolution_profile` at all; it owns its own
    phase artifacts and exposes them through `Spell`'s phase/introspection
    properties. So removing the field is a bounded contract cleanup: update
    bind, `Spell`, and Nexus publish to use `.profile`, and only pass profile
    data into `SpellCrafter` if we explicitly want the crafter to seed from the
    completed profile later.
  EVIDENCE:
  - src/melder/spellbook/spell.py:101-110
  - src/melder/spellbook/spell.py:165-166
  - src/melder/spellbook/spell.py:299-302
  - src/melder/spellbook/spell.py:543-545
  - src/melder/spellbook/spell.py:609-610
  - src/melder/spellbook/bind/bind.py:292-292
  - src/melder/aether/nexus/frame_descriptor_manager.py:403-431
  - src/melder/spellbook/spell_crafter/spell_crafter.py:231-240
  - src/melder/spellbook/spell.py:752-824
  IMPACT: We can remove the mirror field from `Spell` without reopening the
    broader phase system. The only required runtime updates are direct
    `.profile` normalization and cleanup/test adjustments.
  NEXT: remove `resolution_profile` from `Spell`, stop mirroring it in bind,
    normalize Nexus publish directly through `.profile`, and fix the stale
    tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T18:52:09Z
  TYPE: MEASURE
  CLAIM: The SpellExaminer lane now matches the requested two-step lifecycle
    model too, not just the `general` / `detailed` rename. `SpellGeneralProfile`
    now owns phase 1 binding creation plus phase 2 completion through
    `complete_with_spell(...)`. `SpellDetailedProfile` now inherits
    `SpellGeneralProfile` and adds the richer class/callable/member inspection
    layer during its own completion step. `Bind` now carries one partial general
    profile object across fingerprint/type selection and then completes that
    same object after `Spell` exists instead of rebuilding combined assets. The
    obsolete general/detailed strategy files are gone, and the same focused test
    tranche still passes with `271 passed`.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/general_profile.py:1-130
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/detailed_profile.py:1-384
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_examiner.py:1-175
  - src/melder/spellbook/bind/bind.py:208-287
  - command:python -m pytest -q tests/unit/melder/spellbook/spell_crafter/spell_examiner/test_spell_examiner.py tests/unit/melder/spellbook/bind/test_bind.py tests/component/melder/spellbook/spell_crafter/spell_examiner tests/unit/melder/spellbook/spell_crafter/spell_examiner/profiles/test_ai_profile.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py tests/unit/melder/aether/test_aetheric_frame_descriptor.py
  IMPACT: The examiner/profile contract is now coherent across both lifecycle
    phases, and bind no longer has to fake a pre-Spell combined profile.
  NEXT: review whether you want another cleanup pass on naming/doc artifacts or
    move back to the next ACL/view lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T18:52:09Z
  TYPE: FACT
  CLAIM: The default-profile-choice change belongs to the same lane and has one
    coherent propagation path. `Spellbook.bind(...)` is the main public entry
    and delegates to `self._bind.bind(...)`. `Conduit.bind(...)` is just a thin
    passthrough into `Spellbook.bind(...)`. Module scanning does not call `Bind`
    directly; `scan_bind` stores metadata, `Scan.scan_module(...)` reads that
    metadata, and then it calls `Spellbook.bind(...)`. The fluent
    `SpellBinder.finalize()` path also delegates to `Spellbook.bind(...)`. So if
    we want profile choice to be a real public binding option with default
    `general`, the minimal coherent propagation set is:
    - `Bind.bind(...)`
    - `Spellbook.bind(...)`
    - `Conduit.bind(...)`
    - `scan_bind` metadata + `Scan.scan_module(...)`
    - `SpellBinder.bind(...)` / `SpellBinder.finalize()`
    - matching interface/docstring surfaces
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:2371-2574
  - src/melder/aether/conduit/conduit.py:2041-2164
  - src/melder/spellbook/bind/scan.py:41-245
  - src/melder/spellbook/spellbinder.py:223-260
  - src/melder/spellbook/spellbinder.py:609-641
  IMPACT: We can add the default profile choice once at the public binding
    entrypoints and keep scan/fluent binding coherent without widening into
    unrelated runtime surfaces.
  NEXT: patch the bind entrypoints and scan metadata to accept `profile` with
    default `general`, then rerun the focused bind/examiner test tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T18:10:55Z
  TYPE: MEASURE
  CLAIM: The requested SpellExaminer cut is now landed and green on the focused
    surface. The old middle-state `binding` / `resolution` / `ai` registry is
    gone. `SpellExaminer` now exposes only `general` and `detailed`, has no
    explicit registry lock, and no longer carries the helper creator methods on
    the class surface. `GeneralProfileStrategy` and `SpellGeneralProfile` were
    added, the old AI-facing profile/strategy were renamed to
    `SpellDetailedProfile` / `DetailedProfileStrategy`, `Bind` now works
    through the combined assets, and the direct `.profile` consumers in
    creation, validation, and Nexus publish were updated to normalize the new
    profile shapes. The focused compile and pytest tranche passed with
    `271 passed`.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_examiner.py:1-207
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/general_profile.py:1-72
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/detailed_profile.py:1-123
  - src/melder/spellbook/spell_crafter/spell_examiner/strategies/general_profile_strategy.py:1-86
  - src/melder/spellbook/spell_crafter/spell_examiner/strategies/detailed_profile_strategy.py:1-367
  - src/melder/spellbook/bind/bind.py:1-518
  - src/melder/spellbook/spellbook_creation_system.py:1-2009
  - src/melder/spellbook/spell_crafter/validation/strategies/callable_profile_hygiene_strategy.py:1-145
  - src/melder/spellbook/spell_crafter/validation/strategies/existing_creation_compatibility_strategy.py:1-104
  - src/melder/aether/nexus/frame_descriptor_manager.py:1-650
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:1-147
  - command:python -m py_compile src/melder/spellbook/spell_crafter/spell_examiner/spell_examiner.py src/melder/spellbook/spell_crafter/spell_examiner/profiles/general_profile.py src/melder/spellbook/spell_crafter/spell_examiner/profiles/detailed_profile.py src/melder/spellbook/spell_crafter/spell_examiner/strategies/general_profile_strategy.py src/melder/spellbook/spell_crafter/spell_examiner/strategies/detailed_profile_strategy.py src/melder/spellbook/bind/bind.py src/melder/spellbook/spell.py src/melder/spellbook/spellbook_creation_system.py src/melder/spellbook/spell_crafter/validation/strategies/callable_profile_hygiene_strategy.py src/melder/spellbook/spell_crafter/validation/strategies/existing_creation_compatibility_strategy.py src/melder/aether/nexus/frame_descriptor_manager.py src/melder/aether/nexus/frame_descriptor/spell_record.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/test_spell_examiner.py tests/unit/melder/spellbook/bind/test_bind.py tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner.py tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner_inspection.py tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner_profiles.py tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner_profile_models.py tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner_strategies.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/profiles/test_ai_profile.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py tests/unit/melder/aether/test_aetheric_frame_descriptor.py
  - command:python -m pytest -q tests/unit/melder/spellbook/spell_crafter/spell_examiner/test_spell_examiner.py tests/unit/melder/spellbook/bind/test_bind.py tests/component/melder/spellbook/spell_crafter/spell_examiner tests/unit/melder/spellbook/spell_crafter/spell_examiner/profiles/test_ai_profile.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py tests/unit/melder/aether/test_aetheric_frame_descriptor.py
  IMPACT: The SpellExaminer lane is back on the requested asset-combine/rename
    model instead of the stale middle-state rebuild, and the direct runtime
    consumers are aligned with it.
  NEXT: review whether you want another rename/cleanup pass on the remaining
    test filenames and adjacent notes, or move to the next ACL/view lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T18:10:55Z
  TYPE: FACT
  CLAIM: The binding and resolution payloads do not already contain the deep
    class/callable inspector profiles. `binding_profile.py` defines the shallow
    bind-time families (`ClassBindingProfile`, `CallableBindingProfile`,
    `InstanceBindingProfile`, `OtherBindingProfile`) used for fingerprinting,
    spell typing, and basic diagnostics. `resolution_profile.py` defines the
    phased resolution artifacts (`requirements`, `symbolic_graph`,
    `resolution_frame`, `validation`). The deep `ClassProfile` and
    `MethodProfile` objects are separate inspector outputs and belong only in
    the richer detailed profile layer, not in binding or resolution directly.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/binding_profile.py:22-271
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/resolution_profile.py:197-246
  - src/melder/spellbook/spell_crafter/spell_examiner/inspectors/profiles/class_profile.py:7-120
  - src/melder/spellbook/spell_crafter/spell_examiner/inspectors/profiles/method_profile.py:7-120
  IMPACT: The proposed redesign should keep binding and resolution as internal
    detail artifacts under `general`, while the richer class/callable inspector
    objects stay only on `detailed`.
  NEXT: decide whether you want the next pass to reshape `general` /
    `detailed` into explicit two-step profile objects or keep the current landed
    version for now.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T18:10:55Z
  TYPE: DECISION
  CLAIM: The next correction is the lifecycle fix. `general` and `detailed`
    should become the real two-step profile objects: phase 1 builds the binding
    side from the raw candidate, then phase 2 completes the same object after
    `Spell` exists. `SpellDetailedProfile` should inherit
    `SpellGeneralProfile`, so the richer path adds only the extra
    class/callable/member inspection layer on top of the general
    binding+resolution base. This means the extra strategy layer is now
    redundant and should be removed.
  EVIDENCE:
  - user_instruction: "the general profile can build the bind profile and the resolution profile, and I'm not asking you to rebuild everything I'm asking you to combine and rename assets"
  - user_instruction: "general owns bind and resolutionframe part one is bind then after we return the spell we implement part to the general operations"
  - user_instruction: "same thing for detailed"
  - user_instruction: "We also want the ai_profile to inherit the general profile"
  IMPACT: The current landed `general` / `detailed` rename pass still carries
    the wrong lifecycle model. We need one more bounded refactor so the profile
    objects themselves own the two-step completion flow and bind stops
    rebuilding combined profiles around the wrong phase boundary.
  NEXT: update the patch docs to the two-step profile-object model, then remove
    the general/detailed strategy layer and rewire bind and tests to the new
    lifecycle.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T17:55:43Z
  TYPE: FACT
  CLAIM: The current SpellExaminer lane is not on the requested target model.
    The live checkout still contains the earlier middle-state rebuild:
    `SpellExaminer` is registry-driven but still registers `binding`,
    `resolution`, and `ai`; it still owns an explicit `threading.RLock`; it
    still exposes private helper creators (`_create_binding_profile`,
    `_create_resolution_profile`, `_create_ai_profile`); and `Bind` still has a
    static helper path (`spell_id_inspector`) that constructs a one-off
    `SpellExaminer`. The active patch docs are stale in the same direction: they
    still describe the old safe rebuild rather than the requested
    `general` / `detailed` contract. On the other hand, the current
    `AIProfileStrategy` already builds binding and resolution internally again,
    which matches the user's complaint that the extra helper-argument path
    should not exist there.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/spell_examiner_registry_rebuild/architecture_patch.md:10-28
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_examiner.py:28-92
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_examiner.py:162-310
  - src/melder/spellbook/bind/bind.py:44-48
  - src/melder/spellbook/bind/bind.py:203-205
  - src/melder/spellbook/bind/bind.py:291-292
  - src/melder/spellbook/spell_crafter/spell_examiner/strategies/ai_profile_strategy.py:48-70
  IMPACT: We cannot trust the existing task and patch-doc story as the rebuild
    contract anymore. The lane has to be re-baselined around the actual
    requested model before any new code edits.
  NEXT: refresh the SpellExaminer patch docs and task contract to the requested
    `general` / `detailed` rebuild, then implement against that updated lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T17:55:43Z
  TYPE: FACT
  CLAIM: The rebuild has a broader live consumer map than just `Bind`.
    `Bind._bind_logic(...)` currently fingerprints and types spells from a
    binding-shaped profile returned by `create_profile(..., "binding")`.
    `Bind.spell_id_inspector(...)` still constructs a one-off `SpellExaminer`
    and also expects a binding-shaped result. `spellbook_creation_system.py`
    reads `spell.profile` and currently only extracts disposal methods when that
    profile is a `ClassBindingProfile`. Two validation strategies also assume
    `spell.profile` is binding-profile-shaped for callable hygiene and
    existing-creation checks. Nexus spell publication then special-cases only
    `SpellAIProfile` and otherwise treats `spell.profile` as the binding
    profile, while separately reading `spell.resolution_profile`. So the
    `general` / `detailed` cut has to update four consumer families together:
    bind/fingerprinting, validation, spellbook creation-system disposal logic,
    and Nexus publish normalization.
  EVIDENCE:
  - src/melder/spellbook/bind/bind.py:203-205
  - src/melder/spellbook/bind/bind.py:291-292
  - src/melder/spellbook/spellbook_creation_system.py:445-458
  - src/melder/spellbook/spell_crafter/validation/strategies/callable_profile_hygiene_strategy.py:48-63
  - src/melder/spellbook/spell_crafter/validation/strategies/existing_creation_compatibility_strategy.py:71-83
  - src/melder/aether/nexus/frame_descriptor_manager.py:398-424
  - src/melder/spellbook/spell.py:101-108
  - src/melder/spellbook/spell.py:265-298
  IMPACT: We cannot rebuild SpellExaminer in isolation. The profile-slot
    contract on `Spell` and the small set of live consumers have to be cut
    together or the lane will regress immediately.
  NEXT: refresh the patch docs around the `general` / `detailed` contract and
    explicitly include the bind, validation, spellbook-creation, and Nexus
    publish consumers in the implementation boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T17:55:43Z
  TYPE: DECISION
  CLAIM: The `general` profile cannot truthfully be the first raw-candidate
    artifact inside `Bind._bind_logic(...)` because `ResolutionProfileStrategy`
    only builds from a fully formed `Spell`, while the bind pipeline still
    needs a binding profile earlier to fingerprint the spell id, validate the
    candidate, and determine `SpellType` before the `Spell` object exists. So
    the clean rebuild path is:
    1) keep one direct binding-profile pre-step for fingerprint/type
    2) construct the `Spell`
    3) immediately replace `spell.profile` with a `general` profile built from
       the finished `Spell`
    4) update the remaining consumers to read binding data through that general
       profile instead of assuming raw binding-profile storage on `.profile`
  EVIDENCE:
  - src/melder/spellbook/bind/bind.py:201-267
  - src/melder/spellbook/spell_crafter/spell_examiner/strategies/resolution_profile_strategy.py:11-34
  - src/melder/spellbook/spell.py:265-298
  IMPACT: This resolves the apparent contradiction between the requested
    `general` profile contract and the existing bind-time fingerprint/type
    pipeline without inventing a fake half-resolution object.
  NEXT: update the patch docs to make this bind flow explicit, then implement
    the `general` / `detailed` cut against that contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T17:55:43Z
  TYPE: PLAN
  CLAIM: The patch-doc consumption mapping is now explicit for implementation.
    `architecture_patch.md` locks the lane to the `general` / `detailed`
    rebuild and names the changed-component set. `component_patch_spell_examiner.md`
    maps to the class-surface rewrite in `spell_examiner.py`. `component_patch_bind.md`
    maps to the bind-time pre-binding/general-swap flow in `bind.py`.
    `component_patch_spell_profile_consumers.md` maps to the direct `.profile`
    consumer rewrites in the creation-system, validation strategies, and Nexus
    publish path. `code_description_patch_spell_examiner.md` maps to the exact
    new control flow and the focused validation surface we need to rerun.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/spell_examiner_registry_rebuild/architecture_patch.md:10-28
  - codex/context_compass/system_docs/patches/active/spell_examiner_registry_rebuild/component_patch_spell_examiner.md:7-25
  - codex/context_compass/system_docs/patches/active/spell_examiner_registry_rebuild/component_patch_bind.md:6-20
  - codex/context_compass/system_docs/patches/active/spell_examiner_registry_rebuild/component_patch_spell_profile_consumers.md:10-29
  - codex/context_compass/system_docs/patches/active/spell_examiner_registry_rebuild/code_description_patch_spell_examiner.md:7-25
  IMPACT: The patch gate is now satisfied with a concrete patch-section to
    implementation/validation map instead of stale docs that no longer match the
    requested direction.
  NEXT: implement the `general` / `detailed` rebuild across the examiner, bind,
    and direct consumer surfaces, then rerun the focused SpellExaminer/Bind
    validation tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T17:55:43Z
  TYPE: DECISION
  CLAIM: `detailed` should stay a rename of the current AI-facing object graph,
    not a new wrapper around `general`. The user explicitly said not to rebuild
    that richer path, only to rename it. So the clean shape is:
    - `SpellGeneralProfile`: binding + resolution only
    - `SpellDetailedProfile`: renamed current AI profile with direct
      binding/resolution/class/callable/member fields
    This keeps the detailed path mechanically close to the existing AI profile
    while still letting `.profile` normalize to `general` or `detailed`.
  EVIDENCE:
  - user_instruction: "detailed profile can literally just be renamed from AI Strategy or whatever just rename that shit don't rebuild it"
  IMPACT: The implementation should rename the existing AI profile/strategy path
    instead of wrapping it in another object layer that the user did not ask
    for.
  NEXT: keep `detailed` as a rename of the existing AI-facing profile and build
    only the new `general` profile from scratch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T14:02:00Z
  TYPE: FACT
  CLAIM: The safe SpellExaminer rebuild is landed. `SpellExaminer` is now a
    `Cleanable` runtime object with one registry of named builders and one
    primary `create_profile(target, profile_name, show_dunders, max_repr)`
    entrypoint. Default builders for `binding`, `resolution`, and `ai` are
    registered at construction time. `SpellExaminationKind` is gone. `Bind`
    now owns one long-lived `SpellExaminer` in `__init__` and uses
    `create_profile(..., "binding")` instead of constructing the examiner ad
    hoc per bind call. The direct unit/component surface for the rebuilt
    examiner and bind consumer path passed.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_examiner.py:1-224
  - src/melder/spellbook/bind/bind.py:1-310
  - tests/unit/melder/spellbook/spell_crafter/spell_examiner/test_spell_examiner.py:1-224
  - tests/unit/melder/spellbook/bind/test_bind.py:1-1674
  - tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner_inspection.py:1-125
  - tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner_strategies.py:1-511
  - command:python -m pytest -q tests/unit/melder/spellbook/spell_crafter/spell_examiner/test_spell_examiner.py tests/unit/melder/spellbook/bind/test_bind.py tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner_inspection.py tests/component/melder/spellbook/spell_crafter/spell_examiner/test_spellbook_component_spell_examiner_strategies.py
  IMPACT: The live profile creation surface is now easier to extend later, and
    bind no longer pays the cost of ad hoc SpellExaminer construction.
  NEXT: decide whether the next profile-related slice should rework how
    profiles get attached to spells or return directly to the ACL/view
    configuration design.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the active runtime slice for the SpellExaminer rebuild.
