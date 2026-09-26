"""Inherited disposal contracts across binding, identity and real instance teardown."""

from collections.abc import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests.component.melder.spellbook.test_ordered_disposal_binding import (
    configured_book,
)


class CleanupBase:
    """Expose deterministic disposal observations without owning external resources."""

    def __init__(self) -> None:
        """Create a private per-instance log for ordered teardown assertions."""
        self.calls: list[str] = []

    def cleanup(self) -> None:
        """Record base cleanup; the test retains the log as its teardown observation."""
        self.calls.append("cleanup")

    def flush(self) -> None:
        """Record flush at its actual position in the runtime disposal sequence."""
        self.calls.append("flush")


class InheritedCleanup(CleanupBase):
    """Use the inherited constructor and cleanup without a forwarding implementation."""


class GrandchildCleanup(InheritedCleanup):
    """Inherit cleanup through two class boundaries."""


class UnrelatedMixin:
    """Contribute a first MRO branch without a cleanup declaration."""


class MultipleCleanup(UnrelatedMixin, CleanupBase):
    """Find cleanup in the second inheritance branch."""


class OverrideCleanup(CleanupBase):
    """Replace the base implementation with an observable subclass override."""

    def cleanup(self) -> None:
        """Record only the winning subclass method, never the base method."""
        self.calls.append("override")


class MultipleOverrideCleanup(OverrideCleanup, InheritedCleanup):
    """Resolve a diamond through the first callable definition in Python's MRO."""


class NonCallableShadow(CleanupBase):
    """Hide the base cleanup behind a deliberate non-callable declaration."""

    cleanup = None


class InheritedShadow(NonCallableShadow):
    """Keep an intermediate non-callable shadow authoritative over a deeper method."""


class PropertyShadow(CleanupBase):
    """Ensure disposal admission does not invoke a shadowing property."""

    @property
    def cleanup(self) -> object:
        """Fail if reflection evaluates this descriptor instead of inspecting it statically."""
        raise AssertionError("Binding must not evaluate disposal properties.")


class CleanupMetaclass(type):
    """Declare class-object behavior that does not exist on constructed instances."""

    def cleanup(cls) -> None:
        """Fail if metaclass-only cleanup is treated as an instance disposal method."""
        raise AssertionError("Metaclass cleanup is not instance cleanup.")


class MetaclassOnlyCleanup(metaclass=CleanupMetaclass):
    """Expose no instance cleanup despite its metaclass having a callable member."""


class StaticCleanup:
    """Provide a staticmethod using the existing raw-callable admission rule."""

    @staticmethod
    def cleanup() -> None:
        """Accept a no-argument disposal call without constructing external resources."""
        return


class InheritedStaticCleanup(StaticCleanup):
    """Inherit an already-supported callable descriptor kind."""


class ClassMethodCleanup:
    """Preserve the existing exclusion of raw classmethod descriptors."""

    @classmethod
    def cleanup(cls) -> None:
        """Fail if the inheritance correction silently broadens descriptor eligibility."""
        raise AssertionError("This correction does not add classmethod disposal support.")


class InheritedClassMethodCleanup(ClassMethodCleanup):
    """Retain the same descriptor eligibility across an inheritance boundary."""


class OrderedCleanup(InheritedCleanup):
    """Combine a declared per-spell method with inherited configured methods."""

    def close(self) -> None:
        """Record the declared method's position relative to inherited cleanup and flush."""
        self.calls.append("close")


