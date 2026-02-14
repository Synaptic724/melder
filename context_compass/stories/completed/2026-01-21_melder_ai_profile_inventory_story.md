- Completed: 2026-01-22
- Summary: Delivered full AI profile inventory/provenance updates with supporting tests.

# Story: Expand SpellAIProfile inventory

## Metadata
- Story ID: STORY-2026-01-21-melder-ai-profile-inventory
- Epic: EPIC-2026-01-21-melder-ai-profile-inventory
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-21
- Updated: 2026-01-22

## User Narrative
As a maintainer, I want AI profiles to inventory the full object surface
(classes and instances, including dunders) with consistent provenance so
downstream tools can apply policy later.

## Value / MRP Alignment
This makes AI profile output trustworthy and complete without early filtering.

## Requirements (Functional)
- Always include dunders in AI profile output.
- Capture full source blocks with start/end lines when available.
- Promote properties/descriptors/data members to first-class records.
- Capture docstrings for class and member records when available.
- Include instance attribute inventory for instance-bound objects.
- Record dynamic attribute access signals when present.

## Requirements (Non-Functional)
- Keep profile generation safe for uninspectable members.
- Keep member records consistent across kinds, including instance attributes.

## Scope Boundaries
- In scope:
  - SpellAIProfile and inspector/profile outputs.
  - Object-level member inventory for classes and instances.
- Out of scope:
  - Downchain ACL/policy filtering.
  - Identity/lineage/spellbook context.
  - Capability semantics and policy decisions.
  - Size/perf controls or storage strategy.
  - Cross-object topology or dependency graphs.

## Dependencies / Related Work
- Task: TASK-2026-01-21-melder-ai-profile-inventory-investigation
- Task: TASK-2026-01-21-melder-ai-profile-inventory-implementation

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-21-melder-ai-profile-inventory-investigation - Inventory current profile outputs and gaps.
- [x] Task: TASK-2026-01-21-melder-ai-profile-inventory-implementation - Implement full inventory and provenance.

## Acceptance Criteria
- AI profile includes dunders.
- Full source blocks and line spans captured when available.
- Properties/descriptors include readable/writable semantics and docstrings.
- Instance attribute inventory is captured for instance-bound objects.
- Dynamic attribute signals are present when applicable.

## Validation / Test Plan
- Unit tests for class/method/property outputs and builtins.

## UX / API / Data Notes
- AI profile remains unfiltered; policy is downchain.

## Risks / Mitigations
- Risk: Source capture fails on decorated/builtin callables.
  - Mitigation: best-effort with nulls and flags.

## Decision Log
- 2026-01-21: Start AI profile inventory expansion story.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story created to expand SpellAIProfile inventory and provenance capture.
Scope update captured in `context_compass/artifacts/ai_profile_inventory_ticket_update.md`.
Investigation and implementation tasks are complete; user reported passing the
AI profile strategy tests. Acceptance confirmed; ready for closeout.
