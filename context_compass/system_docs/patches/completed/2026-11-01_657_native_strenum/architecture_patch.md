# Native enum migration contracts

<!-- BEGIN ENTRY: "Native access and creation enum string migration" -->
## Scope and non-goals
Patch: 2026-11-01_657_native_strenum. Author and executor: command_5,
synaptic_python_developer. Owning native task: TASK-2026-11-01-strenum-native-657.
This entry selects only RiftAccessMode and RiftCreationMode. Other native inventory
families remain undispositioned and require their own source-backed entries before edits.

## Changed-components matrix
| Component | Delta | Contract |
| --- | --- | --- |
| Nexus Rift policy vocabulary | Two string-valued Enum families become StrEnum | component_patch_rift_policy_enums |
| Native EnumHelpers | No implementation change selected; preserve its family gate | Existing helper contract |

## Interfaces and invariants
Keep each class in its current module, preserve member names, declaration order and exact
string values. Existing by-value construction and unknown-value refusal remain. Both classes
gain the user-selected StrEnum string rendering, JSON string behavior and string equality.
They share two equal spellings; a helper request for one family must still reject a member
of the other even after an equal raw string warmed the type-sensitive cache.
No unrelated capitalization, cleanup, ownership, native numeric or record-major rule changes.

## Persistence, migration and rollback
The first-party direct symbol census found no production consumer outside the definitions;
that does not prove external or dynamic-use absence. The old and new value tokens remain
identical. Verify actual pre-change by-value pickle payloads load with the migrated classes,
plus JSON and round-trip inputs. Do not claim compatibility for a format not tested.
A source rollback restores both class bases together; verify persisted payload readability
and document the intentional difference in string/equality behavior in the release note.

## Order and validation
Read the definition and existing tests in full, preserve exact source preimages, and record
the patch-to-implementation mapping. Capture causal tests before changing source; run both
existing enum test modules and the new contract tests on the supported 3.14t interpreter.
Verify same-family and foreign-family helper paths in both cache orders, old/new tokens,
unknown values, JSON and pre-change pickle payloads. Review exact diffs; update authored
documentation and graph descriptors/indexes, notch the live version once per source change,
and rebuild/check generated assets and LLM bundles last after ticket closure.

## Remaining unknowns
External consumers and undiscovered dynamic imports are not enumerated by the symbol search.
The other 36 native families and their consumers have no disposition from this entry.
<!-- END ENTRY: "Native access and creation enum string migration" -->

<!-- BEGIN ENTRY: "Native Nexus configuration enum string migration" -->
## Scope and changed components
Qualify NexusFrameMode, RiftSpaceType and RiftValidationMode, their direct Nexus and Rift
configuration normalization, and the real Nexus configuration record/reload boundary.
The earlier RiftAccessMode/RiftCreationMode entry remains distinct. Other families remain
unselected until separately qualified.

## Interface and persistence deltas
Each selected class becomes StrEnum with unchanged names, explicit string values, ordering
and module path. Direct old by-value tokens continue; direct RiftSpaceType("dynamic") remains
invalid, while the two configuration APIs continue to map the raw legacy "dynamic" input to
codegen. An equal foreign Enum never gains admission via that alias.
The Nexus emitted twin records enum member names as plain str even when the members are
StrEnum; the old plain-name checkpoint and recorded-dictionary replay remain valid. No
record-major, cleanup-state, owner, transfer or numeric contract changes.

## Ordering and validation
Consume this entry, component and code-description patches, then record mapping. Capture
actual pre-change pickle representatives and real checkpoint name values. Establish causal
tests for enum string behavior, legacy and foreign alias inputs, typed config boundaries,
plain in-memory checkpoint output, JSON and actual reload. Change the three enum bases and
docstrings with the two configuration boundary fixes in one coherent tranche. Run existing
affected configuration/enum modules, checkpoint regressions and the unchanged new tests.
Preserve first-tranche work and every existing dirty source change.

## Failure and rollback
Unknown names and foreign enum families retain ValueError. The existing dynamic alias is
restricted to non-enum string input; no silent fallback for another family. Rollback must
restore declarations and both configuration consumers together; existing recorded name
strings remain readable. Do not claim arbitrary external pickle or persistence compatibility.
<!-- END ENTRY: "Native Nexus configuration enum string migration" -->

