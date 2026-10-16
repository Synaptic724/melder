"""
TIER: expert (17)
GOAL: LINEAGES, AND A HOT SWAP TAKEN END TO END. An index is a
      version LINEAGE with exactly one SELECTED member. This lesson
      builds one, stages a second version onto it, shows that staging
      changes nothing about what resolves - which is why the swap is a
      two-step act - then takes the swap by the new version's spell_id,
      melds it, and notches back. Everything runs on public calls.

      THE THREE VERBS

        book.bind(...)                v1 active on a fresh index
        conduit.bind_inactive(...)    v2 PARKED on the same index;
                                      returns v2's spell_id
        conduit.notch_spell(          v2 becomes the active member
            spell_index=index, spell_id=v2_id)

      NAME THE VERSION BY ITS SPELL_ID. Every public spell_id->object
      lookup (`get_spell_by_id`, `find_spell_by_id`) resolves any
      lineage spell_id to the spell AS IT EXISTS NOW - the currently
      ACTIVE member - which is documented and correct for what those
      verbs are for. So a parked version is never fetched as an
      object: `notch_spell` takes its spell_id and resolves the exact
      version inside the call. The Spellbook is still not the surface
      you notch from - the conduit's verb does the resolving (owner
      ruling 2026-10-16; until then the verb took only the parked
      OBJECT, no public door handed one out, and this lesson stopped
      at staging).

      WHAT STAGING ACTUALLY BUYS YOU
      `bind_inactive` puts a real, bound, owned spell into the lineage
      and leaves the selection alone. The candidate is inert and
      unmeldable until something promotes it. That separation is what
      lets a swap be PREPARED long before it is TAKEN - the expensive,
      failure-prone half (compiling and registering a new version)
      happens while the old version is still serving.

      AND WHAT A NOTCH DOES WHEN IT HAPPENS
        0. Checks the version: it must belong to the conduit's
           Spellbook and to the index you passed, or the call raises
           ValueError before anything moves.
        1. Parks the outgoing active spell off the four active owned
           maps, then TEARS DOWN ITS CREATION CONTEXT so the door epoch
           bumps and the warm fast-door cannot serve the stale spell.
        2. Promotes the parked candidate into the active maps.
        3. Repoints the index pointer and the framewide binding
           signature, old spell_id -> new spell_id.
        4. Re-registers the index gated + dirty, so revalidation
           recompiles LAZILY on the next resolve rather than inside the
           window.
      All of it happens under one seal, and the sealed conduits' creation
      gates are quiesced for the duration, so no in-flight meld can
      straddle the repoint. You do not arrange any of that; the verb
      does, the same way `link` does in expert 16.

      THE OUTGOING VERSION IS NOT DESTROYED. It stays a member of the
      lineage, parked, which is why a rollback is structurally the same
      act as the swap - a notch back by its spell_id - rather than a
      restore.

      MIND THE LAYER WHEN YOU READ THE SOURCE. `_apply_notch` says
      contracted borrowers are "NOT yet fanned out HERE (owner-side
      only)". That HERE is load-bearing: the seam is the local switch,
      and `Conduit.notch_spell` one layer up does walk the links. A
      statement read out of its scope becomes a false one.
SURFACE EXERCISED: Conduit.bind_inactive, Conduit.notch_spell(spell_id=...),
                   Conduit.meld, SpellIndex.selected_spell_id /
                   spells_in_index, Conduit.get_spell_by_id
VERIFY: RUN GREEN 2026-10-16 on 3.14t, GIL off and on.
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
    before = conduit.meld("HotSwapPricingV1")
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
    still = conduit.meld("HotSwapPricingV1")
    assert still.rate == 100
    print("meld -> rate", still.rate, " (v2 is parked, not resolvable)")
    print("  the costly half of a swap is done while v1 still serves")

    # WHY THE NOTCH IS GIVEN A SPELL_ID. A parked spell_id resolves to
    # the CURRENT member, because that is what the lookups are for: they
    # answer "what is live for this lineage", not "give me the object
    # behind this exact version".
    resolved_from_parked_id = conduit.get_spell_by_id(v2_id)
    assert resolved_from_parked_id is not None
    assert resolved_from_parked_id.spell_id == v1_id
    print()
    print("looking up the PARKED spell_id returned the ACTIVE spell")
    print("  so the notch is told the version by its spell_id instead")

    # TAKE THE SWAP. The spell_id bind_inactive returned names the version;
    # the notch resolves it inside the call and checks that it belongs to
    # this index before anything moves.
    promoted = conduit.notch_spell(spell_index=index, spell_id=v2_id)
    assert promoted.spell_id == v2_id
    assert index.selected_spell_id == v2_id
    assert index.spells_in_index() == {v1_id, v2_id}, (
        "a notch moves the selection; it removes no member"
    )
    after = conduit.meld(spell_id=v2_id)
    assert after.rate == 250
    print()
    print("notch by spell_id: v2 selected, meld -> rate", after.rate)

    # ROLL BACK: the same verb pointed the other way, because v1 was
    # parked, not destroyed.
    conduit.notch_spell(spell_index=index, spell_id=v1_id)
    assert index.selected_spell_id == v1_id
    back = conduit.meld(spell_id=v1_id)
    assert back.rate == 100
    print("notch back by spell_id: v1 selected, meld -> rate", back.rate)

    print()
    print("an index is a lineage with one selection")
    print("staging adds a member; only a notch moves the selection")
    print("nothing is destroyed by a notch, which is why rolling back")
    print("is the same act and not a restore")


if __name__ == "__main__":
    main()
