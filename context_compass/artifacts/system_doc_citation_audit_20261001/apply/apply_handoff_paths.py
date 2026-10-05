"""
Give the two 2026-10-01 handoff paragraphs full source paths where they cite a line (melder_0).

The citation recipe resolves `path:line` against the repository root, so a bare `bind.py:657` reads as a missing
file - the failure src_components itself warns about. Usage: python apply_handoff_paths.py <repo root>
"""
import sys

from apply_support import ApplySession


class HandoffPaths:
    """The two paragraph fixes."""

    @staticmethod
    def apply(session: ApplySession) -> None:
        """
        Stage both fixes.

        Args:
            session: The apply session over the repository root.
        """
        arch = "context_compass/system_docs/src_architecture.md"
        comp = "context_compass/system_docs/src_components.md"
        session.replace(arch,
            "2026-10-01 citation audit (documentation only): the internal-bind call is on bind.py:657 in\n"
            "`Bind._bind_logic` (cited as 404); the bind-guard manifest holds 619 entries at 0.2.8215 (cited as\n"
            "582) and is 641 lines; the conjure sequence's evidence now covers the whole verdict gate (242-263)\n"
            "and the two cache-classifying methods (616-721). The other suspect citations here read true when\n"
            "opened: spellbook.py:3686 and `check_system_state` at 1253-1292. Citations the audit heuristic could\n"
            "not tie to a symbol were not opened.\n",
            "2026-10-01 citation audit (documentation only): the internal-bind call is\n"
            "`src/melder/aether/spellbook/bind/bind.py:657`, in `Bind._bind_logic` (cited as 404); the bind-guard\n"
            "manifest holds 619 entries at 0.2.8215 (cited as 582) and is 641 lines; the conjure sequence's\n"
            "evidence now covers the whole verdict gate (242-263) and the two cache-classifying methods (616-721).\n"
            "The other suspect citations here read true when opened: the Spellbook comment at\n"
            "`src/melder/aether/spellbook/spellbook.py:3686` and `check_system_state` at 1253-1292. Citations\n"
            "the audit heuristic could not tie to a symbol were not opened.\n")
        session.replace(comp,
            "2026-10-01 citation audit (documentation only): nine stale citations remapped - the internal-bind call\n"
            "(bind.py:657 in `Bind._bind_logic`) and `assert_allowed` (62-106), the Crystallizer's `emit`\n"
            "(1619-1671), and the six into mutation_research.py's lock-order block (263, 886-887, 893-896, 901,\n"
            "1000-1001, 3956) - and the conjure flow's evidence tightened (242-263, 616-721). Four other suspects\n"
            "read true when opened (spellbook.py:3686 twice, the occurrence analyzer's contract-default reader,\n"
            "`sha256_profile`'s class branch).",
            "2026-10-01 citation audit (documentation only): nine stale citations remapped - the internal-bind call\n"
            "(`src/melder/aether/spellbook/bind/bind.py:657`, in `Bind._bind_logic`) and `assert_allowed`\n"
            "(62-106), the Crystallizer's `emit` (1619-1671), and the six into the MutationResearch lock-order block\n"
            "(263, 886-887, 893-896, 901, 1000-1001, 3956) - and the conjure flow's evidence tightened (242-263,\n"
            "616-721). Four other suspects read true when opened (the Spellbook comment at\n"
            "`src/melder/aether/spellbook/spellbook.py:3686` twice, the occurrence analyzer's contract-default\n"
            "reader, `sha256_profile`'s class branch).")


def main(argv: list) -> int:
    """
    Apply and write.

    Args:
        argv: `<repo root>`.

    Returns:
        int: 0 on success.
    """
    session = ApplySession(argv[0])
    HandoffPaths.apply(session)
    long_lines = session.long_added_lines()
    if long_lines:
        raise AssertionError("long added lines: " + "; ".join(long_lines))
    for written in session.write():
        print("WROTE", written)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
