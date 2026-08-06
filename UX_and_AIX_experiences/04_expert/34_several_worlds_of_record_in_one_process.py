"""
TIER: expert (34)
GOAL: KEEP TWO SEPARATE WORLDS OF RECORD IN ONE PROCESS. Every lesson so
      far has recorded into one nameless place. It has a name - "default"
      - and you can have others.

      A PROFILE IS WHERE EMISSIONS LAND. Twins accumulate into the active
      profile, and unqualified operations resolve to it. Two profiles are
      two separate bodies of recorded content in one running process: a
      staging record and a production one, or one per tenant, or a
      throwaway you clear between experiments.

      BUT A PROFILE IS NOT A PRIVATE LEDGER, AND THIS IS THE THING TO GET
      RIGHT. `create_checkpoint` snapshots ONE profile's window and
      advances THAT profile's journal mark - the content is partitioned.
      `list_checkpoint_ids()` returns "all checkpoint ids in exact ledger
      creation order" for the PROCESS. Switching profiles does not give
      you a filtered view and does not hide anyone else's seals.
      Same shelf, different boxes. Assume otherwise and you will write an
      assertion that fails - this lesson's author did exactly that.

      YOU CREATE WORLDS BY NAME AND NOTHING ELSE. The facade says so
      outright: "users and agents create worlds by name only;
      PersistenceProfile objects never escape the depths." You never hold
      the profile object, so there is nothing to pass around, alias, or
      accidentally keep alive - the name IS the handle.
      That is worth contrasting with a surface that does NOT do this: the
      ACL authoring chain hands you internal builders and is marked
      "do not drive it directly". Here the internal object is kept buried
      and you are given a name. Same codebase, two answers, and the one
      you get tells you whether a surface is finished.

      SWITCHING MOVES A POINTER. NOTHING ELSE.
      `set_active_profile` "moves the pointer only - no data is copied or
      migrated between profiles". Nothing is merged, nothing is
      duplicated, and the profile you left keeps exactly what it had. If
      you expected a switch to bring your checkpoints along, this is the
      sentence that saves you.

      CLEAR AND DELETE ARE DIFFERENT VERBS ON PURPOSE
        clear_profile   EMPTIES it and KEEPS it - still listed, still
                        activatable. The non-destructive reset.
        delete_profile  REMOVES it. The name stops appearing in
                        list_profile_names().
      And "default" is NEVER DELETABLE - it is the guaranteed landing
      place, the same shape of law as the default research lane that never
      archives (expert 31). Every system needs one thing that cannot be
      removed, or its own fallbacks have nowhere to fall.

      ALL OF IT REQUIRES AN ACTIVATED CRYSTALLIZER, and the refusal is the
      point: "a configured-but-not-activated crystallizer raises rather
      than silently no-opping. Recording is opt-in and this is where that
      shows up." A world that quietly recorded nothing would be worse than
      one that refused.
SURFACE EXERCISED: Crystallizer.active_profile_name / create_profile /
                   set_active_profile / list_profile_names /
                   describe_profile / clear_profile / delete_profile,
                   with create_checkpoint proving the partition is real
VERIFY: authored 2026-08-05; not yet run.
"""
import melder as md


FRAME = "profile-world"


class Ledger:
    def __init__(self) -> None:
        self.entries: list[str] = []


