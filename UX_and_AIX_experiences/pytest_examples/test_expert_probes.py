"""
Expert-tier contract probes. Run on 3.14t:

    pytest UX_and_AIX_experiences/pytest_examples/test_expert_probes.py -v
"""
import melder as md
import pytest

from melder import Aether, Conduit, Crystallizer, MutationResearch, Nexus
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_world() -> None:
    """Per-row world reset.

    Expert is the first tier that touches MutationResearch, so it joins
    the reset here alongside the four the other tiers already needed.
    All five carry process-wide state; without the reset one row's
    checkpoints, profiles or research lanes surface in the next row.
    """
    def _fresh() -> None:
        MutationResearch._reset_singleton_for_tests()
        Crystallizer._reset_singleton_for_tests()
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether

    _fresh()
    yield
    _fresh()


# ---------------------------------------------------------------------------
# Lesson 01 - pod boot, and why the ORDER is the product
# ---------------------------------------------------------------------------

def _staged_boot(profile: str) -> "md.CrystallizerBootstrap":
    boot = md.CrystallizerBootstrap()
    boot.with_profile(profile)
    boot.with_pull_remote(False)
    boot.with_formation_reload(False)
    return boot


def test_probe_bootstrap_setters_are_fluent_and_return_self():
    """Lesson 01 claim: the boot builder follows the same mutate-and-
    return-self law as every other configuration surface in melder."""
    boot = md.CrystallizerBootstrap()
    assert boot.with_profile("probe-pod") is boot
    assert boot.with_pull_remote(False) is boot
    assert boot.with_formation_reload(False) is boot
    assert boot.with_preflight_gate(True) is boot
    print("boot setters pinned: fluent, same object")


def test_probe_bootstrap_report_carries_every_step():
    """Lesson 01 HEADLINE: "the ORDER is the product". Seven steps run in
    a fixed sequence and EVERY ONE reports - including the ones with no
    work, which report None rather than being absent.

    That distinction matters: a missing key means the report shape
    changed; a None means the step was not applicable this boot. A caller
    can tell those apart only if the key is always there."""
    report = _staged_boot("probe-pod-report").bootstrap()
    assert isinstance(report, dict)
    for key in ("activated", "profile_name", "cache_reload", "remote_reload",
                "formation_reload", "chain_report", "restored_checkpoint_id",
                "restore_report"):
        assert key in report, f"{key} missing from the bootstrap report"
    assert report["activated"] is True
    assert report["profile_name"] == "probe-pod-report"
    print("report shape pinned:", len(report), "keys, all present")


def test_probe_first_boot_restores_nothing_and_that_is_not_an_error():
    """Lesson 01 claim: a history-less process boots an EMPTY WORLD -
    `restored_checkpoint_id` is None and no exception is raised.

    This is the half people get wrong. "Nothing to restore" and "the
    thing I was going to restore is damaged" are different outcomes, and
    melder refuses to collapse them: the first boots empty, the second
    raises. A red here means first boot started failing, which would make
    every fresh pod look like a corruption."""
    report = _staged_boot("probe-pod-first").bootstrap()
    assert report["restored_checkpoint_id"] is None
    print("first boot pinned: empty world, no exception")


def test_probe_skipped_steps_report_none_not_a_fake_summary():
    """Lesson 01 claim: with no external manager attached and remote pull
    disabled, steps 4 and 5 have no work - and they say None rather than
    inventing an empty summary that would read like they ran."""
    report = _staged_boot("probe-pod-skips").bootstrap()
    assert report["remote_reload"] is None
    assert report["formation_reload"] is None
    print("skipped steps pinned: None, not a manufactured summary")


def test_probe_bootstrap_is_one_shot():
    """Lesson 01 claim: bootstrap() CONSUMES the object. Same one-shot law
    as AetherConfigurationBuilder.build() (advanced 07) and create_rift()
    consuming its configuration (advanced 09) - three independent
    instances make it a house style, not an accident."""
    boot = _staged_boot("probe-pod-oneshot")
    boot.bootstrap()
    with pytest.raises(RuntimeError):
        boot.bootstrap()
    print("one-shot pinned: the boot object is spent by its run")