<!-- BEGIN ENTRY: "Native SpellframeKind string migration" -->
## Scope and invariants
Convert only SpellframeKind to StrEnum, retaining the none, category and contract names,
their exact string values, order and import path. Its new string/equality behavior is
intentional; no unrelated bind, lookup, lifecycle or owner-transfer rule changes.

## Binding and recorded data
Bind continues assigning its concrete members. SpellIndex.signature_of keeps returning
the same plain value string, BindingManifest keeps hashing the same member-name string,
and SpellCrystal keeps recording the same plain name. Restore and graft still hydrate the
recorded protocol or report the existing shortfall. Keep record-major admission unchanged.

## Ordering and validation
Consume this architecture entry and its component patch before changes. Add causal tests
that read actual pre-change protocol-4 payloads, assert the fixed bare/category binding
hashes, prove signature/value/JSON behavior and retain unknown-value refusal. Run the
existing complete enum, binding-manifest, SpellIndex, bind/phase, spell-crystal and real
protocol restore/graft modules against the final source. Preserve all prior dirty changes.
<!-- END ENTRY: "Native SpellframeKind string migration" -->

<!-- BEGIN ENTRY: "Native research record enum string migration" -->
## Scope and invariants
Convert LaneState, LaneType and TransitionAct to StrEnum in their existing two modules.
Their explicit values, names, order, ownership and lifecycle remain. Raw strings and
same-family members can express the selected vocabulary. Distinct families must not be
mistaken for one another merely because a string value is equal.

## Persistence and error boundaries
ResearchLane.describe and TransitionEntry.describe continue emitting the same plain .value
strings. Plain old JSON payloads hydrate identically. A foreign enum in a lane payload's
state/type keeps the existing wrong-type fallback; a foreign enum as an entry act is refused.
A direct lane-type input accepts a raw string or LaneType member and refuses foreign enum
families before by-value lookup. Unknown tokens retain their existing errors. The same-family
StrEnum member can now act as a string at the documented value surface.

## Ordering and validation
Read and map this architecture, component and control-flow entry. Capture the old JSON and
pickle witnesses, then establish causal tests. Change only the two enum modules and their
existing payload/type normalization branches. Test old JSON bytes, historical pickles,
family collisions, tolerant lane fallback, real ResearchSet creation/journal and cached
MutationResearch checkpoint replay, alongside complete existing research modules.

## Failure and rollback
Preserve open/joined/archived lifecycle, journal chronology and record-major admission.
Rollback must restore both enum classes and their family-aware seams together. Do not infer
compatibility for arbitrary external serialization or unrelated enum families.
<!-- END ENTRY: "Native research record enum string migration" -->

<!-- BEGIN ENTRY: "Native participation enum canonical values" -->
## Scope and selected representation
ParticipationState already is StrEnum. Set its four values to their exact uppercase member
names. Keep the class path, member names/order and ACTIVE-only emission rule.

## Legacy data and typed boundary
The exact four previously accepted lowercase by-value strings remain readable through a
narrow enum missing-value mapping, including their actual protocol-4 pickle payloads.
Canonical uppercase strings are accepted; mixed case, whitespace and unknown values remain
invalid. No generic case folding or cross-family validation bypass is introduced.
InformationRegistry keeps its existing detached lowercase state tokens so historical
snapshot/log consumers see the same plain strings. Its state-writing and filtering APIs
continue to demand an actual ParticipationState member.

## Ordering and validation
Consume this entry, the component patch and code-description patch. Add causal tests for
all four canonical values, exact old tokens/pickles, unknown values, actual registry row
output, strict family input and ACTIVE-only emission. Run the full participation and
mediator tests. Preserve current ownership, locks, lifecycle and unrelated changes.

## Rollback
Restore the enum values, exact legacy-read method and registry projection together.
Historical lowercase row/pickle data stays readable in either representation. The direct
enum .value and str output intentionally change to uppercase and must be release-noted.
<!-- END ENTRY: "Native participation enum canonical values" -->

<!-- BEGIN ENTRY: "Native admission reason canonical values" -->
## Scope and representation
AdmissionReason already is StrEnum. Set its five values to the exact uppercase member
names while keeping class path, names, order, reason identities and admission behavior.

