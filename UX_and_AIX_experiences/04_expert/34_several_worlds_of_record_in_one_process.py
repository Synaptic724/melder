"""
TIER: expert (34)
GOAL: KEEP TWO SEPARATE WORLDS OF RECORD IN ONE PROCESS. Every lesson so
      far has recorded into one nameless place. It has a name - "default"
      - and you can have others.

      A PROFILE IS WHERE EMISSIONS LAND. Checkpoints, twins and the whole
      recorded ledger belong to a profile, and unqualified operations
      resolve to the ACTIVE one. Two profiles are two independent records
      of the same running process: a staging record and a production one,
      or one per tenant, or a throwaway you clear between experiments.

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

    # THE PARTITION IS REAL. A checkpoint sealed here is not over there.
    on_staging = crystallizer.create_checkpoint()
    staging_ids = crystallizer.list_checkpoint_ids()
    assert on_staging in staging_ids
    assert on_default not in staging_ids, (
        "profiles are separate records - default's checkpoint must not "
        "appear in staging's ledger"
    )
    print("sealed a checkpoint on 'staging':", on_staging[:14], "...")
    print("  and 'default's checkpoint is NOT in this ledger - two")
    print("  independent records of one running process")

    # SWITCHING MOVES A POINTER AND NOTHING ELSE.
    crystallizer.set_active_profile("default")
    back_home = crystallizer.list_checkpoint_ids()
    assert on_default in back_home
    assert on_staging not in back_home, (
        "switching must not migrate anything between profiles"
    )
    print()
    print("set_active_profile('default') -> our first checkpoint is back")
    print("  and staging's did NOT come with it. The switch moved a")
    print("  pointer; no data was copied or migrated")

    # DESCRIBE READS THE ACTIVE ONE WHEN YOU NAME NOTHING.
    here = crystallizer.describe_profile()
    named = crystallizer.describe_profile("staging")
    assert isinstance(here, dict) and isinstance(named, dict)
    print()
    print("describe_profile()          -> the ACTIVE one, keys:",
          sorted(here)[:4])
    print("describe_profile('staging') -> that one, keys:",
          sorted(named)[:4])
    print("  None means ACTIVE here, not `all profiles`")

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
