"""Docstring precision for find_spell_by_id: index moves have no None window; keeps EOL."""
import pathlib, sys
OLD = """            skip a registered spell. A writer moves an id between maps in steps
            (notch, index move, transfer between its flip and its inactive-member
            migration); a lookup that lands between two steps answers None for
            that lineage, so answers are not linearized against writers.
"""
NEW = """            skip a registered spell. A notch, and a transfer between its flip
            and its inactive-member migration, move ids between maps in steps;
            a lookup that lands between two steps answers None for that
            lineage, so answers are not linearized against writers. An index
            move only repoints a parked version's index, so a lookup racing it
            answers as before the move or as after it.
"""
for arg in sys.argv[1:]:
    p = pathlib.Path(arg)
    data = p.read_bytes().decode("utf-8")
    crlf = "\r\n" in data
    text = data.replace("\r\n", "\n")
    old = OLD if p.suffix == ".py" and "NEW_FIND" not in text else OLD
    if text.count(old) != 1:
        raise SystemExit(f"{p}: anchor count {text.count(old)}")
    text = text.replace(old, NEW, 1)
    p.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print(f"{p.name}: tweaked ({'CRLF' if crlf else 'LF'})")
