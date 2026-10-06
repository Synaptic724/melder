"""
Component tests of lazy instance_results (S8, 2026-10-03) through real conjures.

Scope:
    A root whose site plan runs in dict mode - its dependency is an existing object, a generic site -
    is melded through a real Conduit and a real SpellSpace: warm and cold melds return the bound
    object, and the creation-cache generation that retires eagerly emitted plans is 17.
"""

from typing import Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.caching_system.caching_system import CachingSystem
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)


class Service:
    """The existing object a Worker depends on."""

    def __init__(self) -> None:
        self.calls = 0


class Worker:
    """Transient root over the existing Service (a dict-mode site plan)."""

    def __init__(self, service: Service) -> None:
        self.service = service


@pytest.fixture(autouse=True)
def reset_aether_singleton() -> None:
    """Fresh Aether per test, as the other component conduit tests do."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _spellbook() -> Spellbook:
    """An automatic-posture Spellbook with the conjure cache off, as the certification harness builds its worlds."""
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=False)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook = Spellbook(configuration=configuration)
    spellbook.configure_aether_frame(
        system_state=None, disposal=None, disposal_method_names=None, system_caching_enabled=False,
    )
    return spellbook


def _bind_world() -> Tuple[Spellbook, Service, str]:
    """Bind one existing Service (unique) and Worker (many); return (spellbook, service, worker_id)."""
    spellbook = _spellbook()
    service = Service()
    spellbook.bind(spell=service, existence=Existence.unique, permissions="create")
    worker_id = spellbook.bind(spell=Worker, existence=Existence.many, permissions="create")
    return spellbook, service, worker_id


def test_conduit_meld_of_a_root_over_an_existing_object_returns_it_warm_and_cold() -> None:
    """The first (cold) and second (warm) melds both receive the bound Service object."""
    spellbook, service, worker_id = _bind_world()
    conduit = spellbook.conjure(name="s8-lazy-root", dynamic=False)
    try:
        first = conduit.meld(spell_id=worker_id)
        second = conduit.meld(spell_id=worker_id)
        assert first is not second
        assert first.service is service and second.service is service
    finally:
        conduit.permanent_cleanup()


def test_spellspace_meld_of_the_same_root_returns_the_existing_object() -> None:
    """A space-scoped meld of the dict-mode root receives the same bound Service."""
    spellbook, service, worker_id = _bind_world()
    conduit = spellbook.conjure(name="s8-lazy-root", dynamic=False)
    try:
        with conduit.enter_spellspace() as space:
            worker = space.meld(spell_id=worker_id)
            again = space.meld(spell_id=worker_id)
        assert worker.service is service and again.service is service and worker is not again
    finally:
        conduit.permanent_cleanup()


def test_cache_generation_17_retires_eagerly_emitted_plans() -> None:
    """The creation-cache generation names the lazy dict so older executors are regenerated."""
    assert CachingSystem.CURRENT_VERSION >= 17
    assert CachingSystem.CACHE_VERSION_HISTORY[17] == "lazy_instance_results"
