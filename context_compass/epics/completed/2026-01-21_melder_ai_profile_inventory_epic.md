- Completed: 2026-01-22
- Summary: Completed rich AI profile inventory expansion with provenance and tests.

# Epic: Rich AI Profile Inventory

## Metadata
- Epic ID: EPIC-2026-01-21-melder-ai-profile-inventory
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-21
- Updated: 2026-01-22
- Target Window: 2026-Q1
- Related Program/Initiative: AI profile enrichment

## Problem / Opportunity
SpellAIProfile does not provide a full-surface inventory, does not include
dunders by default, and only captures preview source snippets. Properties,
descriptors, instance attributes, and dynamic attribute signals are not
captured as first-class records. We need a complete, object-local inventory
with consistent provenance and rich member data.

## MRP Alignment (Most Reasonable Product)
The MRP is a complete, unfiltered AI profile layer that captures truth and
provenance for downstream ACL policy.

## Goals (Outcomes)
- Always include dunders at AI profile stage.
- Capture full source blocks with start/end lines where available.
- Promote non-callable members into first-class tool-shaped records.
- Include properties/descriptors with accessor visibility and docstrings.
- Include instance attribute inventory for instance-bound objects.
- Record dynamic attribute access signals when present.

## Non-Goals (Explicit Exclusions)
- Downstream ACL enforcement.
- Remote transport or AethericRift concerns.
- Identity/lineage/spellbook context.
- Capability semantics and policy decisions.
- Size/perf controls or storage strategy.
- Cross-object topology or dependency graphs.

## Scope Boundaries
- In scope:
  - SpellAIProfile, ClassInspector, MethodInspector, and profile schemas.
  - Object-level member inventory for classes and instances.
  - Properties, descriptors, and instance-bound attributes.
  - Dynamic attribute access signals.
- Out of scope:
  - Code scanning beyond current inspection pipeline.
  - Identity/lineage/spellbook context.
  - Capability semantics and policy decisions.
  - Size/perf controls or storage strategy.
  - Cross-object topology or dependency graphs.

## Success Metrics
- AI profile includes dunders and full source text for Python-defined members.
- Builtins/extensions return null source without failing.
- Property/descriptor members appear with readable/writable semantics.
- Instance attribute inventory is captured for instance-bound objects.
- Dynamic attribute signals are present when applicable.

## Requirements (Functional + Non-Functional)
- No filtering at profile stage.
- Consistent provenance fields per member.
- Docstrings captured for classes/members when available.
- Use normal classes (no dataclasses with objects).

## Constraints / Assumptions
- No TYPE_CHECKING or future annotations.
- Keep profile generation safe for uninspectable members.

## Dependencies / External References
- `SpellAIProfile` and inspector stack in spell_examiner.
- Scope reference: `context_compass/artifacts/ai_profile_inventory_ticket_update.md`.

## Milestones (Track Progress)
- [x] Milestone 1: Investigation completed and schema proposal drafted.
- [x] Milestone 2: Full inventory and provenance implemented.
- [x] Milestone 3: Tests added for dunders/properties/builtins.

## Stories (Required to Complete)
- [x] Story: STORY-2026-01-21-melder-ai-profile-inventory - Expand AI profile inventory.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-01-21-melder-ai-profile-inventory

## Acceptance Criteria (Epic Done)
- AI profile includes dunders and full source blocks when available.
- All members include consistent provenance fields.
- Properties/descriptors and instance attributes are first-class records.
- Dynamic attribute signals are present when applicable.
- Downchain filtering remains responsible for policy/ACL.

## Risks / Mitigations
- Risk: Source capture fails for builtins.
  - Mitigation: null source fields with clear flags.

## Validation / Test Approach
- Unit tests around inspector/profile output shapes.

## Rollout / Adoption Plan
- Land inventory changes first, then derived summaries/tags.

## Decision Log
- 2026-01-21: Start rich AI profile inventory effort.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Epic created to expand SpellAIProfile inventory and provenance capture.
Scope update captured in `context_compass/artifacts/ai_profile_inventory_ticket_update.md`.
Milestones and story tasks are complete; acceptance confirmed and ready for
closeout.
