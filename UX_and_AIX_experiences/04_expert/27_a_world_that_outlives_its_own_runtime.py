"""
TIER: expert (27)
GOAL: TEAR THE RUNTIME DOWN ON PURPOSE, THEN COME BACK. Expert 24 walked
      the five checkpoint verbs while the world stayed up. This is the
      harder half: seal a world, DESTROY the Aether singleton, collect
      the garbage, and unfold the record into a runtime that has never
      seen it.

      THE ONE FACT THE WHOLE LESSON TURNS ON
        Ledger  ->  in-process, dies with the singleton
        Cache   ->  bytes at rest, survives it
      `create_checkpoint()` mints into the LEDGER. That is memory. Tear
      the root down without flushing and the checkpoint goes with it -
      nothing to come back to and NO ERROR to tell you so, because
      nothing went wrong. `flush_checkpoint(id)` is what makes a record
      outlive the process.

      THE TEARDOWN IS PUBLIC, AND IDENTITY-CHECKED
        aether.cleanup()
      Singleton bookkeeping is cleared in a `finally` - `_instance` and
      `_initialized` - so it resets even when a child teardown raises.
      Before that `finally` existed, one failing child left a CLEANED
      HUSK installed as the process singleton for the rest of the run.
      `cleanup()` IS the reset; the private `_reset_singleton_for_tests`
      beside it is for test isolation, and nothing below reaches for it.

      `gc.collect()` here is real work, not ceremony: melder cleans
      deterministically rather than leaving owned objects to the
      collector, so a collect is how the old world is PROVEN gone.

      AND THE LAST RUNG DEMANDS A COMPLETE BUNDLE
      Unfolding into a virgin runtime is the strictest act here and the
      one that can refuse. `load_checkpoint` is MEDIATED: the folded
      chain PRE-FLIGHTS before any replay, and a `blockers` verdict
      refuses at the one seam owning authoritative folded truth. A
      refusal ends "nothing was built" - all-or-nothing declining to
      START rather than half-building a world and unwinding it.

      THE CHAIN COMES FROM THE LEDGER, which is the part worth knowing.
      `plan_checkpoint_load` detaches the target's SAME-PROFILE CHAIN in
      creation order, not the single id you named. After a teardown the
      fresh ledger is empty and `reload_cached_checkpoint` restores only
      the id you ask for - so a world sealed across SEVERAL checkpoints
      and partially reloaded folds an INCOMPLETE chain and refuses
      exactly as a corrupt one would. Seal more than once and you want
      `flush_checkpoint()` with NO argument, then every id back.
SURFACE EXERCISED: md.Crystallizer create_checkpoint / flush_checkpoint /
                   list_checkpoint_ids / list_cached_checkpoint_ids /
                   reload_cached_checkpoint / load_checkpoint,
                   md.Aether cleanup, and the codegen room's
                   validate_codegen / execute_codegen /
                   materialize_codegen across the boundary
VERIFY: rides the owner's 3.14t harness; asserts are the contract.
"""
import gc

import melder as md


FRAME = "outlive-world"

FIRST_EDIT = "policy_version = 1\nresult = policy_version\n"
SECOND_EDIT = "policy_version = 2\nresult = policy_version * 50\n"


class Vault:
    def __init__(self) -> None:
        self.contents = []


def build_world():
    """Stand up custody, record, world and codegen room."""
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )
    research = md.MutationResearch()
    configuration = research.create_configuration()
    configuration.with_defaults().activate()
    research.activate(configuration)

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
    book.bind(spell=Vault, existence="unique", permissions="create",
              binding_name="outlive-vault")
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
    return crystallizer, conduit, rift.space.command_system


def main() -> None:
    crystallizer, conduit, commands = build_world()
    vault = conduit.meld(spell=Vault, binding_name="outlive-vault")
    vault.contents.append("written before any codegen")
    print("world up; custody recording:", crystallizer.activated)

    # Two codegen edits, each materialized - running is not keeping, so
    # each gets an address of its own.
    for label, code in (("edit-1", FIRST_EDIT), ("edit-2", SECOND_EDIT)):
        commands.validate_codegen(code, frame_name=FRAME)
        commands.execute_codegen(code, frame_name=FRAME)
        commands.materialize_codegen(
            code,
            module_name="outlive_policy_%s" % label.replace("-", "_"),
            frame_name=FRAME,
        )
        vault.contents.append(label)
    print("two edits materialized; vault holds", len(vault.contents),
          "entries")

    # SEAL. Minting puts it in the LEDGER - memory, which the next step
    # destroys.
    checkpoint_id = crystallizer.create_checkpoint()
    assert checkpoint_id in crystallizer.list_checkpoint_ids()

    # FLUSH. THIS is what survives. Skip it and the rest of this script
    # has nothing to load, with no error to say why.
    flushed = crystallizer.flush_checkpoint(checkpoint_id)
    assert checkpoint_id in flushed
    assert checkpoint_id in crystallizer.list_cached_checkpoint_ids()
    print("checkpoint", checkpoint_id[:14], "minted and flushed to cache")

    # ---------------- THE TEARDOWN ----------------
    aether = md.Aether()
    del vault, conduit, commands, crystallizer

    aether.cleanup()
    collected = gc.collect()
    print()
    print("aether.cleanup() + gc.collect() ->", collected, "objects collected")

    fresh_aether = md.Aether()
    assert fresh_aether is not aether, (
        "cleanup() must clear the singleton - a fresh Aether() may never "
        "return the cleaned instance"
    )
    print("md.Aether() now returns a NEW root")
    del aether

    # ------- AFTER: a runtime that has never seen this world -------
    reborn = md.Crystallizer()
    reborn.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )
    research = md.MutationResearch()
    configuration = research.create_configuration()
    configuration.with_defaults().activate()
    research.activate(configuration)

    assert checkpoint_id in reborn.list_cached_checkpoint_ids(), (
        "the flushed checkpoint must survive the singleton teardown - if "
        "this fails, the cache is not bytes at rest"
    )
    print("the cache crossed the teardown; our checkpoint is still there")

    # Cache back into the ledger: bookkeeping, not a boot.
    summary = reborn.reload_cached_checkpoint(checkpoint_id)
    assert isinstance(summary, dict)
    print("reload_cached_checkpoint -> summary keys:", sorted(summary)[:5])

    # THE BOOT VERB. Refuses if the folded chain is incomplete.
    try:
        report = reborn.load_checkpoint(checkpoint_id)
    except RuntimeError as refusal:
        print()
        print("load_checkpoint REFUSED at admission:")
        print("  ", str(refusal)[:130])
        print("  preflight ran BEFORE any replay and the message ends")
        print("  `nothing was built` - the chain folded incomplete")
    else:
        assert isinstance(report, dict)
        print()
        print("load_checkpoint -> RestoreReport keys:", sorted(report))
        for key in ("identity_translation", "identity_translation_map",
                    "translation_map", "identity_map"):
            if key in report:
                print("   %s: %d remapped identities" % (key, len(report[key])))
                print("  rebuilt objects get NEW ids - the world that comes")
                print("  back is EQUIVALENT, not identical")
                break

    print()
    print("the CACHE outlived the runtime that minted it; the ledger is memory")
    print("cleanup() IS the reset, and it is public")
    print("the last rung wants a COMPLETE bundle, checked before it builds")


if __name__ == "__main__":
    main()
