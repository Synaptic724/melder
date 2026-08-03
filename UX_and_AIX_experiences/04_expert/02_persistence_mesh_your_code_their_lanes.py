"""
TIER: expert (02)
GOAL: THE EXTERNAL MESH - how melder persists across a host boundary
      WITHOUT taking a database dependency.

      The whole design is one sentence from its own contract:

        "The USER owns storage bootstrap, credentials, durability, and
         handler synchronization; MELDER owns the value-shaped callable
         contract and failure accounting."

      So melder never talks to your database. It calls YOUR functions.
      You hand it callables; it hands them value-shaped payloads and
      counts what went wrong. That is the entire integration surface, and
      it is why the library still has zero dependencies while supporting
      an arbitrary storage backend.

      THE ASYMMETRY THAT MATTERS - WRITES AND READS FAIL DIFFERENTLY

        WRITE lanes (upload / store):
          Handler absent      -> silent NO-OP
          Handler raises      -> LENIENT BY DEFAULT; counted, not raised
        READ lanes (download / fetch):
          Handler absent      -> REFUSES LOUDLY

      Read that twice, because the inconsistency is deliberate and it is
      the most useful thing in this lesson.

      A write that cannot reach the remote must not destroy your LOCAL
      custody - you already have the data, and a network you do not
      control should not be able to fail your checkpoint. So writes
      degrade to counted failures.

      A READ with no handler is a different animal: the caller is asking
      for remote history from a pod that has no remote attached. There is
      no honest answer to return. Handing back an empty result would be a
      lie shaped like an answer (advanced 15), so it refuses.

      "Lenient by default" is a KNOB, not a law - strict mode re-raises
      user exceptions. Default lenient, because the common case is a pod
      that should keep running when the mesh is down.

      FAILURE ACCOUNTING IS THE PRICE OF LENIENCY.
      If writes swallow errors, you need a way to know they happened -
      `upload_failure_count` and `store_failure_count` are that way. A
      lenient system without counters is just a system that loses data
      quietly.

      AND THE WARNING WORTH REPEATING:
        "Handlers are LIVE USER CODE: they run OUTSIDE any
         PersistenceSystem lock."
      Your callable is not protected by melder's locking. If two boots
      race, your handler sees both. Synchronization on the storage side
      is yours - which the contract says up front rather than letting you
      discover it under load.
SURFACE EXERCISED: md.ExternalPersistenceManager,
                   md.ExternalPersistenceManagerConfiguration - the
                   handler-gated lanes, strictness, failure accounting
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


WRITE_LANES = ("upload_checkpoint", "store_unit")
READ_LANES = ("download_checkpoint", "download_profile", "fetch_unit")
INVENTORY_LANES = ("list_units", "delete_unit")
ACCOUNTING = ("upload_failure_count", "store_failure_count")
GATES = ("upload_enabled", "store_enabled", "has_store_handler",
         "stream_emissions_enabled")


def main() -> None:
    # THE SHAPE OF THE INTEGRATION. Everything here is a lane you supply
    # a callable for, a gate that tells you whether one is attached, or a
    # counter that tells you how often yours failed.
    print("WRITE lanes  (absent = silent no-op, error = counted):")
    for lane in WRITE_LANES:
        assert hasattr(md.ExternalPersistenceManager, lane), lane
        print("   ", lane)

    print("READ lanes   (absent = REFUSES loudly):")
    for lane in READ_LANES:
        assert hasattr(md.ExternalPersistenceManager, lane), lane
        print("   ", lane)

    print("inventory:")
    for lane in INVENTORY_LANES:
        assert hasattr(md.ExternalPersistenceManager, lane), lane
        print("   ", lane)

    # THE GATES. You can always ask whether a lane is actually wired,
    # which is what makes the silent write no-op survivable: the silence
    # is checkable rather than mysterious.
    print()
    print("gates - ask before you assume:")
    for gate in GATES:
        assert hasattr(md.ExternalPersistenceManager, gate), gate
        print("   ", gate)

    # THE COUNTERS. Leniency without accounting is just quiet data loss,
    # so the two write lanes each carry a failure count.
    print()
    print("failure accounting - the price of leniency:")
    for counter in ACCOUNTING:
        assert hasattr(md.ExternalPersistenceManager, counter), counter
        print("   ", counter)
    assert len(ACCOUNTING) == len(WRITE_LANES), (
        "every lenient write lane needs its own counter"
    )

    # describe() - the AIX door, same idea as the viewer's onboarding JSON
    # at advanced 13: ask the object what it is, do not infer it.
    assert hasattr(md.ExternalPersistenceManager, "describe")
    print()
    print("describe() present - the mesh reports its own wiring")

    # The configuration is its own exported type, and the manager owns a
    # FROZEN one - the mesh's shape cannot drift under a running pod.
    assert isinstance(md.ExternalPersistenceManagerConfiguration, type)
    print("configuration type exported and frozen once owned")

    print()
    print("melder calls YOUR callables - it never speaks to your database")
    print("writes degrade and count; reads refuse. the asymmetry is the point.")


if __name__ == "__main__":
    main()