@pytest.fixture(autouse=True)
def isolated_world() -> Iterator[None]:
    """Use the suite's existing process-owner reset around each real binding graph."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Spellbook._aether
    try:
        yield
    finally:
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        Spellbook._aether = Aether()
        Conduit._aether = Spellbook._aether


@pytest.mark.parametrize("source", ["explicit", "configured"])
@pytest.mark.parametrize("profile", ["general", "detailed"])
def test_requested_inherited_cleanup_is_retained(source: str, profile: str) -> None:
    """Both candidate sources and profile families admit an inherited callable cleanup."""
    with configured_book(["cleanup"] if source == "configured" else []) as book:
        spell_id = book.bind(
            spell=InheritedCleanup, existence="many", profile=profile,
            disposal_method_names=["cleanup"] if source == "explicit" else [],
        )
        spell = book.find_spell_by_id(spell_id)
        assert spell is not None
        assert spell.disposal_method_names == ["cleanup"]
        assert spell.has_disposal_methods is True
        assert spell_id == Bind.spell_id_inspector(
            InheritedCleanup, spell_name=spell.spell_name,
            existence=Existence.many, disposal_method_names=["cleanup"],
        )


@pytest.mark.parametrize("target,expected", [
    (CleanupBase, "cleanup"), (InheritedCleanup, "cleanup"),
    (GrandchildCleanup, "cleanup"), (MultipleCleanup, "cleanup"),
    (OverrideCleanup, "override"), (MultipleOverrideCleanup, "override"),
])
@pytest.mark.parametrize("existence", ["many", "unique"])
def test_teardown_uses_the_winning_inherited_method(
        target: type[CleanupBase], expected: str, existence: str,
) -> None:
    """Real teardown invokes exactly the callable selected by Python inheritance semantics."""
    with configured_book([]) as book:
        spell_id = book.bind(spell=target, existence=existence, disposal_method_names=["cleanup"])
        conduit = book.conjure()
        instance = conduit.meld(spell_id=spell_id)
        conduit.permanent_cleanup()
        assert instance.calls == [expected]


@pytest.mark.parametrize("target", [
    NonCallableShadow, InheritedShadow, PropertyShadow, MetaclassOnlyCleanup,
    ClassMethodCleanup, InheritedClassMethodCleanup,
])
def test_unavailable_or_unsupported_cleanup_stays_excluded(target: type) -> None:
    """Do not revive shadowed methods, evaluate properties or admit metaclass-only callables."""
    with configured_book(["cleanup"]) as book:
        spell_id = book.bind(spell=target, existence="many", disposal_method_names=["cleanup"])
        spell = book.find_spell_by_id(spell_id)
        assert spell is not None
        assert spell.disposal_method_names == []
        assert spell.has_disposal_methods is False


def test_inherited_staticmethod_keeps_existing_callable_eligibility() -> None:
    """A staticmethod that is eligible when declared remains eligible when inherited."""
    with configured_book([]) as book:
        spell_id = book.bind(
            spell=InheritedStaticCleanup, existence="many", disposal_method_names=["cleanup"],
        )
        spell = book.find_spell_by_id(spell_id)
        assert spell is not None
        assert spell.disposal_method_names == ["cleanup"]


@pytest.mark.parametrize("priority,expected", [
    (False, ["close", "flush", "cleanup"]), (True, ["flush", "cleanup", "close"]),
])
def test_inherited_disposal_preserves_priority_overlap_and_deduplication(
        priority: bool, expected: list[str],
) -> None:
    """Mixed declared/inherited methods retain book overlap ownership and actual call ordering."""
    with configured_book(["flush", "cleanup", "flush"], priority) as book:
        spell_id = book.bind(
            spell=OrderedCleanup, existence="many",
            disposal_method_names=["cleanup", "close", "close", "missing", "__str__"],
        )
        spell = book.find_spell_by_id(spell_id)
        assert spell is not None
        assert spell.disposal_method_names == expected
        conduit = book.conjure()
        instance = conduit.meld(spell_id=spell_id)
        conduit.permanent_cleanup()
        assert instance.calls == expected


def test_unrequested_base_callable_does_not_change_binding_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    """Preserving the shallow profile avoids unrelated ID drift from expanding inherited members."""
    before = Bind.spell_id_inspector(InheritedCleanup, existence=Existence.many)

    def unrelated_method(self: CleanupBase) -> None:
        """Supply an unrequested base method whose existence must not affect the child fingerprint."""
        return

    monkeypatch.setattr(CleanupBase, "unrelated_operation", unrelated_method, raising=False)
    after = Bind.spell_id_inspector(InheritedCleanup, existence=Existence.many)
    assert after == before


def test_inactive_binding_resolves_inherited_cleanup_before_fingerprinting() -> None:
    """A staged member receives its own inherited disposal policy without changing the active one."""
    with configured_book([], dynamic=True) as book:
        active_id = book.bind(spell=InheritedCleanup, existence="many")
        active = book.find_spell_by_id(active_id)
        assert active is not None
        staged_id = book.bind_inactive(
            spell=InheritedCleanup, spell_index=active.spell_index, existence="many",
            disposal_method_names=["cleanup"],
        )
        staged = book._get_owned_spell(staged_id)
        assert staged is not None
        try:
            assert staged_id != active_id
            assert staged.disposal_method_names == ["cleanup"]
            assert active.disposal_method_names == []
            assert active.spell_index.selected_spell_id == active_id
        finally:
            book.cleanup_spell(spell=staged)
