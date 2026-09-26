"""Unresolved inputs execute through every executor family: supplied by the meld, or a named error."""

import marshal
from collections.abc import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import (
    build_package,
    load_creation_context_lazy,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError


class Package:
    """A callable-wrapper type that no spell registers (like a kernel-guarded Melder type)."""


class FalseyPackage(Package):
    """A supplied value must count by presence, not truthiness."""

    def __bool__(self) -> bool:
        """Return False while keeping ordinary identity."""
        return False


class Task:
    """Require an unregistered typed value; the meld that constructs it supplies it."""

    def __init__(self, work: Package) -> None:
        """Retain the supplied value by identity."""
        self.work = work


class Shared:
    """Registered with a shared lifetime to force the generalized family."""


class Pool:
    """Build Task as a dependency so the unresolved input sits one level down."""

    def __init__(self, task: Task, shared: Shared) -> None:
        """Keep both dependencies."""
        self.task = task
        self.shared = shared


class Faulty:
    """Its body raises TypeError with the input supplied: the generic error must be kept."""

    def __init__(self, work: Package) -> None:
        """Fail inside the constructor body, after binding succeeded."""
        raise TypeError("body failure unrelated to inputs")


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


def _build_runtime(book: Spellbook, family: str, cached: bool, task_existence: str = "many") -> tuple[Conduit, str]:
    """Build a family around Task and optionally marshal/reinstall its lazy manifest cache package."""
    task_id = book.bind(spell=Task, existence=task_existence)
    root_id = task_id
    if family != "solo":
        book.bind(spell=Shared, existence="unique" if family == "generalized" else "many")
        root_id = book.bind(spell=Pool, existence="many")
    conduit = book.conjure()
    root = book._spells_by_id[root_id]
    package = build_package(root)
    assert package["family_id"] == f"{family}_codegen_creation"
    if cached:
        detached_package = marshal.loads(marshal.dumps(package))
        root._cleanup_creation_context()
        load_creation_context_lazy(root, detached_package, publish=True)
    return conduit, root_id


def _task_of(result: object, family: str) -> Task:
    """Return the Task a family's root produced."""
    return result if family == "solo" else result.task


@pytest.mark.parametrize(("family", "key"), [
    ("solo", "work"),
    ("many_only", "task>work"),
    ("many_only", "**work"),
    ("generalized", "task>work"),
    ("generalized", "**work"),
])
@pytest.mark.parametrize("cached", [False, True])
@pytest.mark.parametrize("value_kind", ["object", "falsey", "none"])
def test_supplied_value_reaches_the_consumer_by_identity(
    runtime_book: Spellbook, family: str, key: str, cached: bool, value_kind: str,
) -> None:
    """
    Root key, path key and broadcast key deliver the exact supplied object, None included.

    Broadcast keys address dependencies; a solo root takes root keys only (existing behavior).
    """
    conduit, root_id = _build_runtime(runtime_book, family, cached)
    value = None if value_kind == "none" else FalseyPackage() if value_kind == "falsey" else Package()
    for _attempt in range(2):
        assert _task_of(conduit.meld(spell_id=root_id, override={key: value}), family).work is value


@pytest.mark.parametrize("family", ["solo", "many_only", "generalized"])
@pytest.mark.parametrize("cached", [False, True])
def test_missing_value_raises_unresolved_input_error(
    runtime_book: Spellbook, family: str, cached: bool,
) -> None:
    """Omitting the value names the consumer, parameter, expected type and override keys."""
    conduit, root_id = _build_runtime(runtime_book, family, cached)
    with pytest.raises(UnresolvedInputError) as caught:
        conduit.meld(spell_id=root_id)
    error = caught.value
    assert isinstance(error, MeldExecutionError)
    assert (error.spell_name, error.param_name, error.expected_type) == ("Task", "work", "Package")
    assert error.unresolved_params == ("work",)
    assert isinstance(error.__cause__, TypeError)
    message = str(error)
    assert "override={'work': ...}" in message
    assert "'>work'" in message and "'**work'" in message


@pytest.mark.parametrize("family", ["many_only", "generalized"])
@pytest.mark.parametrize("cached", [False, True])
def test_overriding_another_input_still_names_the_missing_one(
    runtime_book: Spellbook, family: str, cached: bool,
) -> None:
    """The override lane reports the unresolved input left out of an otherwise overridden meld."""
    conduit, root_id = _build_runtime(runtime_book, family, cached)
    with pytest.raises(UnresolvedInputError, match="Task.work expects Package"):
        conduit.meld(spell_id=root_id, override={"shared": Shared()})


def test_positional_value_supplies_the_unresolved_input(runtime_book: Spellbook) -> None:
    """A positional override counts as supplying the parameter at that position."""
    conduit, root_id = _build_runtime(runtime_book, "solo", False)
    value = Package()
    assert conduit.meld(spell_id=root_id, override=[value]).work is value


def test_reused_consumer_needs_no_repeated_value(runtime_book: Spellbook) -> None:
    """A stored consumer is reused without its constructor, so it never demands the input again."""
    root_id = runtime_book.bind(spell=Task, existence="unique")
    conduit = runtime_book.conjure()
    value = Package()
    first = conduit.meld(spell_id=root_id, override={"work": value})
    assert conduit.meld(spell_id=root_id) is first
    assert first.work is value


@pytest.mark.parametrize("nested", [False, True])
def test_unrelated_constructor_type_error_keeps_the_existing_error(runtime_book: Spellbook, nested: bool) -> None:
    """With the input supplied, a TypeError from the constructor body is not reported as a missing input."""
    class Holder:
        """Build Faulty as a dependency."""

        def __init__(self, faulty: Faulty) -> None:
            """Keep the dependency."""
            self.faulty = faulty

    runtime_book.bind(spell=Faulty, existence="many")
    root_id = runtime_book.bind(spell=Holder, existence="many") if nested else None
    conduit = runtime_book.conjure()
    value = Package()
    if nested:
        with pytest.raises(MeldExecutionError) as caught:
            conduit.meld(spell_id=root_id, override={"faulty>work": value})
        assert not isinstance(caught.value, UnresolvedInputError)
        assert "body failure" in str(caught.value.__cause__)
    else:
        with pytest.raises(TypeError, match="body failure") as caught:
            conduit.meld(spell=Faulty, override={"work": value})
        assert not isinstance(caught.value, UnresolvedInputError)


def test_all_missing_inputs_are_listed_in_signature_order(runtime_book: Spellbook) -> None:
    """Every unresolved input left out is named; the first one drives the message."""
    class TwoInputs:
        """Two unregistered typed parameters."""

        def __init__(self, first: Package, second: FalseyPackage) -> None:
            """Keep both values."""
            self.first = first
            self.second = second

    root_id = runtime_book.bind(spell=TwoInputs, existence="many")
    conduit = runtime_book.conjure()
    with pytest.raises(UnresolvedInputError) as caught:
        conduit.meld(spell_id=root_id)
    assert caught.value.unresolved_params == ("first", "second")
    assert "Also not supplied: 'second'" in str(caught.value)
    with pytest.raises(UnresolvedInputError) as caught:
        conduit.meld(spell_id=root_id, override={"first": Package()})
    assert caught.value.unresolved_params == ("second",)
    assert caught.value.expected_type == "FalseyPackage"
