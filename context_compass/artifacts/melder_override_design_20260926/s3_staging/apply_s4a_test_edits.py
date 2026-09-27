"""S4a tests: plans decide unresolved inputs before construction (B6) - anchored edits.

Usage: python apply_s4a_test_edits.py <tree_root> [--check]

test_site_plan_lowering.py: a plan raises before building anything when an unresolved input has no key, builds with
the key, and checks a shared site's input inside its miss before its children (a stored site never demands).
test_conduit_component_unresolved_inputs.py: plan families raise with no TypeError cause (solo keeps it), and nothing
under the consumer is constructed, for many_only and generalized. Each anchor must match exactly once or nothing is
written. Engine: apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one

UNIT = "tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py"
COMPONENT = "tests/component/melder/aether/conduit/test_conduit_component_unresolved_inputs.py"

UNIT_IMPORT_OLD = '''from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
'''
UNIT_IMPORT_NEW = '''from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError
'''

UNIT_TAIL_OLD = '''    with pytest.raises(RuntimeError) as caught:
        SitePlanOverrideRuntime(steps=steps, root_spell=root, root_instance_key=("root", None))
    assert not isinstance(caught.value, MeldExecutionError)
'''
UNIT_TAIL_NEW = UNIT_TAIL_OLD + '''

def _unresolved(spell_id: str, name: str, position: int) -> SpellSocketDescriptor:
    """Build one UNRESOLVED_INPUT socket descriptor."""
    return SpellSocketDescriptor(
        spell_id=spell_id, param_name=name, position=position, socket_kind=SocketKind.UNRESOLVED_INPUT,
        is_collection=False, is_optional=False, target_spell_ids=(), parameter_kind="POSITIONAL_OR_KEYWORD",
    )


def _needs_input(spell: SimpleNamespace, topology: SpellLocalTopology) -> None:
    """Let a fake spell answer the live-topology read the unresolved-input error makes."""
    spell._spell_system_states = SimpleNamespace(get_local_topology=lambda index: topology)


def test_plan_raises_an_unsupplied_unresolved_input_before_building_anything() -> None:
    """Root(a: A(x: X), t: T(work)): without a key nothing is built (B6); with `t>work` T gets the value."""
    built: Counter = Counter()
    spells = {name: _spell(name, built) for name in ("x", "a", "t", "root")}
    task_topology = SpellLocalTopology("t", (_unresolved("t", "work", 0),))
    _needs_input(spells["t"], task_topology)
    steps = (
        _step(("x", 3), spells["x"]),
        _step(("a", 1), spells["a"], ("x", (("x", 3),))),
        _step(("t", 2), spells["t"]),
        _step(("root", 0), spells["root"], ("a", (("a", 1),)), ("t", (("t", 2),))),
    )
    topologies = {
        "root": SpellLocalTopology("root", (_socket("root", "a", 0), _socket("root", "t", 1))),
        "a": SpellLocalTopology("a", (_socket("a", "x", 0),)),
        "t": task_topology,
    }
    with pytest.raises(UnresolvedInputError) as caught:
        _compile_plan(steps, topologies, ("root", 0))(None, {})
    assert (caught.value.param_name, caught.value.unresolved_params) == ("work", ("work",))
    assert caught.value.__cause__ is None
    assert built == Counter()
    value = object()
    result = _compile_plan(steps, topologies, ("root", 0), ("t>work",))(None, {"t>work": value})
    assert result.args[1].args == (value,)
    assert built == Counter({"x": 1, "a": 1, "t": 1, "root": 1})


def test_shared_site_unresolved_input_is_checked_in_its_miss_before_its_children() -> None:
    """S(x: X, work) shared: a miss without a key raises before X is built; a stored S never demands."""
    built: Counter = Counter()
    spells = {"x": _spell("x", built), "s": _spell("s", built, Existence.unique_per_conduit),
              "root": _spell("root", built)}
    shared_topology = SpellLocalTopology("s", (_socket("s", "x", 0), _unresolved("s", "work", 1)))
    _needs_input(spells["s"], shared_topology)
    steps = (
        _step(("x", 2), spells["x"]),
        _step(("s", None), spells["s"], ("x", (("x", 2),))),
        _step(("root", 0), spells["root"], ("s", (("s", None),))),
    )
    topologies = {"root": SpellLocalTopology("root", (_socket("root", "s", 0),)), "s": shared_topology}
    meld = SimpleNamespace(_conduit_creations=FakeStore())
    with pytest.raises(UnresolvedInputError):
        _compile_plan(steps, topologies, ("root", 0))(meld, {})
    assert built == Counter()
    value = object()
    first = _compile_plan(steps, topologies, ("root", 0), ("s>work",))(meld, {"s>work": value})
    assert first.args[0].args[1] is value
    second = _compile_plan(steps, topologies, ("root", 0))(meld, {})
    assert second.args[0] is first.args[0]
    assert built == Counter({"x": 1, "s": 1, "root": 2})
'''

CAUSE_OLD = '''    assert error.unresolved_params == ("work",)
    assert isinstance(error.__cause__, TypeError)
'''
CAUSE_NEW = '''    assert error.unresolved_params == ("work",)
    # Plans decide it before calling (B6, 2026-09-26); the solo lane still converts the TypeError.
    if family == "solo":
        assert isinstance(error.__cause__, TypeError)
    else:
        assert error.__cause__ is None
'''

CLASSES_OLD = '''

@pytest.fixture
def runtime_book() -> Iterator[Spellbook]:
'''
CLASSES_NEW = '''

class Counted:
    """A transient dependency that counts its constructions."""

    count = 0

    def __init__(self) -> None:
        """Count one construction."""
        Counted.count += 1


class Needy:
    """A counted dependency plus an unresolved input."""

    def __init__(self, counted: Counted, work: Package) -> None:
        """Keep both."""
        self.counted = counted
        self.work = work


class Outer:
    """Build Needy as a dependency."""

    def __init__(self, needy: Needy) -> None:
        """Keep it."""
        self.needy = needy
''' + CLASSES_OLD

TEST_TAIL_OLD = '''    with pytest.raises(UnresolvedInputError) as caught:
        conduit.meld(spell_id=root_id, override={"first": Package()})
    assert caught.value.unresolved_params == ("second",)
    assert caught.value.expected_type == "FalseyPackage"
'''
TEST_TAIL_NEW = TEST_TAIL_OLD + '''

@pytest.mark.parametrize("outer_existence", ["many", "unique_per_conduit"])
def test_nothing_under_the_consumer_is_built_before_the_error(
    runtime_book: Spellbook, outer_existence: str,
) -> None:
    """B6: a missing unresolved input fails before its consumer's dependencies are constructed (both plan families)."""
    runtime_book.bind(spell=Counted, existence="many")
    runtime_book.bind(spell=Needy, existence="many")
    root_id = runtime_book.bind(spell=Outer, existence=outer_existence)
    conduit = runtime_book.conjure()
    Counted.count = 0
    with pytest.raises(UnresolvedInputError) as caught:
        conduit.meld(spell_id=root_id)
    assert caught.value.spell_name == "Needy" and caught.value.__cause__ is None
    assert Counted.count == 0
    value = Package()
    assert conduit.meld(spell_id=root_id, override={"needy>work": value}).needy.work is value
    assert Counted.count == 1
'''

EDITS = {
    UNIT: [("replace", UNIT_IMPORT_OLD, UNIT_IMPORT_NEW), ("replace", UNIT_TAIL_OLD, UNIT_TAIL_NEW)],
    COMPONENT: [
        ("replace", CAUSE_OLD, CAUSE_NEW),
        ("replace", CLASSES_OLD, CLASSES_NEW),
        ("replace", TEST_TAIL_OLD, TEST_TAIL_NEW),
    ],
}


def main() -> None:
    """Check every anchor, then write every file (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    pending = {}
    for rel, edits in EDITS.items():
        path = root / rel
        data = path.read_bytes().decode("utf-8")
        for edit in edits:
            data = _apply_one(data, edit, rel)
        compile(data, rel, "exec")
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
