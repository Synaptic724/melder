"""
Probe: does the Book-wide validation flag drop back to False once the late-bound spell is melded, and does a
resolvable=False Protocol definition ever let it drop? TASK-2026-10-15-trace_meld_contract_scan_gate (melder_1).
Run from the repository root with PYTHONPATH=src; reuses the classes and helpers of probe_meld_contract_scan.py.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import probe_meld_contract_scan as base


def main() -> None:
    """Late bind, meld the late spell, read the flag; then the Protocol world after melding everything melds."""
    book = base.fresh_book("probe_recover", dynamic=True)
    book.bind(spell=base.Svc, existence="unique")
    book.bind(spell=base.Task, existence="many")
    root = book.conjure(name="probe_recover_root", dynamic=True)
    root.meld(spell=base.Task)
    root.bind(spell=base.Other, existence="many")
    print(f"late bind: after bind flag={book._spellbook_validation_required}; {base.risk_view(book, root._id)}")
    root.meld(spell=base.Other)
    print(f"late bind: after melding Other flag={book._spellbook_validation_required}; {base.risk_view(book, root._id)}")
    root.meld(spell=base.Task)
    print(f"late bind: after next Task meld flag={book._spellbook_validation_required}")
    root.cleanup()
    book = base.fresh_book("probe_protocol", dynamic=True)
    book.bind(spell=base.Svc, existence="unique")
    book.bind(spell=base.Task, existence="many")
    book.bind(spell=base.IThing, existence="unique", resolvable=False)
    root = book.conjure(name="probe_protocol_root", dynamic=True)
    root.meld(spell=base.Task)
    root.meld(spell=base.Svc)
    print(f"protocol def: after melding every resolvable spell flag={book._spellbook_validation_required}; "
          f"{base.risk_view(book, root._id)}")
    root.cleanup()


if __name__ == "__main__":
    main()
