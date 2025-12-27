from types import SimpleNamespace

from melder.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.spellbook.spell_crafter.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError


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

    error = SpellbookValidationError([spell])
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
    error = SpellbookValidationError([spell])
    message = str(error)

    assert "Phase 4 issues" in message
    assert "ISSUE_CODE" in message
    assert "IssueStrategy" in message
    assert "Phase 6 diagnostics" in message
    assert "DIAG_CODE" in message
    assert "DiagStrategy" in message
