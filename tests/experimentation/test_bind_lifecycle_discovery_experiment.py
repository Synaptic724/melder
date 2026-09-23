"""Characterize binding admission and existing hooks before adding a bind lifecycle."""

from collections.abc import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests.component.melder.aether.conduit.test_conduit_component_creations import (
    _make_spellbook,
)


class BindAnchor:
    """
    Purpose: Supply an existing index for inactive-binding admission probes.
    Contract: Resource-free class with no constructor dependencies.
    """


class BindCandidate:
    """
    Purpose: Supply a distinct registration target for each isolated runtime.
    Contract: Resource-free class; identity exposes normal scoped creation behavior.
    """


@pytest.fixture(autouse=True)
def isolated_bind_world() -> Iterator[None]:
    """
    Purpose: Prevent runtime singletons leaking across characterization cases.
    Contract: Reset Aether/Nexus and rebind their test class references on both sides.
        Individual tests own and clean their conjured scopes before fixture teardown.
    Yields: None while the test owns the isolated runtime.
    """
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Aether()
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Aether()


@pytest.mark.parametrize("dynamic", [False, True])
@pytest.mark.parametrize("inactive", [False, True])
def test_lesser_bind_entry_points_refuse_before_registration(
    dynamic: bool,
    inactive: bool,
) -> None:
    """
    Purpose: Verify both lesser binding doors in automatic and dynamic worlds.
    Contract: Refusal occurs before either active or inactive registration changes.
    Args: dynamic: Frame posture; inactive: Select bind_inactive instead of bind.
    Returns: None; the existing owner binding stays resolvable after refusal.
    """
    book = _make_spellbook(dynamic=dynamic)
    anchor_id = book.bind(spell=BindAnchor, existence="unique")
    root = book.conjure(dynamic=dynamic)
    lesser = root.create_lesser_conduit()
    try:
        active_before = tuple(book._spells_by_id)
        inactive_before = tuple(book._inactive_spells)
        with pytest.raises(RuntimeError, match="Only normal conduits can bind spells"):
            if inactive:
                lesser.bind_inactive(
                    spell=BindCandidate,
                    spell_index=book._spells_by_id[anchor_id].spell_index,
                    existence="unique",
                )
            else:
                lesser.bind(spell=BindCandidate, existence="unique")
        assert tuple(book._spells_by_id) == active_before
        assert tuple(book._inactive_spells) == inactive_before
        assert isinstance(lesser.meld(spell_id=anchor_id), BindAnchor)
    finally:
        lesser.cleanup()
        root.permanent_cleanup()


@pytest.mark.parametrize("through_root", [False, True])
def test_lesser_can_resolve_a_later_binding_from_its_owning_book(through_root: bool) -> None:
    """
    Purpose: Distinguish registration authority from borrowed definition visibility.
    Contract: A pre-existing lesser sees a later owner registration and creates its
        own per-conduit object. Its root resolves a separate per-conduit instance.
    Args: through_root: Use root.bind rather than direct Spellbook.bind.
    Returns: None.
    """
    book = _make_spellbook(dynamic=True)
    root = book.conjure(dynamic=True)
    lesser = root.create_lesser_conduit()
    try:
        owner = root if through_root else book
        spell_id = owner.bind(spell=BindCandidate, existence="unique_per_conduit")
        local = lesser.meld(spell_id=spell_id)
        assert isinstance(local, BindCandidate)
        assert lesser.meld(spell_id=spell_id) is local
        assert root.meld(spell_id=spell_id) is not local
    finally:
        lesser.cleanup()
        root.permanent_cleanup()


def test_current_pre_activation_post_kwargs_run_at_meld_not_bind() -> None:
    """
    Purpose: Verify the lifecycle that existing similarly named kwargs already serve.
    Contract: Bind/conjure trigger no callbacks; first meld runs pre, construction,
        instance activation and post. A second unique meld runs only pre and post.
    Returns: None; callbacks remain ordinary registered creation hooks.
    """
    events: list[str] = []
    activated: list[object] = []

    class Service:
        """
        Purpose: Make actual instance construction observable.
        Contract: Borrow the test's events list and own no external resources.
        """

        def __init__(self) -> None:
            """
            Purpose: Identify construction separately from hook invocation.
            Contract: Append one marker for each actual instance.
            Returns: None.
            """
            events.append("construct")

    def pre() -> None:
        """
        Purpose: Record the existing zero-argument pre-cast event.
        Contract: Append one marker without constructing an application object.
        Returns: None.
        """
        events.append("pre")

    def activation(instance: object) -> None:
        """
        Purpose: Record the existing activation callback's actual subject.
        Args: instance: The newly created application object.
        Contract: Retain that reference for identity assertions only.
        Returns: None.
        """
        activated.append(instance)
        events.append("activation")

    def post() -> None:
        """
        Purpose: Record the existing zero-argument post-cast event.
        Contract: Append one marker after the meld result is available.
        Returns: None.
        """
        events.append("post")

    book = _make_spellbook()
    spell_id = book.bind(
        spell=Service, existence="unique",
        pre_hooks=[pre], activation_hooks=[activation], post_hooks=[post],
    )
    assert events == []
    root = book.conjure()
    try:
        assert events == []
        first = root.meld(spell_id=spell_id)
        assert events == ["pre", "construct", "activation", "post"]
        assert len(activated) == 1 and activated[0] is first
        assert root.meld(spell_id=spell_id) is first
        assert events == ["pre", "construct", "activation", "post", "pre", "post"]
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("hook_name", ["on_bind_pre", "on_bind_activation", "on_bind_post"])
def test_proposed_bind_hook_names_are_not_current_configuration_slots(hook_name: str) -> None:
    """
    Purpose: Verify that candidate bind-stage names are not already implemented.
    Contract: Existing configuration rejects the name and retains no callback.
    Args: hook_name: Provisional name proposed for the future lifecycle.
    Returns: None; this is characterization, not a test of future hook acceptance.
    """
    book = _make_spellbook()
    try:
        config = book.get_configuration()
        with pytest.raises(ValueError, match="Unknown hook name"):
            config.add_hook(book._id, hook_name, lambda: None)
        assert config.get_hooks(book._id) == {}
    finally:
        book.cleanup()


def test_existing_configuration_hook_registration_is_frozen_after_conjure() -> None:
    """
    Purpose: Expose the registration lifecycle inherited if bind hooks use configuration.
    Contract: A known hook slot still rejects a new callback after conjure freezes config.
    Returns: None.
    """
    book = _make_spellbook(dynamic=True)
    root = book.conjure(dynamic=True)
    try:
        with pytest.raises(RuntimeError, match="hooks after configuration is frozen"):
            book.get_configuration().add_hook(book._id, "on_meld_pre_resolve", lambda: None)
    finally:
        root.permanent_cleanup()


def test_bind_works_with_implicit_defaults_before_explicit_configuration() -> None:
    """
    Purpose: Verify whether callers must configure or freeze before ordinary bind.
    Contract: A fresh Spellbook supplies default configuration and accepts a binding
        while that configuration is still mutable, before any explicit setup call.
    Returns: None; the book is explicitly cleaned without conjuring a runtime.
    """
    book = Spellbook()
    try:
        spell_id = book.bind(spell=BindCandidate, existence="unique")
        assert book._spells_by_id[spell_id].spell is BindCandidate
        assert book.get_configuration()._frozen is False
        assert book._binds_before_configuration_count == 1
    finally:
        book.cleanup()
