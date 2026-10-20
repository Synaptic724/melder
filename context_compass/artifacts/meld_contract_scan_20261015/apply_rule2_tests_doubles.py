"""Rule 2 / D2: registry doubles that receive bind's registration accept `binding_key` (melder_1).

`Spellbook.bind` now passes `register_index(..., binding_key=new_spell._key)`; the doubles mirror the registry's
signature. usage: python <this script> <tree root> [--check]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_lib import apply

ROOT = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]

UNIT = "tests/unit/melder/spellbook/test_spellbook.py"
UNIT_STEPS = [
    ("one",
     """        register_index=lambda spell_index, owner_spellbook_id=None, resolvable=None: lineage_calls.append(
            (spell_index, new_spell, resolvable)
        )
""",
     """        register_index=lambda spell_index, owner_spellbook_id=None, resolvable=None, binding_key=None: (
            lineage_calls.append((spell_index, new_spell, resolvable))
        )
""", ""),
    ("one",
     """        register_index=lambda spell_index, owner_spellbook_id=None, resolvable=None: None
""",
     """        register_index=lambda spell_index, owner_spellbook_id=None, resolvable=None, binding_key=None: None
""", ""),
]

CRAFTER = "tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py"
COMPONENT = "tests/component/melder/spellbook/test_spellbook_component_spellbook.py"
DOUBLE_STEPS = [
    ("one",
     """            owner_spellbook_id: object = None,
            *,
            resolvable: object = None,
    ) -> None:
""",
     """            owner_spellbook_id: object = None,
            *,
            resolvable: object = None,
            binding_key: object = None,
    ) -> None:
""", ""),
    ("one",
     """            resolvable: The registered version's capability, as bind passes it (ignored here).
""",
     """            resolvable: The registered version's capability, as bind passes it (ignored here).
            binding_key: The registered version's binding key, as bind passes it (ignored here).
""", ""),
]

apply(ROOT, UNIT, UNIT_STEPS, CHECK)
apply(ROOT, CRAFTER, DOUBLE_STEPS, CHECK)
apply(ROOT, COMPONENT, DOUBLE_STEPS, CHECK)
