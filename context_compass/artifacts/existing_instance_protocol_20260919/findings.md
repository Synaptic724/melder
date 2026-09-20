# Existing-instance Protocol admission investigation

Status: investigation complete for review; no production repair.
Task: TASK-2026-09-19-investigate-existing-instance-protocol-validation.
Owner: updater_0.

## Question

Why can an existing unique object that lacks an explicitly declared Protocol member reach consumer
injection, and where should that be rejected within Melder's current bind/compiler architecture?

## Boundary

Preserve the current existing-object model. Study admission parity, actual-instance member checks,
compiler assumptions and existing control cases. Broader Protocol semantics and registration redesign
remain separate choices. Results and exact source pointers will be appended as each trace completes.

## Bind To Compiler Trust Boundary

1. Bind recognizes the declared Protocol frame, but its compatibility call is gated on ClassBindingProfile.
   Existing-instance profiles skip that branch and still become normal registered Spell records.
2. The existing compatibility helper checks public entries directly in the Protocol's __dict__:
   attribute existence, and callable-ness when the Protocol entry is callable. It deliberately does
   not perform full typing/signature checking; inherited Protocol members and annotation-only data
   do not enter that loop. Those limits affect the class path too.
3. Phase 3 selects normal dependencies from declared spell/frame/name identity, with indexed and
   scan equivalents. Single resolution requires one candidate; collections collect matches; SpellMap
   filters its explicit target/frame/name. None of these selection methods checks instance members.
4. Phase 3 stores provider Spell payloads and per-parameter graph edges. Therefore declaring the
   frame is sufficient for a bad admitted instance to become a provider candidate.
5. Default Phase 4 includes ExistingCreationCompatibilityStrategy: it verifies value presence,
   unique lifetime, instance/other profile and absence of constructor requirements. AnnotationShapeGuard
   checks annotation shapes, not provider conformance. The Phase-6 DependencyTypeSanityStrategy
   warns about callable SpellTypes; it is not a Protocol member validator.

This makes admission a meaningful shared boundary. The compiler still needs end-to-end qualification,
but the trace does not establish a need to rebuild existing objects or expand their lifetime model.
The next native baseline must confirm that no later stage rejects the incompatible supplied value.

Evidence:
- src/melder/aether/spellbook/bind/bind.py:464-523
- src/melder/aether/spellbook/bind/bind.py:868-912
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:177-251
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:277-543
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:564-637
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:748-987
- src/melder/aether/spellbook/spell_compiler/validation/validation_system.py:157-196
- src/melder/aether/spellbook/spell_compiler/validation/strategies/existing_creation_compatibility_strategy.py:79-163
- src/melder/aether/spellbook/spell_compiler/validation/strategies/annotation_shape_guard_strategy.py
- src/melder/aether/spellbook/spell_compiler/system/validation/dependency_type_sanity_strategy.py

## Fresh Native Baseline

Python 3.14.7 free-threading, with an asserted local Bind import and process-local PYTHONPATH.
Ran the existing eighteen Protocol admission tests unchanged: 4 failed, 14 passed in 0.57 seconds.
All four failures are DID NOT RAISE TypeError for missing/non-callable members on supplied instances,
before and after conjure. Class rejection, valid/inherited-instance injection, grouping-frame and
factory controls passed.

Command:
    .venv_new/Scripts/python.exe -m pytest tests/component/melder/spellbook/test_existing_instance_protocol_admission.py -q -p no:cacheprovider

Evidence: source_preflight.log, native_baseline.log and native_baseline.xml in this folder.
Next: native end-to-end bad-provider paths and a process-local admission-check simulation.
The simulation will change only the test process, not production files; it is hypothesis evidence,
not repair acceptance.

## Native Compiler Paths And Actual Instance Members

The additional path baseline produced 2 failed, 20 passed in 0.64 seconds. The four stock observation
cases all inject the same incompatible MissingReader through annotation, collection, SpellMap and
linked SpellContract paths. Compiler/contract validation succeeds; actual read() use raises AttributeError.
Twelve valid controls cover normal, inherited-implementation and instance-only callable members across
the same four paths. Two new desired-behavior regressions fail because a supplied ShadowedReader has
read=None while its class still exposes a method; admission currently fails to reject it.

Four additional characterization cases preserve existing helper limits: inherited Protocol members
and annotation-only data are unchecked on class and instance paths. These passing observations are
not acceptance of full Protocol conformance and are distinct from the missing instance admission call.

Evidence: test_protocol_paths.py, path_baseline.log and path_baseline.xml.
Checking type(instance) would be the wrong repair: it would accept the shadowed invalid member and
reject a valid member installed only on the instance. The probe must check the actual supplied value.

Staged admission baseline: 2 failed, 1 passed (22 unchanged cases deselected). Incompatible values
also bypass Protocol admission through bind_inactive before/after conjure. A valid instance-only
member survives post-conjure staging, selection and exact-reference meld. Evidence: staged_baseline.log/xml.

## Admission-Only Diagnostic Result

Explicitly loaded admission_probe.py into an isolated pytest process and ran the original eighteen
tests plus the non-stock path/member/staging controls. Result: 39 passed, 4 stock observations deselected
in 0.39 seconds. This includes four intentionally preserved helper-limit characterizations; it is
not a claim of complete Protocol conformance.

