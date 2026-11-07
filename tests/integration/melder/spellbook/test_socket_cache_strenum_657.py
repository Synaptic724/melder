"""Cache-hit replay of an unresolved socket after the #657 enum conversion."""

from pathlib import Path

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
from melder.nexus.nexus import Nexus
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError


class CacheProvider:
    """A registered dependency that gives the consumer a real graph edge."""


class CacheMissing:
    """An intentionally unregistered dependency supplied at meld time."""


class CacheConsumer:
    """A consumer with both a registered and an unresolved dependency."""

    def __init__(self, provider: CacheProvider, missing: CacheMissing) -> None:
        self.provider = provider
        self.missing = missing


def _reset_world() -> None:
    """Replace the test process's singleton world without deleting cache files."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _conjure_world() -> tuple[Spellbook, Conduit]:
    """Build the same cache-enabled graph in a fresh runtime world."""
    _reset_world()
    configuration = Aether()._ensure_frame("socket-cache-657").frame_configuration
    configuration.with_system_caching_enabled(True)
    book = Spellbook(aetheric_frame="socket-cache-657")
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book.bind(spell=CacheProvider, existence="many", permissions="create")
    book.bind(spell=CacheConsumer, existence="many", permissions="create")
    return book, book.conjure(name="socket-cache-root")


def test_cached_unresolved_socket_keeps_its_numeric_plan_contract(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A cache-hit world keeps the unresolved refusal and supplied-value behavior."""
    monkeypatch.setattr(AethericFrameConfiguration, "resolve_system_cache_root_path", lambda self: tmp_path)
    try:
        book, conduit = _conjure_world()
        with pytest.raises(UnresolvedInputError):
            conduit.meld(spell=CacheConsumer)
        supplied = CacheMissing()
        assert conduit.meld(spell=CacheConsumer, override={"missing": supplied}).missing is supplied
        bundle_path = book._get_or_create_caching_system().bundle_path
        before = (bundle_path.read_bytes(), bundle_path.stat().st_mtime_ns)

        def reject_plan_rebuild(**_kwargs: object) -> None:
            """A full cache hit must not rerun the conduit plan phases."""
            pytest.fail("The second world rebuilt its cached conduit plan.")

        with monkeypatch.context() as warm_probe:
            warm_probe.setattr(
                SpellbookCreationSystem, "_run_conduit_plan_resolution_phases",
                staticmethod(reject_plan_rebuild),
            )
            book, conduit = _conjure_world()
            assert (bundle_path.read_bytes(), bundle_path.stat().st_mtime_ns) == before
            with pytest.raises(UnresolvedInputError):
                conduit.meld(spell=CacheConsumer)
            supplied_again = CacheMissing()
            result = conduit.meld(spell=CacheConsumer, override={"missing": supplied_again})
            assert result.missing is supplied_again
            assert isinstance(result.provider, CacheProvider)
    finally:
        _reset_world()
