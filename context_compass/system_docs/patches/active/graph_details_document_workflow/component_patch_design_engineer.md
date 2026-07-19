# component_patch_design_engineer

## Metadata
- Patch ID: graph_details_document_workflow
- Component: design_engineer graph authoring skill chain
- Status: in_progress
- Owner: codex
- Created: 2026-04-19T19:19:24Z
- Updated: 2026-04-19T19:19:24Z

## Component Purpose and Boundary
- Current boundary:
  - design-engineer docs cover architecture/components/tests docs only.
- Target boundary:
  - design-engineer docs also cover authoring and maintaining the graph-details
    manifest that complements architecture/components docs.

## Before/After Behavior Summary
- Before:
  - no explicit design-engineer guidance exists for graph schema authoring,
    relationship modeling, or compressed-storage maintenance.
- After:
  - design-engineer has one explicit graph-details authoring/maintenance skill.

## Interface Deltas
- Inputs:
  - canonical graph workflow doc
  - existing architecture/components docs
- Outputs:
  - graph nodes/relations authored consistently
  - expanded patch copy workflow followed consistently
  - readable graph consumption file regenerated consistently after graph edits
- Error semantics:
  - attempts to maintain the graph without the expand-edit-compress workflow
    are non-compliant
  - attempts to stop after recompressing canonical storage without regenerating
    the readable graph are non-compliant

## State and Lifecycle Deltas
- Owned state changes:
  - add one required design-engineer graph skill
- Lifecycle/cleanup changes:
  - none

## Failure Mode Deltas
- New failure mode:
  - graph updates drift from architecture/components if design guidance is ignored
- Removed failure mode:
  - no explicit authoring contract for the graph manifest
- Changed failure mode:
  - graph maintenance errors become skill-chain violations instead of ad hoc behavior

## Dependency and Ordering Constraints
1. The design-engineer graph skill depends on the canonical graph workflow doc.
2. Architecture/component instruction docs should acknowledge the graph as a
   complementary system surface, not a replacement narrative.

## Validation Expectations
- Test/validation item 1:
  - design-engineer SKILLS routes to the new graph authoring skill
- Evidence target 1:
  - updated `agent_onboarding/default/design_engineer/SKILLS.MD`

## Unknowns and Open Decisions
- UNKNOWN:
  - whether future design-engineer examples should include more than one graph example
- DECISION_REQUEST:
  - none

## Context / Handoff Summary
- What changed:
  - design-engineer gains a graph authoring and maintenance skill
- Remaining risks:
  - architecture/component docs and the graph could drift if not maintained together
- Next entrypoint:
  - `agent_onboarding/default/design_engineer/skills/graph_details_instructions.md`
