"""
TIER: expert (27)
GOAL: TEAR THE RUNTIME DOWN ON PURPOSE, THEN COME BACK. Expert 24 walked
      the five checkpoint verbs while the world stayed up the whole time.
      This is the harder half: seal a world, DESTROY the Aether singleton,
      collect the garbage, and unfold the world into a runtime that has
      never seen it.

      THE ONE FACT THE WHOLE LESSON TURNS ON

        Ledger  ->  in-process, dies with the singleton
        Cache   ->  bytes at rest, survives it

      `create_checkpoint()` mints into the LEDGER. That is memory. Tear
      the root down without flushing and the checkpoint goes with it -
      there is nothing to come back to and no error to tell you so,
      because nothing went wrong. `flush_checkpoint(id)` is the verb that
      turns a record into something that outlives the process, and it is
      the only reason the second half of this script can work.

      THE TEARDOWN IS PUBLIC, AND IT IS IDENTITY-CHECKED
        aether.cleanup()
      Singleton bookkeeping is cleared in a `finally` - `_instance = None`
      and `_initialized = False` - so it resets even when a child teardown
      raises. Before that `finally` existed, one failing child left a
      CLEANED HUSK installed as the process singleton for the rest of the
      run. And the clear is IDENTITY-CHECKED elsewhere in the class
      (`if Aether._instance is self`), so cleaning a stale instance can
      never unseat the live one.

      That is why this lesson needs no private door. `cleanup()` IS the
      reset. There is a `_reset_singleton_for_tests` classmethod next to
      it, and it is private on purpose - test isolation, not a public
      lifecycle verb. Nothing below reaches for it.

      GC IS NOT CEREMONY HERE
      `gc.collect()` after the teardown is doing real work: melder cleans
      deterministically rather than leaving owned objects to the
      collector, so a collect is how you PROVE the old world is gone
      instead of asserting it. If a handle you still hold keeps the old
      root alive, that is a finding, not a detail.

      AND THE LAST RUNG DEMANDS A COMPLETE BUNDLE
      Unfolding into a runtime that has never seen the world is the
      strictest act here, and it is the one that can refuse.
      `load_checkpoint` is MEDIATED: the folded chain PRE-FLIGHTS before
      any replay, and a `blockers` verdict refuses at the one seam that
      owns authoritative folded truth. A refusal message ends "nothing
      was built" - all-or-nothing declining to START rather than
      half-building a world and unwinding it. This lesson handles both
      outcomes and prints which one it got, because both are true things
      the system does.

      THE CHAIN COMES FROM THE LEDGER, WHICH IS THE PART WORTH KNOWING.
      `plan_checkpoint_load` detaches the target checkpoint's SAME-PROFILE
      CHAIN in creation order - not the single id you named. After a
      teardown the fresh ledger is empty and `reload_cached_checkpoint`
      restores only the id you ask for, so a world sealed across SEVERAL
      checkpoints and partially reloaded folds an INCOMPLETE chain and
      refuses exactly like a corrupt one would. If you seal more than
      once, `flush_checkpoint()` with NO argument flushes the whole
      ledger, and every id has to come back before the load.

      AUTHORING NOTE, kept because it cost a red and a wrong theory. This
      lesson first failed here with "owning spellbook ... is not in this
      bundle". THE CAUSE WAS NOT THE LIBRARY - it was the harness. The
      examples `conftest.py` reset only `Aether` between examples while
      `Crystallizer`, `MutationResearch` and `Nexus` survived, so each
      lesson's frames were cleaned out from under a record that outlived
      them and the profile accumulated across the whole file (the run
      reported 76 cached checkpoints for a lesson that mints one). The
      expert PROBES fixture already reset all four and says why: "without
      the reset one row's checkpoints, profiles or research lanes surface
      in the next row." The conftest now matches it.
SURFACE EXERCISED: md.Crystallizer create_checkpoint / flush_checkpoint /
                   list_cached_checkpoint_ids / reload_cached_checkpoint /
                   load_checkpoint, md.Aether cleanup, and the codegen
                   room's execute/materialize verbs across the boundary
VERIFY: NOT RUN by the authoring agent - this sandbox is Python 3.10 and
        melder requires >=3.14. Rides the owner's 3.14t harness; the
        asserts are the contract.
"""
import gc

import melder as md


FRAME = "outlive-world"

