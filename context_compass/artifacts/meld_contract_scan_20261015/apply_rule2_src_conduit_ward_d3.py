"""Rule 2 / D3 docstrings in conduit_ward.py: a version grant's copy follows its version; the emission names both fan-outs.

contract_recheck_on_notch_2026_10_16, component_patch_notch_reactivation ("Grant docstring (every option)").
usage: python <this script> <tree root> [--check]
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
     '''        Adds a single spell to an existing contract with a peer conduit.

        This now contracts the **SpellIndex lineage** and uses the spell's
        current version ID only as the initial reference. On mutation, the
        lineage will advance, and lookups will resolve to the new version.
        When a new contract entry is added, cached consumer creations that
''',
     '''        Adds a single spell to an existing contract with a peer conduit.

        It contracts one version of the spell's SpellIndex lineage. The borrower
        holds a copy of that version: active while the version is the lineage's
        active member, parked while it is not. A notch away parks it on every
        linked peer and a notch back makes it active again, and the copy's
        consumers revalidate at their next meld; a grant of a parked version
        starts parked and becomes active when the owner notches to it
        (corrected 2026-10-16: this said lookups resolve to each new version,
        which only an index link does). An index link (`_add_index_to_contract`)
        follows the lineage to every new version instead.
        When a new contract entry is added, cached consumer creations that
''', ""),
    ("one",
     '''        receivers follow the lineage. Version-anchored borrowers are handled
        separately by the conduit's deactivate fan-out.
''',
     '''        receivers follow the lineage. Version-anchored borrowers are handled
        separately by the conduit's deactivate and activate fan-outs
        (`Conduit._deactivate_borrowed_spell`, `Conduit._activate_borrowed_spell`).
''', ""),
]

apply(ROOT, REL, STEPS, CHECK)
