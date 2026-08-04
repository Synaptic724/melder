"""
TIER: expert (24)
GOAL: SEAL A WORLD, THEN UNFOLD IT AGAIN. Expert 01 taught the pod-boot
      ORDER; expert 09 taught what crosses the wire. This is the round
      trip itself - checkpoint a live world, put it in the cache, and
      unfold it back into the runtime.

      THE FIVE VERBS, IN ORDER
        create_checkpoint(profile, description) -> a ULID id
        describe_checkpoint(id)                 -> what got captured
        flush_checkpoint(id)                    -> seal it into the cache
        reload_cached_checkpoint(id)            -> cache back into ledger
        load_checkpoint(id)                     -> UNFOLD into the runtime
      Only the last one touches the live world. The first four move a
      record around; `load_checkpoint` is the boot verb.

      A RESTORE IS NOT A RESURRECTION, AND THE REPORT SAYS SO
      `load_checkpoint` hands back a RestoreReport carrying:
        status                      did it complete
        built counts                how many of each kind came back
        shortfall entries           what could NOT be rebuilt
        identity translation map    OLD id -> NEW id
      That last field is the one to understand. Rebuilt objects get NEW
      identities - the world that comes back is equivalent, not
      identical - and the map is how you follow one thing across a boot.
      Anything holding a raw pre-restore id and expecting it to still
      resolve is holding a stale address, and the map is the only honest
      way to translate it.

      SHORTFALLS ARE REPORTED, NOT HIDDEN
      A spell whose class can no longer be imported, a module that
      moved, a binding whose target is gone - each becomes a shortfall
      ENTRY rather than a silent omission. Expert 18's law at the boot
      grain: a restore that quietly dropped what it could not rebuild
      would look identical to a world that never had those things, and
      the second invites everyone downstream to invent.

      CHECKPOINTS ACCUMULATE; THEY NEVER OVERWRITE
      Every `create_checkpoint` mints a new ULID and
      `list_checkpoint_ids()` returns them in exact ledger creation
      order. There is no "the checkpoint" - there is a history of them,
      and an id is the whole handle.

      AND THE OPERATOR'S ONE-CALL VERSION
        md.CrystallizerBootstrap()
            .with_crystallizer_configuration(...)
            .with_profile(...)
            .with_pull_remote(False)
            .bootstrap()
      That is expert 01's flow: the same steps in a fixed sequence, for
      the case where you are starting a process rather than inspecting a
      round trip. Note `with_preflight_gate` is an ACCEPTED NO-OP - the
      knob still exists and does nothing, and its own docstring says so
      rather than pretending.
SURFACE EXERCISED: md.Crystallizer create_checkpoint /
                   describe_checkpoint / flush_checkpoint /
                   list_cached_checkpoint_ids / list_checkpoint_ids /
                   reload_cached_checkpoint / load_checkpoint, and
                   md.CrystallizerBootstrap
VERIFY: rides the owner's 3.14t harness; asserts are the contract.
"""
import melder as md


FRAME = "restore-world"


class Ledger:
    def __init__(self) -> None:
        self.entries = []


class Auditor:
    def __init__(self) -> None:
        self.checked = 0


