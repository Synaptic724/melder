# Component Patch: NexusFrameManager Rooted Spellbook-Mediated Realization

## Before
- `NexusFrameManager.create(...)` ensures a frame directly through `Aether`.
- It binds configuration directly into the frame.
- It publishes descriptor/ACL state before rooted runtime creation.
- It only bootstraps a root conduit when `root_conduit_name` is present.
- It returns the frame object.

## After
- `NexusFrameManager` uses `Spellbook` as the realization surface for the
  Nexus-facing creation path.
- It conjures a root conduit by default.
- Root-conduit naming is explicit and caller-overridable.
- Descriptor/ACL/publication state is refreshed from the rooted result.
- The public Nexus-facing result is the rooted conduit, not the frame.

## Validation Expectation
- Focused frame-authoring tests prove the public Nexus/Rift-facing creation
  path is rooted, nameable, Spellbook-mediated, and conduit-returning.
