"""S4 red tests: the stubs carry the managed class the registry keys on, and the existing suites gain the
registry-following and root-export tests. Every anchor must match exactly once or nothing is written."""
import pathlib


def apply(path: str, replacements: list) -> None:
    file = pathlib.Path(path)
    text = file.read_text(encoding="utf-8")
    for old, new in replacements:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"{path}: anchor matched {count} times, nothing written:\n{old[:200]}")
        text = text.replace(old, new)
    file.write_text(text, encoding="utf-8")
    print("updated", path)


POOL_TESTS = "tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity.py"
apply(POOL_TESTS, [
    (
        "        self.spell_id = spell_id\n        self.spell_name = spell_name\n        self.binding_name = \"pooled\"\n",
        "        self.spell_id = spell_id\n        self.spell_name = spell_name\n"
        "        # The managed class: the key ReleaseManagedSpell routes releases by (S4).\n"
        "        self.spell: type = _Pooled\n"
        "        self.binding_name = \"pooled\"\n",
    ),
])
with open(POOL_TESTS, "a", encoding="utf-8") as handle:
    handle.write('''

def test_managed_class_is_the_bound_class_and_survives_cleanup() -> None:
    """The pool keeps the class the registry keys on, readable after teardown."""
    pool = _pool()
    assert pool.managed_class is _Pooled
    pool.cleanup()
    assert pool.managed_class is _Pooled


def test_a_rebind_moves_the_managed_class() -> None:
    """A rebind under the same id that brings another class object re-points the key."""

    class _Redefined:
        """A redefinition of the managed class."""

    pool = _pool()
    rebound = _SpellStub()
    rebound.spell = _Redefined
    pool._rebind_spell(rebound)
    assert pool.managed_class is _Redefined
    assert pool.spell is rebound
''')
print("appended", POOL_TESTS)

apply("tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py", [
    (
        "        self.spell_id = \"stress-sid\"\n        self.spell_name = \"Stressed\"\n",
        "        self.spell_id = \"stress-sid\"\n        self.spell_name = \"Stressed\"\n"
        "        # The managed class: the key ReleaseManagedSpell routes releases by (S4).\n"
        "        self.spell: type = _Worker\n",
    ),
])

apply("tests/unit/melder/aether/conduit/meld/test_meld_doors_managed_spell_quantity.py", [
    (
        "    spell.binding_name = None\n    spell.disposal_method_names = [\"close\"]\n",
        "    spell.binding_name = None\n"
        "    # The managed class: the key ReleaseManagedSpell routes releases by (S4).\n"
        "    spell.spell = _Pooled\n"
        "    spell.disposal_method_names = [\"close\"]\n",
    ),
])