## Legacy and diagnostic boundaries
Exactly the five old lowercase value strings remain accepted by the enum's narrow
missing-value reader, including actual old protocol-4 pickles. Canonical names are
accepted; mixed-case, whitespace and unknown values remain invalid. AdmissionResult's
diagnostic description retains its historic lowercase machine codes so logged/stored
evidence remains compatible. Direct enum value and JSON output intentionally become
uppercase and must be documented.

## Ordering, validation and rollback
Consume the architecture, component and control-flow entries. Test actual old pickles,
both value spellings, invalid inputs and real AdmissionResult description; then make the
single-file change. Run the complete native mediator unit directory. Rollback the value,
legacy reader and description projection together. No admission ownership, locks,
failure-policy behavior, numeric enum or other family is changed.
<!-- END ENTRY: "Native admission reason canonical values" -->

<!-- BEGIN ENTRY: "Native session status and outcome canonical values" -->
## Scope and representation
OutcomePolicy and SessionStatus already are StrEnum. Set their eight values to their exact
uppercase member names, retaining class paths, member names, order and distinct terminal
states. Keep failure policy, rollback ordering, ownership and locks unchanged.

## Legacy and public evidence
The eight exact lowercase historical by-value tokens remain readable through narrowly
listed enum missing-value readers, including actual old protocol-4 pickles. Mixed-case,
whitespace and unknown values remain invalid. Session descriptions and errors retain
their historical lowercase status/policy tokens; direct enum values and JSON intentionally
become uppercase. The old BROKEN.value test is updated to the selected value while keeping
the distinct-state assertion and adding an explicit legacy constructor check.

## Ordering, validation and rollback
Consume the architecture, component and control-flow entries. Test actual old pickles,
canonical/legacy tokens, real session snapshots, errors and unwind/leave-broken behavior.
Apply source and exact test-oracle changes together, then run the full native mediator
unit directory. Rollback source and test expectation together; do not change numeric enums,
other family values or ownership/cleanup contracts.
<!-- END ENTRY: "Native session status and outcome canonical values" -->
<!-- BEGIN ENTRY: "Native scope prefix canonical values" -->
## Scope and representation
ScopePrefix already is StrEnum. Set its three values to their exact uppercase member
names, retaining the module path, member names, order and scope hierarchy. No claim-mode,
transaction, lock, ownership or isolation policy is changed.

## Compatibility and claim keys
Exact historical lowercase by-value tokens and old protocol-4 pickles remain readable;
other enum families are not coerced by the fallback, and mixed-case, whitespace and unknown
values remain invalid. ScopeKey.world, frame, subsystem and is_world retain the exact
existing lowercase keys and behavior. Direct enum value and JSON output become uppercase.
A partial change that splits equal scope keys must not be accepted.

## Ordering, validation and rollback
Consume the architecture, component and control-flow entries. Test the real historical
pickles, canonical/legacy construction, literal scope-key outputs and actual admission
strategy/claim behavior. Apply value, legacy reader and every key projection together;
run the full native mediator unit directory. Roll back those changes together.
<!-- END ENTRY: "Native scope prefix canonical values" -->

<!-- BEGIN ENTRY: "AdmissionReason stable value correction" -->
## Superseding disposition
The earlier Native admission reason canonical values entry is superseded: the original
AdmissionReason explicitly promised stable lowercase values for logs and stored evidence.
Its source has been restored to the verified original. Keep those values and existing
by-value, pickle and verdict behavior unchanged pending a compatible owner disposition.

## Validation
Pin all five original values and their JSON, by-value and captured pickle behavior, plus
actual verdict descriptions. The corrected tests and full mediator directory must pass.
<!-- END ENTRY: "AdmissionReason stable value correction" -->

<!-- BEGIN ENTRY: "Native binding kind string migration" -->
## Scope and changed component
Convert only SpellBindingKind in binding_profile.py. The Spell Examination Profiles
component and Nexus descriptor publication remain in their existing ownership boundaries.
The parent story is #657 and the native executor is command_5.

## Interface and invariant
Keep module path, member names, order and profile identities. The four new StrEnum values
must exactly match CLASS, CALLABLE, INSTANCE and OTHER. The previous numeric by-value
inputs 1-4 must still construct the same members, including old numeric pickle payloads.
The old integer .value output changes to a string and must be documented as breaking;
unknown values remain invalid. Nexus publishes the same kind names. No ownership,
cleanup, locking, numeric exception or other enum is changed.

