# component_patch_engineer

## Metadata
- Patch ID: graph_details_document_workflow
- Component: engineer graph reading and usage skill chain
- Status: in_progress
- Owner: codex
- Created: 2026-04-19T19:19:24Z
- Updated: 2026-04-19T19:19:24Z

## Component Purpose and Boundary
- Current boundary:
  - engineer guidance points to architecture/components/tests docs but has no
    explicit graph-reading workflow.
- Target boundary:
  - engineer guidance includes reading and using the graph-details manifest
    when object wiring and ownership relationships matter.
  - the readable graph view becomes the primary line-based read surface.

## Before/After Behavior Summary
- Before:
  - graph consumption is implicit and undocumented.
- After:
  - engineer has one explicit graph usage skill and the on-demand system-context
    readset includes the graph workflow and graph manifest.

## Interface Deltas
- Inputs:
  - canonical graph workflow doc
  - canonical graph JSON
  - readable graph JSON
- Outputs:
  - consistent graph-assisted object wiring interpretation during engineering work
- Error semantics:
  - graph claims without consulting the canonical manifest should be treated as stale or unsupported

## State and Lifecycle Deltas
- Owned state changes:
  - add one required engineer graph usage skill
  - widen engineer on-demand system-context readset
- Lifecycle/cleanup changes:
  - none

## Failure Mode Deltas
- New failure mode:
  - engineers may over-trust stale graph relationships if they do not cross-check
    architecture/components when conflicts appear
- Removed failure mode:
  - no explicit guidance for how to read the graph
- Changed failure mode:
  - graph reading becomes a documented system-context behavior instead of ad hoc memory

## Dependency and Ordering Constraints
1. The engineer graph usage skill depends on the canonical graph workflow doc and graph manifest.
2. `context_protocol.md` and engineer SKILLS should route to the graph when
   object relationships and ownership questions are in scope.

## Validation Expectations
- Test/validation item 1:
  - engineer SKILLS routes to the new graph usage skill and on-demand graph docs
- Evidence target 1:
  - updated `agent_onboarding/default/engineer/SKILLS.MD`

## Unknowns and Open Decisions
- UNKNOWN:
  - whether future engineer workflows should require graph reads for all
    system-context work or only relationship-heavy work
- DECISION_REQUEST:
  - none

## Context / Handoff Summary
- What changed:
  - engineer gains a graph usage skill and graph docs enter the system-context readset
- Remaining risks:
  - stale graph usage if update discipline is not followed
- Next entrypoint:
  - `agent_onboarding/default/engineer/skills/graph_details_usage.md`
