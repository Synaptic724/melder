import pytest
from melder import Aether, Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_cross_clear_regression() -> None:
    """
    Purpose:
        Ensure this regression test starts with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a non-dynamic Spellbook for the nested-scope regression.
    Contract:
        - Non-dynamic posture (the fast meld lane's only build posture).
        - phase_scheduler_workers_per_spellbook is set to 1 for determinism.
    Returns:
        Spellbook: Configured Spellbook instance.
    """
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(
        configuration,
        dynamic=False,
    )
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


class _SpaceMarker:
    """
    Purpose:
        unique_per_spell_space marker service for the nested-scope regression.
    Contract:
        - Instances are distinguishable by identity.
        - Carries no disposal methods so spellspace recycle takes the
          lock-free reset lane.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()


def test_nested_spellspace_scopes_keep_per_level_storage_until_their_own_exit() -> None:
    """
    Purpose:
        Regression: assert the recursive spellspace contract with per-scope
        assertions placed at the correct lexical level.
    Contract:
        - A -> B -> C -> D nesting yields four distinct scopes, stores, and
          marker instances.
        - Each inner exit leaves every still-open outer scope's storage
          untouched (verified one dedent level at a time).
        - A scope's storage is recycled by ITS OWN exit, which is correct
          runtime behavior, not a cross-clear.
    Regression history:
        A historical component-test defect asserted scope C's storage two
        dedent levels out (after C's own exit had legitimately recycled it),
        which masqueraded as a runtime "cross-clear" bug. Receiver-traced
        clearing calls proved every clear was each scope's own exit-time
        recycle in LIFO order. This test pins the correctly-placed
        assertions as an independent guard.
    """
    spellbook = _make_spellbook()
    marker_id = spellbook.bind(
        spell=_SpaceMarker,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        with conduit.enter_spellspace() as scope_a:
            marker_a = scope_a.meld(spell=marker_id)
            with conduit.enter_spellspace() as scope_b:
                marker_b = scope_b.meld(spell=marker_id)
                assert marker_b is not marker_a
                with conduit.enter_spellspace() as scope_c:
                    marker_c = scope_c.meld(spell=marker_id)
                    assert marker_c is not marker_b
                    assert marker_c is not marker_a
                    with conduit.enter_spellspace() as scope_d:
                        marker_d = scope_d.meld(spell=marker_id)
                        assert marker_d is not marker_c
                        assert scope_d.meld(spell=marker_id) is marker_d
                    # Inside C's body: D's exit left C's storage intact.
                    assert (
                        scope_c._creations.get_creation(marker_id) is marker_c
                    )
                    assert scope_c.meld(spell=marker_id) is marker_c
                # Inside B's body: C's exit left B's storage intact.
                assert scope_b._creations.get_creation(marker_id) is marker_b
                assert scope_b.meld(spell=marker_id) is marker_b
            # Inside A's body: B's exit left A's storage intact.
            assert scope_a._creations.get_creation(marker_id) is marker_a
            assert scope_a.meld(spell=marker_id) is marker_a
    finally:
        conduit.permanent_cleanup()