## Migration, validation and rollback
Consume this entry and component_patch_binding_kind.md, record the mapping, and capture
old pickle fixtures before changing the source. Causal tests check string names, numeric
inputs, pre-change protocol-4 pickle bytes and real profile-to-descriptor output. Run
existing affected profile, strategy and descriptor tests on final source. Review the exact
change, update the canonical maps, graph and release note, and rebuild assets last.
Roll back the enum base, values and legacy reader together if the migration is reverted.
External dynamic and numeric-output users remain UNKNOWN; do not claim universal safety.
<!-- END ENTRY: "Native binding kind string migration" -->
<!-- BEGIN ENTRY: "AdmissionReason exact-string owner correction" -->
## Owner-selected disposition
Mark corrected the prior keep-lowercase choice: all five AdmissionReason values MUST
match their uppercase member names exactly. This supersedes the stable-value hold above.

## Compatibility, ordering and rollback
Retain exact old lowercase by-value inputs and their captured protocol-4 pickle reads.
AdmissionResult.describe MUST continue emitting historical lowercase codes. Direct enum
.value, str and JSON change to uppercase and the release note MUST say so; unknown
external direct-value consumers are not promised the old output. No admission, claim,
wait, ownership or cleanup semantics change. Run causal and full mediator tests, update
canonical docs and assets. Roll back enum values, legacy reader and diagnostic
projection together if this change is reverted.
<!-- END ENTRY: "AdmissionReason exact-string owner correction" -->
<!-- BEGIN ENTRY: "Native incident enum string migration" -->
## Scope and interfaces
Convert IncidentSeverity and IncidentStatus under the DevOps incident component. Each
member's string value MUST match its existing lowercase name exactly. Keep both module
paths, names, order, manager ownership and status transitions. The original integer
values 1-4 MUST remain accepted by-value and in captured old pickle payloads.

## Invariants and limits
IncidentManager's status filter continues identity matching; a raw string or foreign
family does not become a matching status. Transfer failure reporting continues passing
severity members without changing transfer, cleanup or recovery behavior. Direct enum
.value changes from integer to string and new string/equality behavior is intentional;
release-note the break. External direct numeric consumers remain UNKNOWN.

## Ordering, validation and rollback
Consume this entry and the incident-component patch, record mapping, and run causal tests
against old source. Change both enum modules, then validate old pickle/numeric inputs,
canonical strings, real manager transitions/filters and relevant ownership-transfer tests.
Update maps, graph and release note; build assets last. Roll back the two bases, values
and legacy readers together. This entry is linked to native task and parent #657.
<!-- END ENTRY: "Native incident enum string migration" -->
<!-- BEGIN ENTRY: "Native system diagnostic severity string migration" -->
## Scope and interface
Convert SystemDiagnosticSeverity in the existing validation pipeline to StrEnum with
ERROR and WARNING as exact member-name values. Preserve names, order, module and
member identity. Historical numeric inputs 1 and 2 and old numeric pickle payloads
remain readable. Direct .value changes from integer to string and is release-noted.

## Boundary and validation
The validation system continues testing severity by member identity; error and warning
classification and resolution gating, diagnostics ownership and cleanup are unchanged.
Capture old pickle payloads; run causal tests on old source followed by the existing
system-diagnostic and validation tests on the changed source. Unknown external numeric
consumers remain UNKNOWN. Update canonical docs/graph and build assets last. Roll back
the enum base, exact values and legacy lookup together. Native task and parent #657 own
this work; no other component changes are selected by this entry.
<!-- END ENTRY: "Native system diagnostic severity string migration" -->
<!-- BEGIN ENTRY: "Native contract detail enum string migration" -->
## Scope and interface
Convert ContractTypes and DetailReason to StrEnum with values exactly matching their
existing names. Preserve module paths, member order and identities. Old integer
by-value inputs and captured old numeric pickle payloads remain readable. Direct
.value changes from integer to string and is documented as breaking.

## Cross-component invariants
Detail and IndexDetail continue to reject raw strings and foreign enum families.
Ward snapshots retain actual member identities for rollback. Crystallizer's contract
records keep the same plain .name projections for both endpoint and index details.
Grant, removal, transfer, ownership, locks and cleanup semantics do not change.

