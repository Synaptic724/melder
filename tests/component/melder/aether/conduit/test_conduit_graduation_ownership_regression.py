"""Red regressions for Book ownership after lesser-to-normal graduation.

These assert the requested independent-Book contract through real registration,
resolution and cleanup. They intentionally fail until graduation adopts its new
Book. Frame-owned shared configuration remains legitimate; Bind callbacks remain
Book-owned in either configuration mode. No optional upgrade keyword is assumed.
"""

from collections.abc import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)


class TrackedService:
    """Provide a creation whose explicit disposal can be observed independently.

    Contract:
        Each instance owns its counter; cleanup changes only that instance.
        No external resources or callbacks are involved.
    """

    def __init__(self) -> None:
        """Initialize the per-instance count before Melder records this creation."""
        self.cleanup_calls: int = 0

    def cleanup(self) -> None:
        """Record each disposal call so missing or repeated disposal is visible."""
        self.cleanup_calls += 1


class ParentService(TrackedService):
    """Distinct parent-owned binding with inherited observable disposal behavior."""


class GraduatedService(TrackedService):
    """Distinct post-graduation binding with inherited observable disposal behavior."""


class LaterParentService(TrackedService):
    """Fresh parent binding used to observe callbacks after the child is changed."""


class GraduationWorld:
    """Own one root and one lesser for a single graduation regression.

    Contract:
        Builds a real dynamic world with explicit local/shared configuration.
        ParentService is initially owned only by the root Book. Tests choose when
        to graduate so hooks or pooled Spaces can be installed beforehand.
        Cleanup retires both scopes and the original Book even after assertions
        fail; it does not rewrite runtime ownership to make a test pass.
    """

    def __init__(self, *, shared_configuration: bool) -> None:
        """Construct isolated scopes with one worker and runtime caching disabled.

        Args:
            shared_configuration: Whether rich configuration is frame-owned.
        Returns:
            None. The fixture owns cleanup of the constructed runtime.
        """
        self.configuration = SpellbookConfiguration(aether_frame="graduation-regression")
        self.configuration.load_default_dictionary()
        self.configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
        frame_configuration = configure_frame_posture_for_spellbook_configuration(
            self.configuration,
            dynamic=True,
            shared_framewide_spellbook_configuration=shared_configuration,
        )
        frame_configuration.with_system_caching_enabled(False)
        self.book = Spellbook(
            aetheric_frame="graduation-regression",
            configuration=self.configuration,
        )
        self.parent_id = self.book.bind(
            spell=ParentService,
            existence=Existence.unique_per_conduit,
            disposal_method_names=["cleanup"],
        )
        self.root = self.book.conjure(dynamic=True, name="parent")
        self.child = self.root.create_lesser_conduit()

    def graduate(self) -> None:
        """Use the existing public upgrade API without simulating Book adoption."""
        self.child.upgrade_to_normal(name="graduated")

    def cleanup(self) -> None:
        """Retire owned scopes in order without hiding failures from test bodies.

        Contract:
            Uses idempotent public teardown in finally blocks so one failed
            teardown does not skip the remaining owner. Tests may already have
            cleaned either scope while checking the opposite cleanup order.
        Returns:
            None.
        """
        try:
            self.child.permanent_cleanup()
        finally:
            try:
                self.root.permanent_cleanup()
            finally:
                self.book.cleanup()


@pytest.fixture(autouse=True)
def isolated_graduation_roots() -> Iterator[None]:
    """Give each test fresh Aether/Nexus roots and retire them after scope cleanup.

    Contract:
        Mirrors the real-runtime Bind test fixture. No singleton state from a
        failing upgrade case is allowed to affect another configuration mode.
    Yields:
        None while the test and its scope fixture execute.
    """
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Aether()
    try:
        yield
    finally:
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        Spellbook._aether = Aether()
        Conduit._aether = Aether()


