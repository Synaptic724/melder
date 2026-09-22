"""Direct contracts for the private Book-owned existing-conduit conjure route."""

from collections.abc import Iterator
from typing import Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_pool import ConduitPool
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.creations.cluster_creations import ClusterCreations
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
from melder.nexus.nexus import Nexus
from melder.utilities.synchronization.creation_gate import CreationGate
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)
from tests.component.melder.aether.conduit.test_conduit_graduation_ownership_regression import (
    GraduatedService,
    ParentService,
)
from tests.integration.melder.crystallizer.test_crystallizer_restore_integration import (
    _activate_crystallizer,
)


class ExistingConjureCase:
    """Own source and receiving Books while testing conjure independently of upgrade.

    Contract:
        The receiving Book exists before the source conjures, allowing both
        local and shared configuration hooks to be authored before freeze.
        prepare_target performs caller-owned normal status/root preparation;
        it deliberately leaves Book attachment and root registration to the
        private method under test. No production upgrade method is patched.
    """

    def __init__(self, shared: bool) -> None:
        """Create two distinct Books under one explicit dynamic frame policy."""
        config = SpellbookConfiguration(aether_frame="existing-conjure").with_defaults()
        config.with_phase_scheduler_workers(1)
        frame = configure_frame_posture_for_spellbook_configuration(
            config, dynamic=True, shared_framewide_spellbook_configuration=shared,
        )
        frame.with_system_caching_enabled(False)
        self.source = Spellbook(aetheric_frame="existing-conjure", configuration=config)
        self.old_id = self.source.bind(
            spell=ParentService,
            existence=Existence.unique_per_conduit,
            disposal_method_names=["cleanup"],
        )
        assert self.source.find_spell_by_id(self.old_id).disposal_method_names == ["cleanup"]
        self.book = Spellbook(
            aetheric_frame="existing-conjure", configuration=config if shared else None,
        )
        if not shared:
            self.book.get_configuration().with_phase_scheduler_workers(1)
        self.root: Optional[Conduit] = None
        self.target: Optional[Conduit] = None
        self.retained: Optional[ParentService] = None

    def prepare_target(self, *, prewarm: bool = False) -> Conduit:
        """Prepare the supplied runtime; do not conjure or attach the new Book.

        Contract:
            Mirrors the already-existing caller-side normal-root preparation.
            Retains one old creation and its warm lookup to expose stale-cache
            failures. The target is normal/detached but not frame-registered.
        Returns:
            Conduit: The existing target for the private Book method.
        """
        self.root = self.source.conjure(dynamic=True, name="source")
        self.target = self.root.create_lesser_conduit()
        self.retained = self.target.meld(spell_id=self.old_id)
        if prewarm:
            self.target.prewarm_spellspaces(1)
        self.target._conduit_state = ConduitState.normal
        self.target._root_conduit_id = self.target.id
        with self.root._conduit_ward._lock:
            self.target._conduit_ward._convert_to_normal_conduit()
        self.target._conduit_pool = ConduitPool(
            root_conduit=self.target, baseline_idle=20, max_idle=20,
        )
        self.target._cluster_creations = ClusterCreations()
        self.target._meld._root_creations = self.target._creations
        self.target._meld._cluster_creations = self.target._cluster_creations
        self.target._set_creation_gate_controller_for_lineage()
        return self.target

    def cleanup(self) -> None:
        """Clean both runtime owners, including a target rejected before adoption.

        Contract:
            A pre-adoption target still borrows the source Book. Restore only
            its test-prepared cleanup classification so failure teardown cannot
            destroy that Book through normal ownership rules. Assertions are
            never suppressed or repaired by this fixture.
        """
        try:
            if self.target is not None:
                if not self.target.cleaned and self.target._spellbook is self.source:
                    self.target._conduit_pool.cleanup()
                    self.target._cluster_creations.cleanup()
                    self.target._conduit_state = ConduitState.lesser
                    self.target._conduit_ward._conduit_type = ConduitState.lesser
                self.target.permanent_cleanup()
        finally:
            try:
                self.book.cleanup()
            finally:
                if self.root is not None:
                    self.root.permanent_cleanup()
                self.source.cleanup()


@pytest.fixture(autouse=True)
def isolated_existing_conjure_world() -> Iterator[None]:
    """Reset Aether/Nexus before and after each real component test."""
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