def main() -> None:
    # Custody first - nothing is recorded into a crystallizer that is not
    # yet recording (expert 22's ordering law).
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )
    research = md.MutationResearch()
    configuration = research.create_configuration()
    configuration.with_defaults().activate()
    research.activate(configuration)
    print("custody recording:", crystallizer.activated)

    # A REAL WORLD with two spells and a live object.
    # A RECORDED WORLD MUST BE BORN CONFIGURED. With custody active, a
    # dynamic conjure REFUSES if any bind ran before the configuration
    # was finalized - the profile record and default bootstrap would
    # otherwise durably persist binds made against unsettled config.
    spellbook_configuration = (
        md.SpellbookConfiguration(FRAME).with_defaults().finalize()
    )
    book = md.Spellbook(aetheric_frame=FRAME,
                        configuration=spellbook_configuration)
    ledger_id = book.bind(spell=Ledger, existence="unique",
                          permissions="create", binding_name="restore-ledger")
    book.bind(spell=Auditor, existence="many",
              permissions="create", binding_name="restore-auditor")
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
    )
    conduit = book.conjure(name="restore-root")
    ledger = conduit.meld(spell=Ledger, binding_name="restore-ledger")
    ledger.entries.append("before the checkpoint")
    print("world up; ledger holds", len(ledger.entries), "entry")

    # 1. SEAL IT. A checkpoint is minted, not overwritten.
    first_id = crystallizer.create_checkpoint()
    second_id = crystallizer.create_checkpoint()
    assert first_id != second_id
    ledger_of_ids = crystallizer.list_checkpoint_ids()
    print()
    print("two checkpoints minted:", first_id[:10], "...,", second_id[:10])
    print("list_checkpoint_ids() ->", len(ledger_of_ids),
          "in ledger creation order")
    print("  checkpoints ACCUMULATE - there is no 'the' checkpoint, and")
    print("  the id is the whole handle")

    # 2. WHAT IS ACTUALLY IN ONE?
    described = crystallizer.describe_checkpoint(second_id)
    print()
    print("describe_checkpoint keys:", sorted(described)[:8])
    counts = described.get("captured_counts")
    if isinstance(counts, dict):
        live = {k: v for k, v in counts.items() if v}
        print("captured:", live)

    # 3. SEAL IT INTO THE CACHE. Advanced 18's warning still applies -
    #    the cache is FIFO bounded, so a flush can evict an older entry.
    flushed = crystallizer.flush_checkpoint(second_id)
    assert second_id in flushed
    cached = crystallizer.list_cached_checkpoint_ids()
    assert second_id in cached
    print()
    print("flushed ->", len(flushed), " cached now:", len(cached))

    # 4. CACHE BACK INTO THE LEDGER. This is history bookkeeping, not a
    #    world change - nothing has been unfolded yet.
    summary = crystallizer.reload_cached_checkpoint(second_id)
    assert isinstance(summary, dict)
    print("reload_cached_checkpoint -> the checkpoint's own summary")
    print("  still no live object touched; that is the NEXT verb")

    # 5. THE BOOT VERB. This one unfolds the record into the runtime.
    report = crystallizer.load_checkpoint(second_id)
    assert isinstance(report, dict)
    print()
    print("load_checkpoint -> RestoreReport keys:", sorted(report))
    print("   status:", report.get("status"))

    # THE IDENTITY TRANSLATION MAP is the field that changes how you
    # think about a restore.
    translation = None
    for key in ("identity_translation", "identity_translation_map",
                "translation_map", "identity_map"):
        if key in report:
            translation = report[key]
            print(f"   {key}: {len(translation)} remapped identities")
            break
    if translation is None:
        print("   (identity map under another key - see the keys above)")
    print("  rebuilt objects get NEW ids: the world that comes back is")
    print("  EQUIVALENT, not identical. A raw pre-restore id is a stale")
    print("  address, and this map is the only honest way to translate")

    # SHORTFALLS: what could not be rebuilt, named rather than dropped.
    for key in ("shortfall", "shortfalls", "shortfall_entries"):
        if key in report:
            entries = report[key]
            print()
            print(f"   {key}: {len(entries)} entr(y/ies)")
            for entry in list(entries)[:3]:
                print("      ", str(entry)[:88])
            print("  a restore that silently dropped what it could not")
            print("  rebuild would look exactly like a world that never")
            print("  had those things - so it names them instead")
            break

    # THE ORIGINAL SPELL STILL ANSWERS through the pre-restore handle we
    # kept, which is the point of holding OBJECTS rather than ids.
    assert ledger.entries == ["before the checkpoint"]
    print()
    print("the object we held across all of this is untouched:",
          ledger.entries)
    print("  ids go stale across a boot; the handle in your hand does not")

    # 6. THE OPERATOR'S ONE-CALL VERSION exists and is exported.
    assert hasattr(md, "CrystallizerBootstrap")
    print()
    print("md.CrystallizerBootstrap() is the pod-boot form of all of the")
    print("above - same steps, fixed order (expert 01). Note one of its")
    print("knobs, with_preflight_gate, is an ACCEPTED NO-OP that says so")
    print("in its own docstring rather than quietly doing nothing")

    print()
    print("seal, cache, reload, unfold - and only the last one is a boot")
    print("a restore rebuilds an EQUIVALENT world and hands you the map")


if __name__ == "__main__":
    main()
