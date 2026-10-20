"""Rule 2 red tests for the lost-provider report (D1-B): renderer, strategy message, Phase 4 pin (melder_1).

usage: python <this script> <tree root> [--check]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_lib import apply  # noqa: E402  (script-local helper import)

ROOT = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]

RENDER_ANCHOR = "def test_live_phase4_result_is_read() -> None:\n"
RENDER_TESTS = '''def test_gating_warning_is_listed_as_the_spells_reason() -> None:
    """
    Purpose:
        A lineage that a Phase-4 warning gates (a lost SpellContract provider) names that warning as its reason,
        not "No validation error was recorded".
    Contract:
        The gating warning renders as an error line; it is not counted among the hidden warnings.
    """
    spell = _spell(name="Consumer", issues=[_issue("SPELL_CONTRACT_MISSING_PROVIDER", "No provider.", "warning")])

    message = str(SpellbookValidationError([spell]))

    assert message.splitlines() == [
        "Spellbook validation failed. Broken spells: Consumer.",
        "Consumer (frame 'frame-1'):",
        "  - No provider. [SPELL_CONTRACT_MISSING_PROVIDER]",
    ]


def test_other_warnings_stay_counted_beside_a_gating_reason() -> None:
    """Purpose: only gating warnings are listed; every other warning is still only counted."""
    spell = _spell(name="Consumer", issues=[
        _issue("REQUIRED_HOLE", "Supply name.", "warning"),
        _issue("SPELL_CONTRACT_MISSING_PROVIDER", "No provider.", "warning"),
    ])

    message = str(SpellbookValidationError([spell]))

    assert message.splitlines() == [
        "Spellbook validation failed. Broken spells: Consumer.",
        "Consumer (frame 'frame-1'):",
        "  - No provider. [SPELL_CONTRACT_MISSING_PROVIDER]",
        "1 warning not shown (warnings never block conjure); conjure(validation_warnings=True) logs them.",
    ]


def test_gating_warning_is_counted_when_the_block_shows_errors() -> None:
    """Purpose: a spell with errors lists its errors; its gating warning joins the hidden count."""
    spell = _spell(issues=[
        _issue("E1", "The error."),
        _issue("SPELL_CONTRACT_MISSING_PROVIDER", "No provider.", "warning"),
    ])

    message = str(SpellbookValidationError([spell]))

    assert message.splitlines() == [
        "Spellbook validation failed. Broken spells: RootSpell.",
        "RootSpell (frame 'frame-1'):",
        "  - The error. [E1]",
        "1 warning not shown (warnings never block conjure); conjure(validation_warnings=True) logs them.",
    ]


def test_gating_only_block_is_listed_when_diagnostics_are_given() -> None:
    """
    Purpose:
        With conduit diagnostics handed in, a spell whose only reason is a gating warning is still listed; a spell
        with no reason is not.
    """
    gated = _spell(name="Consumer", issues=[_issue("SPELL_CONTRACT_MISSING_PROVIDER", "No provider.", "warning")])
    quiet = _spell(name="Other", spell_id="spell-2")

    message = str(SpellbookValidationError([gated, quiet], system_diagnostics=[_diag("cycle_detected", "Cycle.")]))

    assert message.splitlines() == [
        "Spellbook validation failed. Broken spells: Consumer.",
        "Consumer (frame 'frame-1'):",
        "  - No provider. [SPELL_CONTRACT_MISSING_PROVIDER]",
        "Whole-graph errors:",
        "  - Cycle. [cycle_detected]",
    ]


def test_gating_warning_codes_are_the_codes_phase_4_gates_on() -> None:
    """Purpose: the renderer's gating set is the one code Phase 4 gates a lineage on (pinned there too)."""
    assert SpellbookValidationError.GATING_WARNING_CODES == frozenset({"SPELL_CONTRACT_MISSING_PROVIDER"})


