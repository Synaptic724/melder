# Task: Trace non-resolvable registration ownership and consumer socket handling

## Metadata
- Task ID: TASK-2026-09-19-trace-discoverable-registration-compiler-boundary
- Story: STORY-2026-09-19-discoverable-registration-contract-discovery
- Status: review
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T16:34:27Z
- Updated: 2026-09-19T19:05:38Z

## Objective
Determine where non-resolution mode belongs and where a selected discovery-only dependency becomes
a required caller-supplied socket, preserving the graph relationship. Produce a decision table, not code.

## Ticket Contract
- ENTRY_GATE: Parent epic/story and predecessor PLAIN findings read; this task is the active board route.
- EXECUTION_BOUNDARY: Read bind metadata/identity, Spell/SpellIndex, Phase 1-3, and immediate compiler
  scheduling/validation callers. Record results in this task and synthesize into the story.
- DEPENDENCIES: Parent epic's owner direction and source read map; earlier default-precedence contract.
- EXIT_GATE: Mode ownership and matching options have source evidence, an explicit recommendation,
  unresolved choices, and minimal future regression scenarios for owner discussion.
- FAILURE_ESCALATION: Stop at a product decision that source cannot settle; record the alternatives
  instead of introducing a flag/enum or changing behavior during investigation.

## Scope Boundaries
- In scope: one selected registration's path from bind to compiler scheduling and consumer Phase 3 lookup.
- Out of scope: runtime edits, test-file creation/execution, full Nexus/restore redesign, instance lifetimes.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Entry points, mode ownership, fingerprints, matching, scheduling, validation,
  socket records and concrete meld doors are traced. The proposed change map is ready for discussion.

## Steps / Checklist
- [x] Read parent epic, story, and predecessor Notes covering the latest owner direction and PLAIN.
- [x] Use current src_components/index and source graph slices for the binding/compiler surfaces.
- [x] Read Bind._bind_logic, relevant Spell/SpellIndex metadata, and identity construction completely.
- [x] Trace target selection for a concrete annotation, abstract spellframe, and explicit binding target.
- [x] Identify the earliest point that knows which registration was selected and whether it may resolve.
- [x] Trace where discovery-only roots would otherwise enter constructor validation and plan generation.
- [x] Compare the original PLAIN proposal against an explicit resolved supplied-input category; do not choose
  solely from enum naming. State what each downstream consumer needs.
- [x] Write a semantic table for direct/non-resolvable, selected provider, required/defaulted consumer,
  unresolved annotation, and nested caller-supplied cases. Keep untraced branches UNKNOWN.
- [x] Write the minimum future regression cases and prepare the result for discussion.
- [x] Append findings after each complete source unit before continuing investigation.

## Deliverables
- Mode ownership/identity recommendation with alternatives and evidence.
- Candidate-selection-to-socket call path and graph metadata requirements.
- First regression matrix and explicit unresolved decisions.

