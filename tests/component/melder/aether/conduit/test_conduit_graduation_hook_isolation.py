"""Public graduation discards former runtime hooks and reapplies only selected policy."""

from typing import TYPE_CHECKING

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)
from tests.component.melder.aether.conduit import (
    test_conduit_graduation_ownership_regression as graduation_support,
)
from tests.component.melder.aether.conduit.test_conduit_graduation_ownership_regression import (
    GraduatedService,
    LaterParentService,
    ParentService,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell

isolated_graduation_roots = graduation_support.isolated_graduation_roots


class HookRecorder:
    """Record actual callback dispatch without retaining application resources.

    Contract:
        Each instance owns only its event list. Different recorders distinguish
        configuration callbacks, former-Book Bind mutations and runtime overlays.
    """

    def __init__(self) -> None:
        """Initialize an ordered callback trace for one hook source."""
        self.events: list[str] = []

    def pre(self, reference: object) -> None:
        """Observe a real pre-bind call; the original reference is never changed."""
        self.events.append("bind-pre")

    def activation(self, spell: Spell) -> None:
        """Observe the constructed Spell without modifying its registration."""
        self.events.append("bind-activation")

    def post(self, spell: Spell) -> None:
        """Observe successful Book registration."""
        self.events.append("bind-post")

    def conduit(self, *args: object) -> None:
        """Observe configured creation, link or cleanup lifecycle dispatch."""
        self.events.append("conduit")

    def meld(self, *args: object) -> None:
        """Observe pre-resolution dispatch on a Conduit or SpellSpace."""
        self.events.append("meld")


class HookWorld:
    """Own a root and lesser with deliberately distinct callback sources.

    Contract:
        Configuration events are either defaults or restricted to the old Book
        ID. Book runtime callbacks and lesser overlays are always separate from
        configuration. All scopes use real configuration, Bind, Meld and wards.
    """

    def __init__(self, *, shared: bool, defaults: bool = False) -> None:
        """Build a dynamic frame with local/shared rich policy and observable hooks.

        Args:
            shared: Whether the frame owns the rich configuration.
            defaults: Whether callbacks apply to future Books as configuration seeds.
        """
        self.configured = HookRecorder()
        self.book_runtime = HookRecorder()
        self.lesser_runtime = HookRecorder()
        self.space_runtime = HookRecorder()
        self.configuration = SpellbookConfiguration("graduation-hooks").with_defaults()
        self.configuration.with_phase_scheduler_workers(1)
        if defaults:
            self.configuration.with_bind_hooks(
                pre=[self.configured.pre], activation=[self.configured.activation], post=[self.configured.post],
            )
        frame_configuration = configure_frame_posture_for_spellbook_configuration(
            self.configuration, dynamic=True, shared_framewide_spellbook_configuration=shared,
        )
        frame_configuration.with_system_caching_enabled(False)
        self.book = Spellbook(aetheric_frame="graduation-hooks", configuration=self.configuration)
        self.configuration.add_hooks(
            None if defaults else self.book.id,
            on_conduit_activated=self.configured.conduit,
            on_conduit_post_link=self.configured.conduit,
            on_conduit_cleanup_start=self.configured.conduit,
            on_meld_pre_resolve=self.configured.meld,
        )
        self.old_id = self.book.bind(spell=ParentService, existence=Existence.many)
        self.root: Conduit = self.book.conjure(dynamic=True, name="source")
        self.child: Conduit = self.root.create_lesser_conduit()
        self.root.add_bind_hooks(
            pre=[self.book_runtime.pre], activation=[self.book_runtime.activation], post=[self.book_runtime.post],
        )
        self.child.register_conduit_hooks({
            "on_conduit_post_link": self.lesser_runtime.conduit,
            "on_conduit_cleanup_start": self.lesser_runtime.conduit,
            "on_meld_pre_resolve": self.lesser_runtime.meld,
        })

    def clear_events(self) -> None:
        """Start a new observation window without changing any hook registry."""
        self.configured.events.clear()
        self.book_runtime.events.clear()
        self.lesser_runtime.events.clear()
        self.space_runtime.events.clear()

    def cleanup(self) -> None:
        """Retire both scopes and Books even if a failed assertion interrupts the test."""
        try:
            self.child.permanent_cleanup()
        finally:
            try:
                self.root.permanent_cleanup()
            finally:
                self.book.cleanup()


@pytest.mark.parametrize("shared", [False, True], ids=["local", "framewide"])
@pytest.mark.parametrize("space_kind", ["manual", "managed", "pooled"])
def test_upgrade_discards_old_book_hooks_and_lesser_and_space_overlays(
    shared: bool, space_kind: str,
) -> None:
    """Old Book-specific maps and local runtime changes must not reach the new root.

    Contract:
        Warm every old callback path before upgrading. Then exercise new Bind,
        Conduit/Space Meld, descendant creation, linking and cleanup without any
        old callback firing. The former root must still execute its own hooks.
    """
    world = HookWorld(shared=shared)
    space = (
        world.child.enter_spellspace() if space_kind == "managed"
        else world.child.create_spellspace()
    )
    active_managed = space_kind == "managed"
    try:
        space._meld.set_meld_hooks(
            {"on_meld_pre_resolve": [world.space_runtime.meld]},
            create_local_hooks=True,
        )
        world.child.meld(spell_id=world.old_id)
        space.meld(spell_id=world.old_id)
        assert "meld" in world.configured.events
        assert "meld" in world.lesser_runtime.events
        assert world.space_runtime.events == ["meld"]
        if space_kind == "pooled":
            space.cleanup()
        world.clear_events()

        world.child.upgrade_to_normal("independent")
        if space_kind == "pooled":
            assert world.child.create_spellspace() is space
        new_id = world.child.bind(spell=GraduatedService, existence=Existence.many)
        assert isinstance(world.child.meld(spell_id=new_id), GraduatedService)
        assert isinstance(space.meld(spell_id=new_id), GraduatedService)
        assert world.child.link(world.root)
        descendant = world.child.create_lesser_conduit()
        assert isinstance(descendant.meld(spell_id=new_id), GraduatedService)
        descendant.cleanup()
        if active_managed:
            space.__exit__(None, None, None)
            active_managed = False
        else:
            space.cleanup()
        world.child.permanent_cleanup()
        assert world.configured.events == []
        assert world.book_runtime.events == []
        assert world.lesser_runtime.events == []
        assert world.space_runtime.events == []

        world.root.bind(spell=LaterParentService, existence=Existence.many)
        world.root.meld(spell_id=world.old_id)
        another = world.root.create_lesser_conduit()
        another.cleanup()
        assert world.book_runtime.events == ["bind-pre", "bind-activation", "bind-post"]
        assert "meld" in world.configured.events
        assert "conduit" in world.configured.events
    finally:
        if active_managed:
            space.__exit__(None, None, None)
        space.permanent_cleanup()
        world.cleanup()


@pytest.mark.parametrize("explicit", [False, True], ids=["adopt-frame-policy", "supply-canonical-policy"])
def test_framewide_defaults_are_reapplied_without_copying_runtime_hook_changes(explicit: bool) -> None:
    """Shared policy deliberately seeds new hooks, while every Book remains independent.

    Contract:
        The canonical frozen config is reused, both when omitted and explicitly
        supplied. Former runtime overlays disappear. Mutating new runtime hooks
        leaves both the canonical seed and the former root's behavior unchanged.
    """
    world = HookWorld(shared=True, defaults=True)
    child_callbacks = HookRecorder()
    space = world.child.create_spellspace()
    try:
        space._meld.set_meld_hooks(
            {"on_meld_pre_resolve": [world.space_runtime.meld]}, create_local_hooks=True,
        )
        space.meld(spell_id=world.old_id)
        assert world.space_runtime.events == ["meld"]
        world.clear_events()
        world.child.upgrade_to_normal(
            "independent", configuration=world.configuration if explicit else None,
        )
        assert world.child._spellbook is not world.book
        assert world.child._spellbook.get_configuration() is world.configuration
        assert world.child._spellbook.spells == {}
        assert world.configured.events == ["conduit"]
        world.clear_events()

        new_id = world.child.bind(spell=GraduatedService, existence=Existence.many)
        world.child.meld(spell_id=new_id)
        space.meld(spell_id=new_id)
        assert world.child.link(world.root)
        assert world.configured.events == [
            "bind-pre", "bind-activation", "bind-post", "meld", "meld", "conduit",
        ]
        assert world.book_runtime.events == []
        assert world.lesser_runtime.events == []
        assert world.space_runtime.events == []

        world.child.clear_bind_hooks()
        world.child.add_bind_hooks(pre=[child_callbacks.pre])
        world.child.register_conduit_hooks({
            "on_meld_pre_resolve": child_callbacks.meld,
            "on_conduit_post_link": child_callbacks.conduit,
        })
        world.clear_events()
        world.root.bind(spell=LaterParentService, existence=Existence.many)
        world.root.meld(spell_id=world.old_id)
        assert world.configured.events == ["bind-pre", "bind-activation", "bind-post", "meld"]
        assert world.book_runtime.events == ["bind-pre", "bind-activation", "bind-post"]
        assert child_callbacks.events == []
        assert all(world.configuration.get_bind_hooks())

        world.clear_events()

        class AdditionalService:
            """A distinct post-clear binding avoids the independent duplicate-name guard."""

        world.child.bind(spell=AdditionalService, existence=Existence.many)
        assert world.configured.events == []
        assert child_callbacks.events == ["bind-pre"]
        world.child.meld(spell_id=new_id)
        assert child_callbacks.events == ["bind-pre", "meld"]
        world.root.permanent_cleanup()
        assert not world.configuration.cleaned
        assert isinstance(space.meld(spell_id=new_id), GraduatedService)
        assert not world.child._spellbook.cleaned
    finally:
        space.permanent_cleanup()
        world.cleanup()


def test_local_config_default_hooks_are_discarded_when_upgrade_uses_fresh_defaults() -> None:
    """Local omission does not copy even the former Book's configured default callbacks."""
    world = HookWorld(shared=False, defaults=True)
    try:
        world.clear_events()
        world.child.upgrade_to_normal("independent")
        new_id = world.child.bind(spell=GraduatedService, existence=Existence.many)
        world.child.meld(spell_id=new_id)
        assert world.child.link(world.root)
        world.child.permanent_cleanup()
        assert world.configured.events == []
        assert world.book_runtime.events == []
        assert world.lesser_runtime.events == []
        assert not world.configuration.cleaned
    finally:
        world.cleanup()


@pytest.mark.parametrize("shared", [False, True], ids=["local", "framewide"])
def test_failed_upgrade_preserves_old_hook_behavior_until_successful_retry(
    shared: bool, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A pre-attachment failure cannot clear callbacks on the still-borrowing lesser."""
    world = HookWorld(shared=shared)
    space = world.child.create_spellspace()
    try:
        space._meld.set_meld_hooks(
            {"on_meld_pre_resolve": [world.space_runtime.meld]}, create_local_hooks=True,
        )

        def fail_phases(*, spellbook: Spellbook, **kwargs: object) -> None:
            """Reject the receiving Book before any lookup/hook attachment occurs."""
            raise RuntimeError("hook rollback probe")

        with monkeypatch.context() as patch:
            patch.setattr(SpellbookCreationSystem, "run_resolution_phases_for_conduit", fail_phases)
            with pytest.raises(RuntimeError, match="hook rollback probe"):
                world.child.upgrade_to_normal("independent")
        world.clear_events()
        world.child.meld(spell_id=world.old_id)
        space.meld(spell_id=world.old_id)
        world.root.bind(spell=LaterParentService, existence=Existence.many)
        assert world.configured.events == ["meld", "meld"]
        assert world.lesser_runtime.events == ["meld", "meld"]
        assert world.space_runtime.events == ["meld"]
        assert world.book_runtime.events == ["bind-pre", "bind-activation", "bind-post"]
        world.clear_events()

        world.child.upgrade_to_normal("independent")
        new_id = world.child.bind(spell=GraduatedService, existence=Existence.many)
        world.child.meld(spell_id=new_id)
        space.meld(spell_id=new_id)
        assert world.configured.events == []
        assert world.book_runtime.events == []
        assert world.lesser_runtime.events == []
        assert world.space_runtime.events == []
    finally:
        space.permanent_cleanup()
        world.cleanup()


def test_framewide_policy_does_not_become_process_wide() -> None:
    """Another AethericFrame owns its own configuration and receives none of these hooks."""
    world = HookWorld(shared=True, defaults=True)
    other_config = SpellbookConfiguration("other-frame").with_defaults()
    configure_frame_posture_for_spellbook_configuration(
        other_config, dynamic=True, shared_framewide_spellbook_configuration=True,
    ).with_system_caching_enabled(False)
    other_book = Spellbook(aetheric_frame="other-frame", configuration=other_config)
    other_root = other_book.conjure(dynamic=True, name="source")
    try:
        world.clear_events()
        spell_id = other_root.bind(spell=GraduatedService, existence=Existence.many)
        assert isinstance(other_root.meld(spell_id=spell_id), GraduatedService)
        assert other_book.get_configuration() is other_config
        assert other_book.get_configuration() is not world.configuration
        assert other_book._bind.capture_hooks() == ((), (), ())
        assert world.configured.events == []
        assert world.book_runtime.events == []
    finally:
        other_root.permanent_cleanup()
        world.cleanup()