## Ordering, validation and rollback
Consume this entry and the component patch, map them to the ticket and add causal tests.
Validate old pickles/numeric inputs, exact names, strict Detail boundaries and real
contract recording/restoration alongside transfer and ward tests. Unknown external
numeric-output consumers remain UNKNOWN. Update canonical docs/graph and build assets
last. Roll back both enum bases, values and legacy readers together. Native task and
parent #657 retain their existing ownership.
<!-- END ENTRY: "Native contract detail enum string migration" -->
<!-- BEGIN ENTRY: "Native permission and policy enum string migration" -->
## Scope and interface
Convert Permissions and Policies to StrEnum, keeping their paths, names, order and
member identities. Each value exactly matches its existing lowercase name. Historic
numeric by-value inputs and captured old numeric pickle payloads remain readable.
Direct .value changes from integer to string and is release-noted.

## Authority and persistence invariants
Bind and ward entry points preserve same-family and plain-string handling and reject
foreign enum families in both cache orders. Permission ceilings and policy direction,
including blocked and whitelist rules, remain unchanged. Contract records continue
emitting plain member names; ownership, transfer, claims, locks and cleanup do not change.

## Ordering, validation and rollback
Consume this entry and the component patch, map source and tests, then run causal tests
on old source. Test old numeric pickles, exact strings, type-sensitive helper inputs,
actual policy/capability gates and real checkpoint restore. Unknown external numeric
output consumers are not qualified. Update canonical docs/graph and rebuild assets last.
Rollback the two enum bases, exact values and legacy readers together. This entry is
owned by the existing native task and parent #657.
<!-- END ENTRY: "Native permission and policy enum string migration" -->
<!-- BEGIN ENTRY: "Native existence and managed mode string migration" -->
## Scope and interface
Convert Existence and ManagedSpellMode to StrEnum, with values exactly matching existing
member names and unchanged module paths, order, bare str output and identities. Old
numeric by-value inputs and captured protocol-4 pickle payloads remain readable. The
new direct .value strings replace integer outputs and must be release-noted.

## Boundary and persistence invariants
Bind._normalize_managed_mode accepts its own members and plain names but MUST reject
foreign enum members before the str branch, retaining the documented TypeError for an
Existence member. Existing binding-manifest hashes and spell-crystal name fields stay
unchanged. Pool lifetimes, leasing, ownership, transfers and cleanup do not change.

## Order, validation and rollback
Consume architecture, component and control entries and map them in the native task.
Capture old fixtures, run causal tests, apply both enum changes and the Bind guard
coherently. Validate numeric/pickle reads, family inputs, binding hashes, actual bind,
managed pools and checkpoint restore. Unknown external numeric outputs remain UNKNOWN.
Update docs/graph and build assets last. Roll back both enums and the guard together.
<!-- END ENTRY: "Native existence and managed mode string migration" -->
<!-- BEGIN ENTRY: "Native frame system state string migration" -->
## Scope and interface
Convert SystemState to StrEnum with automatic and dynamic as exact member-name values.
Keep its module, names, order and member identities. Preserve old numeric by-value
inputs and captured old pickles; disclose that direct .value changes to string.

## Frame posture and persistence invariants
The frame configuration MUST check SystemState before primitive str when flattening a
record, so its dev-ops payload and system_state_name remain plain name strings. Typed
conversion and the automatic/dynamic link, transfer, bind and ownership gates stay.
No frame lifecycle, lock, record version or other ownership behavior changes.

## Ordering, validation and rollback
Consume and map architecture, component and control entries. Run causal tests on old
source, then apply the enum and frame projection together. Validate old numeric/pickle
inputs, typed/foreign-family conversion, actual in-memory and JSON frame recording,
checkpoint/replay and automatic/dynamic ownership gates. External numeric-output
consumers remain UNKNOWN. Update docs/graph; build assets last. Roll back enum and
projection together. Native task and parent #657 retain their existing ownership.
<!-- END ENTRY: "Native frame system state string migration" -->
<!-- BEGIN ENTRY: "Native SpellType string migration" -->
## Scope and interface
Convert SpellType to StrEnum with all fourteen values exactly equal to member names.
Preserve its module, names, order, existing bare str output and member identities.
Historical numeric inputs 1-14 and captured old pickle payloads remain readable.
Direct .value changes from integer to string and is release-noted.

