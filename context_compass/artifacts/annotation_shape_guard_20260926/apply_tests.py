"""Apply the test edits for the caller-supplied-container fix to a repository root (argv[1])."""
import pathlib
import sys

from apply_fix import cut_between, edit


def unit_guard(root: pathlib.Path) -> None:
    """Guard unit tests: containers emit nothing; list[Any] warns; the removed helper's test goes."""
    rel = "tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_annotation_shape_guard_strategy.py"
    cut_between(root, rel,
                "def test_annotation_shape_guard_flags_unsupported_collection_di_shape() -> None:\n",
                "def test_annotation_shape_guard_warns_for_list_forward_ref() -> None:\n",
                '''def test_annotation_shape_guard_leaves_container_parameters_to_phase_1() -> None:
    """set/frozenset/dict/tuple parameters are PLAIN caller inputs in Phase 1; the guard emits nothing for them."""
    strategy = AnnotationShapeGuardStrategy()
    plain = ParameterDIShape.PLAIN
    context = _Context(
        requirements=_Requirements(
            [
                _Parameter("items", set["FrameKey"], plain),
                _Parameter("frozen", frozenset["FrameKey"], plain),
                _Parameter("by_name", dict[str, "FrameKey"], plain),
                _Parameter("parts", tuple["FrameKey", ...], plain),
                _Parameter("meta", dict[str, typing.Any], plain),
            ]
        )
    )

    strategy.validate(context)

    assert context.issues == []


def test_annotation_shape_guard_warns_for_list_of_any() -> None:
    """typing.Any is not a DI target (as in Phase 1), so list[Any] draws the list-element warning."""
    strategy = AnnotationShapeGuardStrategy()
    context = _Context(
        requirements=_Requirements([_Parameter("values", list[typing.Any], ParameterDIShape.PLAIN)])
    )

    strategy.validate(context)

    assert [issue.code for issue in context.issues] == ["LIST_ELEMENT_NOT_DI_TARGET"]


''')
    cut_between(root, rel,
                "def test_collection_args_have_di_targets_ignores_ellipsis_and_detects_target() -> None:\n",
                "def test_looks_like_di_target_heuristics_cover_supported_shapes() -> None:\n", "")


def unit_holes(root: pathlib.Path) -> None:
    """Required-holes unit test for the container hint (appended at the end of the file)."""
    rel = "tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_required_holes_strategy.py"
    path = root / rel
    raw = path.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace("\r\n", "\n").rstrip("\n") + "\n"
    text += '''

def test_validate_container_hole_names_list_only_collection_injection() -> None:
    """
    Purpose:
        Ensure container-typed required holes say Melder injects collections only as list[T].
    Contract:
        set/frozenset/dict/tuple annotations add the hint naming the container; other annotations do not.
    Returns:
        None.
    Raises:
        AssertionError: If the hint is missing or attached to a non-container parameter.
    """
    strategy = RequiredHolesStrategy()
    issues: list[SpellValidationIssue] = []
    params = [
        _ParamStub("ops", 0, dict[str, object]),
        _ParamStub("tags", 1, set[str]),
        _ParamStub("frozen", 2, frozenset[str]),
        _ParamStub("parts", 3, tuple[int, ...]),
        _ParamStub("count", 4, int),
        _ParamStub("raw", 5, None),
    ]
    context = _make_context(
        spell=_SpellStub(),
        requirements=_RequirementsStub(required_holes=params),
        issues=issues,
    )

    strategy.validate(context)

    messages = {issue.details["parameter_name"]: issue.message for issue in issues}
    for name, container in (("ops", "dict"), ("tags", "set"), ("frozen", "frozenset"), ("parts", "tuple")):
        assert "Melder injects collections only as list[T]" in messages[name]
        assert f"a {container} parameter is always supplied by the caller" in messages[name]
    assert "list[T]" not in messages["count"]
    assert "list[T]" not in messages["raw"]
    assert all(issue.code == "REQUIRED_HOLE" for issue in issues)
'''
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))
    print("appended", rel, repr(newline))


