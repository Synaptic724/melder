# Task: Define selection of non-resolvable definitions and executable providers

## Completion
- Completed: 2026-09-20T00:25:59Z
- Summary: Defined exact lookup, provider/definition matching and descriptor/collection semantics without changing uniqueness.
- Acceptance: Owner requested turn-in, then required two repairs first; both are verified.

## Metadata
- Task ID: TASK-2026-09-19-define-discoverable-registration-selection
- Story: STORY-2026-09-19-discoverable-registration-contract-discovery
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T18:45:34Z
- Updated: 2026-09-20T00:25:59Z

## Objective
Define a consistent selection table for registered non-resolvable definitions, executable providers,
and OVERRIDE_REQUIRED inputs without weakening existing binding identity or provider selection.

## Ticket Contract
- ENTRY_GATE: Parent epic/S1 and the previous socket contract are read; owner selected OVERRIDE_REQUIRED
  and directed continuation; this task is routed from attention_board.
- EXECUTION_BOUNDARY: Source discovery and decision/regression tables for root lookup, Phase-3 matching,
  descriptor/collection selection, active/parked registries, and binding-key coexistence. No runtime edits.
- DEPENDENCIES: Per-Spell resolvable=True direction; accepted OVERRIDE_REQUIRED name and explained meaning;
  previous trace's execution/descriptive target separation and existing default precedence.
- EXIT_GATE: Source-backed selection table and concrete recommended policies, with any unresolved
  product choices named and implementation/test owners mapped into S2/S3/S4.
- FAILURE_ESCALATION: Preserve UNKNOWN when source does not decide a product rule. Do not introduce a
  new registration namespace, bypass uniqueness, or revive existing-object ownership redesign.

## Scope Boundaries
- In scope: one Base definition, Consumer input and resolvable implementation, then selector contrasts.
- Out of scope: implementation, full runtime/cache qualification, graph-edge storage and version redesign.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner-authorized turn-in after delivered scope and reported failure repairs passed.

## Owner-Selected Direction
- Public registration modifier remains resolvable: bool = True on bind and bind_inactive.
- The resolved parameter category is OVERRIDE_REQUIRED, replacing the proposed name CALLER_SUPPLIED.
- A required parameter targeting such a registration needs a supplied override when its consumer is
  constructed. Its graph reference remains; Melder does not construct the referenced definition.
- Ordinary Python defaults remain PLAIN and unchanged. No separate requiredness bool is necessary
  for a category that already means required.
- Keep resolution policy on each Spell version and active/parked state independent.

## Required Reading and Continuation Map
1. Parent epic and S1, then the previous task's current contract and latest owner decision:
   - `tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md`
   - `tickets/stories/completed/2026-09-19_discoverable_registration_contract_discovery_story.md`
   - `tickets/tasks/completed/2026-09-19_define_caller_supplied_socket_contract_task.md`
2. Use current component indexes; read Binding Pipeline, Spellbook Core, DI Descriptors, Meld Resolution
   Runtime and SpellCompiler slices. Reuse unchanged source already read in the same session.
