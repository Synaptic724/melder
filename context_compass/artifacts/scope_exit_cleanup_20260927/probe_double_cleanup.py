"""Probe: does calling cleanup() twice on a pooled scope return it to its pool twice?

Run from a worktree root with the 3.14 environment: PYTHONPATH=src:. python <this file>
"""

import sys

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import set_frame_system_state_for_spellbook_configuration


def world() -> Conduit:
    """Return a fresh dynamic root conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, "dynamic")
    configuration.load_default_dictionary()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration).conjure(dynamic=True, name="root")


def main() -> int:
    """Clean a manual SpellSpace twice and a lesser twice; report the pools."""
    assert sys.version_info >= (3, 14), sys.version
    root = world()
    space = root.create_spellspace()
    space.cleanup()
    space.cleanup()
    pool = root._spellspace_pool
    print("spellspace: idle entries", len(pool._idle), "copies of the same space", list(pool._idle).count(space))
    a = root.enter_spellspace()
    b = root.enter_spellspace()
    print("spellspace: next two managed leases are the same object:", a is b)
    b.__exit__(None, None, None)
    a.__exit__(None, None, None)
    lesser = root.create_lesser_conduit()
    lesser.cleanup()
    lesser.cleanup()
    cpool = root._conduit_pool
    print("lesser: idle entries", len(cpool._idle), "copies of the same lesser", list(cpool._idle).count(lesser))
    first = root.create_lesser_conduit()
    second = root.create_lesser_conduit()
    print("lesser: next two acquisitions are the same object:", first is second)
    Aether._reset_singleton_for_tests()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