@pytest.fixture(params=[False, True], ids=["local", "framewide"])
def existing_case(request: pytest.FixtureRequest) -> Iterator[ExistingConjureCase]:
    """Supply one local/shared configuration case and retire its owned scopes."""
    case = ExistingConjureCase(request.param)
    try:
        yield case
    finally:
        case.cleanup()


def test_existing_conjure_retains_target_and_store_with_an_empty_new_book(
    existing_case: ExistingConjureCase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return the supplied identity without allocating any replacement Conduit."""
    target = existing_case.prepare_target()
    target_id = target.id
    creations = target._creations

    def reject_allocation(*args: object, **kwargs: object) -> None:
        """Fail if the private route accidentally enters Conduit construction."""
        raise AssertionError("Existing-conduit conjure must not construct another Conduit.")

    monkeypatch.setattr(Conduit, "__init__", reject_allocation)
    returned = existing_case.book._conjure_existing_conduit(target, name="adopted")

    assert returned is target
    assert target.id == target_id
    assert target._creations is creations
    assert existing_case.book.conduit is target
    assert target._spellbook is existing_case.book
    assert existing_case.book.spells == {}
    assert existing_case.source.find_spell_by_id(existing_case.old_id) is not None
    with pytest.raises(KeyError):
        target.meld(spell_id=existing_case.old_id)
    assert existing_case.root.meld(spell_id=existing_case.old_id) is not existing_case.retained


def test_existing_conjure_runs_new_definitions_under_the_supplied_id(
    existing_case: ExistingConjureCase,
) -> None:
    """Compile the receiving Book, stamp its actual owner and preserve old isolation."""
    new_id = existing_case.book.bind(spell=GraduatedService, existence=Existence.unique)
    target = existing_case.prepare_target()
    existing_case.book._conjure_existing_conduit(target, name="adopted")

    value = target.meld(spell_id=new_id)
    assert isinstance(value, GraduatedService)
    assert target.meld(spell_id=new_id) is value
    assert existing_case.book.find_spell_by_id(new_id)._owner_conduit_id == target.id
    assert existing_case.source.find_spell_by_id(new_id) is None
    assert target.purge(spell_id=new_id) == 1


def test_existing_conjure_supports_later_binding_through_the_same_conduit(
    existing_case: ExistingConjureCase,
) -> None:
    """An initially empty receiving Book supports later public bind and hook updates."""
    target = existing_case.prepare_target()
    source_calls: list[object] = []
    receiving_calls: list[object] = []
    existing_case.source.add_bind_hooks(pre=[source_calls.append])
    existing_case.book._conjure_existing_conduit(target, name="adopted")
    target.add_bind_hooks(pre=[receiving_calls.append])

    new_id = target.bind(spell=GraduatedService, existence=Existence.unique)

    assert receiving_calls == [GraduatedService]
    assert source_calls == []
    assert existing_case.source.find_spell_by_id(new_id) is None
    assert isinstance(target.meld(spell_id=new_id), GraduatedService)
    assert target.purge(spell_id=new_id) == 1


def test_existing_conjure_uses_receiving_configuration_hooks_in_normal_order(
    existing_case: ExistingConjureCase,
) -> None:
    """Keep pre/activation/post ordering and replace former local runtime hooks."""
    events: list[tuple[str, object]] = []
    stale_calls: list[object] = []
    config = existing_case.book.get_configuration()
    config.add_hooks(
        existing_case.book._id,
        on_conduit_pre_created=lambda: events.append(("pre", None)),
        on_conduit_activated=lambda conduit: events.append(("activation", conduit)),
        on_conduit_post_created=lambda conduit: events.append(("post", conduit)),
        on_meld_pre_resolve=lambda spell: events.append(("meld", spell)),
    )
    new_id = existing_case.book.bind(spell=GraduatedService, existence=Existence.unique)
    target = existing_case.prepare_target()
    target.register_conduit_hooks({"on_meld_pre_resolve": stale_calls.append})
    existing_case.book._conjure_existing_conduit(target, name="adopted")

    assert events == [("pre", None), ("activation", target), ("post", target)]
    assert target._creation_gate.enabled
    target.meld(spell_id=new_id)
    assert [stage for stage, _subject in events] == ["pre", "activation", "post", "meld"]
    assert stale_calls == []


@pytest.mark.parametrize("space_kind", ["pooled", "manual", "managed"])
def test_existing_conjure_rebinds_retained_spellspace_lookup(
    existing_case: ExistingConjureCase,
    space_kind: str,
) -> None:
    """Retained Space doors use the receiving Book without retaining old lookup access."""
    new_id = existing_case.book.bind(
        spell=GraduatedService, existence=Existence.unique_per_spell_space,
    )
    target = existing_case.prepare_target(prewarm=space_kind == "pooled")
    if space_kind == "pooled":
        space = target._spellspace_pool._idle[-1]
    elif space_kind == "manual":
        space = target.create_spellspace()
    else:
        space = target.enter_spellspace()
    try:
        existing_case.book._conjure_existing_conduit(target, name="adopted")
        if space_kind == "pooled":
            assert target.create_spellspace() is space
        assert isinstance(space.meld(spell_id=new_id), GraduatedService)
        with pytest.raises(KeyError):
            space.meld(spell_id=existing_case.old_id)
    finally:
        if space_kind == "managed":
            space.__exit__(None, None, None)
        else:
            space.cleanup()


def test_existing_conjure_cleans_its_book_and_preserves_retained_disposal(
    existing_case: ExistingConjureCase,
) -> None:
    """The new Book owns teardown while retained old creations still dispose locally."""
    target = existing_case.prepare_target()
    existing_case.book._conjure_existing_conduit(target, name="adopted")
    target.permanent_cleanup()

    assert existing_case.book.cleaned
    assert existing_case.retained.cleanup_calls == 1
    assert not existing_case.source.cleaned
    assert isinstance(existing_case.root.meld(spell_id=existing_case.old_id), ParentService)


def test_existing_conjure_refuses_a_second_conjure_on_the_same_book(
    existing_case: ExistingConjureCase,
) -> None:
    """Both private and public conjure retain the one-Book/one-root contract."""
    target = existing_case.prepare_target()
    existing_case.book._conjure_existing_conduit(target, name="adopted")
    with pytest.raises(RuntimeError, match="already conjured"):
        existing_case.book._conjure_existing_conduit(target, name="again")
    with pytest.raises(RuntimeError, match="already conjured"):
        existing_case.book.conjure(name="another")


def test_existing_conjure_rejects_lesser_status_without_promoting_it(
    existing_case: ExistingConjureCase,
) -> None:
    """Normal status is a caller precondition, not a side effect of this method."""
    target = existing_case.prepare_target()
    target._conduit_state = ConduitState.lesser
    with pytest.raises(RuntimeError, match="normal status"):
        existing_case.book._conjure_existing_conduit(target)
    assert target._conduit_state is ConduitState.lesser
    assert target._spellbook is existing_case.source
    assert existing_case.book.conduit is None


def test_existing_conjure_rejects_cross_frame_target(
    existing_case: ExistingConjureCase,
) -> None:
    """Frame rejection occurs before any target association changes."""
    target = existing_case.prepare_target()
    other = Spellbook(aetheric_frame="different-frame")
    try:
        with pytest.raises(ValueError, match="same frame"):
            other._conjure_existing_conduit(target)
        assert target._spellbook is existing_case.source
        assert other.conduit is None
    finally:
        other.cleanup()


def test_existing_conjure_duplicate_name_does_not_replace_target_book(
    existing_case: ExistingConjureCase,
) -> None:
    """Failed root naming restores admission and leaves the supplied runtime unadopted."""
    target = existing_case.prepare_target()
    with pytest.raises(ValueError, match="already exists"):
        existing_case.book._conjure_existing_conduit(target, name="source")
    assert target._spellbook is existing_case.source
    assert existing_case.book.conduit is None
    assert target._creation_gate.enabled
    assert target.id not in target._aetheric_frame._conduits


def test_existing_conjure_preserves_a_previously_parked_gate(
    existing_case: ExistingConjureCase,
) -> None:
    """The private route must not open admission that its caller deliberately parked."""
    target = existing_case.prepare_target()
    target._creation_gate.close()
    existing_case.book._conjure_existing_conduit(target, name="adopted")
    assert not target._creation_gate.enabled
    target._creation_gate.open()


def test_existing_conjure_rejects_an_existing_root_before_compiling(
    existing_case: ExistingConjureCase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Do not run phases under an unrelated already-registered root's ID."""
    existing_case.prepare_target()

    def reject_compilation(**kwargs: object) -> None:
        """Catch any attempt to compile before the existing-root refusal."""
        raise AssertionError("Root admission must precede phase execution.")

    monkeypatch.setattr(SpellbookCreationSystem, "run_resolution_phases_for_conduit", reject_compilation)
    with pytest.raises(ValueError, match="already registered"):
        existing_case.book._conjure_existing_conduit(existing_case.root, name="wrong")
    assert existing_case.root._spellbook is existing_case.source
    assert existing_case.book.conduit is None


def test_existing_conjure_phase_failure_releases_admission_and_allows_retry(
    existing_case: ExistingConjureCase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A pre-attachment compiler failure must leave the target and Book reusable."""
    target = existing_case.prepare_target()

    def fail_resolution(**kwargs: object) -> None:
        """Inject failure at the normal resolution boundary before attachment."""
        raise RuntimeError("resolution probe failed")

    with monkeypatch.context() as patch:
        patch.setattr(SpellbookCreationSystem, "run_resolution_phases_for_conduit", fail_resolution)
        with pytest.raises(RuntimeError, match="resolution probe failed"):
            existing_case.book._conjure_existing_conduit(target, name="adopted")
    assert target._spellbook is existing_case.source
    assert existing_case.book.conduit is None
    assert target._creation_gate.enabled
    assert existing_case.book._conjure_existing_conduit(target, name="adopted") is target


def test_existing_conjure_drain_failure_restores_gate_without_attaching(
    existing_case: ExistingConjureCase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed temporary drain cannot leave the original runtime parked by this call."""
    target = existing_case.prepare_target()

    def fail_drain(gate: CreationGate, **kwargs: object) -> None:
        """Model the real timeout contract: park first, then raise."""
        gate.close()
        raise RuntimeError("drain probe failed")

    monkeypatch.setattr(CreationGate, "close_and_drain", fail_drain)
    with pytest.raises(RuntimeError, match="drain probe failed"):
        existing_case.book._conjure_existing_conduit(target, name="adopted")
    assert target._creation_gate.enabled
    assert target._spellbook is existing_case.source
    assert existing_case.book.conduit is None


def test_existing_conjure_refuses_terminal_gate(
    existing_case: ExistingConjureCase,
) -> None:
    """Terminal teardown cannot be converted back into live Book ownership."""
    target = existing_case.prepare_target()
    target._creation_gate.close_and_wait_until_free()
    with pytest.raises(RuntimeError, match="terminally closed"):
        existing_case.book._conjure_existing_conduit(target, name="adopted")
    assert target._spellbook is existing_case.source
    assert existing_case.book.conduit is None


def test_existing_conjure_rejects_invalid_policy_before_attachment(
    existing_case: ExistingConjureCase,
) -> None:
    """Normal policy validation must run even though no Conduit is constructed."""
    target = existing_case.prepare_target()
    with pytest.raises(ValueError):
        existing_case.book._conjure_existing_conduit(target, policy="unknown_policy")
    assert target._spellbook is existing_case.source
    assert existing_case.book.conduit is None


def test_existing_conjure_rejects_invalid_local_configuration() -> None:
    """Config validation fails before replacing the supplied runtime's Book."""
    case = ExistingConjureCase(shared=False)
    try:
        target = case.prepare_target()
        case.book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 0)
        with pytest.raises(ValueError, match="positive integer"):
            case.book._conjure_existing_conduit(target)
        assert target._spellbook is case.source
        assert case.book.conduit is None
    finally:
        case.cleanup()


def test_existing_conjure_records_new_book_and_preserved_conduit(
    existing_case: ExistingConjureCase,
) -> None:
    """Record receiving Book identity even when it adopted already-locked frame config."""
    target = existing_case.prepare_target()
    existing_case.book.cleanup()
    existing_case.book = Spellbook(aetheric_frame="existing-conjure")
    calls: list[object] = []
    existing_case.book.add_bind_hooks(pre=[calls.append])
    recorder = _activate_crystallizer()
    existing_case.book._conjure_existing_conduit(target, name="adopted")

    checkpoint = recorder.checkpoint_replay_data(recorder.create_checkpoint())
    book_payload = checkpoint["payloads"]["spellbook"][existing_case.book.id]
    conduit_payload = checkpoint["payloads"]["conduit"][target.id]
    assert book_payload["hook_names"] == ["bind:pre"]
    assert conduit_payload["spellbook_id"] == existing_case.book.id
    assert conduit_payload["conduit_id"] == target.id
