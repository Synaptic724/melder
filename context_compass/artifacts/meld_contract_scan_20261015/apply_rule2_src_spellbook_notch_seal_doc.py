"""Rule 2 docstring correction in spellbook.py: the notch seal is EXCLUSIVE and the owning Conduit admits it.

`_notch_spell` and `_apply_notch` said the notch claims the owning spellbook INTENT; the notch strategy's plan
(`NotchTransactionStrategy.build_start_plan` -> `_seal_scope_keys`) claims the spellbook, the acting conduit and the
conduits linked to it, and the binding key, all EXCLUSIVE, and freezes those conduits' creation gates. Reported by
melder_0 (M0-177); spellbook.py is melder_1's file for rule 2, whose `_apply_notch` it edits.
usage: python <this script> <tree root> [--check]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_lib import apply

ROOT = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]
REL = "src/melder/aether/spellbook/spellbook.py"

STEPS = [
    ("one",
     '''        Contract:
            - Admits a `notch` transaction (claims the owning spellbook INTENT
              and the spell binding key EXCLUSIVE), performs the selected-spell
              switch inside the held window, then commits.
''',
     '''        Contract:
            - Runs inside the `notch` transaction the owning Conduit admits and
              ends (`Conduit.notch_spell`): its seal claims this spellbook, the
              acting conduit, the conduits linked to it and the spell binding key,
              all EXCLUSIVE, and freezes those conduits' creation gates
              (`NotchTransactionStrategy`; corrected 2026-10-16: this said the
              spellbook admits the transaction and claims itself INTENT). It
              performs the selected-spell switch inside the held window.
''', ""),
    ("one",
     '''        Runs inside the held `notch` transaction window (owning spellbook INTENT
        + binding key EXCLUSIVE). A SpellIndex holds a SET of member spell ids;
''',
     '''        Runs inside the held `notch` transaction window (the owning spellbook,
        the acting conduit, the conduits linked to it and the binding key, all
        EXCLUSIVE; corrected 2026-10-16: this said spellbook INTENT). A
        SpellIndex holds a SET of member spell ids;
''', ""),
]

apply(ROOT, REL, STEPS, CHECK)