def component(root: pathlib.Path) -> None:
    """Component guard test: a set[T] parameter draws no guard issue and a REQUIRED_HOLE with the hint."""
    rel = "tests/component/melder/spellbook/spell_crafter/validation/test_spellbook_component_validation_strategies.py"
    cut_between(root, rel,
                "def test_component_annotation_shape_guard_flags_unsupported_collection_shape() -> None:\n",
                "def test_component_annotation_shape_guard_warns_on_list_non_di_element() -> None:\n",
                '''def test_component_annotation_shape_guard_leaves_set_parameters_to_the_caller() -> None:
    """
    Purpose:
        Validate that a set[T] constructor parameter is a caller input, not a DI error.
    Contract:
        - Phase 1 never injects set[T]; AnnotationShapeGuardStrategy emits no issue for it.
        - RequiredHolesStrategy reports it as REQUIRED_HOLE with the list-only collection hint.
    Returns:
        None.
    Raises:
        AssertionError: If the guard judges the parameter or the hint is missing.
    """
    spellbook = _make_spellbook()
    strategy = AnnotationShapeGuardStrategy()
    holes = RequiredHolesStrategy()

    class UsesSet:
        """
        Purpose:
            Provide a spell whose constructor takes a caller-supplied set of services.
        Contract:
            - Declares set[BasicService], which Melder never injects.
        Args:
            services: Services collection supplied by the caller.
        """

        def __init__(self, services: set[BasicService]) -> None:
            """
            Purpose:
                Capture the supplied services.
            Contract:
                Stores the services on the instance.
            Args:
                services: Collection of services.
            Returns:
                None.
            """
            self.services = services

    try:
        spell_id = spellbook.bind(
            spell=UsesSet,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        compiler_test_helpers.run_phase_requirements(spell)
        requirements = spell.requirements
        context, issues = _make_context(
            spell=spell,
            spellbook=spellbook,
            requirements=requirements,
        )
        try:
            strategy.validate(context)
            assert issues == []
            holes.validate(context)
            assert [issue.code for issue in issues] == ["REQUIRED_HOLE"]
            assert "Melder injects collections only as list[T]" in issues[0].message
        finally:
            context.cleanup()
    finally:
        holes.cleanup()
        strategy.cleanup()
        spellbook.cleanup()


''')


