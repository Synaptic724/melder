# Story: Carry default-resolvable policy through binding and version identity

## Completion
- Completed: 2026-09-20T00:25:59Z
- Summary: Delivered native immutable per-version resolvable policy with compatible True identities and distinct False identities.
- Acceptance: Owner requested turn-in, then required two repairs first; both are verified.

## Metadata
- Story ID: STORY-2026-09-19-discoverable-registration-modifier
- Epic: EPIC-2026-09-19-discoverable-non-resolvable-registrations
- Sequence: S2
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T17:25:45Z
- Updated: 2026-09-20T00:25:59Z

## User Narrative
As a user or agent, I can register a definition with resolvable=False through bind or bind_inactive,
while calls that omit the modifier retain normal resolution behavior.

## Value / MRP Alignment
Keep the public change to one bool, with consistent identity and forwarding across registration paths.

## Ticket Contract
- ENTRY_GATE: S1 settles target families, fingerprint compatibility and per-Spell policy; a scoped
  implementation task and required patch contracts exist before code edits.
- EXECUTION_BOUNDARY: Registration transport, admission, Spell storage, fingerprint/inspection and
  version-member semantics. Construction and graph consumers are delivered through S3-S6.
- DEPENDENCIES: S1; coordinate the shared schema with S3 and the durable payload contract with S6.
- EXIT_GATE: Modifier transport/identity tests pass and downstream stories have the documented contract.
- FAILURE_ESCALATION: Escalate target-family or identity changes that exceed S1; preserve uniqueness rules.

## Requirements (Functional)
- Add resolvable: bool = True to Spellbook.bind and Spellbook.bind_inactive and Conduit forwarding APIs.
- Validate the bool at shared Bind admission and carry it through direct/decorator paths.
- Store policy on each Spell version; no live toggle or new Existence/Permissions value.
- Keep selected/parked state independent. A parked True version remains True after selection.
- Make default omission equal explicit True and keep False policy identity distinct as agreed in S1.
- Keep Bind.spell_id_inspector and sha256_profile consistent with real binding.
- Preserve generic metadata transport without accidentally leaving the native modifier in metadata.
- Preserve fluent reset semantics; use existing SpellBinder kwargs transport unless S1 requires more.
- Continue normal creation of custody/research records so False entries have durable graph identities.

## Requirements (Non-Functional)
- No mandatory application inheritance, decorators, new global registry or unrelated lifecycle changes.
- No schema choice based on convenience alone; record old-SHA/cache behavior explicitly.
- Preserve current internal-target guard and collision behavior except accepted admission changes.

## Scope Boundaries
- In scope: binding APIs, Spell policy, fingerprint inputs, inactive member transitions and related tests.
- Out of scope: new socket execution, Nexus graph rendering, arbitrary instance-ownership redesign.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner-authorized turn-in after delivered scope and reported failure repairs passed.

## Dependencies / Related Work
- Parent: `tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md`
- Prerequisite: `tickets/stories/completed/2026-09-19_discoverable_registration_contract_discovery_story.md`
- Next: `tickets/stories/completed/2026-09-19_caller_supplied_socket_compiler_story.md`
- Evidence: `tickets/tasks/completed/2026-09-19_trace_discoverable_registration_compiler_boundary_task.md`

## Required Reading Before Work
1. Parent epic, accepted S1 decisions, and the evidence task's current recommendation/notes.
   Read `tickets/tasks/completed/2026-09-19_define_discoverable_registration_selection_task.md` for frame-wide
   key uniqueness and active/parked distinctions, then the admission/identity task for SHA policy.
2. `system_docs/src_architecture_index.md` and `system_docs/src_components_index.md`.
   Read component slices: Binding Pipeline; Spellbook Core; Spellbook Configuration and System State.
3. Verify `system_docs/src_graph_index.md`, then read graph sections for the following source owners.
4. Read relevant implementation methods completely, including forwarding and identity callers:
   - `src/melder/aether/spellbook/spellbook.py` — bind, bind_inactive, registration, notch and index moves.
   - `src/melder/aether/spellbook/bind/bind.py` — bind, _bind_logic, sha256_profile, spell_id_inspector.
   - `src/melder/aether/spellbook/spell.py` — constructor, slots, cleanup, policy/owner state.
   - `src/melder/aether/spellbook/bind/spell_index.py` — immutable identity and selected/member semantics.
   - `src/melder/aether/spellbook/resolution_style_matrix.py` — existing family restrictions.
   - `src/melder/aether/conduit/conduit.py` — bind/bind_inactive forwarding.
   - `src/melder/aether/spellbook/spellbinder.py` — bind, with_kwargs, finalize, reset.
   - `src/melder/utilities/helpers/general_helpers.py` — SpellInputUtils canonical keys.
   - `src/melder/aether/aetheric_frame/aetheric_frame.py` — lookup claims and their container delegate.
