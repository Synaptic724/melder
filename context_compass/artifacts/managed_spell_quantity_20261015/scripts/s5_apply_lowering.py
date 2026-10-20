"""Apply the S5 lowering edits (parts 1-3) to site_plan_lowering.py, each old text exactly once."""
import pathlib
import runpy
import sys

TARGET = pathlib.Path(
    "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py"
)


def main() -> int:
    edits = []
    for part in sys.argv[1:]:
        edits.extend(runpy.run_path(part)["EDITS"])
    text = TARGET.read_text(encoding="utf-8")
    for number, (old, new) in enumerate(edits, 1):
        if text.count(old) != 1:
            print("edit", number, "matches", text.count(old), repr(old[:100]))
            return 1
        text = text.replace(old, new)
    TARGET.write_text(text, encoding="utf-8", newline="")
    print("applied", len(edits), "edits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
