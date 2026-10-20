"""Probe (melder_0, 2026-10-19): case U3 of probe_index_unlink_leftovers.py with the notch's traceback and both
sides' state - where the AttributeError comes from, and what the lender and the borrower hold after it.

Read-only on src/: run from the folder above, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_index_unlink_leftovers_u3_trace.py
"""
import pathlib
import sys
import traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from probe_index_unlink_leftovers import fresh_aether, show, stage_french, world


def main() -> None:
    """U3 with the traceback."""
    fresh_aether()
    lender_book, borrower_book, lender, borrower, index, english_id, french_id, names = world("u3t")
    ids = {"English": english_id, "French": french_id}
    lender.cleanup_spell(spell=lender_book._inactive_spells[french_id])
    stage_french(lender, index)
    try:
        lender.notch_spell(spell_index=index, spell_id=french_id)
        print("notch -> done")
    except Exception:
        print("notch raised; traceback (innermost frames):")
        lines = traceback.format_exc().rstrip("\n").split("\n")
        for line in lines[-24:]:
            print("  " + line)
    print(f"lender index selects: {names.get(index.selected_spell_id, index.selected_spell_id[:10])}")
    print(f"lender active versions: {sorted(names.get(i, i[:10]) for i in lender_book._spells_by_id)}")
    print(f"lender parked versions: {sorted(names.get(i, i[:10]) for i in lender_book._inactive_spells)}")
    try:
        made = lender.meld(spell_id=index.selected_spell_id)
        print(f"lender.meld(selected) -> {type(made).__name__}.greet() = {made.greet()!r}")
    except Exception as error:
        print(f"lender.meld(selected) raised {type(error).__name__}: {error}")
    show("borrower after the notch", borrower_book, borrower, lender, index.id, ids)
    fresh_aether()


if __name__ == "__main__":
    main()
