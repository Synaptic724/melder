"""Behavioral contracts for Book-owned registration hooks, independent of Meld hooks."""

import gc
import weakref
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from types import ModuleType
from typing import TYPE_CHECKING, Any, Protocol, Union

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.bind.scan import scan_bind
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbinder import SpellBinder
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.custom_exceptions.hook_execution_error import HookExecutionError
from tests.component.melder.aether.conduit.test_conduit_component_creations import (
    _make_spellbook,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.bind.spell_index import SpellIndex


class HookService:
    """Dependency-free class used to observe registration separately from creation."""


class HookAlternative:
    """Distinct dependency-free version used for staged and repeated registration tests."""


@pytest.fixture(autouse=True)
def isolated_hook_world() -> Iterator[None]:
    """
    Purpose: Give each case an isolated Aether/Nexus world.
    Contract: Reset process roots before and after; tests clean their owned scopes.
    Yields: None while the test uses the fresh world.
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


def test_registration_stages_receive_reference_and_same_completed_spell() -> None:
    """
    Purpose: Prove ordering, callback subjects and activation customization.
    Contract: Bind constructs no application object; post can find the registered Spell.
    Returns: None; the book is cleaned even if an assertion fails.
    """
    book = _make_spellbook()
    events: list[tuple[str, object]] = []

    def pre(reference: object) -> None:
        """Record the unchanged incoming reference before its Spell exists."""
        events.append(("pre", reference))

    def activation(spell: Spell) -> None:
        """Record the actual unpublished Spell and add application metadata."""
        assert book.find_spell_by_id(spell.spell_id) is None
        spell.metadata["activated"] = True
        events.append(("activation", spell))

    def post(spell: Spell) -> None:
        """Verify registration and activation effects before recording completion."""
        assert book.find_spell_by_id(spell.spell_id) is spell
        assert spell.metadata["activated"] is True
        events.append(("post", spell))

    try:
        book.add_bind_hooks(pre=[pre], activation=[activation], post=[post])
        spell_id = book.bind(spell=HookService, existence="unique")
        registered = book.find_spell_by_id(spell_id)
        assert events == [("pre", HookService), ("activation", registered), ("post", registered)]
        assert registered.user_created_object is None
    finally:
        book.cleanup()


@pytest.mark.parametrize("stage", ["pre", "activation", "post"])
def test_append_clear_and_register_again_preserves_order(stage: str) -> None:
    """
    Purpose: Exercise each public registration stage's full update lifecycle.
    Contract: Appends and duplicates run in order; clear affects subsequent binds.
    Args: stage: Selected callback stage.
    Returns: None.
    """
    book = _make_spellbook()
    calls: list[str] = []

    def first(_subject: object) -> None:
        """Append the first callback's marker without changing the subject."""
        calls.append("first")

    def second(_subject: object) -> None:
        """Append the second callback's marker without changing the subject."""
        calls.append("second")

    try:
        book.add_bind_hooks(**{stage: [first]})
        book.add_bind_hooks(**{stage: [second, first]})
        book.bind(spell=HookService, existence="unique", binding_name="one")
        assert calls == ["first", "second", "first"]
        book.clear_bind_hooks()
        book.clear_bind_hooks()
        book.bind(spell=HookService, existence="unique", binding_name="two")
        assert calls == ["first", "second", "first"]
        book.add_bind_hooks(**{stage: [second]})
        book.bind(spell=HookService, existence="unique", binding_name="three")
        assert calls == ["first", "second", "first", "second"]
    finally:
        book.cleanup()


@pytest.mark.parametrize("stage", ["pre", "activation", "post"])
def test_bad_callback_rejects_the_whole_registration_update(stage: str) -> None:
    """
    Purpose: Prevent partially installed callback batches.
    Contract: One invalid callback leaves every previously configured stage unchanged.
    Args: stage: Stage containing the invalid callback.
    Returns: None.
    """
    book = _make_spellbook()
    calls: list[object] = []
    additions: dict[str, Any] = {"pre": [calls.append], stage: [object()]}
    try:
        book.add_bind_hooks(post=[calls.append])
        with pytest.raises(TypeError, match="callable"):
            book.add_bind_hooks(**additions)
        spell_id = book.bind(spell=HookService, existence="unique")
        assert calls == [book.find_spell_by_id(spell_id)]
    finally:
        book.cleanup()


@pytest.mark.parametrize("stage,phase", [
    ("pre", "pre_bind"), ("activation", "bind_activation"), ("post", "post_bind"),
])
def test_hook_failure_keeps_phase_cause_and_stops_later_callbacks(stage: str, phase: str) -> None:
    """
    Purpose: Verify actionable failure and explicit publication timing.
    Contract: First callback failure stops the stage; post failure keeps its binding.
    Args: stage: Configured stage; phase: Expected HookExecutionError phase.
    Returns: None.
    """
    book = _make_spellbook()
    subjects: list[object] = []
    later: list[object] = []
    failure = ValueError("reference refused")

    def reject(subject: object) -> None:
        """Retain the failed stage's subject and raise the original test exception."""
        subjects.append(subject)
        raise failure

    try:
        book.add_bind_hooks(**{stage: [reject, later.append]})
        with pytest.raises(HookExecutionError) as raised:
            book.bind(spell=HookService, existence="unique")
        assert raised.value.phase == phase
        assert raised.value.original_exception is failure
        assert raised.value.__cause__ is failure
        assert later == []
        if stage == "pre":
            assert subjects == [HookService]
        else:
            assert isinstance(subjects[0], Spell)
            if stage == "activation":
                assert subjects[0].cleaned is True
            else:
                assert book.find_spell_by_id(subjects[0].spell_id) is subjects[0]
        book.clear_bind_hooks()
        if stage != "post":
            retry_id = book.bind(spell=HookService, existence="unique")
            assert book.find_spell_by_id(retry_id).spell is HookService
    finally:
        book.cleanup()


def test_activation_failure_cleans_its_index_and_preserves_existing_binding() -> None:
    """
    Purpose: Prevent unpublished teardown from entering registered-world removal.
    Contract: Failed Spell/index retire; an earlier binding stays live and meldable.
    Returns: None.
    """
    book = _make_spellbook()
    original_id = book.bind(spell=HookService, existence="unique")
    allocated: list[Union[Spell, SpellIndex]] = []

    def fail(spell: Spell) -> None:
        """Retain the new allocations to observe deterministic failure cleanup."""
        allocated.extend([spell, spell.spell_index])
        raise RuntimeError("activation failed")

    book.add_bind_hooks(activation=[fail])
    try:
        with pytest.raises(HookExecutionError):
            book.bind(spell=HookAlternative, existence="unique")
        assert all(item.cleaned for item in allocated)
        assert book.find_spell_by_id(original_id).cleaned is False
        book.clear_bind_hooks()
        root = book.conjure()
        try:
            assert isinstance(root.meld(spell_id=original_id), HookService)
        finally:
            root.permanent_cleanup()
    finally:
        book.cleanup()


def test_callback_updates_do_not_change_the_remaining_stages_of_current_bind() -> None:
    """
    Purpose: Make reentrant registry replacement deterministic.
    Contract: A pre callback's clear/add affects the next bind, not current activation/post.
    Returns: None.
    """
    book = _make_spellbook()
    old_calls: list[object] = []
    new_calls: list[object] = []

    def update(_reference: object) -> None:
        """Replace callbacks during pre while the current bind retains its old set."""
        book.clear_bind_hooks()
        book.add_bind_hooks(activation=[new_calls.append], post=[new_calls.append])

    try:
        book.add_bind_hooks(pre=[update], activation=[old_calls.append], post=[old_calls.append])
        first_id = book.bind(spell=HookService, existence="unique")
        first = book.find_spell_by_id(first_id)
        assert old_calls == [first, first] and new_calls == []
        second_id = book.bind(spell=HookAlternative, existence="unique")
        second = book.find_spell_by_id(second_id)
        assert old_calls == [first, first] and new_calls == [second, second]
    finally:
        book.cleanup()


def test_registry_can_change_from_another_thread_during_activation() -> None:
    """
    Purpose: Detect construction-lock retention across user callbacks.
    Contract: Another thread can update the registry while activation waits for that update.
    Returns: None; bounded waits turn lock inversion into a clear failure.
    """
    book = _make_spellbook()
    entered = Event()
    updated = Event()
    old_post: list[object] = []
    new_post: list[object] = []

    def activation(_spell: Spell) -> None:
        """Wait for the concurrent registration update after entering activation."""
        entered.set()
        assert updated.wait(5), "registration was blocked behind the callback"

    def update() -> None:
        """Clear and install the next operation's callbacks on the worker thread."""
        assert entered.wait(5)
        book.clear_bind_hooks()
        book.add_bind_hooks(post=[new_post.append])
        updated.set()

    try:
        book.add_bind_hooks(activation=[activation], post=[old_post.append])
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(update)
            first_id = book.bind(spell=HookService, existence="unique")
            future.result(timeout=5)
        assert old_post == [book.find_spell_by_id(first_id)] and new_post == []
        second_id = book.bind(spell=HookAlternative, existence="unique")
        assert new_post == [book.find_spell_by_id(second_id)]
    finally:
        book.cleanup()


@pytest.mark.parametrize("cleanup_book", [False, True])
def test_callback_references_release_without_disposing_user_callback(cleanup_book: bool) -> None:
    """
    Purpose: Prove callback ownership and deterministic release.
    Contract: Clear/book cleanup drops its callbacks but never calls user cleanup.
    Args: cleanup_book: Retire the Book instead of clearing its registry.
    Returns: None.
    """
    disposed: list[bool] = []

    class Callback:
        """User-owned callable with an observable cleanup method and weak reference support."""

        def __call__(self, _reference: object) -> None:
            """Accept a reference without side effects."""

        def cleanup(self) -> None:
            """Record an impermissible disposal by the callback registry."""
            disposed.append(True)

    book = _make_spellbook()
    callback = Callback()
    reference = weakref.ref(callback)
    binder = book._bind
    book.add_bind_hooks(pre=[callback])
    del callback
    try:
        assert reference() is not None
        if cleanup_book:
            book.cleanup()
            assert binder.cleaned
        else:
            book.clear_bind_hooks()
        gc.collect()
        assert reference() is None and disposed == []
    finally:
        book.cleanup()


@pytest.mark.parametrize("entry", ["direct", "fluent", "scan", "conduit"])
def test_registration_entry_points_dispatch_once(entry: str) -> None:
    """
    Purpose: Qualify wrappers without adding per-wrapper hook implementations.
    Contract: Each completed registration invokes each Book-owned stage once.
    Args: entry: Public registration path to exercise.
    Returns: None.
    """
    book = _make_spellbook(dynamic=True)
    pre: list[object] = []
    activation: list[Spell] = []
    post: list[Spell] = []
    root = None
    try:
        book.add_bind_hooks(pre=[pre.append], activation=[activation.append], post=[post.append])
        if entry == "fluent":
            binder = SpellBinder(book)
            spell_id = binder.bind(HookService, existence="unique").finalize()
        elif entry == "scan":
            module = ModuleType("bind_hook_scan_case")

            @scan_bind(existence="unique", permissions="create")
            class Scanned:
                """Resource-free scan target; only the scanner performs its binding."""

            Scanned.__module__ = module.__name__
            module.__dict__["Scanned"] = Scanned
            assert pre == []
            spell_id, = book.scan(module)
        elif entry == "conduit":
            root = book.conjure(dynamic=True)
            spell_id = root.bind(spell=HookService, existence="unique")
        else:
            spell_id = book.bind(spell=HookService, existence="unique")
        spell = book.find_spell_by_id(spell_id)
        assert pre == [spell.spell]
        assert activation == [spell] and post == [spell]
    finally:
        if root is not None:
            root.permanent_cleanup()
        book.cleanup()


def test_inactive_post_observes_parked_member_on_final_index() -> None:
    """
    Purpose: Verify staging uses the same lifecycle with its own completion state.
    Contract: Activation sees the new index; post sees the final shared index and inactive Spell.
    Returns: None; later notch/meld must not rerun registration callbacks.
    """
    book = _make_spellbook(dynamic=True)
    anchor_id = book.bind(spell=HookService, existence="unique")
    target_index = book.find_spell_by_id(anchor_id).spell_index
    events: list[tuple[str, Spell]] = []
    fresh_indexes: list[SpellIndex] = []

    def activation(spell: Spell) -> None:
        """Observe fresh construction before the inactive member is parked and folded."""
        assert spell.spell_index is not target_index
        fresh_indexes.append(spell.spell_index)
        events.append(("activation", spell))

    def post(spell: Spell) -> None:
        """Observe the final parked member and target index after staging succeeds."""
        assert spell.spell_index is target_index and spell._active is False
        assert book._inactive_spells[spell.spell_id] is spell
        events.append(("post", spell))

    root = book.conjure(dynamic=True)
    try:
        book.add_bind_hooks(activation=[activation], post=[post])
        staged_id = root.bind_inactive(
            spell=HookAlternative, spell_index=target_index, existence="unique",
        )
        assert [phase for phase, _spell in events] == ["activation", "post"]
        assert events[0][1] is events[1][1]
        assert fresh_indexes[0].cleaned
        root.notch_spell(spell_index=target_index, spell=events[1][1])
        assert isinstance(root.meld(spell_id=staged_id), HookAlternative)
        assert len(events) == 2
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("kind", ["class", "function", "instance", "definition"])
def test_supported_reference_families_keep_their_native_contract(kind: str) -> None:
    """
    Purpose: Verify hook subjects without changing registration families or identity.
    Contract: Pre receives the exact input; activation/post receive its Spell, never a new instance.
    Args: kind: Native reference family to bind.
    Returns: None.
    """
    class Definition(Protocol):
        """Descriptive, non-resolvable interface used to qualify native admission."""

    def factory() -> HookService:
        """Return an application object only if a future caller invokes this function."""
        return HookService()

    targets: dict[str, object] = {
        "class": HookService, "function": factory,
        "instance": HookService(), "definition": Definition,
    }
    target = targets[kind]
    pre: list[object] = []
    activated: list[Spell] = []
    post: list[Spell] = []
    book = _make_spellbook()
    try:
        book.add_bind_hooks(pre=[pre.append], activation=[activated.append], post=[post.append])
        spell_id = book.bind(spell=target, existence="unique", resolvable=kind != "definition")
        spell = book.find_spell_by_id(spell_id)
        assert pre == [target] and pre[0] is target
        assert activated == [spell] and post == [spell]
        assert spell.spell is target
        if kind == "instance":
            root = book.conjure()
            try:
                assert root.meld(spell_id=spell_id) is target
            finally:
                root.permanent_cleanup()
    finally:
        book.cleanup()


def test_bind_activation_preserves_native_hash_and_existing_creation_hook_precedence() -> None:
    """
    Purpose: Keep bind customization separate from native identities and Meld hooks.
    Contract: Explicit bind creation-hook kwargs replace the corresponding activation-configured list.
    Returns: None.
    """
    book = _make_spellbook()
    shadowed: list[object] = []
    created: list[object] = []
    registered: list[Spell] = []

    def activation(spell: Spell) -> None:
        """Add metadata and a creation callback before explicit bind kwargs are attached."""
        spell.metadata["configured"] = True
        spell._set_hooks(activation_hooks=[shadowed.append])
        registered.append(spell)

    try:
        expected_id = Bind.spell_id_inspector(
            HookService, spell_name="HookService", existence=Existence.unique,
        )
        book.add_bind_hooks(activation=[activation])
        spell_id = book.bind(
            spell=HookService, existence="unique", activation_hooks=[created.append],
        )
        assert spell_id == expected_id and created == [] and shadowed == []
        book.clear_bind_hooks()
        root = book.conjure()
        try:
            instance = root.meld(spell_id=spell_id)
            assert root.meld(spell_id=spell_id) is instance
            assert created == [instance] and shadowed == []
            assert len(registered) == 1
        finally:
            root.permanent_cleanup()
    finally:
        book.cleanup()


def test_nested_bind_and_outer_batch_keep_per_registration_post_order() -> None:
    """
    Purpose: Exercise finite callback reentrancy through real mediator joins.
    Contract: Nested registration completes before the outer post; posts run inside the batch.
    Returns: None.
    """
    book = _make_spellbook()
    events: list[tuple[str, object]] = []

    def activation(spell: Spell) -> None:
        """Bind one distinct dependency only while activating the outer target."""
        events.append(("activation", spell.spell))
        if spell.spell is HookService:
            book.bind(spell=HookAlternative, existence="unique")

    def post(spell: Spell) -> None:
        """Record per-registration completion without waiting for the batch to end."""
        events.append(("post", spell.spell))

    try:
        book.add_bind_hooks(activation=[activation], post=[post])
        with book.transaction("bind"):
            book.bind(spell=HookService, existence="unique")
            assert events == [
                ("activation", HookService), ("activation", HookAlternative),
                ("post", HookAlternative), ("post", HookService),
            ]
        root = book.conjure()
        root.permanent_cleanup()
    finally:
        book.cleanup()


def test_book_hooks_do_not_leak_through_shared_configuration_or_presets() -> None:
    """
    Purpose: Keep callbacks owned by the original Book/Bind rather than configuration.
    Contract: A shared-config book and a preset clone start with empty callback registries.
    Returns: None.
    """
    book = _make_spellbook()
    other = Spellbook(configuration=book.get_configuration())
    preset = book.create_new_preset_spellbook()
    calls: list[object] = []
    try:
        book.add_bind_hooks(pre=[calls.append])
        other.bind(spell=HookService, existence="unique", binding_name="other")
        preset.bind(spell=HookService, existence="unique", binding_name="preset")
        assert calls == []
        book.bind(spell=HookService, existence="unique", binding_name="owner")
        assert calls == [HookService]
    finally:
        preset.cleanup()
        other.cleanup()
        book.cleanup()


@pytest.mark.parametrize("inactive", [False, True])
def test_collision_skips_post_and_retires_the_unpublished_activated_spell(inactive: bool) -> None:
    """
    Purpose: Qualify failures that occur after successful bind activation.
    Contract: A duplicate keeps the original binding, skips post and cleans its rejected allocation.
    Args: inactive: Attempt to park the duplicate instead of binding it actively.
    Returns: None.
    """
    book = _make_spellbook(dynamic=True)
    activated: list[Spell] = []
    posts: list[Spell] = []
    try:
        book.add_bind_hooks(activation=[activated.append], post=[posts.append])
        spell_id = book.bind(spell=HookService, existence="unique")
        with pytest.raises(RuntimeError):
            if inactive:
                book.bind_inactive(
                    spell=HookService, existence="unique", spell_index=activated[0].spell_index,
                )
            else:
                book.bind(spell=HookService, existence="unique")
        assert len(activated) == 2 and posts == [activated[0]]
        assert activated[1].cleaned
        assert book.find_spell_by_id(spell_id) is activated[0]
    finally:
        book.cleanup()


def test_pre_return_value_does_not_replace_or_reject_the_target() -> None:
    """
    Purpose: Keep callback return handling identical to synchronous activation hooks.
    Contract: False is ignored; pre checks reject through explicit exceptions.
    Returns: None.
    """
    book = _make_spellbook()
    try:
        book.add_bind_hooks(pre=[lambda _reference: False])
        spell_id = book.bind(spell=HookService, existence="unique")
        assert book.find_spell_by_id(spell_id).spell is HookService
    finally:
        book.cleanup()


def test_failed_existing_object_activation_does_not_dispose_the_supplied_instance() -> None:
    """
    Purpose: Keep unpublished Spell teardown separate from user-object ownership.
    Contract: A supplied instance survives failed activation without its cleanup being called.
    Returns: None.
    """
    class Supplied:
        """Externally constructed value with observable resource disposal."""

        def __init__(self) -> None:
            """Start live; the application owns the eventual disposal decision."""
            self.disposed = False

        def cleanup(self) -> None:
            """Mark disposal so an incorrect registration teardown is observable."""
            self.disposed = True

    def fail(_spell: Spell) -> None:
        """Reject this registration without requesting disposal of its supplied object."""
        raise ValueError("reject supplied registration")

    supplied = Supplied()
    book = _make_spellbook()
    try:
        book.add_bind_hooks(activation=[fail])
        with pytest.raises(HookExecutionError):
            book.bind(spell=supplied, existence="unique")
        assert supplied.disposed is False
        book.clear_bind_hooks()
        spell_id = book.bind(spell=supplied, existence="unique")
        assert book.find_spell_by_id(spell_id).user_created_object is supplied
    finally:
        book.cleanup()


@pytest.mark.parametrize("clear", [False, True])
def test_cleaned_book_rejects_hook_registration_and_clearing(clear: bool) -> None:
    """
    Purpose: Keep public hook management inside the normal Book lifetime.
    Contract: Calls after cleanup fail through the standard cleaned-state guard.
    Args: clear: Exercise clearing rather than adding callbacks.
    Returns: None.
    """
    book = _make_spellbook()
    book.cleanup()
    with pytest.raises(RuntimeError):
        if clear:
            book.clear_bind_hooks()
        else:
            book.add_bind_hooks(pre=[lambda _reference: None])


@pytest.mark.parametrize("entry", ["conduit", "spellbook", "inactive"])
def test_conduit_bind_hook_facade_uses_the_owning_book_registry(entry: str) -> None:
    """
    Purpose: Qualify all three callbacks configured through the public Conduit facade.
    Contract: Active, staged and direct-Book binds each invoke the same owner callbacks once.
    Args: entry: Binding door used after configuring callbacks through Conduit.
    Returns: None; all scopes are explicitly retired.
    """
    book = _make_spellbook(dynamic=True)
    anchor_id = book.bind(spell=HookService, existence="unique")
    target_index = book.find_spell_by_id(anchor_id).spell_index
    root = book.conjure(dynamic=True)
    references: list[object] = []
    activation: list[Spell] = []
    post: list[Spell] = []
    try:
        root.add_bind_hooks(
            pre=[references.append], activation=[activation.append], post=[post.append],
        )
        if entry == "inactive":
            spell_id = root.bind_inactive(
                spell=HookAlternative, spell_index=target_index, existence="unique",
            )
        else:
            registrar = root if entry == "conduit" else book
            spell_id = registrar.bind(spell=HookAlternative, existence="unique")
        assert references == [HookAlternative]
        assert len(activation) == 1 and activation == post
        assert post[0].spell_id == spell_id
        if entry == "inactive":
            assert post[0]._active is False and post[0].spell_index is target_index
        else:
            assert book.find_spell_by_id(spell_id) is post[0]
    finally:
        root.permanent_cleanup()


def test_conduit_clear_removes_book_and_facade_registrations_and_allows_registering_again() -> None:
    """
    Purpose: Prove the facade clears the owner's registry instead of a separate local overlay.
    Contract: Book and Conduit registrations append together; clear affects both public bind doors.
    Returns: None; re-registration starts a fresh callback sequence.
    """
    class ReboundService:
        """
        Purpose: Supply a distinct, dependency-free target after clearing hooks.
        Contract: Its name does not collide with the earlier post-conjure bindings.
        """

    book = _make_spellbook(dynamic=True)
    owner_calls: list[object] = []
    conduit_calls: list[object] = []
    replacement_calls: list[object] = []
    book.add_bind_hooks(pre=[owner_calls.append])
    root = book.conjure(dynamic=True)
    try:
        root.add_bind_hooks(pre=[conduit_calls.append])
        root.bind(spell=HookService, existence="unique", binding_name="first")
        assert owner_calls == [HookService] and conduit_calls == [HookService]
        root.clear_bind_hooks()
        book.bind(spell=HookAlternative, existence="unique", binding_name="second")
        assert owner_calls == [HookService] and conduit_calls == [HookService]
        root.add_bind_hooks(pre=[replacement_calls.append])
        root.bind(spell=ReboundService, existence="unique", binding_name="third")
        assert replacement_calls == [ReboundService]
        assert owner_calls == [HookService] and conduit_calls == [HookService]
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("dynamic", [False, True])
@pytest.mark.parametrize("clear", [False, True])
def test_lesser_cannot_configure_or_clear_borrowed_book_bind_hooks(dynamic: bool, clear: bool) -> None:
    """
    Purpose: Preserve the normal conduit's authority over its Book's binding policy.
    Contract: Lesser refusal happens before delegation and preserves the owner's callbacks.
    Args: dynamic: Frame posture; clear: Attempt clearing instead of registering.
    Returns: None.
    """
    book = _make_spellbook(dynamic=dynamic)
    callbacks: list[object] = []
    book.add_bind_hooks(pre=[callbacks.append])
    before = book._bind.capture_hooks()
    root = book.conjure(dynamic=dynamic)
    lesser = root.create_lesser_conduit()
    try:
        with pytest.raises(RuntimeError, match="Only normal conduits"):
            if clear:
                lesser.clear_bind_hooks()
            else:
                lesser.add_bind_hooks(pre=[callbacks.append])
        assert book._bind.capture_hooks() == before
    finally:
        lesser.cleanup()
        root.permanent_cleanup()


@pytest.mark.parametrize("clear", [False, True])
def test_cleaned_conduit_rejects_bind_hook_management(clear: bool) -> None:
    """
    Purpose: Keep facade calls within the Conduit's existing lifetime contract.
    Contract: Cleaned-state refusal precedes access to retired Book/state references.
    Args: clear: Exercise clearing instead of registering.
    Returns: None.
    """
    book = _make_spellbook(dynamic=True)
    root = book.conjure(dynamic=True)
    root.permanent_cleanup()
    with pytest.raises(RuntimeError):
        if clear:
            root.clear_bind_hooks()
        else:
            root.add_bind_hooks(pre=[lambda _reference: None])


def test_automatic_conduit_hook_setup_keeps_book_parity_without_enabling_bind() -> None:
    """
    Purpose: Distinguish hook configuration from actual binding admission.
    Contract: A normal automatic conduit can add/clear callbacks; its bind remains disabled.
    Returns: None.
    """
    book = _make_spellbook()
    root = book.conjure()
    callbacks: list[object] = []
    try:
        root.add_bind_hooks(pre=[callbacks.append])
        assert book._bind.get_hook_names() == ("bind:pre",)
        with pytest.raises(RuntimeError, match="Bind is disabled"):
            root.bind(spell=HookService, existence="unique")
        assert callbacks == []
        root.clear_bind_hooks()
        assert book._bind.get_hook_names() == ()
    finally:
        root.permanent_cleanup()


def test_conduit_hook_facade_preserves_book_batch_validation() -> None:
    """
    Purpose: Ensure the facade forwards every supplied stage to Book validation.
    Contract: An invalid activation callback prevents valid pre callbacks from being installed.
    Returns: None.
    """
    book = _make_spellbook(dynamic=True)
    root = book.conjure(dynamic=True)
    callbacks: list[object] = []
    invalid_callbacks: Any = [object()]
    try:
        with pytest.raises(TypeError, match="callable"):
            root.add_bind_hooks(pre=[callbacks.append], activation=invalid_callbacks)
        root.bind(spell=HookService, existence="unique")
        assert callbacks == []
    finally:
        root.permanent_cleanup()
