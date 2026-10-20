"""Rule 2 red tests: the borrower Book's contracted-map mutators mark the copy key's consumers (melder_1).

usage: python <this script> <tree root> [--check]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_lib import apply  # noqa: E402  (script-local helper import)

ROOT = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]

IMPORTS_OLD = """import contextlib
import types
import threading
"""
IMPORTS_NEW = """import contextlib
import time
import types
import threading
"""

IMPORTS2_OLD = """from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
"""
IMPORTS2_NEW = """from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_state import SpellSystemState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
"""

IMPORTS3_OLD = """from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
"""
IMPORTS3_NEW = """from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
"""

ANCHOR = "def test_cleanup_components_swallows_clear_and_cleanup_failures() -> None:\n"
TESTS = '''_COPY_KEY = ("frame", "binding")


def _contracted_book(*, conjured: bool = True) -> Spellbook:
    """
    Purpose:
        Build a Spellbook whose contracted maps start empty, with its collaborators beside the maps stubbed.
    Contract:
        - The Book keeps its real SpellSystemStates (the frame's registry), so a contract mark is observable on a
          consumer lineage registered there.
        - Collection marks, staged-key refreshes and RiskManager calls are recorded no-ops.
    Args:
        conjured: The Book's `_conjured` flag.
    Returns:
        Spellbook: The Book under test.
    """
    sb = Spellbook()
    sb._logger = DummySafeLogger()
    sb._contracted_spells = {}
    sb._lookup_contracted_spells = {}
    sb._contracted_spell_ids = {}
    sb._contracted_spells_by_id = {}
    sb._inactive_contracted_spells = {}
    sb._conjured = conjured
    sb._conduit = DummyConduit("borrower", "borrower")
    sb._mark_collection_dependents_dirty = lambda frame_keys: None
    sb._try_update_staged_contract_keys = lambda conduit_id: None
    sb._register_spell_with_risk_manager = lambda conduit_id, spell: None
    sb._unregister_spell_with_risk_manager = lambda conduit_id, spell: None
    return sb


def _contracted_copy(spell_id: str = "sid-1") -> DummySpell:
    """
    Purpose:
        Build a borrowed copy under the frame "Frame" and the binding "binding" (key ("frame", "binding")).
    Returns:
        DummySpell: The copy, with its index, its `key` and its `_key` set as a live Spell carries them.
    """
    index = DummySpellIndex(versions={spell_id}, sid=f"lineage-{spell_id}", current=spell_id)
    spell = DummySpell(
        spell_id=spell_id,
        versions={spell_id},
        spell_name="SpellName",
        binding_name="binding",
        spellframe="Frame",
    )
    spell.spell_index = index
    spell.key = _COPY_KEY
    spell._key = _COPY_KEY
    return spell


def _consumer_of_copy_key(sb: Spellbook) -> SpellSystemState:
    """
    Purpose:
        Register, in the Book's registry, a lineage the Book owns whose topology consumes the copy's key, and leave
        it `valid`.
    Returns:
        SpellSystemState: The consumer lineage's state.
    """
    states = sb._spell_system_states
    index = SpellIndex("consumer-v1")
    states.register_index(index, owner_spellbook_id=sb._id)
    states.register_local_topology(
        index,
        SpellLocalTopology(
            spell_id="consumer-v1",
            sockets=(
                SpellSocketDescriptor(
                    spell_id="consumer-v1",
                    param_name="service",
                    position=0,
                    socket_kind=SocketKind.SPELL_CONTRACT,
                    is_collection=False,
                    is_optional=False,
                    target_spell_ids=(),
                    contract_key=_COPY_KEY,
                ),
            ),
        ),
    )
    state = states.get_by_index_id(index.id)
    assert state is not None
    state.clear_dirty(time.time())
    return state


def _assert_marked_then_reset(state: SpellSystemState) -> None:
    """Assert rule 2's contract mark on the consumer, then make it `valid` again for the next step."""
    assert state.validity is SpellValidity.gated
    assert state.has_flag(SpellState.contract_unvalidated)
    state.set_validity(SpellValidity.valid, flags_to_remove=[SpellState.contract_unvalidated])


def test_every_change_of_an_active_contracted_copy_marks_the_consumers_of_its_key() -> None:
    """
    Purpose:
        Prove rule 2's marking: an add, a park, a reactivation and a removal of an active contracted copy each gate
        the Book's consumers of the copy's key with `contract_unvalidated` (mark only).
    """
    sb = _contracted_book()
    state = _consumer_of_copy_key(sb)
    spell = _contracted_copy()

    sb._add_contracted_spell(spell, "peer")
    _assert_marked_then_reset(state)

    sb._deactivate_contracted_spell("peer", spell)
    _assert_marked_then_reset(state)

    sb._reactivate_contracted_spell("peer", spell)
    _assert_marked_then_reset(state)

    sb._remove_contracted_spell("sid-1", "peer")
    _assert_marked_then_reset(state)
    assert sb._contracted_spells["peer"] == {}


def test_clearing_a_peers_copies_marks_the_keys_of_the_active_copies() -> None:
    """A clear of one peer's copies gates the consumers of every active copy's key it removed."""
    sb = _contracted_book()
    state = _consumer_of_copy_key(sb)
    sb._add_contracted_spell(_contracted_copy(), "peer")
    state.set_validity(SpellValidity.valid, flags_to_remove=[SpellState.contract_unvalidated])

    sb._clear_contracted_spells_for_conduit("peer")

    _assert_marked_then_reset(state)


def test_contracted_copy_changes_mark_nothing_before_conjure() -> None:
    """Before conjure nothing is marked: conjure runs phases 1-4 for every spell."""
    sb = _contracted_book(conjured=False)
    state = _consumer_of_copy_key(sb)
    spell = _contracted_copy()

    sb._add_contracted_spell(spell, "peer")
    sb._deactivate_contracted_spell("peer", spell)
    sb._reactivate_contracted_spell("peer", spell)
    sb._remove_contracted_spell("sid-1", "peer")

    assert state.validity is SpellValidity.valid
    assert not state.has_flag(SpellState.contract_unvalidated)


def test_parked_contracted_copy_changes_mark_nothing() -> None:
    """Adding or removing a parked copy marks nothing: no consumer resolves a parked copy."""
    sb = _contracted_book()
    state = _consumer_of_copy_key(sb)

    sb._add_inactive_contracted_spell(_contracted_copy("sid-parked"), "peer")
    sb._remove_contracted_spell("sid-parked", "peer")

    assert state.validity is SpellValidity.valid
    assert not state.has_flag(SpellState.contract_unvalidated)


class _RecordingContractRegistry:
    """
    Purpose:
        Registry double for the Book's contract mark: records each call's Book id, keys and whether the Book lock
        is held at the call, and optionally raises.
    """

    def __init__(self, book: Spellbook, *, error: Optional[Exception] = None) -> None:
        """Bind the Book whose lock is checked; `error` is raised from every mark when given."""
        self.book = book
        self.error = error
        self.calls: list[tuple[str, frozenset[tuple[str, str]], bool]] = []

    def mark_contract_dependents_dirty(
            self,
            *,
            spellbook_id: str,
            contract_keys: Any = None,
    ) -> set[str]:
        """Record the call; raise the configured error when there is one."""
        self.calls.append((spellbook_id, frozenset(contract_keys), self.book._lock._is_owned()))
        if self.error is not None:
            raise self.error
        return set()


def test_contract_marks_run_with_the_book_lock_free() -> None:
    """Each mutator marks once, with the copy's key, after it releases the Book lock."""
    sb = _contracted_book()
    registry = _RecordingContractRegistry(sb)
    sb._spell_system_states = cast(Any, registry)
    spell = _contracted_copy()

    sb._add_contracted_spell(spell, "peer")
    sb._deactivate_contracted_spell("peer", spell)
    sb._reactivate_contracted_spell("peer", spell)
    sb._remove_contracted_spell("sid-1", "peer")
    sb._add_contracted_spell(_contracted_copy("sid-2"), "peer")
    sb._clear_contracted_spells_for_conduit("peer")

    assert registry.calls == [(sb._id, frozenset({_COPY_KEY}), False)] * 6


def test_contract_mark_failure_is_logged_and_propagates_after_the_map_change() -> None:
    """A registry failure is logged and raised; the map change it followed stays published."""
    sb = _contracted_book()
    sb._spell_system_states = cast(Any, _RecordingContractRegistry(sb, error=RuntimeError("registry gone")))
    spell = _contracted_copy()

    with pytest.raises(RuntimeError, match="registry gone"):
        sb._add_contracted_spell(spell, "peer")

    assert sb._contracted_spells["peer"][spell.spell_index] is spell
    assert any("Failed to mark contract dependents dirty" in str(message) for message, _ in sb._logger.error_calls)


'''

STEPS = [
    ("one", IMPORTS_OLD, IMPORTS_NEW, ""),
    ("one", IMPORTS2_OLD, IMPORTS2_NEW, ""),
    ("one", IMPORTS3_OLD, IMPORTS3_NEW, ""),
    ("one", ANCHOR, TESTS + ANCHOR, ""),
]

apply(ROOT, "tests/unit/melder/spellbook/test_spellbook.py", STEPS, CHECK)
