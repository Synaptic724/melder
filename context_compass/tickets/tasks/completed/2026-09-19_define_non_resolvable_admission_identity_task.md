# Task: Define non-resolvable target admission and version identity

## Completion
- Completed: 2026-09-20T00:25:59Z
- Summary: Defined target admission and capability fingerprints while preserving the owner-selected existing version rules.
- Acceptance: Owner requested turn-in, then required two repairs first; both are verified.

## Metadata
- Task ID: TASK-2026-09-19-define-non-resolvable-admission-identity
- Story: STORY-2026-09-19-discoverable-registration-contract-discovery
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T19:01:16Z
- Updated: 2026-09-20T00:25:59Z

## Objective
Finish the next S1 boundary: determine which non-resolvable definitions can be admitted and how their
capability and source revisions are identified without breaking current binding/restore contracts.

## Ticket Contract
- ENTRY_GATE: Required re-entry is complete; parent epic/S1 and the socket/selection results are read;
  attention_board routes this task. OVERRIDE_REQUIRED is the owner-selected internal category name.
- EXECUTION_BOUNDARY: Bind admission and fingerprint inputs, Spell metadata, SpellCrystal custody,
  and the minimal MutationResearch identity path needed to distinguish registration from source revision.
  Source investigation and design only; no feature implementation or test-file creation.
- DEPENDENCIES: Default-True per-Spell resolvable policy, OVERRIDE_REQUIRED meaning, and selection table.
- EXIT_GATE: Supported target-family table, omitted/True/False fingerprint policy, body-only revision
  findings, scoped regression cases and S2/S5/S6 implications are ready for S1 discussion.
- FAILURE_ESCALATION: Name gaps in actual version/custody behavior. Do not silently redesign source
  identity, expand instance ownership, or bypass the internal-bind guard.

## Scope Boundaries
- In scope: class/abstract/Protocol admission questions and existing fingerprint/custody/research keys.
- Out of scope: ownership redesign, arbitrary live-instance migration, new global registries, runtime patching.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner-authorized turn-in after delivered scope and reported failure repairs passed.

## Required Reading Before Work
1. Current decisions and latest notes:
   - `tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md`
   - `tickets/stories/completed/2026-09-19_discoverable_registration_contract_discovery_story.md`
   - `tickets/tasks/completed/2026-09-19_define_caller_supplied_socket_contract_task.md`
   - `tickets/tasks/completed/2026-09-19_define_discoverable_registration_selection_task.md`
2. Use verified component indexes: Binding Pipeline, Spell Examination Profiles, Crystallizer Root,
   MutationResearch Root and ResearchSet. Slice only the branch needed for the current question.
3. Read the actual admission/fingerprint unit and its direct profile/identity callees:
   - `src/melder/aether/spellbook/bind/bind.py` — _bind_logic, spell_id_inspector, sha256_profile.
   - `src/melder/aether/spellbook/spell.py` — policy storage, binding metadata and version identity.
   - `src/melder/aether/spellbook/spell_compiler/spell_examiner/profiles/binding_profile.py`
   - `src/melder/aether/spellbook/resolution_style_matrix.py`
   - `src/melder/utilities/helpers/id_builder.py`
4. Follow identity into custody and world-entry deduplication:
   - `src/melder/crystallizer/crystals/spell_crystal.py`
   - `src/melder/mutation_research/mutation_research.py` — record_world_entry and material acquisition.
   - `src/melder/mutation_research/research_set/research_node.py`
   - `src/melder/mutation_research/research_set/research_set.py` — registration/identity/ancestry callees.
   Follow crystal-analysis callees only if they decide the body/source revision question.
5. Existing semantic cache/version checks are the mechanism to reuse; read their exact consumers when
   defining compatibility. Do not invent an alternative invalidation framework.
6. Before designing executable regressions, use test indexes and read the relevant Bind fingerprint,
   Protocol admission, SpellCrystal and research identity tests. Reuse unchanged reads from this session.

## Steps / Checklist
- [x] Trace actual module/Protocol/class/callable/existing-object admission and profile construction.
- [x] Recommend initial False target families with a reason for each inclusion/exclusion.
- [x] Trace all inputs to the binding SHA and inspector parity.
- [x] Specify omitted=True compatibility and explicit False identity discrimination.
- [x] Trace SpellCrystal and research keys for a body-only source change with the same signature.
- [x] Separate registration identity, source/module identity and graph relationship version requirements.
- [x] Record S2/S5/S6 effects and remaining owner choices before implementation.

## Deliverables
- Target-family admission table.
- Source-backed fingerprint/custody identity decision record and first regression cases.
- S1 handoff sufficient to create implementation patch contracts without guessing these boundaries.

## Owner Decision: Preserve Existing Version Rules

