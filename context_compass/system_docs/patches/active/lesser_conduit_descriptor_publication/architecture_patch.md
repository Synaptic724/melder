# Architecture Patch: Lesser Conduit Descriptor Publication

## Patch Scope and Non-Goals
Scope:
- publish lesser conduits through the existing conduit-record model
- remove lesser conduit records on lesser cleanup
- preserve same-id overwrite behavior on lesser -> normal upgrade

Non-goals:
- frame summary redesign
- new descriptor record families
- spellspace publication

## Changed-Components Matrix
| component | change |
|---|---|
| `Conduit` | lesser create/cleanup/publication gates |
| `FrameDescriptorManager` | conduit publish eligibility expands beyond normal-only |

## Interface and Boundary Deltas
- lesser conduits become descriptor-visible
- `ConduitRecord.payload.conduit_state` remains the discriminator between
  normal and lesser
- frame publication remains coarse and root-oriented

## Cross-Component Invariants
- `conduit_id` remains stable through lesser -> normal upgrade
- descriptor upsert by `conduit_id` means upgrade overwrites the same record
- lesser create/dispose must not force frame-summary churn

## Migration / Rollout Order
1. expand publish eligibility for conduits
2. publish lesser conduits on lesser creation
3. remove lesser conduit records on lesser cleanup
4. validate upgrade overwrite semantics

## Rollback Strategy
- restore normal-only publish/remove gating if lesser publication proves too
  noisy or unstable in the first cut

## Validation Expectations and Evidence Plan
- focused tests for:
  - lesser creation publishes a conduit record
  - lesser cleanup removes the record
  - upgrade to normal keeps the same descriptor record identity

## Ticket Coverage Map
- epic:
  - `tickets/epics/2026-04-11_publish_lesser_conduits_into_nexus_descriptor_epic.md`
- story:
  - `tickets/stories/2026-04-11_enable_lesser_conduit_descriptor_publication_story.md`
- task:
  - `tickets/tasks/2026-04-11_implement_lesser_conduit_descriptor_publication.md`

## Unknowns and Decision Requests
- UNKNOWN: whether `parent_conduit_id` is needed in the next slice for useful
  lesser topology navigation