No compiler behavior was replaced. The probe adds only the existing direct-member check for actual
non-callable supplied instances, then delegates to unchanged Bind. It is a simulation, not a source
patch. Its early wrapper position does not qualify production guard ordering or custom examiner profiles.
Production placement should be the existing Protocol branch after normal target/profile/existence checks.

Evidence: admission_probe.py, admission_probe.log and admission_probe.xml.

## Recommended Repair Boundary

The missing guarantee belongs at admission: a supplied instance registered under a Protocol must
satisfy the same currently supported member rules that class binding applies. Compiler resolution
uses the declared frame and graph identity; it should not need another object-construction or
registration system to make this guarantee true.

Proposed production change:
- src/melder/aether/spellbook/bind/bind.py: extend the existing Protocol branch in _bind_logic to
  InstanceBindingProfile and OtherBindingProfile alongside ClassBindingProfile.
- Pass the actual supplied value to the member check, not type(value). Keep the existing class
  branch's behavior and diagnostics compatible; emit an appropriate supplied-object failure message.
- Generalize _structurally_implements_protocol's candidate annotation/docstring from class-only
  wording to the class-or-instance value it actually examines. Preserve its current member coverage
  for this repair; a broader Protocol checker is a separate decision.
- Place the check after existing target/profile/existence validation, before the Spell is published
  through Spellbook's normal maps. Do not replicate the diagnostic wrapper's earlier placement.

No production compiler change is indicated by the traced paths or thirty-nine selected diagnostic
checks. No new metadata profile, source policy, lifetime or external-registration API is needed to
close this particular admission hole. This conclusion is bounded to the declared-member contract
and scenarios investigated here, not a proof of all possible custom profile or mutation behavior.

Entrypoint coverage:
- Active Spellbook.bind and bind_inactive both call the same Bind.bind/_bind_logic pipeline.
- Bind's direct/decorator routes converge on _bind_logic.
- SpellBinder.finalize delegates to Spellbook.bind. Its Protocol policy should stay at that shared seam.
- Conduit binding facades already delegate to their owning book; no separate member checker is proposed.

Evidence:
- src/melder/aether/spellbook/bind/bind.py:228-323
- src/melder/aether/spellbook/spellbook.py:4834-4864
- src/melder/aether/spellbook/spellbook.py:5137-5162
- src/melder/aether/spellbook/spellbinder.py:826-870
- src/melder/aether/conduit/conduit.py:3097-3278
- tests/unit/melder/spellbook/bind/test_bind.py:1091-1102

## Tests And Documentation For An Approved Patch

- Update the old unit test test_instance_profile_under_protocol_spellframe: it currently asserts
  that an object with no foo member is accepted under a Protocol requiring foo. This expectation
  conflicts with the requested repair, rather than exposing another compiler defect.
- Keep the eighteen native admission regressions and controls. Add the actual-instance shadowing,
  instance-only callable, inactive binding and valid staging/selection cases to their appropriate
  permanent test modules after the repair is approved.
- Retain native annotation, collection, SpellMap and cross-conduit SpellContract identity/use checks.
  Invalid instance admission should fail before those graphs accept a false declaration.
- Verify class error behavior, callable factory admission, ordinary concrete/string grouping,
  uniqueness and constructor opacity stay unchanged.
- Update Bind's public/internal contracts and relevant registration/component documentation. Refresh
  affected graph descriptors/indexes and required source/build bundles after production changes.
- Do not regenerate runtime assets for this investigation alone; production source was not changed.

## Separate Shared Checker Limits

Inherited Protocol members and annotation-only fields are omitted by the current direct-__dict__
helper for class bindings too. Four native cases demonstrate that limit. Expanding coverage would
be a broader contract change with separate class-versus-instance questions, especially fields that
only exist after initialization. Signature/return-type validation is explicitly outside the helper's
documented scope. Recommend admission parity first, then decide whether broader coverage is wanted.

This is also not continuous health monitoring of a mutable object. A member changed after successful
bind is a different lifecycle/mutation contract. The proposed repair checks the supplied value when
it is admitted; it does not add reflective Protocol checks to every meld.

## Verification And Limits

- Original stock suite: 4 failed, 14 passed.
- Additional stock path/member suite: 2 failed, 20 passed.
- Three newly added staged cases: 2 failed, 1 passed, 22 prior cases deselected.
- Admission-only simulation: 39 passed, 4 stock observations deselected; includes four preserved
  shared-limit characterizations. It is not a production acceptance run.
- Ruff F checks pass for both new diagnostic files.
- Bind, Phase 3 and ExistingCreationCompatibilityStrategy SHA256 values match the captured pre-probe
  values in source_hashes_before.json. No production repair was applied.
- Full repository suite, permanent patch guard ordering, custom examiner profiles, concurrency and
  changed-after-bind conformance were not newly qualified. No performance claims are made.

## Resume

Review the bounded Bind admission repair and decide separately whether to expand the shared Protocol
checker. The exact runtime change, permanent tests and documentation must follow that choice. Preserve
the current unique-only existing-object model and all unrelated working-tree changes.
