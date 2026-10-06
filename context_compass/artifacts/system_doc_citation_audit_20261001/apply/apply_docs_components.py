"""
Apply the 2026-10-01 citation audit to src_components (melder_0).

Every anchor must match once; nothing is written unless all edits apply and no added prose line passes 120
characters. The 13 new core entries are measured from disk at apply time.
Usage: python apply_docs_components.py <repo root> <verified_at UTC>
"""
import pathlib
import sys
from typing import List, Tuple

from apply_support import ApplySession


class ComponentsAudit:
    """
    The edits of this pass to src_components.

    Attributes:
        DOC: Repo-relative document path.
        NEW_CORE: The Key Files with no core entry, each with its note (the class it defines and the entry
            that names it).
    """

    DOC: str = "context_compass/system_docs/src_components.md"
    NEW_CORE: Tuple[Tuple[str, str], ...] = (
        ("src/melder/_build_assets/_system_documents/system_documents.py",
         "loader of the four package-root system documents (Packaged Hardcopy Documents)."),
        ("src/melder/aether/conduit/meld/creation_context/creation_context_factory.py",
         "`CreationContextFactory`: builds spell-shaped CreationContexts (Meld Resolution Runtime)."),
        ("src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py",
         "`CreationContextRebuild`: holds the affected index gates through a rebuild (Meld Resolution Runtime)."),
        ("src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py",
         "`SharedCompilerExecutions`: static execution helpers shared by the phases (SpellCompiler)."),
        ("src/melder/aether/spellbook/spell_compiler/shared_assets/codegen_signature.py",
         "`CodegenSignature`: the one codegen signature path (SpellCompiler)."),
        ("src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py",
         "`SpellCompilerArtifact`: the spell-scoped compiler artifact container (SpellCompiler)."),
        ("src/melder/aether/spellbook/spell_compiler/spell_examiner/inspectors/class_inspector.py",
         "`ClassInspector`: class inventory for the examiner (Spell Examination Profiles)."),
        ("src/melder/aether/spellbook/spell_compiler/spell_examiner/inspectors/inspector_utility.py",
         "`InspectorUtility`: low-level helpers of the inspector layer (Spell Examination Profiles)."),
        ("src/melder/aether/spellbook/spell_compiler/spell_examiner/inspectors/method_inspector.py",
         "`MethodInspector`: callable inventory for the examiner (Spell Examination Profiles)."),
        ("src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py",
         "`BindingProfileStrategy`: binding profiles from user objects (Spell Examination Profiles)."),
        ("src/melder/utilities/custom_exceptions/spellbook_validation_error.py",
         "`SpellbookValidationError`: names the spells conjure cannot build (SpellCompiler)."),
        ("src/melder/utilities/helpers/general_helpers.py",
         "`EnumHelpers` and `SpellInputUtils` (spell-key normalization) (Spell Validation Strategies)."),
        ("src/melder/utilities/helpers/signature_reflection.py",
         "`SignatureReflection`: signatures and annotations with unavailable names (Spell Examination Profiles)."),
    )

    @staticmethod
    def core_block(root: pathlib.Path, stamp: str) -> str:
        """
        Measure each new core file and render its entry.

        Args:
            root: Repository root.
            stamp: verified_at for the measurements.

        Returns:
            str: The entries, in the document's shape.
        """
        parts: List[str] = []
        for path, note in ComponentsAudit.NEW_CORE:
            count = len((root / path).read_bytes().decode("utf-8").splitlines())
            parts.append(f"- path: `{path}`\n  start_line: 1\n  end_line: {count}\n  loc: {count}\n"
                         f"  verified_at: {stamp}\n  note: {note}\n")
        return "".join(parts)

    @staticmethod
    def apply(session: ApplySession, stamp: str) -> None:
        """
        Stage every edit on `session`.

        Args:
            session: The apply session over the repository root.
            stamp: verified_at for the measured entries.
        """
        doc = ComponentsAudit.DOC
        s = session.replace
        s(doc, "  - src/melder/aether/spellbook/bind/bind.py:84-97 (`assert_allowed`)\n",
          "  - src/melder/aether/spellbook/bind/bind.py:62-106 (`assert_allowed`)\n")
        s(doc, "  `src/melder/aether/spellbook/bind/bind.py:404` -\n"
               "  `assert_allowed(spell, context=\"bind\")`. (Was cited as `:363` here and `:364`\n"
               "  in `src_architecture.md` before subsequent edits; the current call is on 404. The documents disagreeing\n",
          "  `src/melder/aether/spellbook/bind/bind.py:657` (in `Bind._bind_logic`) -\n"
          "  `assert_allowed(spell, context=\"bind\")`. (Was cited as `:363` here and `:364`\n"
          "  in `src_architecture.md` before subsequent edits, and as `:404` in both until 2026-10-01; the\n"
          "  current call is on 657. The documents disagreeing\n")
        s(doc, "  - src/melder/crystallizer/crystallizer.py:1587-1594 (`emit` records through\n",
          "  - src/melder/crystallizer/crystallizer.py:1619-1671 (`emit` records through\n")
        s(doc, "one line apart - :830 then :831,\n  and :944 then :945.\n",
          "one line apart - :886 then :887,\n  and :1000 then :1001.\n")
        s(doc, "  - src/melder/mutation_research/mutation_research.py:220 (`_emission_lock` created)\n"
               "  - src/melder/mutation_research/mutation_research.py:830-831 (emission then root)\n"
               "  - src/melder/mutation_research/mutation_research.py:837-840 (the `on_mutation` wiring)\n"
               "  - src/melder/mutation_research/mutation_research.py:845 (emitter called under both)\n"
               "  - src/melder/mutation_research/mutation_research.py:944-945 (same order on the load path)\n"
               "  - src/melder/mutation_research/mutation_research.py:3900 (`_emission_lock` re-entered)\n",
          "  - src/melder/mutation_research/mutation_research.py:263 (`_emission_lock` created)\n"
          "  - src/melder/mutation_research/mutation_research.py:886-887 (emission then root)\n"
          "  - src/melder/mutation_research/mutation_research.py:893-896 (the `on_mutation` wiring)\n"
          "  - src/melder/mutation_research/mutation_research.py:901 (emitter called under both)\n"
          "  - src/melder/mutation_research/mutation_research.py:1000-1001 (same order on the load path)\n"
          "  - src/melder/mutation_research/mutation_research.py:3956 (`_emission_lock` re-entered)\n")
        s(doc, "     EVIDENCE: `src/melder/aether/spellbook/spellbook_creation_system.py:242-260`,\n"
               "     `src/melder/aether/spellbook/spellbook_creation_system.py:616-723`.\n",
          "     EVIDENCE: `src/melder/aether/spellbook/spellbook_creation_system.py:242-263`,\n"
          "     `src/melder/aether/spellbook/spellbook_creation_system.py:616-721`.\n")
        s(doc, "  582-entry manifest start refusing binds mid-suite with no signal. Preserve\n",
          "  619-entry manifest start refusing binds mid-suite with no signal. Preserve\n")
        s(doc, "  `MANIFEST_ENTRY_COUNT` (582 at the current build).\n",
          "  `MANIFEST_ENTRY_COUNT` (619 at 0.2.8215).\n")
        s(doc, "- path: `src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py`\n"
               "  start_line: 1\n  end_line: 667\n  loc: 667\n  verified_at: 2026-09-26T20:10:34Z\n",
          "- path: `src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py`\n"
          "  start_line: 1\n  end_line: 641\n  loc: 641\n  verified_at: " + stamp + "\n")
        session.insert_before(doc, "### Full Package Inventory (exhaustive, retained)\n",
                              ComponentsAudit.core_block(session.root, stamp))
        s(doc, "has drifted from the Key Files union (12 key files without an entry, 19 entries no Key Files list names).\n",
          "has drifted from the Key Files union (corrected by the audit below: 13 key files had no entry and no entry\n"
          "was unclaimed; the 12 and 19 first written here came from a parser that missed part of one list).\n")
        session.insert_after(doc, "## Context / Handoff Summary\n\n",
            "2026-10-01 citation audit (documentation only): nine stale citations remapped - the internal-bind call\n"
            "(bind.py:657 in `Bind._bind_logic`) and `assert_allowed` (62-106), the Crystallizer's `emit`\n"
            "(1619-1671), and the six into mutation_research.py's lock-order block (263, 886-887, 893-896, 901,\n"
            "1000-1001, 3956) - and the conjure flow's evidence tightened (242-263, 616-721). Four other suspects\n"
            "read true when opened (spellbook.py:3686 twice, the occurrence analyzer's contract-default reader,\n"
            "`sha256_profile`'s class branch). The bind-guard count is 619 at 0.2.8215 (was 582) and the\n"
            "manifest's code-map extent 641. The core set is the Key Files union again (227 = 227): the 13 claimed\n"
            "files that had no entry are measured and added; no entry was unclaimed. Citations the audit\n"
            "heuristic could not tie to a symbol were not opened.\n\n")


def main(argv: list) -> int:
    """
    Apply and write.

    Args:
        argv: `<repo root> <verified_at UTC>`.

    Returns:
        int: 0 on success.
    """
    session = ApplySession(argv[0])
    ComponentsAudit.apply(session, argv[1])
    long_lines = session.long_added_lines()
    if long_lines:
        raise AssertionError("long added lines: " + "; ".join(long_lines))
    for written in session.write():
        print("WROTE", written)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