## Classification and validation invariants
Bind continues selecting identical members from actual profile shapes. The resolution
matrix continues mapping names to the same class/callable/existing-object policies;
existence, ownership, lifecycle, persistence and cleanup behavior do not change.

## Order, validation and rollback
Consume this entry and its component patch; add causal tests for all old numeric
pickles and exact values. Validate Bind classification, the real matrix and relevant
registration/restore tests. Unknown external numeric-output consumers remain UNKNOWN.
Update canonical docs/graph and build assets last. Roll back base, values and legacy
reader together. Native task and parent #657 retain ownership.
<!-- END ENTRY: "Native SpellType string migration" -->
<!-- BEGIN ENTRY: "Native override target kind string migration" -->
## Scope and interface
Convert TargetSpecKind to StrEnum with PATH, UNIQUE and BROADCAST as exact values.
Preserve module path, member order and identities; numeric by-value inputs 1-3 and
captured old pickle payloads remain readable. Direct integer .value becomes a string
and is release-noted.

## Override and validation invariants
TargetSpec.parse retains its path, unique and broadcast grammar, resulting member
identities, parameter/path fields and malformed-key errors. OverrideKeyResolver keeps
its identity-based dispatch, target ranking, cuts and errors. No DAG, cache, ownership,
lock or lifecycle behavior changes.

## Ordering and rollback
Consume this entry and component patch, add causal tests, then change the enum only.
Test old numeric pickles, exact strings, parsing and real resolver/override behavior.
Unknown external numeric-output consumers remain UNKNOWN. Update docs/graph and build
assets last. Roll back base, values and legacy reader together under native task #657.
<!-- END ENTRY: "Native override target kind string migration" -->
<!-- BEGIN ENTRY: "Native CLEANED lifecycle enum string migration" -->
## Scope and representation
Convert SpellValidity, ConduitState and RecordedUnitState to StrEnum with values exactly
matching their existing member names, including CLEANED. Keep names, order, module paths
and terminal member identities. Direct numeric/lowercase CLEANED .value changes are
explicitly release-noted; old numeric and cleaned string inputs and old pickles remain
readable. ConduitState.__str__ retains its documented lowercase output.

## Persistence and family invariants
The native helper continues resolving case-insensitive names while rejecting foreign
enum families, including when equal canonical values warm the cache. PersistenceProfile
continues emitting state.name; old cleaned and canonical CLEANED major-5 records MUST
continue suppressing reconstruction in sequential and parallel drivers. Enabled/disabled
replay, unsupported-major refusal, state/ownership lifecycles and lock order stay.

## Ordering, validation and rollback
Consume and map this entry and component/control patches. Update the historical #656
base/direct-value test for the selected representation while retaining name order,
old-input mappings, foreign-family and lowercase rendering assertions. Run causal tests,
then both unit and real cached restore tests on final source. Unknown external direct
numeric consumers remain UNKNOWN. Update canonical docs and graph; build assets last.
Roll back all three bases/values/readers and test oracle together.
<!-- END ENTRY: "Native CLEANED lifecycle enum string migration" -->
<!-- BEGIN ENTRY: "Native state change reason string migration" -->
## Scope and representation
Convert SpellStateChangeReason to StrEnum with each value exactly its existing member
name, retaining its module, member names and ordering. Original numeric inputs 1-27
and old pickle payloads remain readable. Direct numeric .value and the default string
rendering change and are release-noted; external consumers remain UNKNOWN.

## Boundaries and validation
SpellSystemState retains reason member identity across transitions. Test all names,
legacy numeric values and captured old pickles, then run existing state-registry,
component and ownership-transfer controls. This entry does not migrate SpellState;
its set-based family-equality boundary needs separate qualification before that edit.
No lifecycle, lock, validity or ownership-transfer semantics are changed.

## Ordering and rollback
Map this entry and its component contract before the source change; run causal red,
then focused and native state/transfer tests. Update canonical maps and graph; build
assets last. Roll back the base, values and legacy reader as one change.
<!-- END ENTRY: "Native state change reason string migration" -->

