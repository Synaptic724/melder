"""
TIER: expert (02)
GOAL: THE ASYMMETRY AT THE EDGE OF YOUR WORLD, demonstrated rather than
      described. Melder never speaks to your database - it calls YOUR
      callables. So the interesting question is what happens when one of
      them is missing or broken, and the answer is deliberately different
      for writes and reads.

        WRITES DEGRADE AND COUNT.  A missing write lane is a silent
          no-op. A write lane that RAISES is swallowed and TALLIED. Your
          local seal never fails because a network you do not own did.
        READS REFUSE.  A missing read lane raises. "A missing lane means
          UNAVAILABLE, NOT EMPTY" - because an empty answer would be
          indistinguishable from "your remote has nothing", and that is
          the one reply that must never be guessed.

      LENIENCY WITHOUT ACCOUNTING IS JUST QUIET DATA LOSS. That is why
      the manager carries `upload_failure_count` and `store_failure_count`
      and puts them in `describe_external_persistence_manager()`. Your
      handler is allowed to fail; you are not allowed to be unaware of it.

      AND CALLABLES NEVER ENTER THE RECORD. Handlers live in a separate
      configuration and the description "expose[s] handler PRESENCE flags,
      never callable objects", because executable code cannot be
      serialized into a world record. A recorded world stays code-free and
      portable, which is what lets it be restored somewhere your storage
      code has never run.

      LOCAL CUSTODY IS NEVER HOSTAGE TO A NETWORK YOU DO NOT OWN. Expert
      09 shows the same rule from the wiring side; this lesson is the
      failure side of it.
SURFACE EXERCISED: ExternalPersistenceManagerConfiguration store/fetch/
                   list handlers, configure_external_persistence_manager,
                   flush_checkpoint through a working and then a FAILING
                   handler, reload_profile_from_external with no read
                   lane, and the failure counters in the describe payload
VERIFY: rewritten 2026-08-05 to DEMONSTRATE the asymmetry it previously
        only asserted in prose; not yet run.
"""
import melder as md


FRAME = "mesh-edge-world"

WRITTEN: list = []


def store_ok(kind: str, profile_name: str, unit_id: str,
             payload: dict) -> None:
    WRITTEN.append((kind, unit_id))


def store_broken(kind: str, profile_name: str, unit_id: str,
                 payload: dict) -> None:
    raise IOError("the database is on fire")


class Ledger:
    def __init__(self) -> None:
        self.entries: list = []


def _mesh(store_handler):
    configuration = md.ExternalPersistenceManagerConfiguration()
    configuration.with_store_handler(store_handler)
    return configuration


def main() -> None:
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )

    spellbook_configuration = (
        md.SpellbookConfiguration(FRAME).with_defaults().finalize()
    )
    book = md.Spellbook(aetheric_frame=FRAME,
                        configuration=spellbook_configuration)
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
        ai_native=True,
    )
    book.bind(spell=Ledger, existence="unique", permissions="create",
              binding_name="mesh-edge-ledger")
    book.conjure(name="mesh-edge-root")

    # A WRITE LANE ONLY. No fetch handler, no list handler - deliberately
    # a half-wired mesh, which is the whole subject of this lesson.
    crystallizer.configure_external_persistence_manager(_mesh(store_ok))
    wiring = crystallizer.describe_external_persistence_manager()
    assert wiring["attached"] is True
    print("mesh attached with a WRITE lane and no read lane")
    print("  and the record holds no callables - only presence flags:")
    assert not [k for k, v in wiring.items() if callable(v)]
    print("   ", sorted(k for k in wiring if "handler" in k or "enabled" in k))

    # THE WRITE LANE WORKS.
    checkpoint_id = crystallizer.create_checkpoint()
    flushed = crystallizer.flush_checkpoint(checkpoint_id)
    assert checkpoint_id in flushed
    print()
    print("flush_checkpoint ->", checkpoint_id[:14], "...")
    print("  your store handler received", len(WRITTEN), "unit(s)")

    # THE READ LANE IS MISSING, AND IT REFUSES. This is the half that
    # does NOT degrade quietly.
    try:
        crystallizer.reload_profile_from_external("default")
        raise AssertionError("a missing read lane must refuse, not answer")
    except RuntimeError as unavailable:
        print()
        print("reload_profile_from_external with no fetch/list lane:")
        print("  ", str(unavailable)[:96])
        print("  UNAVAILABLE is not EMPTY. An empty answer here would be")
        print("  indistinguishable from `your remote has nothing`, and")
        print("  that is the one reply that must never be guessed")

    # NOW A WRITE LANE THAT FAILS. Re-configuring replaces the manager,
    # so the counters below start clean.
    crystallizer.configure_external_persistence_manager(_mesh(store_broken))
    before = crystallizer.describe_external_persistence_manager()
    assert before["store_failure_count"] == 0, before
    print()
    print("re-wired with a handler that raises. store_failure_count:",
          before["store_failure_count"])

    # THE LOCAL SEAL STILL SUCCEEDS. That is the guarantee.
    second_id = crystallizer.create_checkpoint()
    flushed_again = crystallizer.flush_checkpoint(second_id)
    assert second_id in flushed_again, (
        "the LOCAL seal must not fail because a remote handler raised"
    )
    assert second_id in crystallizer.list_cached_checkpoint_ids()
    print("flush_checkpoint ->", second_id[:14], "... returned CLEANLY")
    print("  and it is in the local cache. Your handler raised IOError and")
    print("  the local custody did not care - that is the guarantee")

    # AND THE FAILURE WAS COUNTED. Leniency with a receipt.
    after = crystallizer.describe_external_persistence_manager()
    assert after["store_failure_count"] > 0, after
    print()
    print("store_failure_count:", before["store_failure_count"], "->",
          after["store_failure_count"])
    print("  leniency without accounting is just quiet data loss. The")
    print("  write was allowed to fail; you were not allowed to be")
    print("  unaware of it. If you need the failure to be LOUD instead,")
    print("  that is what strict uploads are for.")

    print()
    print("writes degrade and COUNT; reads REFUSE")
    print("melder called your callables and never touched your database")


if __name__ == "__main__":
    main()
