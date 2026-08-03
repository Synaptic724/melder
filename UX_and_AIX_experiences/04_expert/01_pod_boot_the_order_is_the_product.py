"""
TIER: expert (01)
GOAL: BOOTING A POD. Advanced 17-18 taught checkpoint and load as two
      verbs you call yourself. This is the operator's version: one entry
      point that runs the whole restart flow in a fixed sequence.

      melder's own contract line is the lesson title:

          "Contract (the ORDER is the product)"

      Read that as a claim, because it is one. Every step below is
      something you could call by hand. The value CrystallizerBootstrap
      adds is not the calls - it is that they happen in THIS order, and
      the order encodes reasoning you would otherwise have to rediscover
      after a bad restart.

      THE SEVEN STEPS
        1. Activate the crystallizer (the persistence system comes up
           with it).
        2. Attach the external manager, when one is configured.
        3. Reload the profile's LOCAL cache. An empty cache is tolerated.
        4. Pull the profile's REMOTE history when enabled AND a manager
           is attached - then RE-FLUSH the pulled ids so the local cache
           actually holds them.
        5. Pull REMOTE FORMATIONS (mesh-aware boot). Default-on when the
           attached manager carries the generic fetch+list lanes;
           legacy-only managers skip SILENTLY.
        6. Verify the chain. "broken" REFUSES loudly; anything else rides
           the report.
        7. Load the most recent checkpoint by EXACT LEDGER INSERTION
           ORDER - not by timestamp.

      WHY THE ORDER IS LOAD-BEARING
      Local before remote (3 before 4) means a pod that cannot reach the
      network still boots on what it has. The re-flush inside step 4 is
      the part people miss: pulling remote history does not by itself put
      it in the local cache, so a pod that pulled and then lost the
      network would have come back empty. Verify (6) sits BEFORE load (7)
      so a broken chain refuses instead of half-restoring a world. And
      insertion order rather than timestamp in step 7 means two
      checkpoints written in the same second still have one answer.

      THE TWO REFUSAL SHAPES, BOTH DELIBERATE
        BROKEN CHAIN     -> RuntimeError. Loud. There is no correct
                            partial restore of a broken lineage.
        NO HISTORY AT ALL-> boots an EMPTY WORLD, `restored_checkpoint_id`
                            is None. A first boot is not an error.
      That distinction is the whole difference between "nothing to
      restore" and "the thing I was going to restore is damaged", and
      melder refuses to collapse them into one outcome.

      IT IS ONE-SHOT. bootstrap() consumes the object; calling it twice
      raises. Same law as AetherConfigurationBuilder.build() (advanced 07)
      and create_rift() consuming its configuration (advanced 09).
SURFACE EXERCISED: md.CrystallizerBootstrap - with_profile,
                   with_pull_remote, with_formation_reload,
                   with_preflight_gate, bootstrap
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


REPORT_KEYS = (
    "activated",
    "profile_name",
    "cache_reload",
    "remote_reload",
    "formation_reload",
    "chain_report",
    "restored_checkpoint_id",
    "restore_report",
)


def main() -> None:
    # THE FLUENT SETUP. Every with_* returns self, like every other
    # configuration surface in melder.
    boot = md.CrystallizerBootstrap()
    assert boot.with_profile("expert-pod") is boot
    assert boot.with_pull_remote(False) is boot
    assert boot.with_formation_reload(False) is boot
    assert boot.with_preflight_gate(True) is boot
    print("boot staged for profile 'expert-pod'")

    # No external manager attached, no remote pull requested - so steps 2,
    # 4 and 5 have nothing to do. This is the offline restart case, and it
    # is the one that must work when everything else is on fire.
    report = boot.bootstrap()
    assert isinstance(report, dict)
    print("bootstrap ran; report keys:", len(report))

    # THE REPORT IS THE RECORD. Every step reports, including the ones
    # that did nothing - a None is "this step was not applicable", which
    # is different from the key being absent.
    for key in REPORT_KEYS:
        assert key in report, f"{key} missing from the bootstrap report"
        print(f"  {key:24s} {report[key]!r}"[:88])

    assert report["activated"] is True
    assert report["profile_name"] == "expert-pod"

    # A HISTORY-LESS PROCESS BOOTS AN EMPTY WORLD. Not an error - there
    # was simply nothing to restore. This is the FIRST BOOT case.
    print()
    print("restored checkpoint:", report["restored_checkpoint_id"])
    print("first boot restores nothing, and that is not a failure")

    # Steps that had no work report None rather than a fake summary.
    assert report["remote_reload"] is None, "no manager attached"
    assert report["formation_reload"] is None, "formation reload disabled"
    print("skipped steps reported None, not an invented summary")

    # ONE-SHOT. The object is consumed by the run.
    try:
        boot.bootstrap()
        raise AssertionError("expected a refusal - bootstrap is one-shot")
    except RuntimeError as error:
        print()
        print("second bootstrap refused:", type(error).__name__)

    print()
    print("the ORDER is the product - local before remote, verify before load")
    print("broken chain REFUSES; no history at all boots empty. not the same.")


if __name__ == "__main__":
    main()
