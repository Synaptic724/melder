"""Supplied-input compatibility uses ordinary constructor errors and existing runtime lanes."""

import marshal
from collections.abc import Iterator
from typing import Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import (
    build_package,
    load_creation_context_lazy,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


class ExternalValue:
    """An externally created value whose registered definition must never be constructed by Melder."""


class FalseyValue(ExternalValue):
    """A supplied object must not be mistaken for omission because it is falsey."""

    def __bool__(self) -> bool:
        """Return False while retaining ordinary object identity."""
        return False


class SuppliedConsumer:
    """Require a nullable external value without providing a Python default."""

    def __init__(self, external: Optional[ExternalValue]) -> None:
        """Retain the supplied value by identity; Python rejects omission."""
        self.external = external


class DescriptorConsumer:
    """An explicit descriptor selects the registered definition for caller supply."""

    def __init__(self, external: ExternalValue = SpellMap(spell=ExternalValue)) -> None:
        """Retain the effective value, exposing any accidentally injected descriptor."""
        self.external = external


class SharedDependency:
    """Force the generalized family when registered with a shared lifetime."""


class OrdinaryRequiredConsumer:
    """Existing plain-argument behavior with no non-resolvable registration involved."""

    def __init__(self, count: int) -> None:
        """Store a required ordinary Python input."""
        self.count = count


class OrdinaryOuter:
    """Control graph for the existing eager child-construction behavior."""

    def __init__(self, child: OrdinaryRequiredConsumer) -> None:
        """Keep the selected child."""
        self.child = child


class OuterConsumer:
    """Make the supplied socket nested below an ordinary injectable child."""

    def __init__(self, child: SuppliedConsumer, shared: SharedDependency) -> None:
        """Retain both dependencies for nested override and branch-replacement assertions."""
        self.child = child
        self.shared = shared


@pytest.fixture
def runtime_book() -> Iterator[Spellbook]:
    """Create and tear down an isolated world with deterministic compilation and no disk cache."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    book = Spellbook()
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book._aetheric_frame_configuration.with_system_caching_enabled(False)
    try:
        yield book
    finally:
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether


def _build_runtime(book: Spellbook, family: str, cached: bool) -> tuple[Conduit, str]:
    """Build a family and optionally marshal/reinstall its actual lazy manifest cache package."""
    book.bind(spell=ExternalValue, existence="unique", resolvable=False)
    consumer_id = book.bind(spell=SuppliedConsumer, existence="many")
    root_id = consumer_id
    if family != "solo":
        book.bind(spell=SharedDependency, existence="unique" if family == "generalized" else "many")
        root_id = book.bind(spell=OuterConsumer, existence="many")
    conduit = book.conjure()
    root = book._spells_by_id[root_id]
    package = build_package(root)
    assert package["family_id"] == f"{family}_codegen_creation"
    if cached:
        detached_package = marshal.loads(marshal.dumps(package))
        root._cleanup_creation_context()
        load_creation_context_lazy(root, detached_package, publish=True)
    return conduit, root_id


@pytest.mark.parametrize("family", ["solo", "many_only", "generalized"])
@pytest.mark.parametrize("cached", [False, True])
@pytest.mark.parametrize("value_kind", ["object", "falsey", "none"])
def test_supplied_values_survive_each_family_and_manifest_hydration(
    runtime_book: Spellbook, family: str, cached: bool, value_kind: str,
) -> None:
    """Ordinary, falsey and None supplied values reach consumers through every executor family."""
    conduit, root_id = _build_runtime(runtime_book, family, cached)
    value = None if value_kind == "none" else FalseyValue() if value_kind == "falsey" else ExternalValue()
    key = "external" if family == "solo" else "child>external"
    for _attempt in range(2):
        result = conduit.meld(spell_id=root_id, override={key: value})
        consumer = result if family == "solo" else result.child
        assert consumer.external is value


@pytest.mark.parametrize("family", ["solo", "many_only", "generalized"])
@pytest.mark.parametrize("cached", [False, True])
def test_missing_required_values_keep_existing_constructor_failure(
    runtime_book: Spellbook, family: str, cached: bool,
) -> None:
    """Missing Python arguments fail without a new preflight ordering or exception contract."""
    conduit, root_id = _build_runtime(runtime_book, family, cached)
    with pytest.raises((TypeError, MeldExecutionError), match="external"):
        conduit.meld(spell_id=root_id)


@pytest.mark.parametrize("family", ["many_only", "generalized"])
@pytest.mark.parametrize("cached", [False, True])
def test_whole_branch_override_preserves_existing_eager_construction(
    runtime_book: Spellbook, family: str, cached: bool,
) -> None:
    """Existing eager child construction still requires its input before the parent replaces it."""
    conduit, root_id = _build_runtime(runtime_book, family, cached)
    child = SuppliedConsumer(ExternalValue())
    with pytest.raises((TypeError, MeldExecutionError), match="external"):
        conduit.meld(spell_id=root_id, override={"child": child})
    result = conduit.meld(
        spell_id=root_id, override={"child": child, "child>external": child.external},
    )
    assert result.child is child


def test_unique_consumer_reuse_needs_no_repeated_supplied_value(runtime_book: Spellbook) -> None:
    """An input is not required again when ordinary unique reuse avoids construction."""
    runtime_book.bind(spell=ExternalValue, existence="unique", resolvable=False)
    root_id = runtime_book.bind(spell=SuppliedConsumer, existence="unique")
    conduit = runtime_book.conjure()
    value = ExternalValue()
    first = conduit.meld(spell_id=root_id, override={"external": value})
    assert conduit.meld(spell_id=root_id) is first
    assert first.external is value


def test_positional_value_reaches_the_required_constructor(runtime_book: Spellbook) -> None:
    """The existing positional-override path supplies the ordinary required argument."""
    conduit, root_id = _build_runtime(runtime_book, "solo", False)
    value = ExternalValue()
    assert conduit.meld(spell_id=root_id, override=[value]).external is value


def test_explicit_definition_descriptor_uses_supplied_value(runtime_book: Spellbook) -> None:
    """An explicit False descriptor remains override-addressable and does not inject its marker."""
    runtime_book.bind(spell=ExternalValue, existence="unique", resolvable=False)
    root_id = runtime_book.bind(spell=DescriptorConsumer, existence="many")
    conduit = runtime_book.conjure()
    value = ExternalValue()
    assert conduit.meld(spell_id=root_id, override={"external": value}).external is value


def test_ordinary_branch_override_also_constructs_its_registered_child(runtime_book: Spellbook) -> None:
    """Characterize eager construction independently of the new registration capability."""
    runtime_book.bind(spell=OrdinaryRequiredConsumer, existence="many")
    root_id = runtime_book.bind(spell=OrdinaryOuter, existence="many")
    conduit = runtime_book.conjure()
    child = OrdinaryRequiredConsumer(3)
    with pytest.raises((TypeError, MeldExecutionError), match="count"):
        conduit.meld(spell_id=root_id, override={"child": child})
