"""
TIER: expert (17)
GOAL: LINEAGES, AND THE STAGING HALF OF A HOT SWAP. An index is a
      version LINEAGE with exactly one SELECTED member. This lesson
      builds one, stages a second version onto it, and shows that
      staging changes nothing about what resolves - which is the whole
      reason the swap is a two-step act.

      THE THREE VERBS, AND WHERE THE USER SURFACE ENDS

        book.bind(...)                v1 active on a fresh index
        conduit.bind_inactive(...)    v2 PARKED on the same index
        conduit.notch_spell(...)      v2 becomes the active member

      THE FIRST TWO ARE YOURS. THE THIRD IS NOT DRIVEN BY HAND, and
      that is a design statement rather than a missing door.
      `notch_spell` takes the PARKED SPELL OBJECT, and there is no
      public way to get one: every public id->object lookup
      (`get_spell_by_id`, `find_spell_by_id`) resolves any lineage id to
      the spell AS IT EXISTS NOW - the currently ACTIVE member - which
      is documented and correct for what those verbs are for. The parked
      object lives in the Spellbook's private parking lot, and the
      Spellbook is not the surface you notch from. Melder's facade rule
      again: IF A FACADE COVERS IT, THE COLLABORATOR IS NOT USER
      SURFACE. Reaching past the facade to hand-drive a notch is using
      the wrong object, not discovering a gap.

      So this lesson stops where the public surface stops. Everything
      below runs; nothing below reaches into a private map.

      WHAT STAGING ACTUALLY BUYS YOU
      `bind_inactive` puts a real, bound, owned spell into the lineage
      and leaves the selection alone. The candidate is inert and
      unmeldable until something promotes it. That separation is what
      lets a swap be PREPARED long before it is TAKEN - the expensive,
      failure-prone half (compiling and registering a new version)
      happens while the old version is still serving.

      AND WHAT A NOTCH DOES WHEN IT HAPPENS (read, do not hand-drive)
        1. Parks the outgoing active spell off the four active owned
           maps, then TEARS DOWN ITS CREATION CONTEXT so the door epoch
           bumps and the warm fast-door cannot serve the stale spell.
        2. Promotes the parked candidate into the active maps.
        3. Repoints the index pointer and the framewide binding
           signature, old id -> new id.
        4. Re-registers the index gated + dirty, so revalidation
           recompiles LAZILY on the next resolve rather than inside the
           window.
      All of it happens under one seal, and the sealed conduits' creation
      gates are quiesced for the duration, so no in-flight meld can
      straddle the repoint. You do not arrange any of that; the verb
      does, the same way `link` does in expert 16.

      THE OUTGOING VERSION IS NOT DESTROYED. It stays a member of the
      lineage and stays resolvable by id, which is why a rollback is
      structurally the same act as the swap rather than a restore.

      MIND THE LAYER WHEN YOU READ THE SOURCE. `_apply_notch` says
      contracted borrowers are "NOT yet fanned out HERE (owner-side
      only)". That HERE is load-bearing: the seam is the local switch,
      and `Conduit.notch_spell` one layer up does walk the links. A
      statement read out of its scope becomes a false one.
SURFACE EXERCISED: Conduit.bind_inactive, SpellIndex.selected_spell_id /
                   spells_in_index, and the public boundary in front of
                   notch_spell
VERIFY: RUN GREEN 2026-08-03 on the owner's 3.14t harness.
"""
import melder as md


class HotSwapPricingV1:
    def __init__(self) -> None:
        self.rate = 100


class HotSwapPricingV2:
    def __init__(self) -> None:
        self.rate = 250


def main() -> None:
    book = md.Spellbook(aetheric_frame="hotswap-world")
    v1_id = book.bind(
        spell=HotSwapPricingV1, existence="unique", permissions="create",
    )
    conduit = book.conjure(dynamic=True, name="hotswap-root")
    print("v1 bound and active")

    # THE INDEX IS PUBLICLY REACHABLE from the active spell, and it is a
    # LINEAGE: a set of member ids plus exactly one selection.
    active = conduit.get_spell_by_id(v1_id)
    assert active is not None
    index = active.spell_index
    assert index.selected_spell_id == v1_id
    assert index.spells_in_index() == {v1_id}
    print("index: 1 member, selected =", v1_id[:12], "...")

    # v1 RESOLVES. This is the world as it stands.
    before = conduit.meld(spell=HotSwapPricingV1)
    assert before.rate == 100
    print("meld -> rate", before.rate)

    # STAGE A CANDIDATE. It is bound, owned, and a real member of the
    # lineage - and it changes nothing about what resolves.
    v2_id = conduit.bind_inactive(
        spell=HotSwapPricingV2,
        spell_index=index,
        existence="unique",
        permissions="create",
    )
    assert index.spells_in_index() == {v1_id, v2_id}
    assert index.selected_spell_id == v1_id, (
        "staging must NOT move the selection - preparing a swap and "
        "taking it are two different acts"
    )
    print()
    print("v2 staged: 2 members, selection UNCHANGED")

    # AND THE PARKED CANDIDATE IS INERT. The expensive half of the swap
    # has already happened - v2 is compiled, registered and owned - while
    # the old version is still the one serving traffic.
    still = conduit.meld(spell=HotSwapPricingV1)
    assert still.rate == 100
    print("meld -> rate", still.rate, " (v2 is parked, not resolvable)")
    print("  the costly half of a swap is done while v1 still serves")

    # THE PUBLIC BOUNDARY, DEMONSTRATED RATHER THAN ASSERTED IN PROSE.
    # A parked id resolves to the CURRENT member, because that is what
    # these verbs are for: they answer "what is live for this lineage",
    # not "give me the object behind this exact version".
    resolved_from_parked_id = conduit.get_spell_by_id(v2_id)
    assert resolved_from_parked_id is not None
    assert resolved_from_parked_id.spell_id == v1_id
    print()
    print("looking up the PARKED id returned the ACTIVE spell")
    print("  not a bug and not a gap - the parked object belongs to the")
    print("  Spellbook, and the Spellbook is not what you notch from")

    # SO THE LESSON STOPS HERE, ON PURPOSE.
    assert hasattr(conduit, "notch_spell")
    print()
    print("conduit.notch_spell(spell_index=, spell=) exists and is the")
    print("promoting verb; it takes the parked OBJECT, which no public")
    print("door hands out. Staging is yours; promotion is the runtime's.")

    print()
    print("an index is a lineage with one selection")
    print("staging adds a member; only a notch moves the selection")
    print("nothing is destroyed by a notch, which is why rolling back")
    print("is the same act and not a restore")


if __name__ == "__main__":
    main()