@pytest.fixture(params=[False, True], ids=["local-config", "framewide-config"])
def graduation_world(request: pytest.FixtureRequest) -> Iterator[GraduationWorld]:
    """Run every ownership regression under both supported configuration owners.

    Args:
        request: Pytest's selected configuration-sharing parameter.
    Yields:
        GraduationWorld: A live root and lesser, not yet upgraded.
    Lifecycle:
        Scope cleanup runs before the autouse singleton fixture is retired.
    """
    world = GraduationWorld(shared_configuration=request.param)
    try:
        yield world
    finally:
        world.cleanup()


def test_graduation_attaches_an_independent_book_to_the_new_root(
    graduation_world: GraduationWorld,
) -> None:
    """The upgraded Book must report the new root as its attached conduit.

    Contract:
        Book identity and its public conduit property establish actual ownership;
        merely calling the preset factory does not satisfy this relationship.
    """
    graduation_world.graduate()
    graduated_book = graduation_world.child._spellbook

    assert graduated_book is not graduation_world.book
    assert graduated_book.conduit is graduation_world.child
    assert graduation_world.book.conduit is graduation_world.root


def test_graduated_binding_is_not_registered_in_the_parent_book(
    graduation_world: GraduationWorld,
) -> None:
    """A new child binding must resolve locally without becoming parent-owned.

    Contract:
        This tests only new ownership; it does not decide whether the upgraded
        conduit continues borrowing previously visible parent definitions.
    """
    graduation_world.graduate()
    child_id = graduation_world.child.bind(
        spell=GraduatedService,
        existence=Existence.unique_per_conduit,
    )

    assert isinstance(graduation_world.child.meld(spell_id=child_id), GraduatedService)
    assert graduation_world.child._spellbook.find_spell_by_id(child_id) is not None
    assert graduation_world.book.find_spell_by_id(child_id) is None


@pytest.mark.parametrize("stage", ["pre", "activation", "post"])
def test_graduation_starts_with_empty_book_bind_hooks(
    graduation_world: GraduationWorld,
    stage: str,
) -> None:
    """Parent Bind callbacks must not run for the new Book's registrations.

    Args:
        graduation_world: Real local- or frame-configured scopes.
        stage: Bind lifecycle stage whose isolation is being checked.
    Contract:
        Configuration sharing does not copy parent Bind callback tuples.
    """
    parent_calls: list[object] = []
    graduation_world.root.add_bind_hooks(**{stage: [parent_calls.append]})
    graduation_world.graduate()

    graduation_world.child.bind(spell=GraduatedService, existence=Existence.unique)

    assert parent_calls == []


@pytest.mark.parametrize("stage", ["pre", "activation", "post"])
def test_graduated_bind_hook_registration_does_not_change_parent_hooks(
    graduation_world: GraduationWorld,
    stage: str,
) -> None:
    """Adding child callbacks must not make parent registrations execute them.

    Args:
        graduation_world: Real scopes with either configuration ownership mode.
        stage: Bind callback stage to register on the graduated conduit.
    Contract:
        Mutation through the normal-Conduit facade targets its own Book only.
    """
    child_calls: list[object] = []
    graduation_world.graduate()
    graduation_world.child.add_bind_hooks(**{stage: [child_calls.append]})

    graduation_world.root.bind(spell=LaterParentService, existence=Existence.unique)

    assert child_calls == []


@pytest.mark.parametrize("stage", ["pre", "activation", "post"])
def test_graduated_bind_hook_clear_preserves_parent_callbacks(
    graduation_world: GraduationWorld,
    stage: str,
) -> None:
    """Clearing child hooks must preserve the parent's next bind callback.

    Args:
        graduation_world: Real scopes with either configuration ownership mode.
        stage: Parent callback stage that must survive child clearing.
    Contract:
        Assert actual callback execution and payload, not only registry contents.
    """
    parent_calls: list[object] = []
    graduation_world.root.add_bind_hooks(**{stage: [parent_calls.append]})
    graduation_world.graduate()
    graduation_world.child.clear_bind_hooks()

    parent_id = graduation_world.root.bind(
        spell=LaterParentService,
        existence=Existence.unique,
    )
    expected = (
        LaterParentService
        if stage == "pre"
        else graduation_world.book.find_spell_by_id(parent_id)
    )
    assert parent_calls == [expected]


