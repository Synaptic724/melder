# Component Patch: General Workflow Catalog

## Purpose
Capture the first real workflow catalog for the `general` role.

## Before/After
Before:
- `general` had only one active workflow: `cleanup_context_compass`

After:
- active:
  - `cleanup_context_compass`
  - `start_context_compass_work`
  - `turn_in_selected_tickets`
  - `sync_attention_board`
- on-demand:
  - `role_creation`
  - `workflow_creation`

## Key Rules
- active workflows are baseline-readable for the role
- on-demand workflows are discoverable but should not be read until explicitly
  selected by the user or clearly triggered by the task
- the optional pair stays in the manifest but outside the active list