## Required Source Routes
- `system_docs/src_components_index.md`: Binding Pipeline, DI Descriptors, SpellCompiler and Validation.
- `src/melder/aether/spellbook/bind/bind.py`: Bind._bind_logic and identity inputs.
- `src/melder/aether/spellbook/spell.py`: constructor metadata, compiler ownership, requirement lifecycle.
- `src/melder/aether/spellbook/bind/spell_index.py`: selected member and immutable index identity.
- `src/melder/aether/spellbook/resolution_style_matrix.py`: allowed registration families/lifetimes.
- `src/melder/aether/spellbook/spellbook.py`: bind/bind_inactive and conjure entry.
- `src/melder/aether/spellbook/spellbook_creation_system.py`: root selection and phase admission.
- `src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py`.
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py` and `compiler_phase_3.py`.
- Phase 3 candidate index/resolvers and required validation callers reached from those source methods.
Use the parent epic for subsequent Nexus/research/persistence reads; do not preload them in this task.

## Files / Paths Impacted
- This task's Notes and Context / Handoff Summary.
- Parent story/epic decision summaries and coordination boards as the discovery state changes.
- No production or test source files.

## Proposed Minimal Modifier
This is a source-grounded proposal, not an applied patch. Keep the public contract to one keyword:
`resolvable: bool = True` on both bind and bind_inactive. Omitted and explicit True mean existing
resolution behavior; explicit False declares a visible/versioned registration with no resolution.

### API and storage
- `Spellbook.bind` and `Spellbook.bind_inactive`: consume the keyword explicitly and forward it.
- `Conduit.bind` and `Conduit.bind_inactive`: mirror the same keyword/default and delegate normally.
- `Bind.bind` and `Bind._bind_logic`: carry the bool through direct/decorator paths, validate it
  once at shared admission, and pass it to Spell and identity calculation.
- `Spell.__init__` / slots / cleanup: store the bool as bind-time policy on the individual Spell.
  Recommend no live setter; a policy change belongs to a new registration/version.
- Leave SpellIndex responsible for membership/selection. Do not reuse `_active`, `SpellType`,
  Existence, Permissions, `resolution_required`, or `resolution_complete` for this capability.
- SpellBinder's existing bind/with_kwargs/finalize channel can forward the keyword and already
  resets it between registrations. A separate fluent setter is not required for the first slice.

### Identity and compatibility
- `Bind.sha256_profile` and `Bind.spell_id_inspector` must accept the same bool/default and encode
  the resolution policy consistently. Generic metadata kwargs are not fingerprint inputs today.
- Resolve schema/legacy-SHA policy before editing; equal omitted/True inputs must produce equal IDs,
  while otherwise-identical False/True versions cannot accidentally share an executable cache identity.
- Keep canonical name keys and existing uniqueness rules. A new mode/SHA does not create another
  binding-name slot. A discoverable Base/default and an implementation bound as Base/default both
  normalize to the same key; existing explicit names can distinguish coexisting registrations.
- `bind_inactive(..., resolvable=True)` stays parked. Inactive selection does not imply False mode.

### Selection, sockets and compilation
- Preserve Phase 1 signature facts and Phase 2 descriptive annotation metadata.
- Phase 3 is the selected-registration boundary: evaluate resolvable provider matches separately
  from discovery-only matches before applying provider ambiguity/missing-candidate policy.
- For an input whose selected target is non-resolvable, emit an explicit resolved caller-supplied
  category while retaining the descriptive target and original declaration. This replaces the earlier
  preference for PLAIN lowering. The owner subsequently selected OVERRIDE_REQUIRED; see the socket task.
- Current requirement/symbolic records expose read-only shape properties and topology is frozen.
  Do not poke `_di_shape` in place. Build an explicit resolved socket result and make downstream
  validation/planning consume that result consistently.
- Phase-4 BindingResolutionCycleStrategy currently derives edges from Phase-1 shapes, independently
  of Phase 3. It must not reconstruct an injection edge for a caller-supplied dependency.
- Retain descriptive inspection for a non-resolvable root, but do not require its constructor
  dependencies to resolve or schedule its construction plan. Coordinate structural handling,
  Phase-5 executable roots and `_is_spell_plan_phase_eligible`; filtering Phase 8 alone is insufficient.

### Direct execution and later epic work
- ConduitMeld/SpellSpaceMeld execution must refuse the mode before hooks, creation or reuse. Include
  meld_existing_spell. Keep raw registration lookup available for graph discovery.
- Do not hide the restriction inside `_ensure_lineage_resolvable`: book-level risk policy can skip it.
  Fast doors, mode changes via selected versions, and cache hydration require explicit qualification.
- Nested construction is prevented by the compiler's supplied-input policy, not by assuming all
  dependency execution calls the top-level Meld method.
- Carry the bool through SpellCrystal capture/describe and active/staged restore/graft. Legacy
  records without it should retain the old resolvable meaning; exact schema changes belong to S5.
- Nexus publication/research views must expose the capability and descriptive target relationships.
  These remain required epic work; this first trace does not claim their schema is implemented.

## Semantic Table for Discussion
| Case | Proposed behavior | State of decision |
| --- | --- | --- |
| bind omits modifier or passes True | Existing resolvable registration | Owner-directed |
| bind passes False | Selected graph-visible definition; direct meld refuses | Owner direction |
| bind_inactive omits modifier | Parked resolvable version; eligible only after selection | Derived from independent axes |
| bind_inactive passes False | Parked definition; selection does not turn mode True | Proposed per-version policy |
| Required input has one selected False target | Caller-supplied value required when constructing | Owner direction; metadata design pending |
| Ordinary explicit Python default | Preserve default unless overridden | Existing accepted contract |
| One resolvable provider plus discoverable frame definition | Use provider; keep descriptive definition link | Proposed matching policy |
| Multiple resolvable providers | Preserve existing ambiguity rules | Compatibility recommendation |
| No registered target at all | Preserve current missing-provider behavior | Compatibility recommendation |
| Explicit SpellMap/SpellContract, collections, multiple False matches | Settle exact selection/supply policy separately | OPEN |
| Optional annotation without a default | Do not silently turn omission into a default None | Proposed supplied-input rule |
| Consumer already exists in its scope | Follow existing reuse semantics | Compatibility requirement |

## Minimum Future Regressions
- Default omission equals explicit True for both APIs; False is stored and identity-distinct.
- Bind and bind_inactive forward through Conduit; successive fluent registrations do not leak False.
- A registered abstract/helper False target remains visible and does not execute its constructor.
- Conjure handles a False target whose own constructor references unregistered helpers.
- Direct id/name/frame and spellspace meld refuse even when the book skips ordinary validation.
- Required consumer input preserves target metadata and accepts the supplied object by identity;
  missing input fails usefully while ordinary defaults continue working.
- A resolvable implementation of a discoverable abstract frame remains selectable under normal key rules.
- Park/notch and serialized cache/restore paths preserve mode; nested construction never recreates the target.
These are proposed tests. Generalized/deep override behavior and a full mode round trip remain unexecuted.

## Decisions Still Needed Before Implementation
- Exact resolved-socket metadata owner and the way Phase 4 consumes its caller-supplied policy.
- Fingerprint schema handling for legacy True registrations and accepted record compatibility.
- Initial False target families (classes versus Protocol/module/existing-instance targets).
- Explicit descriptor and collection semantics; no blanket policy change is inferred for those cases.

## Validation
- Tests: Not run. No feature implementation exists.
- Verify source claims by full method/call-path reads; search output is navigation only.
- Before later test authoring, read the test architecture/component documents and relevant fixtures.

## Risks / Rollback Notes
- A mode on a type annotation can incorrectly suppress a different resolvable registration.
- A non-resolvable root can still enter compile/validation unless admission distinguishes its role.
- PLAIN preserves an annotation but currently omits a concrete graph target in Phase 3.
- Do not infer generalized/cache behavior from the already-inspected solo invocation helper.

## Applicable Anti-Patterns
- [ ] No unsupported claim that the implementation is just a flag.
- [ ] No lost graph edge to make resolution pass.
- [ ] No None/default substitution for a required input.
- [ ] No coding before the current design question is answered.

## Done Checklist
- [x] Required source paths read for this bounded question.
- [x] Decision table and candidate recommendation recorded.
- [x] Evidence/UNKNOWN boundaries and first regression scenarios recorded.
- [ ] Owner discussion completed; story and board reflect the result.

## Dependencies / Related Work
- `tickets/epics/2026-09-19_discoverable_non_resolvable_registrations_epic.md`
- `tickets/stories/2026-09-19_discoverable_registration_contract_discovery_story.md`
- `tickets/tasks/2026-09-19_understand_nexus_crystallizer_spellbook_task.md`

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: registration mode, identity, selected target, supplied-input socket, compile admission.
- IF_UNKNOWN: none

## Noting Behavior
- Complete a method/call-path read unit, then record findings with evidence and one next action.
- Distinguish confirmed current behavior from the proposed new contract.

## Notes
- DATETIME: 2026-09-19T16:34:27Z
  TYPE: PLAN
  CLAIM: Discovery begins with mode ownership and selected-target handling. Earlier work established
    that PLAIN preserves an annotated symbolic socket but produces no concrete dependency edge.
    That fact constrains the design; it does not prove that the new mode can skip all other changes.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py:49-184
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:545-898
  IMPACT: The next pass can start from a concrete boundary instead of repeating broad orientation.
  NEXT: Read Bind._bind_logic and the Spell/SpellIndex identity owners, then document mode placement options.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T16:45:32Z
  TYPE: DECISION
  CLAIM: Owner directs a simple modifier on bind and bind_inactive; omission must keep bindings
    resolvable. Investigate the working signature resolvable: bool = True, including forwarding
    APIs and per-version storage. Inactive selection and non-resolution mode are independent axes.
    This turn asks how to do it; the current task remains source discovery, not implementation.
  EVIDENCE: Owner directive: "add the modifer into bind and bind_inactive" and "bind defautls to
    the resolvable"; predecessor analysis remains linked in Dependencies / Related Work.
  IMPACT: Public direction is narrowed; avoid a separate registration framework or new lifecycle enum.
  NEXT: Trace both entry points through Bind, fingerprint construction, Spell and SpellIndex.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T16:48:25Z
  TYPE: FACT
  CLAIM: Bind.bind forwards into _bind_logic for direct/decorator paths; _bind_logic computes the
    fingerprint, creates SpellIndex, validates policy, and constructs Spell. sha256_profile currently
    includes structural profile/name/frame/binding/existence/disposal values, not leftover kwargs.
    Those kwargs are forwarded to Spell after fingerprinting. No resolvable modifier exists here.
    Class admission rejects Protocol targets and kernel manifest entries; it has no general ABC check.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:241-698
  - src/melder/aether/spellbook/bind/bind.py:700-932
  - context_compass/system_docs/src_graph.md:5777-5841
  IMPACT: A meaningful mode needs explicit transport/storage/identity semantics; stuffing a flag
    into existing generic kwargs would not distinguish resolution behavior or cached identities.
  NEXT: Read Spell and SpellIndex ownership plus bind_inactive and public forwarding paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T16:50:53Z
  TYPE: FACT
  CLAIM: Spell stores per-registration identity, target, metadata and compiler state. SpellIndex
    stores only stable index identity, selected member and membership. bind_inactive constructs a
    new Spell through the same Bind entry, parks it, then moves it onto the caller's existing index.
    Conduit bind/bind_inactive delegate to Spellbook; SpellBinder carries kwargs through finalize and
    resets them between registrations. Class families already have their ordinary Existence policy.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:237-610
  - src/melder/aether/spellbook/bind/spell_index.py:12-281
  - src/melder/aether/spellbook/spellbook.py:4752-4956
  - src/melder/aether/conduit/conduit.py:3097-3280
  - src/melder/aether/spellbook/spellbinder.py:222-366
  - src/melder/aether/spellbook/spellbinder.py:641-666
  - src/melder/aether/spellbook/spellbinder.py:826-870
  - src/melder/aether/spellbook/resolution_style_matrix.py:44-491
  IMPACT: A bind-time bool on each Spell is the minimal proposed owner; putting it on SpellIndex
    would make one mode apply to every member. Keep inactive/selected state separate from capability.
    Existing fluent kwargs can forward the modifier once Spellbook consumes it explicitly.
  NEXT: Trace selected-target matching and compiler root admission before finalizing the change map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T16:54:14Z
  TYPE: FACT
  CLAIM: Phase 3 matches both bound target and spellframe, using a pass-local candidate index or
    equivalent scan. Single DI raises for zero/multiple candidates; collections include all matches.
    The first point that knows actual matching Spell registrations is Phase 3, not the signature-only
    Phase-1 classifier. Structural scheduling currently visits all local active Spells, while plan
    eligibility excludes existing creations and requires a Phase-5 blueprint. Phase-4 binding-cycle
    validation independently reads Phase-1 requirement shapes, so a Phase-3-only shape change would
    leave validation using stale injection meaning. Lookup keys remain (frame-or-name, binding name).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:126-545
  - src/melder/aether/spellbook/spellbook_creation_system.py:1359-1474
  - src/melder/aether/spellbook/spellbook_creation_system.py:1896-1994
  - src/melder/aether/spellbook/spellbook_creation_system.py:2421-2472
  - src/melder/aether/spellbook/spellbook_creation_system.py:2611-2874
  - src/melder/aether/spellbook/spellbook_creation_system.py:3084-3157
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:471-612
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:173-279
  - src/melder/utilities/helpers/general_helpers.py:109-423
  IMPACT: Keep the public bool simple but coordinate matching, required-input policy, structural
    validation and planning. Preserve existing binding-key uniqueness: a new SHA/mode alone does
    not create a new name slot, and Base/default plus Implementation-as-Base/default normalize equally.
  NEXT: Identify common direct-meld entry checks, then write the minimum proposed edit and regression map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T16:57:02Z
  TYPE: FACT
  CLAIM: ConduitMeld and SpellSpaceMeld implement concrete execution doors. Each can hit the live
    spell pool or an epoch-guarded memoized executor before shared lookup/validation helpers run.
    _ensure_lineage_resolvable is conditional on the book validation flag, so placing the new
    capability restriction there alone would be insufficient. The non-resolution error belongs
    before execution/context building and successful fast-door publication; graph lookup stays legal.
    The compiler-system structural helper runs phases 1-4 sequentially without a mode distinction.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:143-457
  - src/melder/aether/conduit/meld/spellspace_meld.py:168-468
  - src/melder/aether/conduit/meld/meld.py:596-644
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:771-823
  - src/melder/aether/aetheric_frame/aetheric_frame.py:876-895
  IMPACT: Reuse existing guard/invalidation structure, but enforce mode independently of risk-based
    validation. A bool fixed at bind time can prevent discovery-only targets from publishing executors;
    mode transitions and cache hydration must be qualified before claiming warm-path safety.
  NEXT: Record the proposed minimal API/storage/compiler map and the remaining semantic choices.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T17:00:56Z
  TYPE: FACT
  CLAIM: Requirement and symbolic dependency shapes are read-only property surfaces, while
    SpellSocketDescriptor is a frozen value record with runtime target IDs and no separate
    discovery target association. Concrete reuse-only meld doors also return existing objects
    after identity lookup, so they belong in the mode restriction alongside construction doors.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_parameter_requirements.py:15-311
  - src/melder/aether/spellbook/spell_compiler/symbolic_graph/spell_symbolic_dependency.py:12-256
  - src/melder/aether/spellbook/spell_compiler/topology/spell_local_topology.py:11-228
  - src/melder/aether/conduit/meld/conduit_meld.py:458-609
  - src/melder/aether/conduit/meld/spellspace_meld.py:469-620
  IMPACT: PLAIN lowering needs an explicit resolved metadata path rather than private mutation of
    earlier phase captures. The API/storage placement is clear; exact socket schema remains open.
  NEXT: Discuss the proposed change map, then deepen the resolved-socket/validation policy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T17:00:56Z
  TYPE: PLAN
  CLAIM: The bounded trace is ready for discussion. Recommend one explicit resolvable: bool = True
    keyword on bind/bind_inactive and Conduit facades, stored per Spell, included consistently in
    fingerprint/inspection, with no new public lifecycle or registration framework. Remaining code
    work is enumerated in Proposed Minimal Modifier and must preserve Nexus graph/persistence scope.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:241-698
  - src/melder/aether/spellbook/spellbook.py:4752-5290
  - src/melder/aether/spellbook/spell.py:237-610
  - src/melder/aether/spellbook/bind/spell_index.py:12-281
  IMPACT: The owner has a concrete source-backed design route without premature implementation.
  NEXT: Settle resolved-socket target metadata and Phase-4 consumption in the next focused discussion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T17:11:38Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Owner explicitly invites an independent recommendation rather than requiring the earlier
    PLAIN mechanism. Recommendation: keep the small public resolvable=True modifier and per-Spell
    policy, but represent caller-supplied dependencies explicitly in the resolved socket model.
    A dedicated internal supplied-input category preserves target identity, required/default rules,
    and graph relationships without rewriting Phase-1 declaration facts or importing SpellContract's
    linked-provider lifecycle. Phase 3 selects real providers or establishes caller supply; downstream
    validation/planning consumes that resolved result. PLAIN remains the existing ordinary/default
    argument category. Exact internal enum/field spelling is not chosen by this note.
    Tradeoff: an explicit resolved category adds schema/planner work, but makes the meaning visible
    to validators, diagnostics, Nexus and persistence; PLAIN plus scattered special flags can hide it.
    Confirm on a small end-to-end abstract-definition/consumer case before expanding the epic's matrix.
    This supersedes the preference for PLAIN in Proposed Minimal Modifier; it is a recommendation,
    not owner-approved implementation or permission to change runtime code.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_parameter_requirements.py:15-311
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:126-898
  - src/melder/aether/spellbook/spell_compiler/topology/spell_local_topology.py:11-228
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:173-279
  IMPACT: Public simplicity and explicit compiler semantics can coexist. Graph registration need
    not force construction, and an external input need not masquerade as an ordinary argument.
  NEXT: Discuss the explicit supplied-input category with the owner before implementing the modifier.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Successor discovery task: `tickets/tasks/2026-09-19_define_caller_supplied_socket_contract_task.md`.
All implementation stories and their reading requirements are linked from the epic. Resume through
that new task after required REONBOARD; this trace is retained evidence, not the active work unit.

Latest recommendation after the owner invited independent judgment: keep resolvable=True publicly,
but prefer an explicit caller-supplied category in resolved sockets over lowering to ordinary PLAIN.
Preserve Phase-1 declaration metadata; let Phase 3 decide the supplied/provider outcome, and have
validation/planning/Nexus consume that same result. This recommendation supersedes the earlier PLAIN
preference in the proposed map. No runtime code is changed or approved by this discussion.

First discovery result is in review. See Proposed Minimal Modifier, Semantic Table, and Minimum
Future Regressions above. The public route is one bool defaulting True, stored per Spell; inactive
selection remains separate. Bind and bind_inactive converge through Bind. Mode must affect identity,
compiler admission/matching, direct execution and later crystal/Nexus propagation. Phase-3-only
mutation of PLAIN is insufficient because Phase 4 independently reads Phase-1 declarations.
Next deepen the resolved socket metadata and validation policy. No production code or tests changed.
