# Required caller inputs: investigation and epic history

- Recorded: 2026-09-24T11:49:47Z
- Agent: workflows_0
- Ticket: tickets/tasks/2026-09-24_investigate_required_caller_inputs_task.md
- Scope: investigation only; no production or application source changes.
- Verified native import: melder_private/src/melder/__init__.py, source version 0.2.52.

## Conclusion

The runtime already accepts supplied objects by identity and rejects missing required Python arguments.
The missing authoring capability is a parameter-scoped declaration that says a typed required input
comes from the caller without binding its type. Current Phase 3 insists on a registered candidate
before it can create an OVERRIDE_REQUIRED input.

Current flow:

```text
required custom-type annotation -> SINGLE_BY_ANNOTATION -> Phase 3 candidate lookup
  resolvable provider found  -> executable dependency
  one False definition      -> OVERRIDE_REQUIRED reference-only input -> supplied runtime value
  no matching registration  -> RuntimeError before meld or its override map can be used
```

Source:
- src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:975-1226
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:435-513,693-926
- src/melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.py:64-133

## The epics and the stricter-conjure question

| Change | Evidence | Relationship to this failure |
| --- | --- | --- |
| September 19 non-resolvable registration epic | completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md | Introduced OVERRIDE_REQUIRED for selected registered definitions; preserved ordinary Python missing-input errors. |
| September 23 creation-cache compatibility epic | completed/2026-09-23_invalidate_creation_cache_on_melder_version_change_epic.md | Added exact release admission and cache schema 9; explicitly kept resolution semantics. |
| August 3 whole-pipeline value-only IR epic | 2026-08-03_comptime_ir_phase_pipeline_epic.md | Still ready/unassigned; it is a design proposal, not evidence of a newly shipped strict-input rule. |
| June 28 cold-build resolution gate | spellbook_creation_system.py:242-250,349-409; commit b823784f48 | Makes conduit-level resolution errors fail at conjure; these cases fail earlier during structural Phase 3. |
| Existing zero-provider refusal | compiler_phase_3.py:492-497; blame traces to May 20 b9ec49dee7 | This exact branch predates the recent epics. History establishes it existed then, not its first-ever introduction. |

Epic names above are relative to context_compass/tickets/epics. Historical blame receipts are
phase3_history.log and conjure_gate_history.log. The July 5 collection-DI epic also records the
later resolution gate, but concerns collection wiring/empty-provider policy and cache behavior.

The actual conjure method executes _prepare_spellbook_for_conjure (structural phases) before it
classifies creation-cache posture or enforces the later conduit-resolution verdict. The original
minimal fixture additionally disables disk caching, so cache schema 9 does not cause its refusal.
Source: src/melder/aether/spellbook/spellbook_creation_system.py:203-317.

## Reproduced behavior

Independent CommandOps selection against verified local source: **5 failed, 1 passed in 2.87s**.
The passing case carries a real caller-owned, unregistered Package through a plain object's override.
Failures:
- Task bound before conjure: Phase 3 rejects work_callable: Package.
- Task bound into an already-conjured dynamic root: bind transaction commit hits the same refusal.
- AgentPoolsBootstrap root generation: Task.work_callable.
- AgentsBootstrap root generation: StackContext.entry.
- CommandCenterBootstrap root generation: CommandCenter.conduit.

Receipts: application.log / application.xml. The driver's output verifies CPython 3.14.7 free-threaded,
source version 0.2.52 and the exact local Melder import path. No package installation occurred.
command_0 independently reproduced the same selection in 1.18s; its handoff is recorded under
priv_commandops/context_compass/artifacts/2026-09-24_reported_area_and_center_failures/.

Existing native capability controls:
- 32 runtime cases pass: ordinary/falsey/None supplied objects, missing required arguments,
  all three executor families, cached manifest hydration, nested inputs and existing reuse behavior.
- Six compiler cases pass: False definition references and ordinary provider precedence.
- Receipts: native_runtime.log / .xml and native_compiler.log / .xml (36 compiler cases deselected).

