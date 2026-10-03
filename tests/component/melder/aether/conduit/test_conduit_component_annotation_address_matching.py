"""
Component tests of address-key annotation matching (2026-10-03) through real conjures.

Scope:
    A consumer annotated with a class is served by an existing object of that class bound bare
    (no spellframe), whether the annotation is the class object or its `TYPE_CHECKING`-style
    string spelling; the cache generation that retires bundles captured under the identity
    matcher is 18.
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
    """The existing object the consumers depend on."""

    def __init__(self) -> None:
        self.calls = 0


class TypedWorker:
    """Consumer annotated with the class object."""

    def __init__(self, service: Service) -> None:
        self.service = service


class NamedWorker:
    """Consumer annotated with the class name, as a TYPE_CHECKING-only import leaves it at runtime."""

    def __init__(self, service: "Service") -> None:
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
    """An automatic-posture Spellbook with the conjure cache off."""
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=False)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook = Spellbook(configuration=configuration)
    spellbook.configure_aether_frame(
        system_state=None, disposal=None, disposal_method_names=None, system_caching_enabled=False,
    )
    return spellbook


def _bind_world() -> Tuple[Spellbook, Service, str, str]:
    """Bind one bare existing Service and the two consumers; return (spellbook, service, typed_id, named_id)."""
    spellbook = _spellbook()
    service = Service()
    spellbook.bind(spell=service, existence=Existence.unique, permissions="create")
    typed_id = spellbook.bind(spell=TypedWorker, existence=Existence.many, permissions="create")
    named_id = spellbook.bind(spell=NamedWorker, existence=Existence.many, permissions="create")
    return spellbook, service, typed_id, named_id


def test_a_bare_existing_object_serves_a_consumer_annotated_with_its_class() -> None:
    """No spellframe is needed: the instance's class is its type key."""
    spellbook, service, typed_id, _named_id = _bind_world()
    conduit = spellbook.conjure(name="key-matching-root", dynamic=False)
    try:
        worker = conduit.meld(spell_id=typed_id)
        assert worker.service is service
        assert conduit.meld(spell_id=typed_id).service is service
    finally:
        conduit.permanent_cleanup()


def test_the_string_and_the_object_annotation_resolve_the_same_binding() -> None:
    """A TYPE_CHECKING-style string annotation and the class object are the same key."""
    spellbook, service, typed_id, named_id = _bind_world()
    conduit = spellbook.conjure(name="key-matching-root", dynamic=False)
    try:
        typed = conduit.meld(spell_id=typed_id)
        named = conduit.meld(spell_id=named_id)
        assert typed.service is service and named.service is service
    finally:
        conduit.permanent_cleanup()


def test_cache_generation_18_retires_bundles_captured_under_identity_matching() -> None:
    """The creation-cache generation names the key matcher so older bundles are regenerated."""
    assert CachingSystem.CURRENT_VERSION >= 18
    assert CachingSystem.CACHE_VERSION_HISTORY[18] == "annotation_address_matching"
