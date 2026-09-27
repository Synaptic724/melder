"""Run each Melder introspection site against user code (and Melder's own classes) and report.

Usage: python -X gil=0 probe_call_sites.py <src_root>
Prints one line per site: OK / RAISED <ExceptionType>: <message>.
"""
import sys
import traceback

sys.path.insert(0, sys.argv[1])
sys.path.insert(0, "/home/claude/work/probes_inspect")

import probe_user_mod as um  # noqa: E402  (probe script, not repository code)
from melder.aether.aether import Aether  # noqa: E402
from melder.aether.spellbook.spellbook import Spellbook  # noqa: E402
from melder.aether.conduit.conduit import Conduit  # noqa: E402
from melder.aether.spellbook.existence.existence import Existence  # noqa: E402
from melder.utilities.helpers.package import Package  # noqa: E402
from melder.utilities.ai_native_support_tools.protocol_crafter import ProtocolCrafter  # noqa: E402
from melder.aether.spellbook.spell_compiler.spell_examiner.spell_examiner import SpellExaminer  # noqa: E402
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy import (  # noqa: E402
    SpellOccurrenceGraphAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_occurrence_contract_processor_strategy import (  # noqa: E402
    SpellOccurrenceContractProcessorStrategy,
)

results = []


def site(name, fn):
    try:
        value = fn()
        results.append((name, "OK", value))
    except Exception as exc:  # probe: report, do not stop
        tb = traceback.extract_tb(exc.__traceback__)
        melder_frames = [f for f in tb if "/melder/" in f.filename]
        where = ""
        if melder_frames:
            f = melder_frames[-1]
            where = f" @ {f.filename.split('/src/')[-1]}:{f.lineno}"
        results.append((name, f"RAISED {type(exc).__name__}: {exc}{where}", None))


Aether._reset_singleton_for_tests()
aether = Aether()
Spellbook._aether = aether
Conduit._aether = aether
book = Spellbook(aetheric_frame="inspect-probe")
engine_id = book.bind(spell=um.Engine, existence=Existence.unique, permissions="create")
car_id = book.bind(spell=um.Car, existence=Existence.many, permissions="create")
conduit = book.conjure(name="inspect-probe", dynamic=True)

site("A meld user Car (TYPE_CHECKING-annotated default)", lambda: type(conduit.meld(spell_id=car_id)).__name__)

car_spell = book.find_spell_by_id(car_id)
site("   car spell found", lambda: type(car_spell).__name__)
site("   requirements after conjure", lambda: repr(car_spell._compiler_artifact._requirements)[:60])
site("B analyzer _iter_spell_contract_defaults(car)",
     lambda: list(SpellOccurrenceGraphAnalyzerStrategy._iter_spell_contract_defaults(car_spell)))
site("B' processor _iter_spell_contract_defaults(car)",
     lambda: list(SpellOccurrenceContractProcessorStrategy._iter_spell_contract_defaults(car_spell)))
site("C ConduitWard._get_spell_contract_keys(car)", lambda: conduit._conduit_ward._get_spell_contract_keys(car_spell))
site("C' lesser conduit create + meld", lambda: type(conduit.create_lesser_conduit().meld(spell_id=car_id)).__name__)

site("D Package(make_car).describe()", lambda: Package(um.make_car).describe())
site("D' Package(make_car).signature", lambda: Package(um.make_car).signature)

crafter = ProtocolCrafter()
site("E ProtocolCrafter.craft_protocol_code(Car)", lambda: crafter.craft_protocol_code(um.Car))
site("E' ProtocolCrafter.craft_protocol_code(Conduit)", lambda: crafter.craft_protocol_code(Conduit)[:40])
site("E'' ProtocolCrafter.craft_protocol_code(Spellbook)", lambda: crafter.craft_protocol_code(Spellbook)[:40])

examiner = SpellExaminer()
site("F SpellExaminer general(Car class)", lambda: type(examiner.create_profile(um.Car, "general")).__name__)
site("F' SpellExaminer detailed(Car class)", lambda: type(examiner.create_profile(um.Car, "detailed")).__name__)
site("F'' SpellExaminer detailed(car spell)", lambda: type(examiner.create_profile(car_spell, "detailed")).__name__)
site("F''' SpellExaminer detailed(make_car fn)", lambda: type(examiner.create_profile(um.make_car, "detailed")).__name__)
site("G SpellExaminer detailed(Conduit class)", lambda: type(examiner.create_profile(Conduit, "detailed")).__name__)
site("G' SpellExaminer detailed(Spellbook class)", lambda: type(examiner.create_profile(Spellbook, "detailed")).__name__)

for name, status, value in results:
    shown = "" if value is None else f" -> {str(value)[:110]!r}"
    print(f"{name}: {status}{shown if status == 'OK' else ''}")
