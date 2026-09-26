"""Apply the test side of the conjure-report change (2026-09-26) to a repository root.

Usage: python apply_reporting_tests.py <repo_root>
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import append_block, create_file, replace_block

root = pathlib.Path(sys.argv[1])
T = root / "tests"
U4 = T / "unit/melder/spellbook/spell_crafter/validation/strategies"
U6 = T / "unit/melder/spellbook/spell_crafter/system/validation"

# --- exception renderer tests: rewritten to the new contract --------------------------------
sve = T / "unit/melder/utilities/custom_exceptions/test_spellbook_validation_error.py"
raw = sve.read_bytes().decode("utf-8")
assert "Spellbook validation failed; one or more spells are broken." in raw, "exception test moved"
ending = "\r\n" if raw.count("\r\n") * 2 > raw.count("\n") else "\n"
new_text = (pathlib.Path(__file__).parent / "new_files/test_spellbook_validation_error.py").read_text(encoding="utf-8")
sve.write_bytes(new_text.replace("\n", ending).encode("utf-8"))
print("rewrote test_spellbook_validation_error.py")

# --- guard: list[Any] is plain data; a user class inside the element still warns ----------------
replace_block(U4 / "test_annotation_shape_guard_strategy.py", '''def test_annotation_shape_guard_warns_for_list_of_any() -> None:
    """typing.Any is not a DI target (as in Phase 1), so list[Any] draws the list-element warning."""
    strategy = AnnotationShapeGuardStrategy()
    context = _Context(
        requirements=_Requirements([_Parameter("values", list[typing.Any], ParameterDIShape.PLAIN)])
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == ["LIST_ELEMENT_NOT_DI_TARGET"]''', '''def test_annotation_shape_guard_leaves_plain_data_lists_silent() -> None:
    """list[Any] and list[str] are plain caller inputs: no list-element warning (2026-09-26)."""
    strategy = AnnotationShapeGuardStrategy()
    context = _Context(
        requirements=_Requirements([
            _Parameter("values", list[typing.Any], ParameterDIShape.PLAIN),
            _Parameter("names", list[str], ParameterDIShape.PLAIN),
        ])
    )

    strategy.validate(context)

    assert context.issues == []


def test_annotation_shape_guard_warns_when_a_user_class_hides_in_the_element() -> None:
    """list[Optional[Plugin]] may have meant injection: warn, and say it is left to the caller."""
    class Plugin:
        """User class stand-in."""

    strategy = AnnotationShapeGuardStrategy()
    context = _Context(
        requirements=_Requirements([
            _Parameter("plugins", list[typing.Optional[Plugin]], ParameterDIShape.PLAIN),
        ])
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == ["LIST_ELEMENT_NOT_DI_TARGET"]
    assert "left for the caller to supply" in context.issues[0].message''')

# --- required holes: the list-only hint only for containers of user classes ---------------------
replace_block(U4 / "test_required_holes_strategy.py", '''    strategy = RequiredHolesStrategy()
    issues: list[SpellValidationIssue] = []
    params = [
        _ParamStub("ops", 0, dict[str, object]),
        _ParamStub("tags", 1, set[str]),
        _ParamStub("frozen", 2, frozenset[str]),
        _ParamStub("parts", 3, tuple[int, ...]),
        _ParamStub("count", 4, int),
        _ParamStub("raw", 5, None),
    ]''', '''    class Operation:
        """User class stand-in held inside the containers."""

    strategy = RequiredHolesStrategy()
    issues: list[SpellValidationIssue] = []
    params = [
        _ParamStub("ops", 0, dict[str, Operation]),
        _ParamStub("tags", 1, set[Operation]),
        _ParamStub("frozen", 2, frozenset[Operation]),
        _ParamStub("parts", 3, tuple[Operation, ...]),
        _ParamStub("count", 4, int),
        _ParamStub("raw", 5, None),
        _ParamStub("payload", 6, dict[str, Any]),
        _ParamStub("labels", 7, set[str]),
        _ParamStub("anything", 8, dict[str, object]),
    ]''')
replace_block(U4 / "test_required_holes_strategy.py", '''    assert "list[T]" not in messages["count"]
    assert "list[T]" not in messages["raw"]''', '''    assert "list[T]" not in messages["count"]
    assert "list[T]" not in messages["raw"]
    # Plain data containers are ordinary caller inputs: no hint (2026-09-26).
    for name in ("payload", "labels", "anything"):
        assert "list[T]" not in messages[name]''')
replace_block(U4 / "test_required_holes_strategy.py", "from typing import Iterable, List, Optional",
              "from typing import Any, Iterable, List, Optional")

# --- component guard test: list[int] is plain data --------------------------------------------
cvs = T / "component/melder/spellbook/spell_crafter/validation/test_spellbook_component_validation_strategies.py"
replace_block(cvs, '''def test_component_annotation_shape_guard_warns_on_list_non_di_element() -> None:
    """
    Purpose:
        Validate AnnotationShapeGuardStrategy warns on list elements that are not DI targets.
    Contract:
        - list[int] yields LIST_ELEMENT_NOT_DI_TARGET warnings.''', '''def test_component_annotation_shape_guard_leaves_list_of_data_silent() -> None:
    """
    Purpose:
        Validate AnnotationShapeGuardStrategy treats a list of plain data as a caller input.
    Contract:
        - list[int] yields no LIST_ELEMENT_NOT_DI_TARGET warning (2026-09-26); only a user
          class inside the element draws it.''')
replace_block(cvs, '''        try:
            strategy.validate(context)
            assert len(issues) == 1
            issue = issues[0]
            assert issue.code == "LIST_ELEMENT_NOT_DI_TARGET"
            assert issue.severity == "warning"
        finally:''', '''        try:
            strategy.validate(context)
            assert [issue.code for issue in issues if issue.code == "LIST_ELEMENT_NOT_DI_TARGET"] == []
        finally:''')

# --- Phase-6 local test: lookup values model the Spell contract -----------------------------------
p6 = T / "unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_6_local.py"
replace_block(p6, '''        spell_lookup={"root": object()},
    )

    assert len(diagnostics) == 2''', '''        spell_lookup={"root": SimpleNamespace(spell_name="Root")},
    )

    assert len(diagnostics) == 2
    assert all("not visible" in diag.message for diag in diagnostics)
    named = {diag.root_id: diag.message for diag in diagnostics}
    assert "'Root'" in named["root"]
    assert "spell id root-duplic" in named["root-duplicate"]''')

# --- meld-path test: the message names the spell (ids are no longer printed) -------------------------
replace_block(T / "unit/melder/aether/conduit/meld/test_meld.py", """    with pytest.raises(SpellbookValidationError) as exc_info:
        meld._gated_validation_required(spell)

    assert "spell-1" in str(exc_info.value)""", """    with pytest.raises(SpellbookValidationError) as exc_info:
        meld._gated_validation_required(spell)

    # The report names spells, not ids (2026-09-26); the spell object stays on the error.
    assert exc_info.value.broken_spells == [spell]
    assert "Broken spells: Spell." in str(exc_info.value)""")

# --- local-rerun gate: the conduit reasons reach the message ----------------------------------------
replace_block(T / "unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py", """    scoped phase artifacts.
    \"\"\"
    spellbook = _StubSpellbook()
    cleanup_calls = []

    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_target_foundational_resolution_phases",
        staticmethod(lambda **kwargs: {"root_blueprints_local": ["rb"]}),
    )""", """    scoped phase artifacts.
    \"\"\"
    from melder.aether.spellbook.spell_compiler.system.system_diagnostic import SystemDiagnostic

    spellbook = _StubSpellbook()
    cleanup_calls = []
    reason = SystemDiagnostic("scope_ordering_violation", "Holder depends on Leaf.", spell_id="spell-1")
    spellbook._spell_system_states = types.SimpleNamespace(
        get_conduit_resolution_state=lambda conduit_id: types.SimpleNamespace(list_diagnostics=lambda: [reason]),
    )

    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_target_foundational_resolution_phases",
        staticmethod(lambda **kwargs: {"root_blueprints_local": ["rb"]}),
    )""")
replace_block(T / "unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py", """    with pytest.raises(SpellbookValidationError):
        SpellbookCreationSystem.run_resolution_phases_for_target_spell(
            spellbook=spellbook,
            conduit_id="cid",
            target_spell=types.SimpleNamespace(spell_id="spell-1"),
        )

    assert cleanup_calls == [{"spell-1"}]""", """    with pytest.raises(SpellbookValidationError) as exc_info:
        SpellbookCreationSystem.run_resolution_phases_for_target_spell(
            spellbook=spellbook,
            conduit_id="cid",
            target_spell=types.SimpleNamespace(spell_id="spell-1"),
        )

    assert cleanup_calls == [{"spell-1"}]
    # The phase artifacts are cleaned before the raise; the conduit diagnostics carry the reason.
    assert "Holder depends on Leaf. [scope_ordering_violation]" in str(exc_info.value)""")

# --- appended contract tests ----------------------------------------------------------------------
append_block(U4 / "test_circular_dependency_strategy.py", '''

def test_validate_names_each_cycle_member_and_closes_the_loop_once() -> None:
    """
    Purpose:
        The message names the cycle by spell name and closes it once ("A -> B -> A").
    Contract:
        No doubled start node; a fix sentence follows; details keep ids.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell_a = _SpellStub(spell_id="a", spell_name="Alpha", dependencies=["b"])
    spell_b = _SpellStub(spell_id="b", spell_name="Beta", dependencies=["a"])
    spellbook = _SpellbookStub([spell_a, spell_b])
    context = _make_context(spell=spell_a, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    message = issues[0].message
    assert "'Alpha' -> 'Beta' -> 'Alpha'." in message
    assert "-> 'Alpha' -> 'Alpha'" not in message
    assert "give that parameter a default" in message
''')
append_block(U4 / "test_parameter_policy_strategy.py", '''

def test_parameter_policy_skips_variadic_any_annotation() -> None:
    """*args: Any / **kwargs: Any are not DI (typing.Any is a class since 3.11), as in Phase 1."""
    strategy = ParameterPolicyStrategy()
    context = _Context(
        requirements=_Requirements(
            [
                _Parameter(name="args", di_shape=ParameterDIShape.PLAIN, annotation=typing.Any,
                           is_var_positional=True),
                _Parameter(name="kwargs", di_shape=ParameterDIShape.PLAIN, annotation=typing.Any,
                           is_var_keyword=True),
            ]
        )
    )

    strategy.validate(context)

    assert context.issues == []


def test_parameter_policy_variadic_message_says_what_to_do() -> None:
    """The variadic error explains Melder never injects *args/**kwargs and points to list[...]."""
    class Plugin:
        """User class stand-in."""

    strategy = ParameterPolicyStrategy()
    context = _Context(
        requirements=_Requirements(
            [_Parameter(name="plugins", di_shape=ParameterDIShape.PLAIN, annotation=Plugin, is_var_positional=True)]
        )
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == ["VARIADIC_DI_UNSUPPORTED"]
    assert "never injects variadic parameters" in context.issues[0].message
    assert "list[...]" in context.issues[0].message
''')
append_block(U6 / "test_scope_ordering_strategy.py", '''

def test_scope_ordering_violation_names_both_spells_and_the_fix() -> None:
    """The message names holder and dependency with their existences and says how to fix it."""
    from types import SimpleNamespace

    index = SpellSystemIndex()
    index.upsert_node(SpellSystemNode(spell_id="root", lineage_id="lr", dependencies={"child"},
                                      existence=Existence.unique))
    index.upsert_node(SpellSystemNode(spell_id="child", lineage_id="lc", dependencies=set(),
                                      existence=Existence.unique_per_spell_space))
    diagnostics: list = []

    ScopeOrderingStrategy().run(
        index=index, blueprints={}, phase4_results={}, broken_spell_ids=set(), spell_system_states=object(),
        spell_lookup={"root": SimpleNamespace(spell_name="Holder"), "child": SimpleNamespace(spell_name="Leaf")},
        diagnostics=diagnostics, cancel_event=None,
    )

    message = diagnostics[0].message
    assert "Spell 'Holder' (unique) depends on 'Leaf' (unique_per_spell_space)" in message
    assert "Give 'Holder' the same or a shorter existence (or many), or give 'Leaf' a longer one." in message
''')
append_block(U6 / "test_cycle_detection_strategy.py", '''

def test_cycle_message_names_blocked_spells_and_records_ids():
    """The cycle diagnostic names the spells in or behind the cycle and keeps their ids in details."""
    from types import SimpleNamespace

    diagnostics = []
    CycleDetectionStrategy().run(
        index=_index(_node("a", {"b"}), _node("b", {"a"}), _node("c", set())),
        blueprints={}, phase4_results={}, broken_spell_ids=set(), spell_system_states=object(),
        spell_lookup={"a": SimpleNamespace(spell_name="Alpha"), "b": SimpleNamespace(spell_name="Beta")},
        diagnostics=diagnostics, cancel_event=None,
    )

    assert len(diagnostics) == 1
    assert "Cycle detected" in diagnostics[0].message
    assert "'Alpha', 'Beta'" in diagnostics[0].message
    assert diagnostics[0].details["blocked_spell_ids"] == ["a", "b"]


def test_cycle_message_caps_the_named_list():
    """More than ten blocked spells are summarised as "and N more"."""
    nodes = [_node(f"n{i:02d}", {f"n{(i + 1) % 12:02d}"}) for i in range(12)]
    diagnostics = []
    CycleDetectionStrategy().run(
        index=_index(*nodes), blueprints={}, phase4_results={}, broken_spell_ids=set(),
        spell_system_states=object(), spell_lookup={}, diagnostics=diagnostics, cancel_event=None,
    )

    assert "and 2 more" in diagnostics[0].message
    assert len(diagnostics[0].details["blocked_spell_ids"]) == 12
''')
append_block(T / "unit/melder/utilities/helpers/test_general_helpers.py", '''

def test_spell_input_utils_describe_spell_id_prefers_names():
    """describe_spell_id quotes a known spell's name and shortens unknown ids."""
    from types import SimpleNamespace

    spells = {"a" * 64: SimpleNamespace(spell_name="CodecPacket")}

    assert SpellInputUtils.describe_spell_id("a" * 64, spells) == "'CodecPacket'"
    assert SpellInputUtils.describe_spell_id("b" * 64, spells) == "spell id " + "b" * 12
    assert SpellInputUtils.describe_spell_id(None, spells) == "an unknown spell"
''')

# --- integration: what a user sees from a real conjure -------------------------------------------
create_file(T / "integration/melder/spellbook/test_spellbook_integration_validation_report.py",
            (pathlib.Path(__file__).parent / "new_files/test_spellbook_integration_validation_report.py").read_text(encoding="utf-8"))
print("done")
