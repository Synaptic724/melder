# Code Description Patch: Compiler capability decisions

<!-- BEGIN ENTRY: Selected target to required override -->
## Phase-3 Flow
1. Read original symbolic sockets and parameter-kind facts from requirements.
2. For a False root, keep declaration/topology metadata and an empty constructor dependency set.
3. For a True root, use the existing scan/pass-index matching and named descriptor selectors.
4. Implicit single annotation: choose the True candidate subset when nonempty, otherwise the original
   False subset. Require one selected candidate; keep existing missing/ambiguity diagnostics.
5. Collection: retain matching True entries in original order; zero is still a valid empty collection.
6. SpellMap: retain original selection/cardinality. A selected False with a present spell_override
   refuses, because that payload would configure construction that is disabled.
7. A selected False single/SpellMap creates a reference-only OVERRIDE_REQUIRED socket. Other selected
   targets produce existing DAG edges. Defaults/PLAIN and unresolved SpellContract remain metadata-only.

## Validation and Root Plans
Use local topology to identify required supplied inputs and omit their construction-cycle edges.
Do not run constructor-DI restrictions on False roots. Retain unrelated registration/profile checks.
Phase 5 uses a resolvable-only executable snapshot while state stores retain descriptive topology.
Cache-payload and scheduler eligibility agree with that boundary, including direct phase entry.

## Required Input Transport
Build immutable plain-value rows from local topology, with actual signature position/kind and selected
reference IDs. Carry them through model and both plan variants; presence at runtime is S4's job.
Do not encode required input as an empty dependency list, fake default, optional collection or new provider.
Existing compile signatures include new consumed fields; no external cache framework is introduced.

## Edge and Failure Cases
Optional without a default still requires supply when its selected target is False. Ordinary defaults
remain PLAIN. An unhealthy/blocked True provider does not fall back to False. Explicit selectors do not
redirect. A False SpellContract provider is an explicit incompatibility, even in dynamic mode.
Referenced IDs never expand occurrences or create constructor paths below the supplied value.

## Non-Goals and Handoff
No runtime argument checking, direct-meld guard, ownership/disposal redesign, Nexus commands or crystal
replay in this S3 patch. S4 must guard constructor execution and all fast/cache doors using these rows.
<!-- END ENTRY: Selected target to required override -->