def main() -> None:
    crystallizer = md.Crystallizer()

    # RECORDING IS OPT-IN, and asking a configured-but-inactive
    # crystallizer about profiles REFUSES rather than answering emptily.
    try:
        crystallizer.list_profile_names()
        raise AssertionError("expected a refusal before activation")
    except RuntimeError as inactive:
        print("profiles before activation ->", str(inactive)[:88])
        print("  a world that quietly recorded nothing would be worse")
        print("  than one that refused")

    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )

    # THE ONE YOU HAVE ALREADY BEEN USING HAS A NAME.
    assert crystallizer.active_profile_name == "default"
    assert "default" in crystallizer.list_profile_names()
    print()
    print("active profile:", crystallizer.active_profile_name)
    print("  every earlier lesson recorded here without naming it")

    # A WORLD WORTH RECORDING.
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
              binding_name="profile-ledger")
    book.conjure(name="profile-root")

    on_default = crystallizer.create_checkpoint()
    print()
    print("sealed a checkpoint on 'default':", on_default[:14], "...")

    # A SECOND WORLD OF RECORD, BY NAME. No object is handed back.
    crystallizer.create_profile("staging")
    assert crystallizer.active_profile_name == "staging", (
        "create_profile activates by default"
    )
    assert set(crystallizer.list_profile_names()) >= {"default", "staging"}
    print()
    print("create_profile('staging') -> active is now:",
          crystallizer.active_profile_name)
    print("  it returned None. The NAME is the handle; the profile object")
    print("  never escapes the depths, so there is nothing to alias or")
    print("  accidentally keep alive")

    # AND HERE IS THE LINE PEOPLE GET WRONG, INCLUDING THE AUTHOR OF THIS
    # LESSON ON THE FIRST TRY. A profile decides what a checkpoint
    # CONTAINS. It does not give you a private ledger.
    on_staging = crystallizer.create_checkpoint()
    everything = crystallizer.list_checkpoint_ids()
    assert on_staging in everything
    assert on_default in everything, (
        "list_checkpoint_ids returns ALL ids - the ledger is process-wide"
    )
    print("sealed a checkpoint on 'staging':", on_staging[:14], "...")
    print()
    print("list_checkpoint_ids() ->", len(everything), "ids, and BOTH are")
    print("  here. Its contract says `all checkpoint ids in exact ledger")
    print("  creation order` - one ledger for the process. Switching")
    print("  profiles does not hand you a private one.")
    print("  What the profile partitions is the CONTENT: create_checkpoint")
    print("  snapshots ONE profile's twin window and advances THAT")
    print("  profile's journal mark. Same shelf, different boxes.")

    # SWITCHING MOVES A POINTER AND NOTHING ELSE - including not moving
    # the ledger, which is why both ids are still listed below.
    crystallizer.set_active_profile("default")
    assert crystallizer.active_profile_name == "default"
    after_switch = crystallizer.list_checkpoint_ids()
    assert set(after_switch) == set(everything), (
        "the switch moves a pointer; it does not copy, migrate or hide"
    )
    print()
    print("set_active_profile('default') -> the ledger is unchanged:",
          set(after_switch) == set(everything))
    print("  `moves the pointer only - no data is copied or migrated`")
    print("  cuts both ways: nothing follows you, and nothing is taken")

    # YOU CAN ALSO NAME THE PROFILE EXPLICITLY rather than switching to
    # it - the argument is there so a caller never has to move the
    # pointer just to seal somewhere.
    targeted = crystallizer.create_checkpoint(profile_name="staging")
    assert crystallizer.active_profile_name == "default", (
        "checkpointing another profile must not move the active pointer"
    )
    print()
    print("create_checkpoint(profile_name='staging') ->", targeted[:14],
          "... and the active profile is still",
          crystallizer.active_profile_name)

    # DESCRIBE READS THE ACTIVE ONE WHEN YOU NAME NOTHING - and this is
    # where the CONTENT partition is visible, since the ledger read is
    # not. `describe_profile` reports per-level twin counts and the
    # emission sequence for ONE profile.
    active_view = crystallizer.describe_profile()
    default_view = crystallizer.describe_profile("default")
    staging_view = crystallizer.describe_profile("staging")
    assert isinstance(active_view, dict)
    assert active_view == default_view, (
        "None must resolve to the ACTIVE profile, which is 'default' here"
    )
    print()
    print("describe_profile()          -> the ACTIVE one (keys:",
          "%s)" % sorted(active_view)[:4])
    print("describe_profile('staging') -> that one    (keys:",
          "%s)" % sorted(staging_view)[:4])
    print("  None means ACTIVE, not `all profiles` - proven by the two")
    print("  reads above being equal while 'default' is active")
    print("  and THIS is where the partition shows: per-profile twin")
    print("  counts and emission sequence, not the shared ledger")

    # CLEAR EMPTIES AND KEEPS. DELETE REMOVES.
    crystallizer.clear_profile("staging")
    assert "staging" in crystallizer.list_profile_names(), (
        "clear is the NON-destructive reset - the profile survives"
    )
    print()
    print("clear_profile('staging')  -> still listed:",
          "staging" in crystallizer.list_profile_names())

    crystallizer.delete_profile("staging")
    assert "staging" not in crystallizer.list_profile_names()
    print("delete_profile('staging') -> still listed:",
          "staging" in crystallizer.list_profile_names())
    print("  two verbs because emptying a world and removing it are")
    print("  different intentions, and one of them is recoverable")

    # AND THE DEFAULT IS NEVER DELETABLE.
    try:
        crystallizer.delete_profile("default")
        raise AssertionError("expected a refusal: default is guaranteed")
    except ValueError as refusal:
        print()
        print("delete_profile('default') refused -", str(refusal)[:80])
        print("  the same shape of law as the default research lane that")
        print("  never archives: every system needs one thing that cannot")
        print("  be removed, or its own fallbacks have nowhere to fall")

    print()
    print("one process, several records, and you addressed them by name")


if __name__ == "__main__":
    main()
