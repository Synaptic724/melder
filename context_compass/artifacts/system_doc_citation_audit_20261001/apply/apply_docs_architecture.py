"""
Apply the 2026-10-01 citation audit to src_architecture (melder_0).

Every anchor must match once; nothing is written unless all edits apply and no added prose line passes 120
characters. Usage: python apply_docs_architecture.py <repo root> <verified_at UTC>
"""
import sys

from apply_support import ApplySession


class ArchitectureAudit:
    """The edits of this pass to src_architecture, as one ordered list."""

    DOC: str = "context_compass/system_docs/src_architecture.md"

    @staticmethod
    def apply(session: ApplySession, stamp: str) -> None:
        """
        Stage every edit on `session`.

        Args:
            session: The apply session over the repository root.
            stamp: verified_at for the remeasured C1 entry.
        """
        doc = ArchitectureAudit.DOC
        # The internal-bind call site moved with the bind hooks (2026-09-22); it is in Bind._bind_logic.
        session.replace(doc, "  `src/melder/aether/spellbook/bind/bind.py:404` -\n",
                        "  `src/melder/aether/spellbook/bind/bind.py:657` (in `Bind._bind_logic`) -\n")
        # Conjure sequence: the whole verdict gate, and the two classifying methods without the next decorator.
        session.replace(doc,
                        "     - src/melder/aether/spellbook/spellbook_creation_system.py:242-260\n"
                        "     - src/melder/aether/spellbook/spellbook_creation_system.py:517-544\n"
                        "     - src/melder/aether/spellbook/spellbook_creation_system.py:616-723\n",
                        "     - src/melder/aether/spellbook/spellbook_creation_system.py:242-263\n"
                        "     - src/melder/aether/spellbook/spellbook_creation_system.py:517-544\n"
                        "     - src/melder/aether/spellbook/spellbook_creation_system.py:616-721\n")
        # The bind-guard count follows the committed manifest.
        session.replace(doc, "`MANIFEST_ENTRY_COUNT` (582 at\n  the current build).",
                        "`MANIFEST_ENTRY_COUNT` (619 at\n  0.2.8215).")
        session.replace(doc, "a silently-dead patch would let the real 582-entry manifest begin refusing",
                        "a silently-dead patch would let the real 619-entry manifest begin refusing")
        # C1: the manifest's extent (641 lines at 0.2.8215).
        session.replace(doc,
                        "- path: `src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py`\n"
                        "  start_line: 1\n  end_line: 667\n  loc: 667\n  verified_at: 2026-09-26T20:10:34Z\n",
                        "- path: `src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py`\n"
                        "  start_line: 1\n  end_line: 641\n  loc: 641\n  verified_at: " + stamp + "\n")
        session.insert_after(doc, "## Context / Handoff Summary\n\n",
            "2026-10-01 citation audit (documentation only): the internal-bind call is on bind.py:657 in\n"
            "`Bind._bind_logic` (cited as 404); the bind-guard manifest holds 619 entries at 0.2.8215 (cited as\n"
            "582) and is 641 lines; the conjure sequence's evidence now covers the whole verdict gate (242-263)\n"
            "and the two cache-classifying methods (616-721). The other suspect citations here read true when\n"
            "opened: spellbook.py:3686 and `check_system_state` at 1253-1292. Citations the audit heuristic could\n"
            "not tie to a symbol were not opened.\n\n")


def main(argv: list) -> int:
    """
    Apply and write.

    Args:
        argv: `<repo root> <verified_at UTC>`.

    Returns:
        int: 0 on success.
    """
    session = ApplySession(argv[0])
    ArchitectureAudit.apply(session, argv[1])
    long_lines = session.long_added_lines()
    if long_lines:
        raise AssertionError("long added lines: " + "; ".join(long_lines))
    for written in session.write():
        print("WROTE", written)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
