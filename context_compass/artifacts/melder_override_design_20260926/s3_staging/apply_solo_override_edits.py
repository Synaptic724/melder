"""Solo graph uses a real override: `SoloRootA(leaf: SoloLeafA)` with the leaf overridden - anchored edits.

Usage: python apply_solo_override_edits.py <tree_root> [--check]

Owner (2026-09-26): the solo case of benchmarks/testing_other_di/test_overrides_all.py must meld with an override,
not a bound existing object. A melder override targets constructor parameters, so the solo root gains one input and
every library overrides that input (the builders are generic over the spec). The melder builder's existing-object
mode and the spec field that selected it are removed; every graph now melds `override={key: instance}`.
Each anchor must match exactly once (either line ending) or nothing is written. Engine: apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one

BENCH = "benchmarks/testing_other_di/test_overrides_all.py"

EDITS = [
    ("replace",
     '''# ---- SOLO ---------------------------------------------------------------------------


class SoloRootA(_NoDeps):
    __slots__ = ()
''',
     '''# ---- SOLO ---------------------------------------------------------------------------
# One object per step: the root's only input is the override, so every library builds the root alone with
# the supplied leaf (a melder override targets constructor parameters; a root with none has nothing to override).


class SoloLeafA(_NoDeps):
    __slots__ = ()


class SoloRootA:
    __slots__ = ("leaf",)

    def __init__(self, leaf: SoloLeafA) -> None:
        self.leaf = leaf
'''),
    ("replace",
     '''    melder_override_key: str | None
    melder_override_mode: str
''',
     '''    melder_override_key: str
'''),
    ("replace",
     '''            classes=(SoloRootA,),
            override_target=SoloRootA,
            override_accessor=lambda root: (root,),
            melder_override_key=None,
            melder_override_mode="existing",
''',
     '''            classes=(SoloLeafA, SoloRootA),
            override_target=SoloLeafA,
            override_accessor=lambda root: (root.leaf,),
            melder_override_key="leaf",
'''),
    ("replace", '            melder_override_key="a",\n            melder_override_mode="payload",\n',
     '            melder_override_key="a",\n'),
    ("replace", '            melder_override_key="l0",\n            melder_override_mode="payload",\n',
     '            melder_override_key="l0",\n'),
    ("replace", '            melder_override_key="**leaf",\n            melder_override_mode="payload",\n',
     '            melder_override_key="**leaf",\n'),
    ("replace", '            melder_override_key="left>left>left>left>left>left>left>left",\n'
                '            melder_override_mode="payload",\n',
     '            melder_override_key="left>left>left>left>left>left>left>left",\n'),
    ("replace",
     '''    if g.melder_override_mode == "existing":
        root_id = spellbook.bind(spell=override_instance, existence=Existence.unique, permissions="create")
    else:
        ids: dict[type, str] = {}
        for cls in g.classes:
            ids[cls] = spellbook.bind(spell=cls, existence=Existence.many, permissions="create")
        root_id = ids[g.root_type]
''',
     '''    ids: dict[type, str] = {}
    for cls in g.classes:
        ids[cls] = spellbook.bind(spell=cls, existence=Existence.many, permissions="create")
    root_id = ids[g.root_type]
'''),
    ("replace",
     '''        if g.melder_override_mode == "existing":
            root = conduit.meld(spell_id=root_id)
        else:
            root = conduit.meld(spell_id=root_id, override={g.melder_override_key: override_instance})
''',
     '''        root = conduit.meld(spell_id=root_id, override={g.melder_override_key: override_instance})
'''),
]


def main() -> None:
    """Check every edit, then write (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    path = root / BENCH
    data = path.read_bytes().decode("utf-8")
    for edit in EDITS:
        data = _apply_one(data, edit, BENCH)
    compile(data, BENCH, "exec")
    if "melder_override_mode" in data:
        raise SystemExit("melder_override_mode still referenced")
    if not check:
        path.write_bytes(data.encode("utf-8"))
    print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
