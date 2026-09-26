from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, Sequence, cast

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


def _spell(
        name: str = "RootSpell",
        spell_id: str = "spell-1",
        frame: Any = "frame-1",
        issues: Sequence[SpellValidationIssue] = (),
        phase6_errors: Sequence[SystemDiagnostic] = (),
) -> "Spell":
    """
    Purpose:
        Build a spell stand-in exposing the attributes the renderer reads.
    Contract:
        Phase 4 issues sit on `validation_result_phase4.issues`; Phase 6 errors on
        `validation_result_phase6.errors`.
    Returns:
        Spell: The stand-in, cast for typing.
    """
    return cast("Spell", SimpleNamespace(
        spell_name=name,
        spell_id=spell_id,
        spellframe=frame,
        validation_result_phase4=SimpleNamespace(issues=list(issues)),
        validation_result_phase6=SimpleNamespace(errors=list(phase6_errors), warnings=[]),
    ))


def _issue(code: str, message: str, severity: str = "error") -> SpellValidationIssue:
    """Build one Phase-4 issue with a source and details the renderer must not print."""
    return SpellValidationIssue(
        severity=severity, code=code, message=message, source="SomeStrategy", details={"param": "value"}
    )


def _diag(code: str, message: str, spell_id: Any = None,
          severity: SystemDiagnosticSeverity = SystemDiagnosticSeverity.ERROR) -> SystemDiagnostic:
    """Build one system diagnostic with a source and details the renderer must not print."""
    return SystemDiagnostic(code=code, message=message, severity=severity, spell_id=spell_id,
                            source="DiagStrategy", details={"impact": "root"})


def test_message_example_lists_errors_by_spell_with_fix_and_code() -> None:
    """
    Purpose:
        Pin the full layout for one broken spell with an error, a warning and a frame.
    Contract:
        First line names the spell; the block lists the error message then its code; the
        warning is only counted.
    """
    spell = _spell(issues=[_issue("REQUIRED_HOLE", "Supply name.", "warning"),
                           _issue("CIRCULAR_DEPENDENCY", "Spell 'RootSpell' is part of a cycle.")])

    message = str(SpellbookValidationError([spell]))

    assert message == "\n".join([
        "Spellbook validation failed. Broken spells: RootSpell.",
        "RootSpell (frame 'frame-1'):",
        "  - Spell 'RootSpell' is part of a cycle. [CIRCULAR_DEPENDENCY]",
        "1 warning not shown (warnings never block conjure); conjure(validation_warnings=True) logs them.",
    ])


def test_first_line_keeps_matcher_substrings_and_hides_ids() -> None:
    """
    Purpose:
        Keep "Spellbook validation failed" and "Broken spells" for callers that match on them,
        while dropping the spell id from the text.
    """
    spell = _spell(spell_id="a" * 64, issues=[_issue("X", "Bad.")])

    message = str(SpellbookValidationError([spell]))

    assert message.startswith("Spellbook validation failed. Broken spells: RootSpell.")
    assert "a" * 12 not in message


def test_empty_input_uses_fallback_message() -> None:
    """Purpose: no spells and no diagnostics keep the historical fallback text."""
    assert str(SpellbookValidationError([])) == "SpellbookValidationError raised with no broken spells."


def test_warnings_details_and_sources_are_never_printed() -> None:
    """
    Purpose:
        Prove the body carries errors only.
    Contract:
        Warning messages, strategy sources and details payloads are absent; warnings are counted.
    """
    spell = _spell(issues=[_issue("W1", "first warning", "warning"),
                           _issue("W2", "second warning", "warning"),
                           _issue("E1", "The error.")])

    message = str(SpellbookValidationError([spell]))

    assert "first warning" not in message and "second warning" not in message
    assert "SomeStrategy" not in message and "details" not in message and "'param'" not in message
    assert "2 warnings not shown" in message
    assert "  - The error. [E1]" in message


