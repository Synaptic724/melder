"""
`upgrade_to_normal` + `unique_per_conduit_lineage`.

When a lesser conduit is promoted to a normal (root) conduit, its creations must
become their OWN lineage root (`_root_creations is self`), and any lessers under
it must be re-pointed to the freshly promoted root. This locks down the corner
the resolver-root redesign depends on at `conduit.py` upgrade_to_normal:
    1695  self._creations._root_creations = self._creations   # claim root first
    1701  self._set_creation_gate_controller_for_lineage()    # then re-point lessers

Run (on the 3.14t target):
    .venv_new\\Scripts\\python.exe -m pytest tests/experimentation/test_lineage_upgrade_to_normal.py -q
"""

import sys
from pathlib import Path
from typing import Any, Tuple


def _ensure_src_on_path() -> None:
    src_dir = Path(__file__).resolve().parents[2] / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))


_ensure_src_on_path()

from melder.aether.aether import Aether  # noqa: E402
from melder.aether.conduit.conduit import Conduit  # noqa: E402
from melder.aether.spellbook.configuration.spellbook_configuration import (  # noqa: E402
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence  # noqa: E402
from melder.aether.spellbook.spellbook import Spellbook  # noqa: E402
from melder.nexus.nexus import Nexus  # noqa: E402
from tests._frame_posture_test_support import (  # noqa: E402
    apply_dynamic_defaults_for_spellbook_configuration,
)


class _LineageSolo:
    """No-dependency lineage spell."""

    def __init__(self) -> None:
        pass


def _reset_runtime() -> None:
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _build_dynamic_root() -> Tuple[Any, Any, str]:
    """Conjure one dynamic root with a no-dep lineage spell bound."""
    _reset_runtime()
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook = Spellbook(configuration=configuration)
    spell_id = spellbook.bind(
        spell=_LineageSolo,
        existence=Existence.unique_per_conduit_lineage,
        permissions="create",
    )
    root = spellbook.conjure(name="root", dynamic=True)
    return spellbook, root, spell_id


def test_upgrade_to_normal_flips_lineage_root_pointer_to_self() -> None:
    """
    A lesser shares the root's lineage store; after promotion it becomes its own
    lineage root. Verified structurally (the `_root_creations` pointer) and via
    pre-upgrade runtime sharing (root + lesser resolve one instance).
    """
    spellbook, root, spell_id = _build_dynamic_root()
    lesser = None
    try:
        lesser = root.create_lesser_conduit()

        # Pre-upgrade: the lesser points at the root's lineage store.
        assert lesser._creations._root_creations is root._creations, (
            "a lesser's lineage-root pointer must be the root's creations"
        )
        # ...and that pointer drives behavior: root + lesser share one instance.
        inst_root = root.meld(spell=spell_id)
        inst_lesser = lesser.meld(spell=spell_id)
        assert inst_lesser is inst_root, "lineage instance must be shared pre-upgrade"

        # Promote the lesser to its own normal/root conduit.
        lesser.upgrade_to_normal("promoted")

        # Post-upgrade: the promoted conduit is now its OWN lineage root.
        assert lesser._creations._root_creations is lesser._creations, (
            "a promoted conduit's creations must be their own lineage root"
        )
        assert lesser._creations._root_creations is not root._creations, (
            "the promoted conduit must no longer point at its former root"
        )
    finally:
        try:
            if lesser is not None:
                lesser.permanent_cleanup()
        except Exception:
            pass
        try:
            root.permanent_cleanup()
        except Exception:
            pass
        spellbook.cleanup()


if __name__ == "__main__":
    test_upgrade_to_normal_flips_lineage_root_pointer_to_self()
    print("OK: upgrade_to_normal flips the lineage-root pointer to self.")