The owner selected Keep existing version rules in the explicit version-policy question. This feature
does not introduce automatic source-body revisions or redefine the normal bind SHA as a source hash.
New definition versions use the existing module/binding/version workflow. A body-only edit retaining
the same hashed identity and structure is not a new binding/research version.

This is consistent with the actual code:
- Bind's v4 class fingerprint consumes names, module, bases/MRO, annotation keys, method names,
  constructor signature and binding metadata. It does not consume arbitrary method bodies.
- SpellCrystal uses spell_id as custody identity while retaining module/source analysis separately.
- ResearchNode uses spell_id as version identity; module_source_sha256 is an optional annotation.
- ResearchSet.record_world_entry returns None for a resident spell_id before checking source metadata.
- Nexus materialization accepts an explicit module name. Using a distinct module identity changes
  the class profile and therefore its binding SHA. Replacing the source under the same module name
  does not create an independent source-version key automatically.

## Proposed Admission Contract

Keep resolvable as a capability on the selected registration, not another SpellType or Existence.
Avoid arbitrary class-only restrictions on a flag attached to general binding APIs.

| Target | Omitted / True | False recommendation |
| --- | --- | --- |
| Ordinary class / application ABC | Existing admission and resolution rules | Admit and reflect; describe without requiring construction. |
| Application Protocol definition | Keep the current concrete-target refusal | Permit explicitly non-resolvable class metadata; never construct the Protocol. |
| Existing valid function/method/lambda binding | Existing callable rules | Same binding eligibility/naming/unique-only rules; prohibit resolution/invocation through Melder. |
| Existing valid instance binding | Existing unique-only model | Same registration/reference/lifecycle model; prohibit resolution and automatic injection. |
| Module or primitive target | Keep existing refusal | Keep existing refusal; this is not a new module-registration API. |
| Melder kernel target in INTERNAL_MANIFEST | Keep existing refusal | Keep existing refusal; capability does not bypass registration protection. |

Supporting False on a prebuilt reference does not introduce new ownership or lifetime semantics.
Existing Creations registration/cleanup policy stays as it is; S4 must block the existing-object
fast-return paths just as it blocks class construction. The earlier ownership redesign remains parked.
The Protocol False admission exception is a concrete recommendation requiring a real profile/compiler
regression; source shows the raw class profile can reflect it without invoking a constructor, but this
discovery has not executed the complete new path.

Keep all ordinary binding validators that are independent of construction (names, accepted input type,
uniqueness and the supported Protocol spellframe member contract). Skip only construction obligations
for False roots; do not blanket-skip reflection/registration validation.

## Proposed Fingerprint and Storage Contract

1. Add native resolvable: bool = True to binding facades, Bind, inspector/hash and Spell construction.
   Validate the public bool once at shared admission and on the independent inspector/hash entry.
2. Omitted and explicit True preserve the existing v4-binding input sequence and resulting SHA exactly.
   Do not append a True token to every existing binding or globally advance the fingerprint prefix.
3. False uses a distinct domain prefix, proposed v4-binding-non-resolvable, with the SAME remaining
   profile/binding inputs and ordering. This separates capability without changing default identities
   or introducing new source reads. Verify inspector parity with the same effective name/frame/binding,
   existence and already-resolved disposal list.
4. Store the native bool on Spell independently of metadata, activity, resolution_required and
   resolution_complete. It is immutable for that bound version, with a read-only property and normal
   cleanup. A new mode is a different version, not a live setter on the current Spell.
5. Generic metadata keys must not impersonate this native field. Current Spell.__init__ accepts unknown
   kwargs into metadata; until implementation, passing resolvable=False that way does not enforce anything.
6. Preserve signature uniqueness and selected/parked behavior from the selection task. A new False SHA
   does not authorize another active registration at the same key.
7. Persist the flag explicitly in SpellCrystal/replay values and forward it through bind_inactive/graft.
   Legacy absence means True; an explicit recorded False must remain False.
8. Use existing compiled-cache semantic-version checks and input signatures for changed executable
   schemas. Preserving True IDs does not justify reusing an incompatible old executable payload.
   S6 must also use the existing record compatibility mechanism so an older reader cannot silently
   discard False and restore a resolvable registration.

## Versioning and Graph Boundaries

No separate automatic source-revision registry is added. For a fresh version, use existing explicit
module/binding identity and index staging/promotion, retaining recorded custody per the resulting
spell_id. Use existing research organization snapshots for organization changes.

S5 must preserve the difference between declared-type references, selected runtime targets and research
organization edges. This pass does not claim every possible architectural relationship already has
a graph storage owner. Specify any new relationship payload inside S5's graph contract, using existing
version rules rather than making a source-body edit silently change all graph identities.

No-source or unreplayable targets retain the existing honest custody/restore limitations. An in-memory
reference is not permission to invent file/source text or to promise reconstruction of supplied instances.