def test_internal_codes_are_marked_once_with_report_footer() -> None:
    """
    Purpose:
        Render Melder bookkeeping codes as internal errors to report.
    Contract:
        The line carries "[internal]"; a repeated internal code appears once; one footer.
    """
    spell = _spell(issues=[_issue("CLASS_PROFILE_MISSING", "Profile missing."),
                           _issue("CLASS_PROFILE_MISSING", "Profile missing again.")])

    message = str(SpellbookValidationError([spell]))

    assert sum(line.startswith("  - [internal]") for line in message.splitlines()) == 1
    assert "  - [internal] Profile missing. [CLASS_PROFILE_MISSING]" in message
    assert message.endswith("Please report them with this message.")


def test_user_errors_carry_no_internal_footer() -> None:
    """Purpose: the internal footer appears only when an internal code is shown."""
    message = str(SpellbookValidationError([_spell(issues=[_issue("X", "Bad.")])]))

    assert "[internal]" not in message and "Melder bugs" not in message


def test_binding_cycle_hidden_when_circular_dependency_shown() -> None:
    """
    Purpose:
        Report one cycle once per spell.
    Contract:
        BINDING_RESOLUTION_CYCLE is hidden when CIRCULAR_DEPENDENCY is present in the same
        block, and shown when it is alone.
    """
    both = _spell(issues=[_issue("CIRCULAR_DEPENDENCY", "Cycle A."), _issue("BINDING_RESOLUTION_CYCLE", "Cycle B.")])
    alone = _spell(name="Other", spell_id="spell-2", issues=[_issue("BINDING_RESOLUTION_CYCLE", "Key cycle.")])

    message = str(SpellbookValidationError([both, alone]))

    assert "Cycle B." not in message
    assert "Cycle A. [CIRCULAR_DEPENDENCY]" in message
    assert "Key cycle. [BINDING_RESOLUTION_CYCLE]" in message


def test_restating_codes_hidden_only_when_another_error_is_shown() -> None:
    """
    Purpose:
        Drop root_not_viable / broken_spell_in_dag when a real reason is shown, keep them otherwise.
    """
    with_reason = str(SpellbookValidationError(
        [_spell(issues=[_issue("X", "Real reason.")])],
        system_diagnostics=[_diag("root_not_viable", "Not viable.", "spell-1")],
    ))
    alone = str(SpellbookValidationError(
        [_spell(issues=[])],
        system_diagnostics=[_diag("root_not_viable", "Not viable.", "spell-1")],
    ))

    assert "Not viable." not in with_reason and "Real reason." in with_reason
    assert "Not viable. [root_not_viable]" in alone


def test_identical_errors_are_listed_once() -> None:
    """Purpose: an exact (code, message) repeat inside a block is dropped."""
    spell = _spell(issues=[_issue("X", "Same."), _issue("X", "Same."), _issue("X", "Different.")])

    message = str(SpellbookValidationError([spell]))

    assert message.count("Same. [X]") == 1
    assert "Different. [X]" in message


def test_system_diagnostics_are_attributed_to_spells_or_the_whole_graph() -> None:
    """
    Purpose:
        Show the conduit reasons the gates hand in.
    Contract:
        An ERROR naming a supplied spell id joins that spell's block; one naming no supplied
        spell lands under "Whole-graph errors:"; WARNING diagnostics are ignored.
    """
    spell = _spell(issues=[])
    diagnostics = [
        _diag("scope_ordering_violation", "Holder depends on Leaf.", "spell-1"),
        _diag("cycle_detected", "Cycle detected among A, B."),
        _diag("visibility_gap_dependency_filtered", "Needs spell id deadbeef0000.", "not-a-supplied-id"),
        _diag("collection_socket_no_providers", "Just a warning.", "spell-1", SystemDiagnosticSeverity.WARNING),
    ]

    message = str(SpellbookValidationError([spell], system_diagnostics=diagnostics))

    assert message.splitlines() == [
        "Spellbook validation failed. Broken spells: RootSpell.",
        "RootSpell (frame 'frame-1'):",
        "  - Holder depends on Leaf. [scope_ordering_violation]",
        "Whole-graph errors:",
        "  - Cycle detected among A, B. [cycle_detected]",
        "  - Needs spell id deadbeef0000. [visibility_gap_dependency_filtered]",
    ]