Commands:
- .venv_new/Scripts/python.exe -m pytest
  tests/component/melder/aether/conduit/test_conduit_component_non_resolvable_overrides.py
  -q --tb=short -p no:cacheprovider
- .venv_new/Scripts/python.exe -m pytest
  tests/component/melder/spellbook/test_spellbook_component_override_required.py
  -k "false_target_requires_override_and_retains_reference or real_provider_takes_precedence_over_descriptive_definition"
  -q --tb=short -p no:cacheprovider

Consumer selection: priv_commandops/tests/component/spectrum/test_manual_package_overrides.py plus
the three root-generation parameter cases in test_area_bootstraps.py for CommandCenterBootstrap,
AgentPoolsBootstrap and AgentsBootstrap. Used priv_commandops/.venv314/Scripts/python.exe -B;
inserted priv_commandops/src then melder_private/src at sys.path[0] and asserted the native import.
pytest options: -q -o pythonpath= -o addopts= --rootdir=<priv_commandops>
--confcutdir=<priv_commandops>/tests/component -p no:cacheprovider --tb=short --show-capture=no --timeout=40.
Full collected identities are retained in application.xml. Coverage was not measured.

## Existing API assessment

- resolvable=False on an application input definition works today and produces OVERRIDE_REQUIRED.
  It requires a registered target. It does not declare an individual consumer parameter.
- Marking the consumer itself False prevents construction of that consumer; it cannot satisfy this need.
- Package and Conduit remain kernel-guarded; no such binding is attempted by the failing tests.
  The owner specifically requires their existing objects through overrides and rejects registering them.
- Bind's extra kwargs are stored as metadata; there is no existing parameter declaration consumed by
  the inspected classifier. An invented keyword would not establish input policy.
- SpellMap selects a registered provider/definition; its spell_override is a construction payload,
  not a declaration that the consumer parameter is supplied externally.
- Ordinary defaults suppress inferred DI, but making a required argument optional changes the
  constructor contract and is not an acceptable correction.

## Recommended bounded design

Add an explicit per-binding list of caller-supplied parameter names. Exact public naming is a design
decision; no example keyword here is claimed to exist. Preserve the application's original required
type annotations and constructor signatures.

Required implementation boundaries:
1. Validate declaration names/kinds against the real constructor. Store the policy as native,
   immutable binding metadata and include it in identity where it changes compilation semantics.
2. Produce OVERRIDE_REQUIRED without resolving a provider or requiring referenced_spell_ids to be
   nonempty. Keep original annotation/position/kind and separate these inputs from executable edges.
3. Preserve ordinary DI missing-provider errors for undeclared parameters. An explicit caller-input
   declaration should remain authoritative even if a matching provider exists or is registered later.
4. Reuse the established override/constructor execution path. The September epic retained ordinary
   Python missing-argument errors and avoided an additional per-call preflight. Reuse need not resupply
   construction inputs when it constructs nothing.
5. Carry the declaration through descriptions, restore/graft and compilation/cache identity. A fix
   confined to conjure or a validation skip would lose the contract on other entry paths.

No global relaxation of unbound annotations, kernel-guard exception, dummy registration, weakened
annotation, redundant wrapper, native ownership transfer or new validation bypass is recommended.
This declaration work should be coordinated with the ongoing effective-override-graph work before
implementation, but it addresses a separate authoring boundary.

## Additional caller-input sites

Phase-1-only inspection, without domain construction, is recorded in phase1_inputs.json:
- StackContext.home: greenlet is also a required SINGLE_BY_ANNOTATION parameter.
- CommandCenter.spectrum: Spectrum is also a required SINGLE_BY_ANNOTATION parameter.

Their current failures stop at earlier parameters, so these are additional declaration candidates,
not newly executed post-fix failures. CommandOps must decide which inputs its normal providers own
and which are always caller-supplied. Melder passes supplied values through; the consumer's own
constructor/cleanup contract still decides domain ownership.

command_0 subsequently confirmed both additional values are exact caller inputs: Spectrum already
passes spectrum=self to center construction, and home is the owning agent thread's existing greenlet.
Its existing ticket retains this acknowledgment and the question/alert have been consumed.
