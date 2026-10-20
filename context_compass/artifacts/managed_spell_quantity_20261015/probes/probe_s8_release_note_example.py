"""
S8 probe: run the release note's 0.2.8248 example as written, plus the claims of its bullets.

The example's notch is a comment, because no public call returns a parked version's Spell (notch_spell needs the
Spell object; find_spell_by_id answers a parked id with the index's live spell). The probe performs that notch with
the Book's internal `_get_owned_spell`, exactly as the S8 integration tests do, and runs every other line verbatim.

Run from the repository root:  python -X gil=0 <this file>  (and -X gil=1)
"""
import pathlib
import re
import sys
import traceback


def example_source() -> str:
    """
    Return the S8 section's python block from the running release note, with the notch performed.

    Returns:
        str: Runnable source.
    """
    note = pathlib.Path("release_docs/next_version_release.md").read_text(encoding="utf-8")
    section = note.split("## A version staged before `conjure` melds after a notch", 1)[1]
    block = re.search(r"```python\n(.*?)```", section, re.S).group(1)
    comment = "# after reports.notch_spell(spell_index=index, spell=<v2's Spell>):\n"
    assert block.count(comment) == 1, "the notch comment moved"
    notch = comment + "reports.notch_spell(spell_index=index, spell=book._get_owned_spell(v2))\n"
    return "import melder as md\n" + block.replace(comment, notch)


def check_example() -> str:
    """
    Run the example verbatim (notch performed) in a fresh namespace.

    Returns:
        str: One result line.
    """
    namespace: dict = {"__name__": "release_note_example"}
    exec(compile(example_source(), "release_note_example", "exec"), namespace)
    service = namespace["service"]
    return f"example: meld after notch -> {type(service).__name__}, render() == {service.render()!r}"


def check_not_meldable_before_notch() -> str:
    """
    A staged id is off resolution until its notch (bullet 2).

    Returns:
        str: One result line.
    """
    import melder as md

    class Before:
        """The active version."""

    class After:
        """The staged version."""

    book = md.Spellbook()
    v1 = book.bind(spell=Before, existence="unique", binding_name="b1")
    index = book.find_spell_by_id(v1).spell_index
    v2 = book.bind_inactive(spell=After, spell_index=index, existence="unique", binding_name="b2")
    root = book.conjure(name="before_notch")
    try:
        root.meld(spell_id=v2)
    except KeyError as error:
        return f"before notch: KeyError {str(error)[:60]!r}"
    return "before notch: MELDED (unexpected)"


def check_managed_pool_from_conjure() -> str:
    """
    A managed version staged before conjure has its pool from conjure on, listed by describe(cls) (bullet 1).

    Returns:
        str: One result line.
    """
    import melder as md

    class PoolV1:
        """The active managed version."""

    class PoolV2:
        """The staged managed version."""

    book = md.Spellbook()
    v1 = book.bind(spell=PoolV1, existence="managed_spell_quantity", binding_name="m1")
    index = book.find_spell_by_id(v1).spell_index
    v2 = book.bind_inactive(spell=PoolV2, spell_index=index, existence="managed_spell_quantity", binding_name="m2")
    rows_before = md.ReleaseManagedSpell().describe(PoolV2)
    root = book.conjure(name="managed")
    rows = md.ReleaseManagedSpell().describe(PoolV2)
    root.notch_spell(spell_index=index, spell=book._get_owned_spell(v2))
    with root.managed_spell_meld(spell_id=v2) as leased:
        name = type(leased).__name__
    after = md.ReleaseManagedSpell().describe(PoolV2)
    return (
        f"managed: describe before conjure {len(rows_before)} row(s), after conjure {len(rows)} "
        f"(spell id matches: {rows[0].get('spell_id') == v2 if rows else False}); leased {name} after the notch; "
        f"after release count={after[0].get('count')} idle={after[0].get('idle_count', after[0].get('idle'))}"
    )


def main() -> None:
    """Run each check, print one line each; exit 1 when one raised."""
    failed = False
    print(f"python {sys.version.split()[0]}, gil enabled: {sys._is_gil_enabled()}")
    for check in (check_example, check_not_meldable_before_notch, check_managed_pool_from_conjure):
        try:
            print(check())
        except Exception:
            failed = True
            print(f"{check.__name__}: RAISED")
            traceback.print_exc()
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