<!-- BEGIN ENTRY: "Native parameter DI shape string migration" -->
## Scope and representation
Convert ParameterDIShape to StrEnum with exact member-name values, preserving names,
order, old numeric inputs and old pickles. Direct integer .value and default str
rendering change and are documented. SocketKind remains a separate unfinished family.

## Family and compiler boundaries
Requirements iteration, Phase 3 dependency-key selection and two Phase 4 strategies
recognize only the intended ParameterDIShape members through identity comparisons.
Equal raw strings or foreign StrEnum members remain non-matching as before. Phase 2's
subsequent identity dispatch already excludes foreign inputs. Normal DI, explicit
SpellMap/SpellContract, required holes, compiler data and lifecycle are unchanged.

## Validation and rollback
Map this entry to the enum and four consumers; run old pickle/name and family-boundary
regressions plus existing compiler/validation/component tests. Numeric SocketKind row
contracts and external consumers remain unqualified. Update maps/graph; build last.
Roll back this enum, its old-input reader and four identity checks together.
<!-- END ENTRY: "Native parameter DI shape string migration" -->

<!-- BEGIN ENTRY: "Native spell state flag string migration" -->
## Representation and ownership
Convert SpellState to exact-name StrEnum values, retaining old numeric 1-14 inputs
and old pickles. Its flag set accepts only SpellState members: same-valued strings
and change reasons cannot remove or impersonate an owned flag. None remains ignored.
Previously retained invalid foreign additions are now ignored and documented.

## Validation and rollback
Test old inputs, colliding reason/string reads and writes, valid flag transitions,
registry/risk behavior and ownership-transfer controls. No lifecycle, validity or
lock ordering changes. Update maps and graph; build assets last. Revert the enum,
legacy reader and typed flag handling together if rollback is required.
<!-- END ENTRY: "Native spell state flag string migration" -->

<!-- BEGIN ENTRY: "Native socket kind string and numeric rows" -->
## Representation and numeric boundary
Convert SocketKind to exact member-name StrEnum values. Its five historical integer
codes remain readable as enum inputs and in old pickles, and actual compiler/plan
rows continue emitting those same integer codes through an explicit projection.
Direct .value and default str rendering change and are release-noted.

## Consumer and persistence behavior
Phase 5/10 IR, Phase 8 topology signatures, site parameters and unresolved-input
plan checks keep their numeric codes. Other value-bearing objects and Phase 5's
missing-attribute repr fallback retain existing behavior. Fresh and cache-hit
site-plan construction must agree; old cached inputs stay readable.

## Validation and rollback
Run causal exact-name and numeric-row tests, then real compiler/site-plan/unresolved
and cached behavior tests. Preserve foreign-family dispatch. Update authored maps,
graph and release note; build assets last. Revert enum, projection and consumers
as one change if required.
<!-- END ENTRY: "Native socket kind string and numeric rows" -->

<!-- BEGIN ENTRY: "Aetheric mediator claim mode exact values" -->
## Enum and wire boundary
The mediator ClaimMode values become EXCLUSIVE, SHARED and INTENT, exactly their
names. Old x/s/ix values and pickle payloads stay readable. A dedicated projection
keeps x/s/ix in the frozen request, claim snapshots and blocking evidence. Direct
.value and str output change and are disclosed.

## Isolation and validation
Compatibility still requires the mediator's own members, with the existing matrix,
lock ordering and all-or-nothing claims. Test legacy and canonical inputs, pickles,
request round-trip, evidence and actual contended claims. The separate DevOps enum
and its consumers remain outside this slice. Update maps/graph and build assets last.
<!-- END ENTRY: "Aetheric mediator claim mode exact values" -->

<!-- BEGIN ENTRY: "Aetheric mediator transaction type exact values" -->
## Enum and reporting boundary
TransactionType values become the exact member names. Exact historical lowercase
values and old pickles stay readable. Historical lowercase transaction tokens
remain in request and staged descriptions, session snapshots, fact records,
strategy descriptions and missing-strategy errors. Direct value and string
rendering change and are disclosed.

## Query and validation
Activity-by-type accepts its existing lowercase string and enum member, and the
new exact canonical value; unknown strings still return no matches. Preserve
ownership, lock ordering, strategy routing and all other plane behavior. Test old
pickles, output tokens, filters and the mediator suite in both GIL modes. Update
maps and graph; rebuild assets last.
<!-- END ENTRY: "Aetheric mediator transaction type exact values" -->