def test_graduated_cleanup_keeps_parent_book_and_creation_usable(
    graduation_world: GraduationWorld,
) -> None:
    """Destroying the graduated root must leave its former parent's Book alive.

    Contract:
        Parent configuration remains usable, its existing creation is reused,
        and it can still register another independent definition afterward.
    """
    parent_creation = graduation_world.root.meld(spell_id=graduation_world.parent_id)
    graduation_world.graduate()
    graduation_world.child.permanent_cleanup()

    assert not graduation_world.book.cleaned, "Graduated cleanup retired the parent Book."
    assert graduation_world.book.get_configuration().get_property(
        "phase_scheduler_workers_per_spellbook",
    ) == 1
    assert graduation_world.root.meld(spell_id=graduation_world.parent_id) is parent_creation
    later_id = graduation_world.root.bind(spell=LaterParentService, existence=Existence.unique)
    assert isinstance(graduation_world.root.meld(spell_id=later_id), LaterParentService)


def test_parent_cleanup_keeps_graduated_book_and_own_binding_usable(
    graduation_world: GraduationWorld,
) -> None:
    """The former parent's child list must no longer own a graduated root.

    Contract:
        An independently bound child creation and its Book survive parent
        teardown. No continued access to parent-owned definitions is asserted.
    """
    graduation_world.graduate()
    child_id = graduation_world.child.bind(
        spell=GraduatedService,
        existence=Existence.unique_per_conduit,
    )
    child_creation = graduation_world.child.meld(spell_id=child_id)
    graduation_world.root.permanent_cleanup()

    assert not graduation_world.child.cleaned, "Parent teardown destroyed the graduated root."
    assert not graduation_world.child._spellbook.cleaned
    assert graduation_world.child.meld(spell_id=child_id) is child_creation
    assert child_creation.cleanup_calls == 0


def test_graduated_cleanup_disposes_its_own_unique_without_disposing_parent(
    graduation_world: GraduationWorld,
) -> None:
    """A post-upgrade unique must belong to the graduated root's disposal scope.

    Contract:
        Child cleanup disposes its own new unique exactly once and leaves the
        parent's creation undisposed. This detects wrong owner stamping at bind.
    """
    parent_creation = graduation_world.root.meld(spell_id=graduation_world.parent_id)
    graduation_world.graduate()
    child_id = graduation_world.child.bind(
        spell=GraduatedService,
        existence=Existence.unique,
        disposal_method_names=["cleanup"],
    )
    child_creation = graduation_world.child.meld(spell_id=child_id)
    graduation_world.child.permanent_cleanup()

    assert child_creation.cleanup_calls == 1
    assert parent_creation.cleanup_calls == 0


@pytest.mark.parametrize("prewarmed", [False, True], ids=["fresh-space", "pooled-space"])
def test_post_graduation_spellspace_resolves_only_the_new_books_local_binding(
    graduation_world: GraduationWorld,
    prewarmed: bool,
) -> None:
    """Fresh and previously pooled Spaces must follow the graduated Book.

    Args:
        graduation_world: Real scopes with either configuration ownership mode.
        prewarmed: Whether the idle Space captured the Book before graduation.
    Contract:
        The new local binding resolves through the Space front door and remains
        absent from the parent's owned registry. No active Space crosses upgrade.
    """
    if prewarmed:
        graduation_world.child.prewarm_spellspaces(1)
    graduation_world.graduate()
    child_id = graduation_world.child.bind(
        spell=GraduatedService,
        existence=Existence.unique_per_spell_space,
    )

    with graduation_world.child.enter_spellspace() as space:
        creation = space.meld(spell_id=child_id)
        assert isinstance(creation, GraduatedService)
        assert space.meld(spell_id=child_id) is creation
        assert graduation_world.book.find_spell_by_id(child_id) is None
