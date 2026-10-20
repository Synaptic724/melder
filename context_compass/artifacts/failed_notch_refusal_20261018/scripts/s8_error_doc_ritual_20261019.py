"""Documentation ritual on S8's error-file edit: name who passes the preface, type _check_preface's input as object.

Edits apply_s8_rollback.py (the edit set the repository gets) and the mirror's spellbook_validation_error.py (CRLF)
with the same three exact replacements, each anchor found exactly once. Usage: s8_error_doc_ritual_20261019.py
<mirror root> --check|--apply
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
APPLY_SCRIPT = HERE / "apply_s8_rollback.py"
ERROR = "src/melder/utilities/custom_exceptions/spellbook_validation_error.py"

SCRIPT_EDITS = [
    ('     "          above follows it unchanged; `Conduit.notch_spell` passes one when it\\n"\n'
     '     "          refuses a notch, saying the notch did not happen.\\n"),\n',
     '     "          above follows it unchanged; a refused notch passes one, saying the\\n"\n'
     '     "          notch did not happen (`Spellbook._notch_spell`, which\\n"\n'
     '     "          `Conduit.notch_spell` calls inside its transaction).\\n"),\n'),
    ("                default). `Conduit.notch_spell` passes one when it refuses a notch.\n",
     "                default). A refused notch passes one (`Spellbook._notch_spell`).\n"),
    ("    def _check_preface(preface: Any) -> None:\n",
     "    def _check_preface(preface: object) -> None:\n"),
]

MIRROR_EDITS = [
    ("          above follows it unchanged; `Conduit.notch_spell` passes one when it\n"
     "          refuses a notch, saying the notch did not happen.\n",
     "          above follows it unchanged; a refused notch passes one, saying the\n"
     "          notch did not happen (`Spellbook._notch_spell`, which\n"
     "          `Conduit.notch_spell` calls inside its transaction).\n"),
    SCRIPT_EDITS[1],
    SCRIPT_EDITS[2],
]


def _edit(text: str, edits: list, where: str) -> str:
    """Apply exact replacements whose anchors occur once; refuse lines over 120 characters."""
    for old, new in edits:
        if text.count(old) != 1:
            raise SystemExit("%s: anchor found %d times: %r" % (where, text.count(old), old[:80]))
        for line in new.split("\n"):
            if len(line) > 120:
                raise SystemExit("%s: line over 120 chars: %s" % (where, line))
        text = text.replace(old, new)
    return text


def main() -> None:
    """Edit both files in memory; write only with --apply and read each back."""
    if len(sys.argv) != 3 or sys.argv[2] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    script_raw = APPLY_SCRIPT.read_bytes().decode("utf-8")
    if "\r\n" in script_raw:
        raise SystemExit("apply script is not LF")
    script_new = _edit(script_raw, SCRIPT_EDITS, APPLY_SCRIPT.name)
    mirror_path = pathlib.Path(sys.argv[1]) / ERROR
    mirror_raw = mirror_path.read_bytes().decode("utf-8")
    if mirror_raw.count("\r\n") != mirror_raw.count("\n"):
        raise SystemExit("mirror error file is not all CRLF")
    mirror_new = _edit(mirror_raw.replace("\r\n", "\n"), MIRROR_EDITS, ERROR).replace("\n", "\r\n")
    print("apply script lines:", script_new.count("\n"), "mirror error file lines:", mirror_new.count("\r\n"))
    if sys.argv[2] == "--apply":
        APPLY_SCRIPT.write_bytes(script_new.encode("utf-8"))
        mirror_path.write_bytes(mirror_new.encode("utf-8"))
        if APPLY_SCRIPT.read_bytes().decode("utf-8") != script_new:
            raise SystemExit("read-back mismatch: apply script")
        if mirror_path.read_bytes().decode("utf-8") != mirror_new:
            raise SystemExit("read-back mismatch: mirror")
        print("applied")


main()
