from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.aether.spellbook.spell_compiler.validation.spell_validation_result import (
    SpellValidationResult,
)
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell


def test_spellbook_validation_error_includes_spell_summary() -> None:
    """
    Purpose:
        Ensure SpellbookValidationError summarizes broken spells.
    Contract:
        The message includes spell name, id, and frame information.
    Returns:
        None.
    Raises:
        AssertionError: If summary details are missing.
    """
    spell = SimpleNamespace(
        spell_name="RootSpell",
        spell_id="spell-1",
        spellframe="frame-1",
    )

    error = SpellbookValidationError([cast("Spell", spell)])
    message = str(error)

    assert "Broken spells" in message
    assert "RootSpell" in message
    assert "id=spell-1" in message
    assert "frame='frame-1'" in message
    assert "Diagnostics" in message


def test_spellbook_validation_error_handles_empty_list() -> None:
    """
    Purpose:
        Verify empty spell lists use the fallback message.
    Contract:
        The error message indicates no broken spells were supplied.
    Returns:
        None.
    Raises:
        AssertionError: If the fallback message is missing.
    """
    error = SpellbookValidationError([])
    assert "no broken spells" in str(error)


def test_spellbook_validation_error_includes_phase_diagnostics() -> None:
    """
    Purpose:
        Ensure diagnostics from Phase 4 and Phase 6 appear in the error message.
    Contract:
        The message includes issue codes, strategy sources, and system diagnostics.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostic content is missing.
    """

    class _Phase4Result:
        """
        Purpose:
            Provide a minimal Phase 4 result stub for diagnostics.
        Contract:
            Exposes issues list as expected by SpellbookValidationError.
        """

        def __init__(self, issues):
            """
            Purpose:
                Store issues for diagnostic formatting.
            Contract:
                Preserves the provided issues list.
            Args:
                issues: Collection of SpellValidationIssue instances.
            Returns:
                None.
            """
            self.issues = issues

    class _Phase6State:
        """
        Purpose:
            Provide a minimal Phase 6 state stub for diagnostics.
        Contract:
            Exposes errors and warnings lists.
        """

        def __init__(self, errors, warnings):
            """
            Purpose:
                Store system diagnostics for formatting.
            Contract:
                Preserves provided error and warning lists.
            Args:
                errors: Collection of SystemDiagnostic errors.
                warnings: Collection of SystemDiagnostic warnings.
            Returns:
                None.
            """
            self.errors = errors
            self.warnings = warnings

    class _SpellStub:
        """
        Purpose:
            Provide a spell stub with validation artifacts attached.
        Contract:
            Exposes names, ids, and validation_result_phase4/phase6.
        """

        def __init__(self, phase4, phase6):
            """
            Purpose:
                Initialize the spell stub with validation artifacts.
            Contract:
                Stores supplied Phase 4 and Phase 6 result objects.
            Args:
                phase4: Phase 4 validation result stub.
                phase6: Phase 6 validation state stub.
            Returns:
                None.
            """
            self.spell_name = "RootSpell"
            self.spell_id = "spell-1"
            self.spellframe = "frame-1"
            self.validation_result_phase4 = phase4
            self.validation_result_phase6 = phase6

    issue = SpellValidationIssue(
        severity="error",
        code="ISSUE_CODE",
        message="Issue message.",
        source="IssueStrategy",
    )
    diag = SystemDiagnostic(
        code="DIAG_CODE",
        message="Diag message.",
        severity=SystemDiagnosticSeverity.ERROR,
        spell_id="spell-1",
        root_id="root-1",
        source="DiagStrategy",
    )

    spell = _SpellStub(
        phase4=_Phase4Result([issue]),
        phase6=_Phase6State([diag], []),
    )
    error = SpellbookValidationError([cast("Spell", spell)])
    message = str(error)

    assert "Phase 4 issues" in message
    assert "ISSUE_CODE" in message
    assert "IssueStrategy" in message
    assert "Phase 6 diagnostics" in message
    assert "DIAG_CODE" in message
    assert "DiagStrategy" in message


