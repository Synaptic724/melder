"""
TIER: advanced (18)
GOAL: THE LOADING HALF - and the one place in melder where a successful
      return deliberately does NOT mean what you would assume.

      TWO PLACES A CHECKPOINT CAN LIVE
        created   an id exists in the running crystallizer
        cached    it has been SEALED to the local cache
      create_checkpoint() gives you the first. flush_checkpoint() moves
      it to the second - and, if a persistence manager is attached, tries
      to ship it onward too.

        flush_checkpoint(id=None) -> list[str]   seal, then ship
        list_cached_checkpoint_ids()             what is sealed locally
        reload_cached_checkpoint(id)  -> dict    read one back
        verify_checkpoint_chain(...)  -> dict    is the lineage intact
        delete_cached_checkpoint(id)  -> str     drop one

      NOW THE TWO WARNINGS, BOTH FROM MELDER'S OWN CONTRACT.

      1. A SUCCESSFUL FLUSH DOES NOT PROVE THE REMOTE RECEIVED ANYTHING.

         "THE REMOTE LEG IS LENIENT BY DEFAULT. Under the default posture
          an [error is tolerated and] a successful return does NOT prove
          the remote received anything - the local seal is [what you
          actually get]."

         Everywhere else in this tier melder refuses rather than
         substituting (lessons 06/13/14/17/18). HERE IT IS DELIBERATELY
         LENIENT, and the reason is sound: a network you do not control
         should not be able to fail your local checkpoint. But it means
         flush() returning cleanly guarantees the LOCAL SEAL and nothing
         about the remote.

         If you need remote confirmation, the return value of flush() is
         not it. Knowing which half of a two-part verb a return value
         covers is the difference between a backup and the belief in one.

      2. FLUSHING CAN EVICT SOMETHING ELSE.

         "The FIFO cap means an old cached checkpoint can be EVICTED AS A
          SIDE EFFECT."

         So flush is not purely additive. The cache is bounded, and
         sealing a new checkpoint may silently retire your oldest. If a
         specific checkpoint matters, do not assume it is still cached -
         list_cached_checkpoint_ids() is the check, and it is cheap.

      THE TIER'S CLOSING IDEA
      Every lesson from 09 onward has been about the same discipline:
      know exactly what a call promises. Two bits instead of one. Names
      instead of contents. A refusal instead of a partial application.
      And here, at the end, a verb that is honest about covering two legs
      with different guarantees.
SURFACE EXERCISED: flush_checkpoint, list_cached_checkpoint_ids,
                   reload_cached_checkpoint, verify_checkpoint_chain,
                   delete_cached_checkpoint
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


def main() -> None:
    crystallizer = md.Crystallizer()
    config = md.CrystallizerConfigurationBuilder().with_defaults().activate()
    crystallizer.activate(config)
    assert crystallizer.activated is True
    print("crystallizer up (builder.activate() - one terminator per rung)")

    # CREATED, not yet sealed.
    checkpoint_id = crystallizer.create_checkpoint(
        description="advanced lesson 18 - to be flushed",
    )
    print()
    print("created:", checkpoint_id)
    print("in create list:", checkpoint_id in crystallizer.list_checkpoint_ids())

    cached_before = crystallizer.list_cached_checkpoint_ids()
    assert isinstance(cached_before, list)
    print("cached before flush:", len(cached_before))

    # SEAL, THEN SHIP. One verb, two legs, different guarantees.
    flushed = crystallizer.flush_checkpoint(checkpoint_id)
    assert isinstance(flushed, list)
    print()
    print("flush_checkpoint ->", flushed)
    print("  ^ this return covers the LOCAL SEAL.")
    print("    it does NOT prove a remote received anything.")

    cached_after = crystallizer.list_cached_checkpoint_ids()
    assert isinstance(cached_after, list)
    print("cached after flush:", len(cached_after))

    # THE CACHE IS BOUNDED. Do not assume; ask. This is cheap and it is
    # the only honest way to know a specific checkpoint survived.
    still_there = checkpoint_id in cached_after
    print("our checkpoint still cached:", still_there)
    if not still_there:
        print("  (FIFO cap evicted it - which the contract warns about)")

    # READ ONE BACK. The id remains the whole handle.
    if still_there:
        reloaded = crystallizer.reload_cached_checkpoint(checkpoint_id)
        assert isinstance(reloaded, dict)
        print()
        print("reload_cached_checkpoint ->", len(reloaded), "keys")
        print("  keys:", sorted(reloaded)[:6])

    # IS THE LINEAGE INTACT? Checkpoints form a chain, not a pile.
    chain = crystallizer.verify_checkpoint_chain()
    assert isinstance(chain, dict)
    print()
    print("verify_checkpoint_chain ->", len(chain), "keys")
    print("  keys:", sorted(chain)[:6])

    # DROPPING ONE IS EXPLICIT. Eviction is a side effect; deletion is a
    # decision - and the two should never be confused.
    if still_there:
        deleted = crystallizer.delete_cached_checkpoint(checkpoint_id)
        assert isinstance(deleted, str)
        assert checkpoint_id not in crystallizer.list_cached_checkpoint_ids()
        print()
        print("delete_cached_checkpoint ->", deleted)
        print("deletion is a DECISION; eviction is a SIDE EFFECT")

    print()
    print("know which leg of a two-part verb the return value covers")
    print("a bounded cache means 'I flushed it' is not 'it is still there'")


if __name__ == "__main__":
    main()