'''

STRATEGY_ANCHOR = "def test_contract_provider_presence_automatic_mode_errors() -> None:\n"
STRATEGY_TEST = '''def test_contract_provider_presence_missing_provider_names_the_contract_and_the_remedy() -> None:
    """
    Purpose:
        A lost provider is reported with the contract it belongs to and how to restore it (D1-B): this warning
        is the reason the validation report gives for a consumer the missing provider gates.
    """
    contract = SpellContract(spellframe="service", binding_name="primary")
    context, issues = _make_context(
        requirements=_RequirementsStub([
            _ParamStub(name="service", di_shape=ParameterDIShape.SPELL_CONTRACT, default_value=contract),
        ]),
        contracted_spells=[],
        system_state=SystemState.dynamic,
    )
    strategy = ContractProviderPresenceStrategy()
    try:
        strategy.validate(context)

        assert [(issue.severity, issue.code) for issue in issues] == [("warning", "SPELL_CONTRACT_MISSING_PROVIDER")]
        assert issues[0].message == (
            "Spell 'spell-name' parameter 'service' has no provider for its SpellContract "
            "(frame_key='service', binding_key='primary'): no active spell with that frame and binding name is "
            "contracted to this Spellbook. Contract one from a linked conduit (add_index_to_contract, or "
            "add_spell_to_contract for one version) and meld again."
        )
        assert issues[0].details == {"parameter_name": "service", "contract_key": ("service", "primary")}
    finally:
        strategy.cleanup()
        context.cleanup()
        contract.cleanup()


'''

PHASE4_IMPORT_OLD = """from tests.unit.melder.spellbook.spell_compiler.support.compiler_test_support import (
    make_spell,
)
"""
PHASE4_IMPORT_NEW = """from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from tests.unit.melder.spellbook.spell_compiler.support.compiler_test_support import (
    make_spell,
)
"""
PHASE4_ANCHOR = "def test_run_skips_revalidation_when_cached_and_still_valid() -> None:\n"
PHASE4_TESTS = '''def _phase4_validity_for_warning(monkeypatch: pytest.MonkeyPatch, code: str) -> Any:
    """Run Phase 4 over a result carrying one warning with `code`; return the last validity it published."""
    spell = make_spell("spell-1")
    artifact = spell._compiler_artifact
    _prime_structural_artifacts(artifact)
    state = _StateStub(compiler_phase_4_module.SpellValidity.unknown)
    result = SimpleNamespace(has_errors=False, issues=[SimpleNamespace(code=code, severity="warning")])
    monkeypatch.setattr(
        compiler_phase_4_module.SharedCompilerExecutions,
        "capture_phase2_5_codegen_ir",
        lambda _spell, _artifact: None,
    )
    CompilerPhase4().run(spell, artifact, _make_validator(result, []), _make_states(state))
    return state.set_validity_calls[-1]["validity"]


def test_run_gates_the_lineage_on_every_code_the_report_lists_as_a_reason(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Phase 4 gates a lineage on exactly the warnings SpellbookValidationError lists as a spell's reason, so a meld
    refused for a gated lineage always names why.
    """
    assert SpellbookValidationError.GATING_WARNING_CODES
    for code in sorted(SpellbookValidationError.GATING_WARNING_CODES):
        assert _phase4_validity_for_warning(monkeypatch, code) is compiler_phase_4_module.SpellValidity.gated


def test_run_marks_the_lineage_valid_on_a_warning_outside_the_reported_reasons(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A warning the report only counts leaves the lineage valid."""
    assert "REQUIRED_HOLE" not in SpellbookValidationError.GATING_WARNING_CODES
    assert _phase4_validity_for_warning(monkeypatch, "REQUIRED_HOLE") is compiler_phase_4_module.SpellValidity.valid


'''

apply(ROOT, "tests/unit/melder/utilities/custom_exceptions/test_spellbook_validation_error.py",
      [("one", RENDER_ANCHOR, RENDER_TESTS + RENDER_ANCHOR, "")], CHECK)
apply(ROOT, "tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_contract_provider_presence_strategy.py",
      [("one", STRATEGY_ANCHOR, STRATEGY_TEST + STRATEGY_ANCHOR, "")], CHECK)
apply(ROOT, "tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_4.py",
      [("one", PHASE4_IMPORT_OLD, PHASE4_IMPORT_NEW, ""), ("one", PHASE4_ANCHOR, PHASE4_TESTS + PHASE4_ANCHOR, "")],
      CHECK)