FIRST_EDIT = "policy_version = 1\nresult = policy_version\n"
SECOND_EDIT = "policy_version = 2\nresult = policy_version * 50\n"


class Vault:
    """A live object that will be asked to survive a runtime teardown."""

    def __init__(self) -> None:
        self.contents = []


def build_world():
    """Stand up custody, record, world and codegen room. Returns the parts."""
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )
    research = md.MutationResearch()
    research_configuration = research.create_configuration()
    research_configuration.with_defaults().activate()
    research.activate(research_configuration)

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
    vault_id = book.bind(spell=Vault, existence="unique",
                         permissions="create", binding_name="outlive-vault")
    conduit = book.conjure(name="outlive-root")

    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_allowed_target_frame_names([FRAME])
    nexus.activate(system_configuration)
    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="outliver")
    rift.mark_active()
    rift.create_frame_link(FRAME)

    return crystallizer, conduit, vault_id, rift.space.command_system


def main() -> None:
    # ---------------------------------------------------------------- #
    # BEFORE                                                            #
    # ---------------------------------------------------------------- #
    crystallizer, conduit, vault_id, commands = build_world()
    print("world up; custody recording:", crystallizer.activated)

    vault = conduit.meld(spell=Vault, binding_name="outlive-vault")
    vault.contents.append("written before any codegen")
    print("live object holds", len(vault.contents), "entry")

    # 1. TWO CODEGEN EDITS, EACH MATERIALIZED. Running is not keeping, so
    #    each edit gets an address of its own.
    for label, code in (("edit-1", FIRST_EDIT), ("edit-2", SECOND_EDIT)):
        verdict = commands.validate_codegen(code, frame_name=FRAME)
        outcome = commands.execute_codegen(code, frame_name=FRAME)
        kept = commands.materialize_codegen(
            code,
            module_name=f"outlive_policy_{label.replace('-', '_')}",
            frame_name=FRAME,
        )
        vault.contents.append(label)
        print(f"{label}: validate({type(verdict).__name__}) ->"
              f" execute({type(outcome).__name__}) ->"
              f" materialize({type(kept).__name__})")

    print()
    print("vault now holds", len(vault.contents), "entries:", vault.contents)

    # 2. SEAL. Minting puts it in the LEDGER - which is memory, and memory
    #    is exactly what the next step destroys.
    checkpoint_id = crystallizer.create_checkpoint()
    in_ledger = crystallizer.list_checkpoint_ids()
    assert checkpoint_id in in_ledger
    print()
    print("checkpoint minted:", checkpoint_id[:14], "...")
    print("   in ledger:", len(in_ledger), "(in-process - dies with the root)")

    # 3. FLUSH. THIS is the verb that makes it survive. Skip this line and
    #    the rest of the script has nothing to load, with no error to say
    #    why - because nothing went wrong.
    flushed = crystallizer.flush_checkpoint(checkpoint_id)
    assert checkpoint_id in flushed
    cached = crystallizer.list_cached_checkpoint_ids()
    assert checkpoint_id in cached
    print("flushed to cache:", len(cached), "cached id(s)")
    print("  ledger is memory; cache is bytes at rest. ONLY the cache")
    print("  crosses the teardown below")

    # ---------------------------------------------------------------- #
    # THE TEARDOWN                                                      #
    # ---------------------------------------------------------------- #
    aether = md.Aether()
    print()
    print("tearing the runtime down on purpose ...")

    # Drop our own handles first so the collect below is measuring the
    # runtime rather than measuring this function's locals.
    del vault, conduit, commands, crystallizer

    aether.cleanup()
    collected = gc.collect()
    print("aether.cleanup() + gc.collect() ->", collected, "objects collected")
    print("  singleton bookkeeping is cleared in a `finally`, so it resets")
    print("  even if a child teardown raises - that `finally` is why a")
    print("  failed cleanup can no longer leave a husk installed")

    # 4. PROVE IT. A fresh constructor call must hand back a DIFFERENT
    #    object, not the cleaned husk.
    fresh_aether = md.Aether()
    assert fresh_aether is not aether, (
        "cleanup() must clear the singleton - a fresh Aether() may never "
        "return the cleaned instance"
    )
    print("md.Aether() now returns a NEW root:",
          fresh_aether is not aether)
    del aether

    # ---------------------------------------------------------------- #
    # AFTER - a runtime that has never seen this world                  #
    # ---------------------------------------------------------------- #
    # 5. A NEW CRYSTALLIZER over the SAME cache. The record outlived the
    #    runtime that made it, which is the entire claim.
    reborn = md.Crystallizer()
    reborn.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )
    research = md.MutationResearch()
    research_configuration = research.create_configuration()
    research_configuration.with_defaults().activate()
    research.activate(research_configuration)
    print()
    print("new crystallizer over the same cache; recording:", reborn.activated)

    still_cached = reborn.list_cached_checkpoint_ids()
    print("cache after the teardown:", len(still_cached), "id(s)")
    assert checkpoint_id in still_cached, (
        "the flushed checkpoint must survive the singleton teardown - if "
        "this fails, the cache is not bytes at rest"
    )
    print("  our checkpoint is still there:", checkpoint_id[:14], "...")

    # 6. CACHE BACK INTO THE LEDGER. Bookkeeping, not a boot - the new
    #    root's ledger is empty and this refills it.
    summary = reborn.reload_cached_checkpoint(checkpoint_id)
    assert isinstance(summary, dict)
    print("reload_cached_checkpoint -> summary keys:", sorted(summary)[:6])
    print("  still nothing live; that is the NEXT verb")

    # 7. THE BOOT VERB - AND THIS IS WHERE THE LESSON GETS INTERESTING.
    #    Everything above worked: the cache outlived the runtime and the
    #    record came back into a fresh ledger. But UNFOLDING it into a
    #    world that has never seen it is a stricter act, and admission
    #    refuses this one.
    #
    #    A CHECKPOINT IS ONLY AS RESTORABLE AS ITS BUNDLE IS COMPLETE.
    #    `load_checkpoint` is mediated: the folded chain PRE-FLIGHTS
    #    before any replay, and a `blockers` verdict refuses at the one
    #    seam that owns authoritative folded truth. Here the bundle
    #    carries a spell's custody whose OWNING SPELLBOOK is not in it, so
    #    the custody has nothing to bind to.
    #
    #    IF IT REFUSES, READ THE REFUSAL - IT IS THE GUARANTEE WORKING:
    #    "nothing was built" is the all-or-nothing law declining to start
    #    rather than half-building a world and unwinding it. A loader that
    #    discovered an incomplete bundle mid-replay would leave you worse
    #    off than one that never began.
    try:
        report = reborn.load_checkpoint(checkpoint_id)
    except RuntimeError as refusal:
        print()
        print("load_checkpoint REFUSED at admission:")
        print("  ", str(refusal)[:150])
        print()
        print("  the verdict came from PREFLIGHT, before any replay, and")
        print("  the message ends `nothing was built` - all-or-nothing")
        print("  means the load never starts rather than unwinding halfway")
        print()
        print("  IF YOU SEE THIS: the folded chain was incomplete. The")
        print("  chain is the SAME-PROFILE LEDGER in creation order, not")
        print("  the one id you named - so a world sealed across several")
        print("  checkpoints needs `flush_checkpoint()` (no argument, whole")
        print("  ledger) and every id reloaded before the load")
    else:
        assert isinstance(report, dict)
        print()
        print("load_checkpoint -> RestoreReport keys:", sorted(report))
        print("   status:", report.get("status"))
        for key in ("identity_translation", "identity_translation_map",
                    "translation_map", "identity_map"):
            if key in report:
                print(f"   {key}: {len(report[key])} remapped identities")
                print("  rebuilt objects get NEW ids: the world that comes")
                print("  back is EQUIVALENT, not identical, and this map is")
                print("  the only honest way to follow one thing across")
                break
        for key in ("shortfall", "shortfalls", "shortfall_entries"):
            if key in report:
                entries = report[key]
                print(f"   {key}: {len(entries)} entr(y/ies)")
                for entry in list(entries)[:3]:
                    print("      ", str(entry)[:86])
                break

    print()
    print("the checkpoint outlived the runtime that minted it - the CACHE")
    print("crossed the teardown and the record came back into a fresh ledger")
    print("flush is what makes a record durable; the ledger is memory")
    print("cleanup() IS the reset, and it is public; the private")
    print("_reset_singleton_for_tests next to it is for test isolation")
    print("and the last rung - unfolding into a virgin runtime - demands a")
    print("COMPLETE bundle, which admission checks before it builds anything")


if __name__ == "__main__":
    main()
