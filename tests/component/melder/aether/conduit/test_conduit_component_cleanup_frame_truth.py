import pytest

from melder import Aether, Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_cleanup_frame_truth() -> None:
    """
    Purpose:
        Isolate frame-truth cleanup tests behind a fresh Aether singleton.
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


class _FrameTruthService:
    """
    Purpose:
        Minimal bindable service so the book carries one local spell.
    Contract:
        - No dependencies; constructible by the runtime without overrides.
    """

    def __init__(self) -> None:
        """
        Initialize the marker service.

        Contract:
            - Owns no resources; nothing to clean.

        Returns:
            None.
        """
        self.alive = True


def _dynamic_book() -> Spellbook:
    """
    Build one dynamic-posture Spellbook for frame-truth cleanup tests.

    Contract:
        - Defaults loaded, dynamic frame posture, single phase worker.

    Returns:
        Spellbook: The configured book.
    """
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(
        configuration,
        dynamic=True,
    )
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


def test_conduit_cleaned_after_its_spellbook_still_leaves_the_frame():
    """
    Purpose:
        Regression for the cleaned-husk frame leak (owner red run, S4
        REOPEN): a conduit cleaned AFTER its spellbook used to lose the
        frame unregistration because step 4's single try/except died on
        the dead book's registry surface before _remove_root_conduit()
        ran - the frame kept a cleaned husk registered.
    Contract:
        - Out-of-order teardown (book first, conduit second) still leaves
          frame._conduits empty and releases the conduit name.
        - The conduit reads cleaned; the public cloud probes agree.
    Returns:
        None.
    Raises:
        AssertionError: If a cleaned husk stays registered in the frame.
    """
    book = _dynamic_book()
    book.bind(
        spell=_FrameTruthService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = book.conjure(dynamic=True, name="frame-truth-keeper")
    frame = Aether()._aetheric_frames["default"]
    assert conduit._id in frame._conduits
    assert frame.conduit_cloud.has_conduit_name("frame-truth-keeper") is True

    # Out-of-order teardown: the book dies first (the engine's fail-fast
    # teardown race produced exactly this ordering before the scheduler
    # quiesce landed; other lanes can still produce it).
    book.cleanup()
    conduit.cleanup()

    assert conduit.cleaned is True
    assert frame._conduits == {}
    assert frame._conduit_ids_by_name == {}
    assert frame.conduit_cloud.has_conduit_name("frame-truth-keeper") is False


def test_in_order_teardown_frame_truth_is_unchanged():
    """
    Purpose:
        Guard the hardening against regression in the normal lane: the
        canonical order (conduit first, book second) keeps the exact same
        frame truth after the step-4 split.
    Contract:
        - frame._conduits and the name map are empty after teardown.
    Returns:
        None.
    Raises:
        AssertionError: If the split changed the canonical lane.
    """
    book = _dynamic_book()
    book.bind(
        spell=_FrameTruthService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = book.conjure(dynamic=True, name="frame-truth-orderly")
    frame = Aether()._aetheric_frames["default"]
    assert conduit._id in frame._conduits

    conduit.cleanup()

    assert conduit.cleaned is True
    assert frame._conduits == {}
    assert frame._conduit_ids_by_name == {}
    assert frame.conduit_cloud.has_conduit_name("frame-truth-orderly") is False
