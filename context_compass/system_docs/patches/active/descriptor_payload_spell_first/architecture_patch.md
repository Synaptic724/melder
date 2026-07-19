# architecture_patch

## Metadata
- Patch ID: descriptor_payload_spell_first
- Status: draft
- Owner: codex
- Created: 2026-04-05T20:54:09Z
- Updated: 2026-04-05T20:54:09Z

## Patch Scope and Non-Goals
- Objective:
  Implement the spell-first descriptor payload contract:
  - Protocol-based payload/record interfaces
  - one `SpellRecord.payload` field
  - spell publish/store/consume path updated to the new payload contract
- Non-goals:
  - conduit/frame payload rollout
  - event bus implementation
  - viewer implementation

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| interfaces | modify | define payload/record Protocol contracts | spell record |
| spell profiles | modify | export sanitized descriptor payloads | interfaces |
| spell record | modify | collapse split profile shards into one payload field | spell profiles |
| descriptor manager | modify | publish/store the payload instead of split shards | spell record |
| frame descriptor | modify | depend on record interfaces instead of only concrete record classes | interfaces |

## Cross-Component Invariants
- `SpellDetailedProfile` defines the minimum descriptor payload floor.
- Published spell payloads must be descriptor-safe and must not retain live
  runtime object references.
- `SpellRecord` keeps its identity/ownership fields but stores one payload
  instead of split spell-profile shards.
- Conduit/frame records remain structurally flat in this slice.

## Context / Handoff Summary
- What changed:
  Spell-first descriptor payload implementation lane is patch-gated.
- What remains:
  Implement the payload/record contract and validate the direct publish path.
