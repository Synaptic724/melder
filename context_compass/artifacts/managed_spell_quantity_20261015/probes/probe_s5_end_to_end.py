"""S5 end-to-end probe: direct meld, injection into many/unique holders, release, hooks' created flag."""
import sys

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import set_frame_system_state_for_spellbook_configuration


class Leased:
    """Managed target."""

    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class Holder:
    """Many holder of one lease."""

    def __init__(self, leased: Leased) -> None:
        self.leased = leased


class Keeper:
    """Unique holder of one lease."""

    def __init__(self, leased: Leased) -> None:
        self.leased = leased


def main() -> int:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    configuration = SpellbookConfiguration(aether_frame="default")
    configuration.load_default_dictionary()
    set_frame_system_state_for_spellbook_configuration(configuration, "automatic")
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(aetheric_frame="default", configuration=configuration)
    book.bind(spell=Leased, existence=Existence.managed_spell_quantity, permissions="create",
              disposal_method_names=["close"])
    book.bind(spell=Holder, existence=Existence.many, permissions="create")
    book.bind(spell=Keeper, existence=Existence.unique, permissions="create")
    root = book.conjure(name="probe-root")
    releaser = ReleaseManagedSpell()
    first = root.meld(spell=Leased)
    print("direct meld:", type(first).__name__)
    releaser.release(first)
    second = root.meld(spell=Leased)
    print("reuse after release:", second is first)
    holder = root.meld(spell=Holder)
    print("holder leased a fresh object (first is out):", holder.leased is not first, type(holder.leased).__name__)
    releaser.release(holder.leased)
    keeper = root.meld(spell=Keeper)
    print("keeper got the released object:", keeper.leased is holder.leased)
    print("keeper stored:", root.meld(spell=Keeper) is keeper)
    print(releaser.describe(Leased))
    root.cleanup()
    print("teardown closed the idle objects:", [obj.closed for obj in (first, holder.leased)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
