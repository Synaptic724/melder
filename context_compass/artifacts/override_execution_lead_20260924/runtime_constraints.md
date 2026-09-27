# Override execution: runtime constraints for the compiler investigation

Owner: updater_0. Date: 2026-09-24.
Task: tickets/tasks/2026-09-24_coordinate_override_execution_investigation_task.md.
Peer compiler trace: tickets/tasks/2026-09-24_investigate_override_compiler_planning_task.md.

## Findings grounded in current source

The ordinary Conduit id fast door is restricted to absent overrides. Explicit call payloads replace
stored mutation overrides, including an explicit empty dictionary that suppresses the stored value.
Normalizing empty inputs before selecting the mutation payload would silently change this precedence.
The normal door's epoch, current context, validation and hook checks must also govern any faster door.

Evidence:
- src/melder/aether/conduit/meld/conduit_meld.py:259-572
- src/melder/aether/conduit/meld/meld.py:1506-1575

The generalized manifest runtime already caches non-overlapping raw-key shapes and binds values on
each call. Overlapping selectors intentionally use the value-dependent conflict path. The generalized
hydrator calls this manifest runtime; its older finalize-step runtime is not the full warmed story.
Retain PATH > UNIQUE > BROADCAST precedence, equal-rank conflict errors and missing/ambiguous selectors.

Evidence:
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_overrides_runtime.py:86-444
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:361-407
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/artifacts/spell_override_targeting_codegen_creation.py:210-427

The generalized emitter still emits every step. Each emitted step routes to its proper store:
many uses the Space store when present, per-conduit uses that Conduit, per-Space uses that Space,
lineage uses the resolving root, cluster uses the elected store, and unique uses the Spell owner.
The generated shared-lifetime paths include the existing-instance override refusal and the relevant
store/Spell locking. A new fast instruction sequence must preserve these operations and their ordering.

Evidence:
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:773-875
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1818-2311
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:2725-2759

The generalized process-wide emitted-source key records targeted spell IDs, per-spell/per-step counts
and positional presence. It does not encode the exact parameter assigned within a targeted step.
Constant-folding socket-name comparisons therefore requires finer source identity, not just deleting
branches. Different same-count selections must not reuse code specialized for different operands.
Values must remain outside the source key and bound static closure so later calls receive their own data.

Evidence:
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_overrides_runtime.py:523-564

## Untimed lifecycle observations

The standalone probe binds a disposable Dependency and a many root, supplies an external Dependency
at the left socket, and records construction, root activation and cleanup. A second form retains a
right socket requesting the same registered class. Each case resets its world and disables disk cache.

| Dependency lifetime | Caller | Generated dependencies: left only | Generated dependencies: left + right | Disposal boundary |
| --- | --- | ---: | ---: | --- |
| many | Conduit | 1 | 2 | Conduit cleanup |
| many | SpellSpace | 1 | 2 | SpellSpace cleanup |
| unique | Conduit | 1 | 1 | Conduit cleanup |
| unique_per_conduit | Conduit | 1 | 1 | Conduit cleanup |
| unique_per_spell_space | SpellSpace | 1 | 1 | SpellSpace cleanup |

In all ten observations:
- The root receives the supplied reference at the left socket.
- The supplied reference receives no disposal call.
- The root activation callback runs once.
- Every generated dependency receives one disposal call at the observed owning scope's cleanup.
- When the right socket exists, it receives a generated dependency rather than the supplied left value.

Thus eager discarded work has observable constructor and disposal effects today. Pruning is a behavior
change, even if it produces the same final root field values. Shared-node pruning also cannot remove a
provider still needed by another socket. These observations do not settle lineage/cluster behavior,
cross-conduit ownership transfer, descendant hooks or concurrent reuse races.

Reproduction:

```powershell
& .venv_new/Scripts/python.exe context_compass/artifacts/override_execution_lead_20260924/probe_override_lifecycle.py
```

Evidence: lifecycle_observations.json and probe_override_lifecycle.py in this directory.

## Existing contract qualification

36 focused tests passed in 1.15 seconds. These cover supplied input identity (ordinary, falsey and
None), both fresh and manifest-hydrated contexts across three families, missing input errors, selector
precedence/conflicts, and shared-root/shared-dependency override rejection. contracts.xml and
contracts.log retain the result. This was not a timed performance measurement or a full-suite run.

The existing eager-branch characterizations are deliberate and currently green:
- tests/component/melder/aether/conduit/test_conduit_component_non_resolvable_overrides.py:146-160
- tests/component/melder/aether/conduit/test_conduit_component_non_resolvable_overrides.py:186-194

They require the registered child's own input even when the parent later replaces that child. Their
presence does not establish that eagerness is desirable; it establishes an explicit behavior boundary.

## Recommended separation for the proposal

First investigate cheaper emitted instructions for the same full occurrence sequence: retain normal
call layout on unchanged steps, apply override substitutions only to targeted parameters, preserve
store/lock/registration/error behavior, and compare with the existing experiment. Keep the public
override API and ordinary no-override door. No speedup is claimed for this unimplemented design.

Treat branch pruning as a separate explicit decision within the epic. If selected, determine live
occurrences from the root after socket substitution, preserve dependencies still reachable elsewhere,
and define the treatment of nested selectors beneath replaced branches. Change the eager-error and
disposal expectations deliberately, with new tests demonstrating the selected contract.

## Qualification matrix for an implementation proposal

| Boundary | Required regression |
| --- | --- |
| Shape reuse | Same keys with changing ordinary/falsey/None values and alternating shapes/arity |
| Selector rules | Exact paths, UNIQUE, BROADCAST, precedence, equal-rank conflicts, unmatched keys |
| Plain arguments | Defaults, required inputs, keyword-only and positional call semantics |
| Occurrences | Repeated many provider, shared diamond and one replaced branch with another live use |
| Lifetimes | Every Existence mode through its authorized Conduit/Space store |
| Ownership | Supplied references remain external; generated retained values dispose exactly once |
| Hooks | Root pre/activation/post and descendant behavior without duplicate or skipped callbacks |
| Existing values | Root reuse and targeted shared-dependency override refusal |
| Persistence | Fresh context, .melc/manifest hydration, revalidation and changed selection |
| Concurrency | Alternating shapes/values cannot mix cached maps or capture another call's values |
| Performance | Matched warm/cold measurements with unchanged no-override baseline and construction counts |

Only the selected implementation scope determines which rows need new tests; reuse existing contracts
where they already prove behavior. No production changes or asset rebuilds occurred in this task.
