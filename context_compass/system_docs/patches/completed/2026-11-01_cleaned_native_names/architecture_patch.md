# Native CLEANED contracts

<!-- BEGIN ENTRY: "Native CLEANED names and persisted state" -->
## Scope and non-goals
Patch: 2026-11-01_cleaned_native_names. Owner/author: command_5,
synaptic_python_developer. Task: TASK-2026-11-01-cleaned-enum-native-persistence.
Correct only three terminal member names and their direct native consumers.
Preserve enum bases, values, declaration order, lowercase siblings, ownership and cleanup.

## Changed-components matrix
| Component | Delta | Contract |
| --- | --- | --- |
| EnumHelpers | Case-insensitive declared-name lookup; preserve family rejection | component_patch_enum_helpers |
| DevOps Control Plane | SpellValidity.CLEANED and direct references | component_patch_devops |
| Conduit Runtime | ConduitState.CLEANED; lowercase string rendering remains | component_patch_conduit |
| ConduitWard and Contracts | Canonical terminal-state assignment | component_patch_ward |
| Meld Resolution Runtime | Use canonical terminal validity member | component_patch_meld |
| Crystallizer Persistence | RecordedUnitState.CLEANED; old/new name read compatibility | component_patch_crystallizer |
| Nexus Root | Canonical recorded cleanup member | component_patch_nexus |
| MutationResearch Root | Canonical recorded cleanup member | component_patch_mutation_research |

## Interface and boundary deltas
Python member access becomes CLEANED with no lowercase Python alias.
External name lookup remains case-insensitive. RecordedUnitState.value remains cleaned.
New journal names are CLEANED; readers accept exact legacy cleaned and canonical CLEANED.
Other member names/values, disabled replay, public verbs and record-major admission remain.

## Cross-component invariants
No transfer disposes a borrowed logger or object. No new after-cleanup safety is promised.
Preserve raw folded state names and later-wins ordering. Both cleaned spellings prevent rebuilding
the recorded singleton and retain the existing honest shortfall, in both replay drivers.
The helper must not accept another enum family through string equality or a warmed cache.

## Migration and rollback
First qualify the helper with causal tests. Read each consumer fully before its exact mechanical
name edit. Change definitions and consumers in the same source tranche; add reader compatibility
before any canonical persisted output is accepted. Do not change the recorder's generic .name path.
Rollback must restore definitions and consumers together, keeping the widened reader while any
CLEANED record may exist; never silently downgrade persisted intent or bypass major5 admission.

## Validation and ticket coverage
The native Task owns all seven component changes and tests; external Ops656 integrates its result.
Prove names/order/values, native case variants and rejected families, canonical captured payloads,
valid major5 old/new cached journal restore without reconstruction, and disabled/enabled controls.
Run complete affected modules, review intentionally, promote docs/descriptors/indexes, take the live
notch/release entry and complete both required build/check families last.

## Unknowns and decisions
Direct-consumer whole-file reads and the exact public cached fixture are pending. They block their
dependent edits/test claims, not the already-read helper component. No compatibility redesign,
value migration, source export, push, release cut or host permission change is authorized.
<!-- END ENTRY: "Native CLEANED names and persisted state" -->
