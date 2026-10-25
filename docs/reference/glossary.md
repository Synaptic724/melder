# Glossary

Use these terms to choose the right boundary before choosing an API.

```{eval-rst}
.. glossary::
   :sorted:

   Aether
      The process-level root that hosts frames and shared runtime services.

   Aetheric frame
      A live world with its own runtime registries, posture, and instance isolation.
      Frame isolation does not namespace spell identity: a spell ID is the object's code,
      so one class bound in two frames is one spell.

   Bind
      Register a class, callable, or existing object and its address/lifetime policy.

   Binding name
      The named slot within a spellframe address. Supply it consistently when resolving.

   Campaign
      Attribution for a particular effort across research history. Eligible writes can
      inherit the active campaign; an unfiltered history query has a different default.

   Checkpoint
      A recorded structural checkpoint identified in ledger creation order. Creating it
      in memory, sealing it locally, and restoring a world from it are separate operations.

   Composition
      An informational set of pinned spell versions, with identity derived from membership.
      Recomposition produces a successor without overwriting the previous roster.

   Conduit
      A runtime scope used to resolve objects. A book conjures one root; lesser conduits
      create narrower scopes. Links connect eligible conduits within the same frame.

   Conjure
      Compile and validate a book's graph, then create its one root conduit.

   Contract
      A relationship governing selected sharing between conduits. The borrower pulls
      a spell from the conduit that owns it after the relationship is linked.

   Crystallizer
      The structural recording, custody, checkpoint, and restore surface.

   Disposal
      Calling configured teardown methods when the owning runtime ends its managed lifetime.
      Application references and ownership still need an explicit lifecycle policy.

   Existence
      The instance reuse and lifetime policy selected for a bound spell.

   Managed spell
      A spell bound with the ``managed_spell_quantity`` existence. Meld leases its objects from
      a pool the owning root keeps; ``ReleaseManagedSpell`` gives them back for reuse.

   Meld
      Resolve an addressed spell into an object according to its graph and existence policy.

   MutationResearch
      The version, lane, residency, composition, and derived comparison/impact record.

   Nexus
      The root of the mediated Rift/room access surface.

   Notch
      Promote a member of a SpellIndex, named by its spell_id, into its selected
      position. Staging a candidate is a separate act. Every member is bound the way the
      index's first version was, so a notch moves the selection, never the address.

   Override
      A mapping of constructor inputs or graph socket targets supplied to meld. The
      lifetime of an object constructed with it still follows that object's existence policy.

   Persistence profile
      A named content window receiving structural emissions. The process checkpoint ledger
      and research-set residency are separate from this partition.

   Posture
      The configured operational policy of a world or room, established through its
      applicable setup and activation sequence.

   Research set
      One independent body of version history, lanes, and residency over the runtime.

   Rift
      A named mediated session that owns one room and explicitly attaches to eligible frames.

   Spell
      A bound object's runtime registration metadata, identity, and lifecycle contract.

   Spell ID
      The SHA256 of a registered object's code: its methods and constructor, class-level
      values and bases, or an existing object's class and data. Nothing from the bind call
      enters it, so one object registers once; how it is bound has its own binding hash.

   SpellContract
      A late-bound dependency socket filled through linking, a borrower pull, and resolution.

   Spellframe
      The category half of a spell's address inside a world. It is not an aetheric frame.

   SpellIndex
      A stable index containing spell members and one current selection. It keeps its
      first version's binding - the kind of spellframe and the address - and admits
      only versions bound the same way.

   SpellMap
      An explicit dependency target, commonly supplied as a constructor parameter default.

   SpellSpace
      A narrower resolution scope supporting the unique-per-spell-space lifetime.

   Synthetic module
      An importable module whose source is carried in the recorded material rather than a file.

   Workstation
      A room-local store of named objects, attributes, methods, and one active target.
      It holds supplied handles; world resolution belongs to the owning command surface.
```

[Full contents](../contents.md) · [API reference](api.md) · [Troubleshooting](troubleshooting.md)