5. Before tests, read the test architecture/components through their indexes and these relevant fixtures:
   - `tests/unit/melder/spellbook/bind/test_bind.py`
   - `tests/unit/melder/spellbook/test_spellbinder.py`
   - `tests/unit/melder/aether/spellbook/test_bind_kwargs_metadata.py`
   - `tests/component/melder/spellbook/test_spellbook_component_spell_index.py`
6. Read the S6 crystal contract before finalizing identity fields. Do not preload the whole restore engine.

## Tasks (Implementation Checklist)
- [x] Execute `tickets/tasks/completed/2026-09-19_implement_resolvable_registration_modifier_task.md`.
- [x] Create a scoped task from accepted S1 decisions and map required patch sections to source/tests.
- [x] Add meaningful registration/default/identity regressions before changing transport.
- [x] Implement explicit forwarding, per-Spell storage, validation and fingerprint consistency.
- [x] Verify active/parked behavior, fluent reuse, and existing collision rules.
- [x] Update consumed profiles/descriptions and document the S3/S6 handoff.

## Acceptance Criteria
- All entry paths retain explicit False and default to True; the modifier does not leak between binds.
- Otherwise-identical omitted/True bindings agree; False identities follow the accepted schema.
- Inactive membership does not override the capability of another version in the same index.
- Existing registration targets, permissions, defaults, and metadata tests retain their contracts.
- No claim of complete non-resolution behavior is made until S3-S6 integration passes.

## Validation / Test Plan
- Passed: 42 new registration cases and 1845 focused compatibility tests; generated source/LLM checks pass.
- Use observable registration identity and public policy output; avoid tests of incidental field layout.

## UX / API / Data Notes
The bool describes capability, not activity or compiler dirtiness. Existing resolution_required stays intact.

## Risks / Mitigations
Fingerprint-only separation does not grant another name slot; use normal naming/uniqueness semantics.

## Applicable Anti-Patterns
- [x] No modifier hidden only in metadata.
- [x] No mode on the shared SpellIndex or conflation with inactive state.
- [x] No standalone feature-completion claim from transport alone.

## Open Questions
Consume S1 answers for False target families, fingerprint schema and legacy default handling.

## Decision Log
- Per-Spell bind-time bool, default True; public application architecture remains unchanged.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: accepted story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: registration transport, identity, selected/parked policy.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-19T17:25:45Z
  TYPE: PLAN
  CLAIM: Stage the narrow registration-policy slice with explicit downstream dependencies.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:241-698
  - src/melder/aether/spellbook/spellbook.py:4752-5290
  IMPACT: The API stays small while mode identity and propagation have one owner.
  NEXT: Read accepted S1 decisions before opening the implementation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9


- DATETIME: 2026-09-19T20:05:28Z
  TYPE: FACT
  CLAIM: S2 native capability is implemented with 42 new passing cases and 1845 focused compatibility
    passes. Default/True legacy hashes are preserved; False uses a distinct domain and stays native
    through direct/decorator/fluent/active/inactive paths. Source docs/graph and generated assets agree.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-19_implement_resolvable_registration_modifier_task.md
  IMPACT: S3 can consume Spell.resolvable; S6 must explicitly capture/replay it. S2 does not enforce
    direct or nested meld refusal and does not persist False in SpellCrystal yet.
  NEXT: Open the compiler implementation task under S3's existing reading and schema contract.
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

## Closure Confirmation
- [x] Owner accepts delivered behavior and evidence.
- [x] Child tasks, artifacts and boards synchronized.

## Noting Behavior
Record registration/identity decisions here; keep tactical evidence in child task notes.

## Context / Handoff Summary
CLOSED at 2026-09-20T00:25:59Z. Delivered native immutable per-version resolvable policy with compatible True identities and distinct False identities.
Final evidence and limits are in the graph/replay and follow-up validation artifacts.
No next implementation step remains in this accepted record.

### Historical pre-closure handoff
S2 implemented and review-ready; execution details are in the child task. Native default-True capability,
False hash discrimination, Protocol admission, active/inactive forwarding and descriptions are verified.
Existing version rules and lifecycle/uniqueness rules remain. Runtime enforcement, Nexus graph and
crystal replay remain S3-S6. No closure or feature-completion claim until their required acceptance.