CREATIONS_TESTS = "tests/unit/melder/aether/conduit/creations/test_creations_managed_quantities.py"
apply(CREATIONS_TESTS, [
    (
        '''    reusable clears that root stores never run (pools untouched).
"""
from threading import RLock
from typing import Any, List, Optional, Tuple

import pytest

from melder.aether.conduit.creations.conduit_creations import ConduitCreations
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
''',
        '''    reusable clears that root stores never run (pools untouched). Since S4 (STORY-2026-10-15-release_managed_spell)
    the store registers every pool it takes with `ReleaseManagedSpell` and unregisters every pool it gives up.
"""
from collections.abc import Iterator
from threading import RLock
from typing import Any, List, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.conduit_creations import ConduitCreations
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spellbook import Spellbook
''',
    ),
    (
        '''            limit: Optional[int] = 256,
            disposal: Tuple[str, ...] = ("close",),
    ) -> None:
        """
        Keep the fields.

        Args:
            spell_id: The version id.
            existence: The binding's Existence.
            mode: The managed mode.
            limit: The managed limit.
            disposal: The disposal method names.
        """
        self.spell_id = spell_id
''',
        '''            limit: Optional[int] = 256,
            disposal: Tuple[str, ...] = ("close",),
            target: Optional[type] = None,
    ) -> None:
        """
        Keep the fields.

        Args:
            spell_id: The version id.
            existence: The binding's Existence.
            mode: The managed mode.
            limit: The managed limit.
            disposal: The disposal method names.
            target: The managed class; `_Probe` when omitted.
        """
        self.spell_id = spell_id
        # The managed class: the key ReleaseManagedSpell routes releases by (S4).
        self.spell: type = target if target is not None else _Probe
        self.spell_index = SpellIndex(spell_id)
''',
    ),
    (
        '''        self.managed_spell_reset_methods = ()
        self._lock = RLock()
''',
        '''        self.managed_spell_reset_methods = ()
        self._lock = RLock()

    def _spell_index_unless_cleaned(self) -> Optional[SpellIndex]:
        """Return the version's index (the registry's selected-version read)."""
        return self.spell_index
''',
    ),
    (
        '''@pytest.fixture
def store() -> ConduitCreations:
''',
        '''def _reset_world() -> None:
    """Install a fresh Aether, and with it a fresh ReleaseManagedSpell, for Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_registry() -> Iterator[None]:
    """A fresh registry per test, so the pools one test registers never meet another's releases."""
    _reset_world()
    yield
    _reset_world()


@pytest.fixture
def store() -> ConduitCreations:
''',
    ),
])
with open(CREATIONS_TESTS, "a", encoding="utf-8") as handle:
    handle.write('''

def _registered(cls: type) -> List[Tuple[str, str]]:
    """
    Return the registry's view of one class: (spell id, holding root) per pool, in registration order.

    Args:
        cls: The managed class.

    Returns:
        List[Tuple[str, str]]: One pair per registered pool.
    """
    return [(entry["spell_id"], entry["holding_conduit_id"]) for entry in ReleaseManagedSpell().describe(cls)]


def test_ensure_registers_the_pool_under_its_class_and_the_stores_root(store: ConduitCreations) -> None:
    """A store that takes a pool registers it, so a release of its class reaches it."""
    pool = store.ensure_managed_quantity(_SpellStub())
    assert _registered(_Probe) == [("managed-sid", "root-1")]
    assert pool.reserve() is None
    ReleaseManagedSpell().release(_Probe("released", []))
    assert pool.idle_count == 1


def test_a_second_stamp_registers_nothing_new(store: ConduitCreations) -> None:
    """Ensure is idempotent, and so is its registration."""
    store.ensure_managed_quantity(_SpellStub())
    store.ensure_managed_quantity(_SpellStub())
    assert _registered(_Probe) == [("managed-sid", "root-1")]


def test_a_rebind_bringing_another_class_moves_the_registration(store: ConduitCreations) -> None:
    """The kept pool is re-keyed under the new class object."""

    class _Redefined:
        """A redefinition of the managed class."""

    store.ensure_managed_quantity(_SpellStub())
    store.ensure_managed_quantity(_SpellStub(target=_Redefined))
    assert _registered(_Probe) == []
    assert _registered(_Redefined) == [("managed-sid", "root-1")]


def test_extract_unregisters_the_pool_it_gives_up(store: ConduitCreations) -> None:
    """A pool in flight between stores is not routable."""
    store.ensure_managed_quantity(_SpellStub())
    store.extract_spell_creations("managed-sid")
    assert _registered(_Probe) == []


def test_restore_registers_the_moved_pool_under_the_restoring_root(store: ConduitCreations) -> None:
    """The pool is routable again, held by the store that took it."""
    source = ConduitCreations(conduit_id="source")
    source.ensure_managed_quantity(_SpellStub())
    assert _registered(_Probe) == [("managed-sid", "source")]
    store.restore_spell_creations("managed-sid", source.extract_spell_creations("managed-sid"))
    assert _registered(_Probe) == [("managed-sid", "root-1")]


def test_restore_unregisters_the_pool_it_replaces(store: ConduitCreations) -> None:
    """The composed pool leaves the registry; releases reach the moved one."""
    composed = store.ensure_managed_quantity(_SpellStub())
    source = ConduitCreations(conduit_id="source")
    moved = source.ensure_managed_quantity(_SpellStub())
    store.restore_spell_creations("managed-sid", source.extract_spell_creations("managed-sid"))
    assert _registered(_Probe) == [("managed-sid", "root-1")]
    assert moved.reserve() is None
    ReleaseManagedSpell().release(_Probe("moved", []))
    assert (moved.idle_count, composed.cleaned) == (1, True)


def test_restore_of_a_pool_the_store_already_holds_keeps_it_registered(store: ConduitCreations) -> None:
    """A row carrying the store's own pool changes nothing in the registry."""
    pool = store.ensure_managed_quantity(_SpellStub())
    store.restore_spell_creations("managed-sid", [{"scope": "managed", "disposable": False, "stored": pool}])
    assert _registered(_Probe) == [("managed-sid", "root-1")]


def test_cleanup_unregisters_every_pool(store: ConduitCreations) -> None:
    """A torn-down root leaves no routable pool behind."""
    store.ensure_managed_quantity(_SpellStub("first"))
    store.ensure_managed_quantity(_SpellStub("second"))
    store.cleanup()
    assert _registered(_Probe) == []


def test_a_store_cleaned_after_the_registry_is_gone_still_cleans(store: ConduitCreations) -> None:
    """Teardown does not need the registry: with it gone, there is nothing to unregister from."""
    pool = store.ensure_managed_quantity(_SpellStub())
    ReleaseManagedSpell._reset_singleton_for_tests()
    store.cleanup()
    assert pool.cleaned is True
''')
print("appended", CREATIONS_TESTS)

SURFACE_TESTS = "tests/unit/melder/test_package_public_surface.py"
apply(SURFACE_TESTS, [
    (
        '''        "SpellframeKind",
    ):
        assert name not in melder.__all__
''',
        '''        "SpellframeKind",
        # STORY-2026-10-15-release_managed_spell: the pool behind a managed spell is kernel machinery owned by its
        # root's store; users give objects back through ReleaseManagedSpell or a lease, never the pool.
        "ManagedSpellQuantity",
    ):
        assert name not in melder.__all__
''',
    ),
])
with open(SURFACE_TESTS, "a", encoding="utf-8") as handle:
    handle.write('''

def test_managed_spell_quantity_surface_is_loaded():
    """
    Purpose:
        The managed lifetime's user-facing names reach the root (STORY-2026-10-15-release_managed_spell): the
        mode enum a binding names, the registry users release through, the lease they hold, and the error a lease
        raises when a pool refuses.
    Contract:
        Identity with the concrete-path objects; every name is in __all__.
    """
    from melder.aether.conduit.creations.managed_spell_lease import ManagedSpellLease
    from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
    from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
    from melder.utilities.custom_exceptions.managed_spell_exhausted_error import (
        ManagedSpellExhaustedError,
    )

    import melder

    assert melder.ManagedSpellMode is ManagedSpellMode
    assert melder.ReleaseManagedSpell is ReleaseManagedSpell
    assert melder.ManagedSpellLease is ManagedSpellLease
    assert melder.ManagedSpellExhaustedError is ManagedSpellExhaustedError
    for name in ("ManagedSpellMode", "ReleaseManagedSpell", "ManagedSpellLease", "ManagedSpellExhaustedError"):
        assert name in melder.__all__
''')
print("appended", SURFACE_TESTS)
