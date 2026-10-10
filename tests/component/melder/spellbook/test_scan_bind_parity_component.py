"""
Component contracts for scan_bind parity over real Book wiring.

Purpose:
    Prove that scanned registrations with the new options run the Book's registration callbacks once per
    actual registration, carry their capability and disposal order into a live conjured world, and that a
    failing scan keeps the registrations it made before the failure in every transaction mode.
"""
from collections.abc import Iterator
from types import ModuleType
from typing import Any, Optional, Protocol

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.scan import scan_bind
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from tests.component.melder.aether.conduit.test_conduit_component_creations import (
    _make_spellbook,
)


@pytest.fixture(autouse=True)
def isolated_scan_component_world() -> Iterator[None]:
    """
    Purpose:
        Give each case an isolated Aether/Nexus world.
    Contract:
        Resets process roots before and after; tests clean the scopes they own.
    Yields:
        None while the test uses the fresh world.
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


def _owned_module(name: str, **members: Any) -> ModuleType:
    """
    Purpose:
        Build a module that owns its members, adding each name in the order given.
    Contract:
        Classes and functions get `__module__ = name`; a value already owned keeps it (aliases).
    Returns:
        ModuleType: The module.
    """
    module = ModuleType(name)
    for attribute, member in members.items():
        member.__module__ = name
        setattr(module, attribute, member)
    return module


@pytest.mark.parametrize("entry", ["spellbook_pre_conjure", "conduit_post_conjure"])
def test_each_scanned_object_runs_registration_callbacks_once(entry: str) -> None:
    """
    Purpose:
        Book-owned pre/activation/post callbacks see one registration per object, aliases included.
    Contract:
        The new options travel with that single registration; pre receives the original reference.
    """
    book = _make_spellbook(dynamic=True)
    pre: list[object] = []
    activation: list[Spell] = []
    post: list[Spell] = []
    root: Optional[Conduit] = None

    class Service:
        """Resource-free scan target registered once although the module names it twice."""

    scan_bind(existence="unique", permissions="create", resolvable=False, owner_team="tools")(Service)
    module = _owned_module("scan_component_callbacks", Service=Service, ServiceAlias=Service)
    try:
        book.add_bind_hooks(pre=[pre.append], activation=[activation.append], post=[post.append])
        if entry == "conduit_post_conjure":
            root = book.conjure(dynamic=True)
            spell_ids = root.scan(module)
        else:
            spell_ids = book.scan(module)
        assert len(spell_ids) == 1
        spell = book.find_spell_by_id(spell_ids[0])
        assert spell is not None
        assert pre == [Service]
        assert activation == [spell] and post == [spell]
        assert spell.resolvable is False
        assert spell.metadata == {"owner_team": "tools"}
    finally:
        if root is not None:
            root.permanent_cleanup()
        book.cleanup()


def test_post_conjure_scan_carries_disposal_order_and_definitions_into_a_live_world() -> None:
    """
    Purpose:
        A post-conjure scan registers a disposal-ordered class and a non-resolvable definition that
        the live conduit then treats exactly like direct bindings.
    Contract:
        The class melds and is disposed with the per-target name before the Book's; the definition is
        discoverable but refuses meld with MeldExecutionError.
    """
    book = _make_spellbook(dynamic=True, disposal=True, disposal_methods=["close"])
    calls: list[str] = []

    class Resource:
        """Live resource whose disposal order is observable."""

        def close(self) -> None:
            """Book-level disposal method."""
            calls.append("close")

        def stop(self) -> None:
            """Per-target disposal method declared on the scan."""
            calls.append("stop")

    class RenderContract(Protocol):
        """Descriptive definition registered through the scan."""

        def render(self) -> str:
            """Return the implementation's representation."""

    scan_bind(existence="unique", permissions="create", disposal_method_names=["stop"])(Resource)
    scan_bind(existence="unique", permissions="create", resolvable=False)(RenderContract)
    module = _owned_module("scan_component_live", Resource=Resource, RenderContract=RenderContract)
    root = book.conjure(dynamic=True)
    try:
        resource_id, contract_id = root.scan(module)
        resource_spell = book.find_spell_by_id(resource_id)
        assert resource_spell is not None
        assert resource_spell.disposal_method_names == ["stop", "close"]
        assert isinstance(root.meld(spell_id=resource_id), Resource)
        with pytest.raises(MeldExecutionError, match="non-resolvable"):
            root.meld(spell_id=contract_id)
    finally:
        root.permanent_cleanup()
        book.cleanup()
    assert calls == ["stop", "close"]


@pytest.mark.parametrize(
    "mode",
    [
        "pre_conjure",
        "spellbook_own_window",
        "conduit_own_window",
        "outer_spellbook_window",
        "outer_conduit_window",
    ],
)
def test_failed_scan_keeps_the_registrations_made_before_the_failure(mode: str) -> None:
    """
    Purpose:
        Pin the documented boundary: a scan is not atomic, with or without an outer bind window.
    Contract:
        The second target collides with the first; the first stays registered and the error propagates.
    """
    book = _make_spellbook(dynamic=True)

    class First:
        """Registered before the failure."""

    class Second:
        """Shares First's binding key, so its bind raises."""

    for target in (First, Second):
        scan_bind(
            existence="unique", permissions="create", spellframe="boundary", binding_name="same",
        )(target)
    module = _owned_module("scan_component_boundary", First=First, Second=Second)
    root: Optional[Conduit] = None
    try:
        if mode != "pre_conjure":
            root = book.conjure(dynamic=True)
        with pytest.raises(RuntimeError):
            if mode in ("pre_conjure", "spellbook_own_window"):
                book.scan(module)
            elif mode == "conduit_own_window":
                assert root is not None
                root.scan(module)
            elif mode == "outer_spellbook_window":
                with book.transaction("bind"):
                    book.scan(module)
            else:
                assert root is not None
                with root.transaction("bind"):
                    root.scan(module)
        assert [spell.spell for spell in book.spells.values()] == [First]
    finally:
        if root is not None:
            root.permanent_cleanup()
        book.cleanup()
