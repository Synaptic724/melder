# Story: binding_manifest_hash - the bind signature becomes a binding manifest with its own SHA256

## Metadata
- Story ID: STORY-2026-10-18-binding_manifest_hash
- Epic: EPIC-2026-10-18-spell_identity_is_the_code
- Status: ready
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-18T11:45:58Z
- Updated: 2026-10-18T11:45:58Z

## User Narrative
As an agent, I want how a spell is kept - its address, lifetime, teardown, capability and settings - recorded as a
binding manifest with its own SHA256 beside the spell_id, so that Melder knows exactly when a spell's binding
changed and never reuses what it built for the old binding.

## Value / MRP Alignment
Once the spell_id is the code (S1), the binding needs its own identity: the creation cache and the record rely on
the spell_id covering the binding today (`StructuralSnapshot.structural_key`: "the spell id already covers the
spell's own signature, names, existence and resolvability"). The owner's design keeps that structure as a manifest.

## Ticket Contract
- ENTRY_GATE: S1's component patch approved; this story's component patch approved; melder_1's release of spell.py
  (the Spell carries the manifest); the board row.
- EXECUTION_BOUNDARY: the binding manifest and its hash (Bind builds it, the Spell carries it, `describe` shows
  it), the SpellCrystal record, the creation cache's structural key and world stamp, the cache generation; tests
  and docs. Not revalidation (S3).
- DEPENDENCIES: S1 (lands with it); melder_1's release of spell.py.
- EXIT_GATE: a binding change without a code change misses both cache tiers; the record round-trips the manifest;
  byte-identical across processes; docs.
- FAILURE_ESCALATION: CONFLICT while spell.py is held; DECISION_REQUEST on which fields the binding hash covers.

## Requirements (Functional)
- The manifest holds the spellframe (with its kind and contract), the binding name, the existence, the resolved
  disposal names in order, resolvable and the managed settings; its binding hash is a SHA256 over it, address-free
  and deterministic.
- The Spell carries the manifest and its hash; `Spell.describe` and the record (the SpellCrystal) show both.
- The structural cache keys a payload by spell_id and binding hash, and the world stamp carries every spell's
  binding hash, so the executor tier's full hit needs them too; a cache generation retires the old bundles.
- Nothing else identifies a spell by its binding.

## Requirements (Non-Functional)
- No new lock; the hash is computed once at bind.
- Byte-identical across processes and GIL modes.

## Scope Boundaries
- In scope: the manifest, its hash, the record and the caches' keys.
- Out of scope: revalidation and the store (S3), the refusals (S4), the migration (S5).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: filed under EPIC-2026-10-18-spell_identity_is_the_code on the owner's direction (chat 2026-10-18); scope and owner set, the open questions named.

## Dependencies / Related Work
- EPIC-2026-10-18-spell_identity_is_the_code
- STORY-2026-10-18-spell_id_hashes_the_object_code
- STORY-2026-10-18-revalidate_on_binding_change

## Tasks (Implementation Checklist)
- [ ] Task: the component patch (Binding Pipeline: the manifest; the creation cache's keys; the record).
- [ ] Task: inventory every spell_id-keyed cache and store (it feeds S3).
- [ ] Task: red tests; implement; docs; notch with S1; the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- Changing only a spell's existence, disposal list, address or resolvable changes its binding hash and not its
  spell_id, and the next conjure misses both cache tiers for it.
- The record carries the manifest and a restore replays it.

## Validation / Test Plan
- `test_changing_only_the_binding_changes_the_binding_hash_not_the_spell_id`,
  `test_a_binding_change_misses_the_creation_cache`; the record round-trip; GIL off and on.

## UX / API / Data Notes
- `Spell` gains the manifest and its binding hash (read-only).

## Risks / Mitigations
- A cache or store keyed by spell_id alone is missed: the inventory task lists them before code.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Which managed settings belong to the binding hash, or to a pool-only setting (S3's question).

## Decision Log
- 2026-10-18T11:45:58Z: filed under EPIC-2026-10-18-spell_identity_is_the_code (the epic's DECISION note).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none yet (the design's probes are rowed under the epic)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: rows are added when this story produces its own artifacts

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - a spell's identity (its code) versus its binding (how it is kept)
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; filed 2026-10-18T11:45:58Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-18T11:45:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Filed from the owner's direction (the epic's DECISION note of 2026-10-18T11:45:58Z); the evidence it starts from is the
    epic's FACT note and its probes. Nothing in src/ moves before this story's component patch is approved.
  EVIDENCE: context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md
  IMPACT: The scope, requirements and acceptance above are the plan the patch docs refine.
  NEXT: the component patch with S1's.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: the binding becomes a manifest with its own SHA256, recorded and part of the caches' keys.
- State: ready (melder_0); waiting on S1's patch and melder_1's release of spell.py.
- Next: the component patch with S1's.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