def test_spellbook_validation_error_accepts_live_phase4_result() -> None:
    """
    Purpose:
        Verify the exception renderer works against the live Phase 4 result
        type rather than only stubbed objects.
    Contract:
        A real SpellValidationResult with one issue renders the issue details
        in the formatted exception message.
    Returns:
        None.
    Raises:
        AssertionError: If the live Phase 4 result is not rendered correctly.
    """
    issue = SpellValidationIssue(
        severity="error",
        code="LIVE_PHASE4",
        message="Live phase4 issue.",
        source="LiveStrategy",
    )
    phase4_result = SpellValidationResult(
        spell_id="spell-1",
        spell_name="RootSpell",
        issues=[issue],
    )
    spell = SimpleNamespace(
        spell_name="RootSpell",
        spell_id="spell-1",
        spellframe="frame-1",
        validation_result_phase4=phase4_result,
        validation_result_phase6=SimpleNamespace(errors=[], warnings=[]),
    )

    error = SpellbookValidationError([cast("Spell", spell)])
    message = str(error)

    assert "LIVE_PHASE4" in message
    assert "LiveStrategy" in message


def test_spellbook_validation_error_message_example_without_diagnostics() -> None:
    """
    Purpose:
        Provide a concrete example of the default validation error message.
    Contract:
        The formatted message matches the expected no-diagnostics layout.
    Returns:
        None.
    Raises:
        AssertionError: If the message does not match the expected format.
    """
    spell = SimpleNamespace(
        spell_name="RootSpell",
        spell_id="spell-1",
        spellframe="frame-1",
    )

    error = SpellbookValidationError([cast("Spell", spell)])
    message = str(error)

    expected = "\n".join(
        [
            "Spellbook validation failed; one or more spells are broken. Broken spells: "
            "RootSpell (id=spell-1, frame='frame-1')",
            "Diagnostics:",
            "Phase 4 issues:",
            "- Spell 'RootSpell' (id=spell-1, frame='frame-1'):",
            "    (none recorded)",
            "Phase 6 diagnostics:",
            "  (none recorded)",
        ]
    )

    assert message == expected


def test_spellbook_validation_error_message_example_with_diagnostics() -> None:
    """
    Purpose:
        Provide a concrete example of the diagnostics-rich error message.
    Contract:
        The formatted message matches the expected diagnostic layout.
    Returns:
        None.
    Raises:
        AssertionError: If the message does not match the expected format.
    """
    issue = SpellValidationIssue(
        severity="error",
        code="ISSUE_CODE",
        message="Issue message.",
        details={"param": "value"},
        source="IssueStrategy",
    )
    diag = SystemDiagnostic(
        code="DIAG_CODE",
        message="Diag message.",
        severity=SystemDiagnosticSeverity.ERROR,
        spell_id="spell-1",
        root_id="root-1",
        details={"impact": "root", "path": "root>dep"},
        source="DiagStrategy",
    )

    spell = SimpleNamespace(
        spell_name="RootSpell",
        spell_id="spell-1",
        spellframe="frame-1",
        validation_result_phase4=SimpleNamespace(issues=[issue]),
        validation_result_phase6=SimpleNamespace(errors=[diag], warnings=[]),
    )

    error = SpellbookValidationError([cast("Spell", spell)])
    message = str(error)

    expected = "\n".join(
        [
            "Spellbook validation failed; one or more spells are broken. Broken spells: "
            "RootSpell (id=spell-1, frame='frame-1')",
            "Diagnostics:",
            "Phase 4 issues:",
            "- Spell 'RootSpell' (id=spell-1, frame='frame-1'):",
            "    - [error] ISSUE_CODE (source=IssueStrategy): Issue message.",
            "      details: {'param': 'value'}",
            "Phase 6 diagnostics:",
            "  - [error] DIAG_CODE (source=DiagStrategy, spell_id=spell-1, root_id=root-1): Diag message.",
            "    details: {'impact': 'root', 'path': 'root>dep'}",
        ]
    )

    assert message == expected