## Initial Regression Design

Tests are designed, not created or executed in this discovery.

- S2: real bind and inspector agree for omitted/True/False with identical effective inputs; omitted/True
  reproduce a fixed legacy fingerprint fixture and False differs; invalid non-bool inputs refuse.
- S2: the flag is native and does not leak into metadata; direct/decorator/fluent/Conduit/inactive paths
  retain it without carrying it into the next bind.
- S2/S3: application ABC and Protocol False targets are inspectable without construction; Protocol True,
  kernel targets, modules and primitives retain their intended refusal boundaries.
- S4: test False across class, callable and existing-object fast paths; existing unique-only/naming and
  disposal behavior remains unchanged. A supplied override does not grant new ownership.
- S2/S5: same-identity body-only changes retain the existing class-hash behavior; a distinct module/bind
  version produces a distinct identity and research entry. Do not assert automatic body-only versioning.
- S6: missing legacy flag becomes True; False round-trips through capture, restore, staged members and
  graft; old executable schemas miss using normal version checks; unsupported readers cannot enable False.

Existing test anchors read for compatibility intent:
- `tests/unit/melder/spellbook/bind/test_bind.py` constructor-signature/source-preview hash cases.
- The selection task's inactive/lookup/descriptor tests and the socket task's default/override tests.
Implementation must add actual new-mode runtime cases rather than claiming those existing tests prove it.

## Files / Paths Impacted
- This task and parent S1/epic plus relevant S2/S5/S6 planning records and routing boards.
- No production or test files during this discovery task.

## Validation
- Runtime tests: Not run. Source investigation and proposed regression design are complete.
- Check source citations and ticket/board agreement before handoff.

## Risks / Rollback Notes
- Permitting Protocol targets under False may require changing an intentional admission refusal.
- Adding a bool to every fingerprint might move legacy True identities unnecessarily.
- Stable bind SHA may not represent body-only or graph-only revisions; this is UNKNOWN until traced.
- Existing objects are a separate parked epic; admitting their references must not become implicit scope.

## Applicable Anti-Patterns
- [x] No treating a metadata kwarg as an implemented native capability.
- [x] No claim that structural identity equals source history without source evidence.
- [x] No new lifetime, alternate cache protocol or guard bypass.

## Done Checklist
- [x] Source findings and recommendations recorded.
- [x] Initial regression cases and downstream implications prepared.
- [x] S1/epic and story requirements synchronized.
- [x] Owner discussion/acceptance recorded before task closure.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: target admission, bind SHA, crystal custody, research deduplication and source revisions.
- IF_UNKNOWN: none

## Noting Behavior
Complete one source unit, then record evidence, impact and one NEXT before another investigation tranche.

