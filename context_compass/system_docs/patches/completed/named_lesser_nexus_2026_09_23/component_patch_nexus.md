# Nexus named-scope publication and consumers

## Before / After
Previously only fresh lesser allocation published. Pooled acquisitions retained old payloads and
named command lookup authorized a descriptor ID but resolved a root-only runtime name. Now named
attachment publishes current topology, soft return retains an unnamed pooled record and name lookup
resolves the exact authorized ID through the established lesser-aware resolver.

## Interfaces
- Private Conduit/Nexus/FrameDescriptorManager conduit publication accepts pooled=False. True builds
  a cleared payload for an existing record only, retaining ID/root/Book ownership metadata.
- CommandSystem adds a private name resolver, sharing raw/frame/id ACL admission with the ID resolver.
- CapabilityCommandSystem.create_lesser_conduit gains name: Optional[str] = None, keyword-only.
- Public Conduit creation, Cloud and Rift refresh APIs remain unchanged.

## State / Failure
Soft return: name None, state pooled_lesser, parent None, depth zero, peers empty. No name remains
in frame Cloud summaries. Same-ID named reuse replaces this payload under current parent ownership.
Anonymous pooled cycles keep their established non-publication behavior; these are publication
snapshots, not leases or a new real-time registry of every anonymous scope operation.
Publication exceptions propagate before final name clearing/detachment; retry still has an owner.

## Validation
Exercise prewarmed/fresh named creation, A -> pooled -> B under a different parent, callback-driven
reuse, nested cleanup, hard deletion/explicit refresh, promotion, both command modes, denied ACLs,
static access refusal, stale names and recorded restore. Preserve unnamed sink-spy regressions.
