"""Rule 2 source change: ConduitWard's contract-key reader names the signature read it now mirrors (melder_1).

Meld's `_iter_spell_contract_defaults` is retired with the per-meld scan; the Phase 8 analyzer keeps its copy.
contract_recheck_on_notch_2026_10_16, component_patch_meld_gate. usage: python <this script> <tree root> [--check]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_lib import apply

ROOT = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]
REL = "src/melder/aether/conduit/conduit_ward/conduit_ward.py"

STEPS = [
    ("one",
     '''            # (Python 3.14 lazy annotations). Mirrors Meld._iter_spell_contract_defaults.
''',
     '''            # (Python 3.14 lazy annotations). Mirrors the Phase 8 analyzer's
            # SpellOccurrenceGraphAnalyzerStrategy._iter_spell_contract_defaults.
''', ""),
]

apply(ROOT, REL, STEPS, CHECK)