## Notes
- DATETIME: 2026-09-19T19:01:16Z
  TYPE: PLAN
  CLAIM: The owner selected OVERRIDE_REQUIRED and continued S1. Socket propagation and selection
    results are recorded. Admission/fingerprint/custody identity is the next independent boundary;
    class/Protocol support and body-only revision identity remain UNKNOWN until this trace.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-19_define_discoverable_registration_selection_task.md
  IMPACT: S2 transport and S5/S6 history/restore will share a source-grounded identity contract.
  NEXT: Read Bind._bind_logic and sha256_profile with the profile types they consume.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T19:07:20Z
  TYPE: FACT
  CLAIM: Bind explicitly refuses modules and Protocol targets before profiling. It has no separate
    abstract-class refusal; class profiles carry class names/MRO/annotation keys/method names and
    constructor signature. The v4-binding class SHA hashes those shape fields plus name/frame/binding,
    existence and ordered disposal names, not ordinary method bodies or annotation values.
    Generic kwargs are forwarded to Spell metadata after hashing. Inspector and bind share sha256_profile.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:333-537
  - src/melder/aether/spellbook/bind/bind.py:540-698
  - src/melder/aether/spellbook/bind/bind.py:701-850
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/profiles/binding_profile.py:64-186
  IMPACT: resolvable must be a native fingerprint input, not merely a metadata kwarg. A body-only
    class edit with all hashed identity/shape fields unchanged cannot acquire a new ID from this
    function alone. This does not yet prove a research-versioning gap: synthetic-module identity
    or a separate source-revision mechanism may distinguish versions; trace that before deciding.
  NEXT: Follow SpellCrystal identity/material and MutationResearch world-entry deduplication.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T19:16:41Z
  TYPE: FACT
  CLAIM: SpellCrystal adopts spell.spell_id as custody identity. ResearchSet.record_world_entry checks
    residence by spell_id before considering optional module_source_sha256, returning None for a
    repeated identity. The root automatic seam does not supply that optional source SHA. Nexus
    materialize_codegen requires a caller-chosen module_name, computes a source hash, then publishes
    that module; SyntheticModule's registry replaces an existing object under the same name. There
    is no automatically minted separate source-revision identity in these paths.
  EVIDENCE:
  - src/melder/crystallizer/crystals/spell_crystal.py:143-342
  - src/melder/mutation_research/mutation_research.py:1234-1312
  - src/melder/mutation_research/research_set/research_set.py:1610-1747
  - src/melder/mutation_research/research_set/research_node.py:79-169
  - src/melder/nexus/rift/command_system/codegen_command_system.py:740-890
  - src/melder/crystallizer/synthetic_module.py:977-1018
  IMPACT: A fresh materialized module identity changes the class profile module field and thus the
    bind SHA; rematerializing a same-named module with only method-body changes does not itself mint
    a distinct binding/research version. The existing workflow must use a distinct version identity.
  NEXT: Apply the owner's version-policy answer to the admission/identity proposal and S5/S6 scope.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T19:16:41Z
  TYPE: DECISION
  CLAIM: Owner chose Keep existing version rules in the explicit version-policy question. Preserve
    normal binding/version semantics; do not introduce automatic body-only source revisions for
    False definitions. Their new versions use existing module/binding identity changes and research
    organization. Recommend leaving omitted/True fingerprints on v4-binding and using a separate
    domain prefix for False, with inspector/bind parity and normal record/cache compatibility gates.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:586-698
  - src/melder/mutation_research/research_set/research_set.py:1610-1747
  IMPACT: The feature extends capability and graph access without redesigning version identity.
    Same-identity body edits are not separate version events; this is an explicit retained behavior.
  NEXT: Finalize the supported-target and fingerprint tables, then hand S1 results to implementation stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T19:19:08Z
  TYPE: PLAN
  CLAIM: Admission and fingerprint recommendations are now concrete. Apply False uniformly to
    currently valid binding families with their existing lifetime/naming rules; add the narrow
    Protocol-definition exception only for False. Preserve v4-binding for omitted/True and use a
    distinct False prefix. Owner chose existing version rules, so no automatic source-body identity
    work is required. Native Spell storage and crystal/replay/cache compatibility are explicit.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:333-850
  - src/melder/aether/spellbook/spell.py:237-502
  - src/melder/aether/spellbook/spell.py:505-610
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:43-137
  - tests/unit/melder/spellbook/bind/test_bind.py:654-665
  IMPACT: S1 can hand a concrete capability/selection/identity contract to implementation. Target-family
    and descriptor details are recorded recommendations; no runtime feature or new test has landed.
  NEXT: Consolidate S1 decisions and prepare the S2 registration implementation task and patch contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T19:27:53Z
  TYPE: FACT
  CLAIM: The owner's retained-version decision is propagated to the epic and S1/S2/S5/S6/S7 records.
    S2 now has a concrete ready registration task and board route. The source/test trees remain
    unchanged; runtime tests and builds were not run. Discovery records preserve evidence and
    implementation still starts with required patch contracts and focused regressions.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-19_implement_resolvable_registration_modifier_task.md:13-93
  - attention_board.md:85-85
  IMPACT: Re-entry can start S2 without repeating completed selection/fingerprint discovery.
  NEXT: Prepare the S2 patch contracts and regression baseline in the successor task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T00:25:59Z
  TYPE: DECISION
  CLAIM: Owner-authorized feature turn-in is complete for this record. Both later reported failures
    are repaired: crystal test-double capability and current-run local cancellation forwarding.
    This acceptance retains ordinary Python errors, existing version rules and documented limits.
  EVIDENCE:
  - artifacts/non_resolvable_graph_replay_20260919/validation.md:1-78
  - artifacts/non_resolvable_followup_20260919/validation.md:1-50
  IMPACT: Record is done; validation evidence is retained and promoted patch contracts are archived.
  NEXT: none; reopen only for a new owner-requested change or new failure evidence.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
CLOSED at 2026-09-20T00:25:59Z. Defined target admission and capability fingerprints while preserving the owner-selected existing version rules.
Final evidence and limits are in the graph/replay and follow-up validation artifacts.
No next implementation step remains in this accepted record.

### Historical pre-closure handoff
Review-ready. Owner retained existing version rules. The tables above recommend uniform capability
across currently valid binding kinds, a False-only Protocol-definition exception, immutable native
Spell storage, unchanged True fingerprints and a distinct False prefix. No automatic body-only source
versioning or existing-object ownership redesign. S2/S3/S4/S5/S6 consume these recorded boundaries.
S1 is consolidated. Next: tickets/tasks/completed/2026-09-19_implement_resolvable_registration_modifier_task.md,
starting with its patch contracts and regressions. No runtime or test edits.
Complete ContextCompass REONBOARD after compaction, then read these current results before source.
