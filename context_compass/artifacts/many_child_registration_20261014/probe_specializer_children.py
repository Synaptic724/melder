"""
Probe: does the opt-in singleton specializer (generalized_singleton_specialization_enabled) build or register the
`many` children of holders it does not rebuild? (TASK-2026-10-14 many-child lane)

Shape: Root (many, no disposal) -> Holder (unique) -> Child (many, disposal `close`). The specializer captures the
warm `unique` Holder; its straight-line body emits every non-captured step, Child included.
Reported per run of N warm melds of Root at the root conduit, then one spellspace cycle:
    built         - Child constructions (1 means only the first build made one)
    root_bucket   - Child entries recorded in the root conduit's store
    closed_early  - Child objects already disposed before root teardown

Run on a copy of `src`:
    PYTHONPATH=<copy>/src:<copy> PYTHONDONTWRITEBYTECODE=1 python probe_specializer_children.py
"""
import sys

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Child:
    """`many` dependency whose disposal method counts its runs."""

    built = 0
    instances: list = []

    def __init__(self) -> None:
        """Count the construction."""
        Child.built += 1
        Child.instances.append(self)
        self.closes = 0

    def close(self) -> None:
        """Disposal method declared at bind."""
        self.closes += 1


class Holder:
    """`unique` holder of one Child."""

    def __init__(self, child: Child) -> None:
        """Keep the child."""
        self.child = child


class Root:
    """`many` root over the unique Holder."""

    def __init__(self, holder: Holder) -> None:
        """Keep the holder."""
        self.holder = holder


def run(specialize: bool, melds: int) -> str:
    """Build one world, meld Root `melds` times plus one spellspace cycle, report."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    Child.built = 0
    Child.instances = []
    configuration = SpellbookConfiguration()
    configuration.with_defaults()
    if specialize:
        configuration.set_property("generalized_singleton_specialization_enabled", True)
    book = Spellbook(configuration=configuration)
    child_id = book.bind(spell=Child, existence=Existence.many, disposal_method_names=["close"])
    book.bind(spell=Holder, existence=Existence.unique)
    root_id = book.bind(spell=Root, existence=Existence.many)
    root = book.conjure(name="spec_probe_root")
    try:
        roots = [root.meld(spell_id=root_id) for _ in range(melds)]
        with root.enter_spellspace() as space:
            space.meld(spell_id=root_id)
        holder = roots[0].holder
        same = all(r.holder is holder for r in roots)
        bucket = root._creations._creations.get(child_id) or []
        closed_early = sum(1 for child in Child.instances if child.closes)
        return (
            f"specialize={specialize}: same_holder={same} built={Child.built} root_bucket={len(bucket)} "
            f"closed_early={closed_early} holder_child_closed={holder.child.closes}"
        )
    finally:
        root.cleanup()


def main() -> int:
    """Print one line per mode."""
    for specialize in (False, True):
        sys.stdout.write(run(specialize, 6) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