def integration(root: pathlib.Path) -> None:
    """Integration tests that asserted the old refusal now assert a caller input and a successful conjure."""
    faults = "tests/integration/melder/spellbook/test_spellbook_integration_di_validation_faults.py"
    edit(root, faults, [
        ('    """A real set[IPlugin] DI annotation (no SpellMap): must be flagged."""\n',
         '    """A set[IPlugin] parameter without a SpellMap: a caller input, reported as a REQUIRED_HOLE."""\n'),
        ('''def test_fault_b_control_genuine_set_shape_errors() -> None:
    """CONTROL (should pass): a real set[IPlugin] DI annotation is flagged."""''',
         '''def test_fault_b_control_set_parameter_is_a_caller_input() -> None:
    """CONTROL: a set[IPlugin] parameter is a caller input - a REQUIRED_HOLE warning, not a shape error."""'''),
        ('''        _phases_1_4(spell)
        assert "UNSUPPORTED_COLLECTION_SHAPE" in _codes4(spell)
    finally:''',
         '''        _phases_1_4(spell)
        codes = _codes4(spell)
        assert "UNSUPPORTED_COLLECTION_SHAPE" not in codes
        assert "REQUIRED_HOLE" in codes
    finally:'''),
    ])
    matrix = "tests/integration/melder/spellbook/test_spellbook_integration_di_shape_compiler_matrix.py"
    edit(root, matrix, [
        ('    """set[IPlugin] is an unsupported collection shape."""\n',
         '    """set[IPlugin] is a caller input: Melder never injects a set."""\n'),
        ('    """dict[str, IPlugin] is an unsupported collection shape."""\n',
         '    """dict[str, IPlugin] is a caller input: Melder never injects a dict."""\n'),
        ('''def test_phase4_unsupported_set_collection_shape_errors() -> None:
    """set[IPlugin] is an UNSUPPORTED_COLLECTION_SHAPE error."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=NeedsPluginSet, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        _phases_1_4(spell)
        assert "UNSUPPORTED_COLLECTION_SHAPE" in _codes4(spell)''',
         '''def test_phase4_set_collection_parameter_is_a_required_hole() -> None:
    """set[IPlugin] is a caller input: a REQUIRED_HOLE warning, never a collection-shape error."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=NeedsPluginSet, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        _phases_1_4(spell)
        codes = _codes4(spell)
        assert "UNSUPPORTED_COLLECTION_SHAPE" not in codes
        assert "REQUIRED_HOLE" in codes'''),
        ('''def test_phase4_unsupported_dict_collection_shape_errors() -> None:
    """dict[str, IPlugin] is an UNSUPPORTED_COLLECTION_SHAPE error."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=NeedsPluginDict, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        _phases_1_4(spell)
        assert "UNSUPPORTED_COLLECTION_SHAPE" in _codes4(spell)''',
         '''def test_phase4_dict_collection_parameter_is_a_required_hole() -> None:
    """dict[str, IPlugin] is a caller input: a REQUIRED_HOLE warning, never a collection-shape error."""
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(spell=NeedsPluginDict, existence=Existence.unique, permissions="create")
        spell = _get_spell(spellbook, spell_id)
        _phases_1_4(spell)
        codes = _codes4(spell)
        assert "UNSUPPORTED_COLLECTION_SHAPE" not in codes
        assert "REQUIRED_HOLE" in codes'''),
    ])
    errors = "tests/integration/melder/spellbook/test_spellbook_integration_resolution_error_matrix.py"
    edit(root, errors, [
        ("from typing import List, Protocol\n", "from typing import Any, List, Protocol\n"),
        ('''NeedsPluginSet.__init__.__annotations__["plugins"] = set[IPlugin]
''', '''class NeedsAnyMapping:
    def __init__(self, meta: dict) -> None:
        self.meta = meta


NeedsPluginSet.__init__.__annotations__["plugins"] = set[IPlugin]
NeedsAnyMapping.__init__.__annotations__["meta"] = dict[str, Any]
'''),
        ('''def test_conjure_with_unsupported_collection_shape_raises() -> None:
    """A set[IPlugin] DI annotation (UNSUPPORTED_COLLECTION_SHAPE) must block conjure."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=NeedsPluginSet, existence=Existence.unique, permissions="create")
        with pytest.raises(Exception):
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()
''', '''def test_conjure_with_set_collection_parameter_succeeds_and_meld_takes_override() -> None:
    """A set[IPlugin] parameter is a caller input: conjure succeeds and meld passes the supplied set through."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=NeedsPluginSet, existence=Existence.unique, permissions="create")
        conduit = spellbook.conjure(name="root")
        plugins: set = set()
        instance = conduit.meld(spell=NeedsPluginSet, override={"plugins": plugins})
        assert instance.plugins is plugins
    finally:
        spellbook.cleanup()


def test_conjure_with_dict_of_any_parameter_succeeds_and_meld_takes_override() -> None:
    """dict[str, Any] is a caller input (Any is never injected): conjure succeeds and meld passes it through."""
    spellbook = _make_spellbook()
    try:
        spellbook.bind(spell=NeedsAnyMapping, existence=Existence.many, permissions="create")
        conduit = spellbook.conjure(name="root")
        meta = {"key": 1}
        instance = conduit.meld(spell=NeedsAnyMapping, override={"meta": meta})
        assert instance.meta is meta
    finally:
        spellbook.cleanup()
'''),
    ])


def main() -> None:
    """Apply every test edit under the root given on the command line."""
    root = pathlib.Path(sys.argv[1])
    unit_guard(root)
    unit_holes(root)
    component(root)
    integration(root)


if __name__ == "__main__":
    main()
