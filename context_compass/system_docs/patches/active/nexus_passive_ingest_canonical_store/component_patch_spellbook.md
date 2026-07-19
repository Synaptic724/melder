# component_patch_spellbook

## Component purpose and boundary in current architecture
`Spellbook` remains the owner of local spell registration and conjure flow. In
this patch it becomes an internal producer of canonical Nexus records at the
stable points where frame/spell truth is already committed.

## Before/after behavior summary
- Before:
  `Spellbook` registered local spells and conjured conduits, but did not
  publish any of that truth into Nexus.
- After:
  `Spellbook` publishes frame/spell information into private Nexus ingest
  methods once the Spellbook is in a stable publishable posture.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  existing bind/conjure mutation points
- Outputs:
  private calls into Nexus publication methods
- Error semantics:
  non-publishable frames return early; publication failures should be explicit
  and local to the private Nexus path

## State and lifecycle deltas
- `Spellbook` may cache one cheap `_nexus_publish_enabled` bool derived from
  the bound frame posture
- `Spellbook.conjure()` becomes the first frame publish point
- `Spellbook.bind()` publishes only after conjure has happened
- pre-conjure local spells remain local until conjure catch-up publish
- version updates should keep `spell.spell_id` aligned with
  `spell_index.selected_spell_id`
- later owned-spell removal and ownership transfer paths should update/remove
  canonical `SpellRecord` state as part of the same mutation flow

## Failure mode deltas
- Publishing before conjure would create half-real spell records with no stable
  owner conduit.
- Requiring Spellbook to maintain Nexus indexes directly would overcouple the
  producer to store internals.

## Dependency and ordering constraints
- Frame posture must be bound before `FrameRecord` publication
- Root conduit must exist before spell catch-up publication assigns
  `owner_conduit_id`
- `Spellbook.bind()` is the correct incremental spell publish point after
  conjure succeeds

## Validation expectations
- Existing local spells are catch-up published on conjure
- later bind-after-conjure publishes incrementally
- no pre-conjure spell publication in the first slice
- version-id changes keep canonical spell identity aligned with the active
  runtime version

## Unknowns and open decisions
- Whether spell removal/destruction should be included in the first spell
  publication slice or deferred to a later follow-up
