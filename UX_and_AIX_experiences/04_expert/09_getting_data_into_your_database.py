"""
TIER: expert (09)
GOAL: THE ACTUAL ANSWER TO "HOW DO I GET MELDER STATE INTO MY DATABASE."

      Expert 02 showed the transport - handler-gated lanes, writes
      degrade, reads refuse. This is the crystallizer side: the verbs
      that decide WHAT crosses the boundary and WHEN.

      THE WIRING, IN ONE CALL
        crystallizer.configure_external_persistence_manager(...)
      One door. From then on the crystallizer owns the mesh and you never
      touch the manager again - which is why lesson 02's manager is not
      something you keep a reference to.

      WHAT ACTUALLY CROSSES, AND IT IS NOT "EVERYTHING"

        PUSH   flush_checkpoint(id)         seal locally, then ship
               store_index_graft_external   push one index graft
        PULL   reload_profile_from_external      history back
               reload_formations_from_external   formations back
               fetch_index_graft_external        one graft back
        LIST   list_index_grafts_external
        AGE    apply_external_retention

      NOTICE WHAT IS MISSING: there is no `sync()`. No "mirror
      everything". Every verb names a KIND of thing and a DIRECTION,
      because a persistence mesh that syncs opaquely is one you cannot
      reason about when it disagrees with itself.

      SEAL-THEN-SHIP IS ONE VERB WITH TWO GUARANTEES
      `flush_checkpoint` does the local seal AND the remote push - and
      advanced 18 already taught the sharp half: the remote leg is
      LENIENT BY DEFAULT, so a successful return proves THE LOCAL SEAL
      and nothing about your database. If you need remote confirmation,
      the return value of flush is not it.

      That is the same leniency lesson 02 measured from the transport
      side. Two lessons, two vantage points, one rule: LOCAL CUSTODY IS
      NEVER HOSTAGE TO A NETWORK YOU DO NOT OWN.

      RETENTION IS EXPLICIT
        apply_external_retention(...)
      Your database does not grow forever, and melder will not guess a
      policy. Ageing data out is a verb you call, not a background
      behaviour you discover.

      AND TWO DESCRIBE DOORS, WHICH IS NOT REDUNDANCY
        describe_external_persistence_manager()  what is WIRED
        describe_external_interface()            what the CONTRACT is
      One tells you the current attachment; the other tells you the shape
      your callables must satisfy. An operator debugging a mesh needs the
      first; someone implementing handlers needs the second.
SURFACE EXERCISED: Crystallizer external lane -
                   configure_external_persistence_manager, the push/pull/
                   list/retention verbs, the two describe doors
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


PUSH = ("flush_checkpoint", "store_index_graft_external")
PULL = ("reload_profile_from_external", "reload_formations_from_external",
        "fetch_index_graft_external")
LIST = ("list_index_grafts_external",)
AGE = ("apply_external_retention",)
DESCRIBE = ("describe_external_persistence_manager",
            "describe_external_interface")


def main() -> None:
    crystallizer = md.Crystallizer()
    config = md.CrystallizerConfigurationBuilder().with_defaults().activate()
    crystallizer.activate(config)
    assert crystallizer.activated is True
    print("crystallizer up")

    # ONE WIRING DOOR. After this the crystallizer owns the mesh.
    assert hasattr(crystallizer, "configure_external_persistence_manager")
    print("wiring door: configure_external_persistence_manager(...)")

    # THE VERBS, BY DIRECTION. Every one names a KIND and a DIRECTION.
    print()
    for label, verbs in (("PUSH", PUSH), ("PULL", PULL),
                         ("LIST", LIST), ("AGE ", AGE)):
        print(f"{label}:")
        for verb in verbs:
            assert hasattr(crystallizer, verb), verb
            print("   ", verb)

    # THE ABSENCE THAT MATTERS. No sync(), no mirror_all().
    for absent in ("sync", "mirror", "mirror_all", "sync_external",
                   "push_everything"):
        assert not hasattr(crystallizer, absent), (
            f"{absent} appeared - an opaque sync verb would make the mesh "
            f"impossible to reason about when it disagrees with itself"
        )
    print()
    print("there is NO sync() - every verb names a kind and a direction")

    # TWO DESCRIBE DOORS, different questions.
    for verb in DESCRIBE:
        assert hasattr(crystallizer, verb), verb
    wiring = crystallizer.describe_external_persistence_manager()
    contract = crystallizer.describe_external_interface()
    assert isinstance(wiring, dict)
    assert isinstance(contract, dict)
    print()
    print("describe_external_persistence_manager ->", len(wiring),
          "keys  (what is WIRED)")
    print("describe_external_interface           ->", len(contract),
          "keys  (what the CONTRACT is)")
    print("an operator debugging needs the first; a handler author the second")

    # SEAL-THEN-SHIP, with the guarantee stated honestly. With no manager
    # attached the remote leg has nothing to do and the local seal still
    # happens - which is the behaviour you want during an outage.
    checkpoint_id = crystallizer.create_checkpoint(description="expert-09")
    flushed = crystallizer.flush_checkpoint(checkpoint_id)
    assert isinstance(flushed, list)
    print()
    print("flush_checkpoint ->", flushed)
    print("  that return covers the LOCAL SEAL. it says nothing about")
    print("  your database - the remote leg is lenient by default.")

    print()
    print("local custody is never hostage to a network you do not own")
    print("retention is a verb you call, not a behaviour you discover")


if __name__ == "__main__":
    main()
