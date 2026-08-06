"""
TIER: expert (09)
GOAL: PUT YOUR WORLD IN YOUR OWN DATABASE - and notice what melder does
      NOT do to get it there. This wires a real mesh, seals a real
      checkpoint, and watches the bytes arrive.

      MELDER NEVER IMPORTS YOUR DATABASE. The whole external lane is four
      callables you write:

        store(kind, profile_name, unit_id, payload) -> None
        fetch(kind, unit_id)                        -> payload | None
        list_units(kind, profile_name)              -> iterable of ids
        delete(kind, unit_id)

      The contract says it plainly: "one callable, one table with a kind
      column, any DB stack - melder never imports it." There is no driver,
      no dialect, no connection string anywhere in the library. `kind` is
      "checkpoint" / "formation" / "emission", so ONE table with a kind
      column carries the entire mesh if you want it to.

      CALLABLES LIVE OUTSIDE THE RECORD, AND THAT IS A LAW WITH A REASON.
      Handlers go in a SEPARATE configuration object, and the record
      "expose[s] handler PRESENCE flags, never callable objects". Why:
      executable code cannot be serialized into a world record, so a
      recorded world stays CODE-FREE AND PORTABLE. A record that embedded
      your storage code would only be restorable somewhere that code
      already ran.

      AN EMPTY CONFIGURATION WILL NOT FREEZE, ON PURPOSE. Upload-on-flush
      defaults True, so a configuration with no write handler is
      incoherent - it promises to upload with nothing to upload through.
      A READ-ONLY deployment must therefore say so out loud by disabling
      upload-on-flush. The default refuses to let you be vague.

      SEAL-THEN-SHIP IS ONE VERB WITH TWO GUARANTEES, AND ONLY ONE OF THEM
      IS YOURS. `flush_checkpoint` does the local seal AND the remote push,
      and the remote leg is LENIENT BY DEFAULT: a successful return proves
      THE LOCAL SEAL and nothing about your database. So this lesson
      ASSERTS the local seal and only REPORTS what the mesh saw - because
      asserting the remote would be teaching you to trust the one half the
      return value does not cover.
      That is the same rule from the other side: LOCAL CUSTODY IS NEVER
      HOSTAGE TO A NETWORK YOU DO NOT OWN.

      AND TWO DESCRIBE DOORS, WHICH IS NOT REDUNDANCY
        describe_external_persistence_manager()  what is WIRED
        describe_external_interface()            what the CONTRACT is
      An operator debugging a mesh needs the first; someone implementing
      handlers needs the second. Neither performs a network call.
SURFACE EXERCISED: ExternalPersistenceManagerConfiguration with real
                   store/fetch/list_units handlers,
                   configure_external_persistence_manager,
                   create_checkpoint / flush_checkpoint through the mesh,
                   both describe doors, and the absence of any sync verb
VERIFY: rewritten 2026-08-05 to WIRE a mesh instead of listing verbs;
        not yet re-run.
"""
import melder as md


FRAME = "mesh-world"

# "Your database". A dict, in memory - because the point is that melder
# does not care what this is. Swap it for sqlite, postgres or S3 and not
# one line of melder changes.
DATABASE: dict[tuple[str, str], dict] = {}
WRITES: list[tuple[str, str, str]] = []


def store(kind: str, profile_name: str, unit_id: str, payload: dict) -> None:
    """One table with a kind column. That is the entire integration."""
    DATABASE[(kind, unit_id)] = payload
    WRITES.append((kind, profile_name, unit_id))


def fetch(kind: str, unit_id: str):
    """None means `unknown remotely` - a real answer, not an error."""
    return DATABASE.get((kind, unit_id))


def list_units(kind: str, profile_name: str):
    return [unit for (k, unit) in DATABASE if k == kind]


class Ledger:
    def __init__(self) -> None:
        self.entries: list[str] = []


def main() -> None:
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )

    # THE HANDLERS GO IN THEIR OWN OBJECT, never into the record.
    mesh = md.ExternalPersistenceManagerConfiguration()
    mesh.with_store_handler(store)
    mesh.with_fetch_handler(fetch)
    mesh.with_list_units_handler(list_units)
    crystallizer.configure_external_persistence_manager(mesh)
    print("mesh attached - melder now has four callables and no idea what")
    print("is behind them")

    # WHAT IS WIRED vs WHAT THE CONTRACT IS. Two questions, two doors,
    # neither one a network call.
    wiring = crystallizer.describe_external_persistence_manager()
    contract = crystallizer.describe_external_interface()
    assert isinstance(wiring, dict) and isinstance(contract, dict)
    assert wiring.get("attached") is True, wiring
    print()
    print("describe_external_persistence_manager ->", len(wiring),
          "keys (what is WIRED)")
    print("describe_external_interface           ->", len(contract),
          "keys (what the CONTRACT is)")

    # PRESENCE FLAGS, NEVER CALLABLES. Search the whole record payload for
    # anything callable - a recorded world has to stay code-free.
    leaked = [key for key, value in wiring.items() if callable(value)]
    assert not leaked, "the record leaked a callable: %s" % leaked
    print("  the wiring record holds no callable objects - only presence")
    print("  flags, because executable code cannot be serialized into a")
    print("  world record and a record that embedded yours would only")
    print("  restore where that code already ran")

    # A WORLD WORTH SEALING.
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
              binding_name="mesh-ledger")
    book.conjure(name="mesh-root")

    # SEAL, THEN SHIP - one verb, two guarantees, one of them yours.
    checkpoint_id = crystallizer.create_checkpoint()
    assert checkpoint_id in crystallizer.list_checkpoint_ids()
    flushed = crystallizer.flush_checkpoint(checkpoint_id)

    # THE LOCAL SEAL IS THE PART THE RETURN VALUE COVERS. Assert it.
    assert checkpoint_id in flushed, flushed
    assert checkpoint_id in crystallizer.list_cached_checkpoint_ids()
    print()
    print("flush_checkpoint ->", checkpoint_id[:14], "...")
    print("  LOCAL SEAL asserted: it is in the cache, on this machine")

    # THE REMOTE LEG IS LENIENT, so this is REPORTED and not asserted.
    # Teaching you to assert it would be teaching you to trust the half
    # the return value does not cover.
    print("  your database received", len(WRITES), "unit(s):")
    for kind, profile_name, unit_id in WRITES[:4]:
        print("     kind=%-11s profile=%-10s unit=%s"
              % (kind, profile_name, unit_id[:14]))
    print("  reported, NOT asserted - the remote leg is lenient by")
    print("  default, so a clean return proves the local seal and nothing")
    print("  about your storage. Local custody is never hostage to a")
    print("  network you do not own. If you need remote confirmation, the")
    print("  return value of flush is not it - strict uploads are")

    # AND THE ABSENCE THAT MATTERS. No sync(), no mirror_all().
    for absent in ("sync", "mirror", "mirror_all", "sync_external",
                   "push_everything"):
        assert not hasattr(crystallizer, absent), (
            "%s appeared - an opaque sync verb would make the mesh "
            "impossible to reason about when it disagrees with itself"
            % absent
        )
    print()
    print("there is NO sync() - every verb names a KIND and a DIRECTION,")
    print("so when the two sides disagree you can say which way the last")
    print("byte was travelling. `sync` cannot answer that question.")

    print()
    print("four callables, one kind column, zero database imports")


if __name__ == "__main__":
    main()