def test_spells_without_errors_are_not_listed_when_diagnostics_explain() -> None:
    """
    Purpose:
        The conjure gate names every spell when an error carries no spell id; the message must
        not list them all.
    """
    spells = [_spell(name=f"S{i}", spell_id=f"id-{i}") for i in range(5)]

    message = str(SpellbookValidationError(spells, system_diagnostics=[_diag("cycle_detected", "Cycle.")]))

    assert message.splitlines()[0] == "Spellbook validation failed. The dependency graph has errors."
    assert "S0" not in message and "S4" not in message
    assert "  - Cycle. [cycle_detected]" in message


def test_meld_path_names_spell_with_no_recorded_error() -> None:
    """
    Purpose:
        Meld raises for invalid/gated/disabled validity without handing diagnostics; say so plainly.
    """
    message = str(SpellbookValidationError([_spell(frame=None)]))

    assert message.splitlines() == [
        "Spellbook validation failed. Broken spells: RootSpell.",
        "RootSpell:",
        "  - No validation error was recorded for this spell; its validity is invalid, gated or disabled.",
    ]


def test_live_phase4_result_is_read() -> None:
    """Purpose: the renderer reads a real SpellValidationResult, not only stand-ins."""
    result = SpellValidationResult(spell_id="spell-1", spell_name="RootSpell",
                                   issues=[_issue("LIVE", "Live error."), _issue("LW", "Live warning.", "warning")])
    spell = cast("Spell", SimpleNamespace(spell_name="RootSpell", spell_id="spell-1", spellframe=None,
                                          validation_result_phase4=result, validation_result_phase6=None))

    message = str(SpellbookValidationError([spell]))

    assert "  - Live error. [LIVE]" in message and "1 warning not shown" in message


def test_errors_and_warnings_views_are_the_fallback_for_missing_issues() -> None:
    """Purpose: a result exposing only `errors`/`warnings` is still rendered."""
    spell = cast("Spell", SimpleNamespace(
        spell_name="RootSpell", spell_id="spell-1", spellframe=None,
        validation_result_phase4=SimpleNamespace(errors=[_issue("E", "Split error.")],
                                                 warnings=[_issue("W", "Split warning.", "warning")]),
    ))

    message = str(SpellbookValidationError([spell]))

    assert "  - Split error. [E]" in message and "1 warning not shown" in message


def test_rendering_survives_unreadable_attributes() -> None:
    """
    Purpose:
        A cleaned or partial spell must not raise a second error while the first is built.
    """
    class _Exploding:
        """Stand-in whose every attribute read raises."""

        def __getattr__(self, name: str) -> Any:
            """Raise for any attribute, like a cleaned object."""
            raise RuntimeError(f"cleaned: {name}")

    message = str(SpellbookValidationError([cast("Spell", _Exploding())]))

    assert message.startswith("Spellbook validation failed. Broken spells: <unknown spell>.")


def test_class_frames_render_by_qualified_name() -> None:
    """Purpose: a Protocol/class spellframe shows its qualified name, not a repr."""
    class Plugin:
        """Frame stand-in."""

    message = str(SpellbookValidationError([_spell(frame=Plugin, issues=[_issue("X", "Bad.")])]))

    assert "RootSpell (frame test_class_frames_render_by_qualified_name.<locals>.Plugin):" in message


def test_broken_spells_attribute_is_kept_as_supplied() -> None:
    """Purpose: tooling keeps the spell objects, including gate fallbacks with no own errors."""
    spells = [_spell(), _spell(name="Other", spell_id="spell-2")]

    error = SpellbookValidationError(spells, system_diagnostics=[_diag("cycle_detected", "Cycle.")])

    assert error.broken_spells is spells
