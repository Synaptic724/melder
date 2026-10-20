"""Rule 2 / D2 test change: the structural-snapshot parity notch event pins the revalidation a notch now causes.

Before rule 2 the after-notch meld of Car silently built the old Engine (its plan named the parked version). Now the
notch marks Car and its meld rechecks its structure: `engine: Engine` does not select EngineAlternative (the kind rule),
so it raises the first meld's UnresolvedInputError; after a notch back Car builds with Engine. Cold and hydrated worlds
must still end alike. contract_recheck_on_notch_2026_10_16 (probe C4). usage: python <this script> <tree root> [--check]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_lib import apply

ROOT = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]
REL = "tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_parity.py"

STEPS = [
    ("one",
     '''from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration
''',
     '''from melder.nexus.nexus import Nexus
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration
''', ""),
    ("between",
     '''def _event_notch(book: Spellbook, conduit: Conduit, ids: Dict[str, str]) -> Any:
''',
     '''def _event_remove(book: Spellbook, conduit: Conduit, ids: Dict[str, str]) -> Any:
''',
     '''def _event_notch(book: Spellbook, conduit: Conduit, ids: Dict[str, str]) -> Any:
    """
    Meld Car, stage an alternative Engine into Engine's index, notch it, meld the new member and Car, then notch back
    to Engine and meld Car again.

    Rule 2 (D2, 2026-10-16): a notch marks every spell that depends on the notched one, so Car's next meld rechecks
    its structure against the version now active. A class annotation selects its own type (the kind rule), so
    `engine: Engine` does not select EngineAlternative: that meld raises the UnresolvedInputError a first meld would
    raise, and after the notch back Car builds with Engine again. Before rule 2 the after-notch meld silently built
    the old Engine, and a dependent melded first after a provider notch failed with "generalized manifest references
    unknown spell_id". Cold and hydrated worlds must end alike either way.
    """
    before = conduit.meld(spell=Car)
    engine_index = book.find_spell_by_id(ids["Engine"]).spell_index
    staged_id = conduit.bind_inactive(spell=EngineAlternative, spell_index=engine_index, existence="unique")
    conduit.notch_spell(spell_index=engine_index, spell_id=staged_id)
    member = conduit.meld(spell_id=staged_id)
    staged_is_active = book.find_spell_by_id(staged_id).spell_id == staged_id
    try:
        after: Any = type(conduit.meld(spell=Car).engine).__name__
    except UnresolvedInputError as error:
        after = (type(error).__name__, "engine" in str(error))
    conduit.notch_spell(spell_index=engine_index, spell_id=ids["Engine"])
    back = conduit.meld(spell=Car)
    return (
        type(before.engine).__name__, type(member).__name__, staged_is_active, after, type(back.engine).__name__,
    )


'''),
]

apply(ROOT, REL, STEPS, CHECK)
