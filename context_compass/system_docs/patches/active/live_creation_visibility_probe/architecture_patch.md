# Patch Architecture: Live Creation Visibility Probe

## Metadata
- Patch ID: `live_creation_visibility_probe`
- Status: active
- Updated: 2026-04-09T00:14:58Z

## Objective
Add one canonical no-create live-creation query path:
- real owner: `Meld`
- public facade: `Conduit.has_live_creation(...)`

## Core Decision
- Reuse the same spell lookup path as `meld(...)`.
- Stop before creation.
- Read live runtime state from `Creations` only as backend storage.
- Do not add hot-path publication hooks.
- Keep a bool facade (`has_live_creation(...)`) and add a richer status
  companion (`describe_live_creation_status(...)`) over the same internal
  probe data.

## Non-Goals
- full static mode
- capability mode
- richer status payload in the first public cut
