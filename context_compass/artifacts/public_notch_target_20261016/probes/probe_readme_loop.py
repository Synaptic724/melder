"""
Acceptance probe: the README's stage -> notch -> meld loop and its revert, run AS WRITTEN on public calls only.

The README section "Then it actually changes the thing" holds two python blocks: the loop (stage with
`bind_inactive`, notch by id, meld) and the revert. They assume `conduit`, `index` and `ReportServiceV2` exist; this
probe builds exactly those - a dynamic root whose index holds v1 - and then execs both blocks verbatim. No private
attribute is touched anywhere.

Run from the repository root:  PYTHONPATH=src python -X gil=0 <this file>   (and -X gil=1)
"""
import pathlib
import re
import sys

import melder as md


def readme_blocks() -> list:
    """
    Return the two python blocks of the README's swap section, verbatim.

    Returns:
        list: [loop block, revert block].
    """
    text = pathlib.Path("README.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    section = text.split("### Then it actually changes the thing", 1)[1]
    blocks = re.findall(r"```python\n(.*?)```", section, re.S)[:2]
    if len(blocks) != 2 or "spell_id=id_v2" not in blocks[0] or "spell_id=id_v1" not in blocks[1]:
        raise SystemExit("the README swap blocks moved or still pass Spell objects")
    return blocks


class ReportService:
    """The version serving now."""

    def run(self) -> str:
        """Report v1."""
        return "v1 report"


class ReportServiceV2:
    """The version the loop stages and promotes."""

    def run(self) -> str:
        """Report v2."""
        return "v2 report"


def main() -> None:
    """Build the README's preconditions, exec both blocks verbatim, check the outcome."""
    print(f"python {sys.version.split()[0]}, gil enabled: {sys._is_gil_enabled()}, melder {md.__version__}")
    book = md.Spellbook()
    spell_id = book.bind(spell=ReportService, existence="unique", binding_name="v1")
    conduit = book.conjure(dynamic=True, name="readme")
    index = conduit.get_spell_by_id(spell_id).spell_index
    namespace = {"conduit": conduit, "index": index, "ReportServiceV2": ReportServiceV2}
    loop, revert = readme_blocks()
    exec(compile(loop, "README:stage-notch-meld", "exec"), namespace)
    service = namespace["service"]
    print(f"loop: selected is id_v2: {index.selected_spell_id == namespace['id_v2']}; "
          f"meld -> {type(service).__name__}.run() == {service.run()!r}")
    exec(compile(revert, "README:revert", "exec"), namespace)
    back = conduit.meld(spell_id=namespace["id_v1"])
    print(f"revert: selected is id_v1: {index.selected_spell_id == namespace['id_v1']}; "
          f"meld -> {type(back).__name__}.run() == {back.run()!r}; members {len(index.spells_in_index())}")
    ok = (
        isinstance(service, ReportServiceV2)
        and index.selected_spell_id == namespace["id_v1"]
        and isinstance(back, ReportService)
    )
    print("README loop:", "OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