<!-- BEGIN ENTRY: "DevOps claim mode exact values" -->
## Representation and acquisition
The DevOps ClaimMode values become EXCLUSIVE, SHARED and INTENT, exactly their
names. Old x/s/ix inputs and pickles remain readable. Explicit projections retain
x/s/ix in each strategy plan, built request and blocking evidence. Direct value
and string rendering change and are disclosed.

## Invariants and validation
Preserve the claim compatibility matrix, all-or-nothing acquisition, lock ordering,
freeze behavior and ownership. Test old tokens and pickles, actual plans, request
round-trip and contention, then affected unit/component and ownership-transfer
paths. Update maps and graph; build assets last.
<!-- END ENTRY: "DevOps claim mode exact values" -->

<!-- BEGIN ENTRY: "DevOps transaction type exact values" -->
## Representation and diagnostics
The sixteen ChangeTransactionType values become exact member names. Exact historical
lowercase inputs and old pickles remain readable. Existing fact-family, embargo
reason, failure and enum-typed activity reporting retain lowercase tokens. Direct
value and string rendering change and must be release-noted.

## Routing and validation
Builder and mediator normalize names as before. Preserve old raw bind/notch inputs
at the structural validator and the identity-specific notch behavior. Preserve all
claims, locks and ownership. Test legacy and canonical inputs, reporting, actual
admission and structural gate, then affected suites and ownership transfers.
Update maps and graph; rebuild assets last.
<!-- END ENTRY: "DevOps transaction type exact values" -->

<!-- BEGIN ENTRY: "Transaction ingress compatibility after exact values" -->
## Scope, components and interfaces
The native #657 task retains ChangeTransactionType exact member-name values. Repair the
Spellbook bind/end boundaries and Conduit posture, dispatch, close and contract-window checks.
A private, stateless transaction comparison projection maps this enum and exact canonical
plain strings to the original lowercase tokens; already-lowercase and unrecognized inputs
retain their existing values. This does not alter enum .value, equality or hashing.

| Component | Contract |
| --- | --- |
| DevOps transaction vocabulary | Original and canonical forms compare by the same transaction token |
| Spellbook Core | Bind windows open, join and close with equivalent recognized forms |
| Conduit Runtime | Posture gates, strategy dispatch and link-family contract checks recognize those forms |

## Invariants, rollout and rollback
Do not change request objects, claim ownership, nested-session lifecycle, locks, cleanup,
transfer stewardship, committed records, or the existing bind-end success propagation.
Unknown and differently cased raw input retains its existing comparison treatment.
Create focused regression tests first, then apply the projection and both boundary repairs
as one source change. Roll back the helper and both callers together if the change is reverted.

## Validation, coverage and unknowns
The native task and parent #657 own this contract. Verify lowercase, exact-name and member
inputs, cross-form matching and mismatches; dynamic/disable gates; real bind and link/contract
windows; and the previously red ownership-transfer selection in both GIL modes. Existing
external direct-value consumers remain UNKNOWN. Update source/test maps and build assets last.
<!-- END ENTRY: "Transaction ingress compatibility after exact values" -->

<!-- BEGIN ENTRY: "Canonical transaction strings retain the structural commit gate" -->
## Boundary and invariant
Direct mediator ingress accepts string transaction kinds and stores the original request.
The new exact BIND and NOTCH values MUST enter the same structural commit gate as their
historical lowercase string values; the BIND enum member remains gated as before.
A plain NOTCH string retains the historical raw-notch behavior. Only the actual NOTCH
member takes the existing compiled-member shortcut. Unknown and mixed-case raw inputs,
foreign-family treatment, request identity, claims, locks and transaction ownership stay.

## Scope, validation and rollback
Change only ChangeControlManager's structural-kind comparison and its regression test.
First reproduce direct mediator commits with old string, exact .value and enum member;
then assert canonical and legacy bind/notch paths, enum-notch identity, and mixed-case
controls. Re-run affected DevOps, Spellbook, contract and ownership-transfer tests in both
GIL modes. Update canonical source/test maps and graph, then rebuild assets last. Revert
this comparison and its test oracle together if the correction is rolled back.
<!-- END ENTRY: "Canonical transaction strings retain the structural commit gate" -->