3. Source selection and name/identity contracts, reading complete relevant methods and callees:
   - `src/melder/aether/spellbook/spellbook.py` — find_spell_index/key/id, uniqueness, binding and parking.
   - `src/melder/aether/conduit/meld/meld.py` — _resolve_spell, ID and key lookup, normalization.
   - `src/melder/utilities/helpers/general_helpers.py` — SpellInputUtils canonical keys.
   - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py` — candidate index, scan,
     annotation, collection and SpellMap selection (read in full during the predecessor task).
   - `src/melder/aether/spellbook/bind/spell_index.py` — selected version and category identity.
   - `src/melder/aether/conduit/meld/contracts/spell_map.py`
   - `src/melder/aether/conduit/meld/contracts/spell_contract.py`
   - `src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py`
   - `src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py`
     — contracted provider selection already read; reopen only where new questions require it.
4. Read actual bind/key/annotation/collection/contract tests before asserting an existing test contract.
   Use the current test indexes and S2-S4 test read maps; keep new regression cases as design here.

## Steps / Checklist
- [x] Confirm root lookup semantics separately from Phase-3 candidate matching.
- [x] Prove binding-key collisions and permitted explicit-name coexistence.
- [x] Verify which registries carry active versus parked versions into matching.
- [x] Define zero/one/many resolvable and non-resolvable candidate outcomes.
- [x] Define explicit SpellMap and SpellContract behavior for a non-resolvable target.
- [x] Define collection behavior without inferring requiredness from collection size.
- [x] Record recommended semantics, regression cases, remaining choices and downstream owners.
- [x] Update S1/epic and relevant implementation story reading requirements.

## Deliverables
- Current-behavior source table and proposed new-mode selection table, clearly separated.
- Small Base/Consumer/Implementation examples with valid registration names.
- Regression design and named remaining S1 decisions.

## Current Selection Boundaries

| Surface | What current source actually selects |
| --- | --- |
| Internal Meld ID lookup | Active local/contracted ID maps; no parked-member search. |
| Root class/name/frame lookup | One normalized (frame_or_name, binding_or_default) key, local then contracted. |
| Single annotation | Matching active pool entries, grouped by SpellIndex; zero/multiple currently fail. |
| Collection annotation | All matching active entries in existing order, across binding names; zero is allowed. |
| SpellMap | Explicit spell/frame/binding filters; exactly one selected candidate required. |
| SpellContract | Contracted providers matching its canonical key; dynamic absence is an unresolved warning. |
| Spellbook.find_spell_by_id | Local index-membership lookup returning the current selected Spell, even for an old member ID. |
| bind_inactive | Parked/member registration, with no active key/ID-pool entry. |

The source evidence for these distinctions is in Notes. Do not equate the lineage introspection
helper with exact-ID runtime resolution or use it to retrieve an old version's capability.

## Recommended New-Mode Selection Rules

The owner accepted the OVERRIDE_REQUIRED name and explained required-value contract. The detailed
selection policies below are this task's recommendation, not evidence of existing feature support.

1. Root meld keeps its current selector. After it selects a Spell, False refuses with the
   non-resolvable-registration error. Do not scan for another provider, including when an override
   payload is present. Registration introspection remains available.
2. Single annotation first computes the existing candidate set. Partition that set by the new
   per-Spell capability; do not alter type/name equality, binding filters, or registration visibility.
3. One True candidate resolves normally, even if False definitions also match. More than one True
   candidate stays ambiguous. Only when there are no True candidates may one False candidate produce
   OVERRIDE_REQUIRED. Multiple False matches require explicit disambiguation; zero total matches keeps
   the existing missing-provider failure.
4. Eligibility here means the new capability plus existing selector rules. It does not mean the
   provider is healthy, permitted or already instantiated. A selected True provider's ordinary
   validity/permission/lifetime failure must not fall back to OVERRIDE_REQUIRED and bypass that failure.
5. SpellMap applies its explicit selectors and existing cardinality first. A unique True result uses
   ordinary DI. A unique False result becomes OVERRIDE_REQUIRED while retaining that target's ID.
   Do not substitute a True registration outside the selector, or discard False matches just to make
   an ambiguous descriptor appear unambiguous.
6. A SpellMap selecting False cannot apply a provider-construction payload. Recommend refusing a
   present spell_override payload for that case (None is the absent value), with guidance to supply
   the consumer parameter through meld override. Never inject the SpellMap object as a Python default.
7. SpellContract retains its linked-provider meaning and current zero/multiple-provider semantics.
   A uniquely selected False provider is an explicit incompatible-provider diagnostic; it cannot
   satisfy the contract and is not converted to OVERRIDE_REQUIRED. Enforce at both validation and
   late runtime/provider resolution. Do not infer a ban on metadata sharing or graph visibility.
8. Collections include the matching True providers in current order and exclude False definitions
   from construction. A required list[Base] with none stays an empty collection, not OVERRIDE_REQUIRED.
   Ordinary collection defaults stay PLAIN. Do not infer omission/None from Optional alone.
9. Keep active/parked state independent. Active False definitions remain registered and discoverable;
   parked True/False versions do not enter runtime candidates. Promotion uses the selected version's
   capability and the normal invalidation/revalidation machinery.
10. Keep binding signature uniqueness. A False definition occupies its ordinary active name slot.
    Use existing binding_name/spellframe choices to coexist with an implementation; the mode does not
    create a second namespace or exception to LookupContainer.claim.

### Descriptive edges must say what they mean

For OVERRIDE_REQUIRED, referenced_spell_ids identifies the selected definition. Never put those IDs
in executable target_spell_ids. When a True provider wins, preserve the original annotation so S5 can
show the declared-type relationship independently of the selected executable provider.

Do not manufacture dependency edges to every rejected False candidate. Collection/selection diagnostics
may report excluded candidates, but that is different from the consumer declaring a dependency on each
of them. Declared type, selected provider and candidate membership need distinct graph meanings in S5.

### Concrete registration example (Proposed API)

```python
definition_id = book.bind(
    spell=Base,
    binding_name="definition",
    existence="unique",
    resolvable=False,
)
provider_id = book.bind(
    spell=Implementation,
    spellframe=Base,
    binding_name="runtime",
    existence="unique",
)
```

These occupy (base, definition) and (base, runtime), using existing names rather than a reserved
new convention. With one implementation and the required Consumer.base: Base input, annotation DI
selects the implementation. Selecting definition_id directly refuses. Explicitly selecting the
definition with SpellMap(Base, binding_name="definition") makes that consumer input OVERRIDE_REQUIRED.
Without an implementation registration, the unique definition match requires the supplied Base value.

Binding Base without a name alongside Implementation under spellframe=Base without a name would
collide at (base, __default__). A different mode or SHA does not avoid that collision.
Python inheritance alone does not register an implementation under Base; use the existing spellframe
relationship. Root meld does not inherit annotation candidate-search behavior.

## Regression Design and Downstream Mapping

No new tests were written or run. Existing source/test contracts inform these proposed regression groups.

- S2: False/True registrations at the same key still collide without disturbing the original; distinct
  named keys coexist; inactive variants reserve identity but do not participate until promotion.
- S3/S4: one True plus one False annotation match resolves True; no True plus one False produces
  OVERRIDE_REQUIRED; two True or two False remain ambiguous in their relevant branches; zero stays missing.
- S4: root ID/key selection of False refuses even with an override and even when another provider exists.
- S3/S4: explicit False SpellMap stays selected, requires a supplied value, and rejects provider-construction
  payloads. Preserve ordinary True/absent/ambiguous descriptor results.
- S3/S4: an unresolved SpellContract stays unresolved in dynamic mode; a selected False provider gets a
  distinct incompatible-provider error; no late cached/compiled path may construct it.
- S3/S4: mixed True/False collections construct only True providers, preserving binding order and the
  existing empty required-list behavior. Retain default identity and declared annotation metadata.
- S3/S4: invalid/gated/permission-denied True providers do not silently turn into OVERRIDE_REQUIRED.
- S3/S4: park/notch changes the selected mode and revalidates affected consumers without discovering
  parked versions through SpellIndex membership. Existing provider artifact ownership remains intact.
- S5: declared-type links and selected-provider links are distinct; rejected candidates are not rendered
  as actual dependencies. Recorded historical members do not borrow the current selected member's mode.

## Remaining S1 Work

- Target admission and fingerprint compatibility need the next bounded task. In particular, determine
  which abstract/class/Protocol definitions can be reflected without requiring construction and decide
  legacy True SHA behavior versus False discrimination using actual Bind/SpellCrystal inputs.
- Body-only source revisions and graph-only revisions must remain distinct from structural bind identity;
  trace existing custody/research keys before assuming the bind SHA provides those versions.
- Nullable collections without ordinary defaults need an explicit qualification case. The read Phase-8
  path only publishes empty dependency lists for non-optional collections; this task does not change
  that pre-existing behavior or claim runtime parity for every Optional collection shape.
- Explicit-selector False policies (especially SpellMap payload refusal and SpellContract error timing)
  are recommendations for owner review. The admission/identity investigation can proceed independently.

## Files / Paths Impacted
- This task; predecessor/current S1/epic handoffs and relevant S2-S4 planning records.
- attention_board and mailbox check-in.

## Validation
- Runtime tests: Not run. Source investigation and test-case design only.
- Verify referenced paths, changed sections and board/ticket agreement.

## Risks / Rollback Notes
- A global provider-first rule might silently change direct root lookup into an unrequested search.
- A mode flag cannot create another canonical binding-key slot.
- Ignoring a False entry too early can turn an explicit non-resolution choice into a missing-provider error.
- Treating a collection with no eligible providers as OVERRIDE_REQUIRED could change existing empty-list semantics.

## Applicable Anti-Patterns
- [x] No blanket annotation-wide ban or implicit alternate provider on an explicit selection.
- [x] No collision bypass or scanning parked versions as active candidates.
- [x] No incidental key change disguised as a capability flag.
- [x] No runtime patch from unresolved matching semantics.

## Done Checklist
- [x] Source trace and tables complete.
- [x] Remaining choices and first regression cases recorded.
- [x] S1 and implementation stories synchronized.
- [x] Owner discussion/acceptance captured before closing the task.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: root keys, annotation candidates, descriptors, collections, inactive versions.
- IF_UNKNOWN: none

## Noting Behavior
Read a complete call-path unit, then record evidence, impact and one NEXT before continuing.

## Notes
- DATETIME: 2026-09-19T18:45:34Z
  TYPE: PLAN
  CLAIM: Owner selected OVERRIDE_REQUIRED and approved continuation. This task isolates selection
    semantics from the completed socket propagation trace. First separate direct root lookup from
    compiler candidate enumeration, then test the proposed provider-first rule against each surface.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-19_define_caller_supplied_socket_contract_task.md:89-116
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:435-647
  IMPACT: Public lookup behavior and binding uniqueness will not be silently broadened by the flag.
  NEXT: Read Meld._resolve_spell and its key/id consumers, with SpellInputUtils canonicalization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T18:50:39Z
  TYPE: FACT
  CLAIM: Root Meld resolution is an ID or exact normalized-key lookup, not a candidate scan. Key
    resolution checks local then contracted maps. SpellInputUtils uses the supplied frame, otherwise
    the spell/name, and an omitted binding becomes __default__. Phase-3 annotation matching is a
    different operation that enumerates candidates. Spellbook's lookup-key guard rejects a different
    SpellIndex at the same normalized key. A provider-first rule must not be applied indiscriminately
    to root Meld or introspection lookups.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:1250-1503
  - src/melder/utilities/helpers/general_helpers.py:333-423
  - src/melder/aether/spellbook/spellbook.py:2225-2409
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:435-503
  IMPACT: Root lookup should select the same registration as today, then enforce resolvable. Only
    candidate-based dependency selection considers eligible providers before OVERRIDE_REQUIRED.
    Different SHAs alone do not establish distinct binding keys.
  NEXT: Read active/parked registration transitions and bind's actual collision call sites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T18:53:57Z
  TYPE: FACT
  CLAIM: Active bind claims the signature through AethericFrame.claim_lookup -> LookupContainer.claim
    before publishing local maps. This frame-wide guard rejects a second different spell ID at the
    same key. bind_inactive publishes only to parked/member storage; owned and contracted deactivation
    remove entries from active lookup/ID pools, and reactivation restores them. SpellIndex membership
    and selection are separate; its methods do not publish Spellbook maps. find_spell_by_id is a
    lineage-membership lookup returning the current local spell, unlike Meld's active exact-ID lookup.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:5026-5290
  - src/melder/aether/aetheric_frame/aetheric_frame.py:876-895
  - src/melder/aether/aetheric_frame/lookup_container.py:93-127
  - src/melder/aether/spellbook/spellbook.py:4752-4964
  - src/melder/aether/spellbook/spellbook.py:1446-1693
  - src/melder/aether/spellbook/spellbook.py:1971-2022
  - src/melder/aether/spellbook/bind/spell_index.py:161-289
  IMPACT: Keep False definitions active/discoverable without treating them as parked. Distinct names
    allow a definition and implementation to coexist; different mode/SHAs never bypass signature
    uniqueness. Phase-3 selection must use active pool entries, not all index members or parked storage.
  NEXT: Finish explicit descriptor/contract semantics and required-collection eligibility.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T18:55:48Z
  TYPE: FACT
  CLAIM: SpellMap stores explicit spell/frame/binding selectors plus an optional constructor override
    payload. Phase 3 filters those selectors and requires exactly one result; it does not use the
    annotation candidate ranking. SpellContract instead derives a canonical key, and Phase-4 provider
    presence scans only contracted maps: zero is a dynamic warning, multiple is an error, and automatic
    mode is refused. Phase 8 independently resolves the same contract key and adds provider occurrences.
    Required non-nullable collections already allow zero providers and inject [] through Phase 8.
  EVIDENCE:
  - src/melder/aether/conduit/meld/contracts/spell_map.py:132-336
  - src/melder/aether/conduit/meld/contracts/spell_contract.py:132-335
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:505-651
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:70-223
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:893-1070
  IMPACT: Recommend selector-first handling for explicit descriptors, not silent provider substitution.
    A unique False SpellMap selection can describe OVERRIDE_REQUIRED; a False SpellContract provider
    cannot satisfy its linked-resolution promise. Collections should enumerate True providers only,
    retain False references descriptively, and preserve their established empty/default behavior.
  NEXT: Read focused lookup/parked/collection/contract test cases, then publish the full selection table.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T19:01:16Z
  TYPE: FACT
  CLAIM: The current-boundary table, ten recommended selection rules, valid named-registration example
    and downstream regression groups are recorded. Lookup and inactive public-surface tests were read;
    contract missing/automatic/ambiguity and named SpellMap/collection cases were read as complete units.
    The empty-collection component test proves topology only; no runtime test execution is claimed.
  EVIDENCE:
  - tests/unit/melder/aether/test_lookup_container.py:39-52
  - tests/component/melder/spellbook/test_spellbook_component_bind_inactive_public_surface.py:103-179
  - tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_contract_provider_presence_strategy.py:336-465
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py:1133-1197
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py:1547-1772
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:972-1035
  IMPACT: Selection is specified without turning direct lookup into a provider search, weakening
    uniqueness, or reusing inactive state for capability. Admission and identity remain the next source unit.
  NEXT: Open tickets/tasks/completed/2026-09-19_define_non_resolvable_admission_identity_task.md.
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
CLOSED at 2026-09-20T00:25:59Z. Defined exact lookup, provider/definition matching and descriptor/collection semantics without changing uniqueness.
Final evidence and limits are in the graph/replay and follow-up validation artifacts.
No next implementation step remains in this accepted record.

### Historical pre-closure handoff
Review-ready. Owner selected OVERRIDE_REQUIRED and its explained meaning; detailed selection policies
are the recommendation above. Keep root exact lookup, candidate-based annotation selection, explicit
descriptor semantics, active/parked state and frame-wide uniqueness distinct. No source/test changes
or runtime tests. Next admission/identity source task:
tickets/tasks/completed/2026-09-19_define_non_resolvable_admission_identity_task.md.
After compaction, REONBOARD, then read the current result before repeating source discovery.
