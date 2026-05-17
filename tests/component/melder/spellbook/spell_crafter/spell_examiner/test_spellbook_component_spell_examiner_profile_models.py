import inspect

from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.spell_examiner.inspectors.profiles.class_profile import (
    ClassProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.inspectors.profiles.method_profile import (
    MethodProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.profiles.detailed_profile import (
    SpellDetailedProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import (
    SpellBindingKind,
    SpellBindingProfile,
)
from melder.spellbook.spell_crafter.profiles.resolution_profile import (
    SpellResolutionFrame,
    SpellResolutionProfile,
    SpellSymbolicEdge,
    SpellSymbolicGraph,
    SpellSymbolicNode,
    SpellValidationIssue,
    SpellValidationResult,
)
from melder.spellbook.spell_crafter.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.spellbook.spell_crafter.spell_requirements_finder.spell_parameter_requirements import (
    SpellParameterRequirement,
)
from melder.spellbook.spell_crafter.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.spellbook.spell_types.spell_types import SpellType


def _make_requirement(name: str = "dep") -> SpellParameterRequirement:
    return SpellParameterRequirement(
        name=name,
        position=0,
        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=str,
        default_value=None,
        has_default=False,
        is_var_positional=False,
        is_var_keyword=False,
        is_keyword_only=False,
        is_optional=False,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
    )


def test_component_method_profile_cleanup_clears_fields() -> None:
    """
    Purpose:
        Validate MethodProfile cleanup clears state.
    Contract:
        - Collection fields are cleared and nulled.
        - Basic attributes are set to None.
    Returns:
        None.
    """
    profile = MethodProfile(
        name="do_work",
        qualname="Worker.do_work",
        module="tests.component",
        id=101,
        type="function",
        repr="repr",
        builtin_mod=False,
        extension_mod=False,
        signature="(value)",
        parameters=[
            {
                "name": "value",
                "kind": "POSITIONAL_OR_KEYWORD",
                "default": None,
                "annotation": None,
            }
        ],
        closure=["payload"],
        decorated=True,
        wrapped_repr="<wrapper>",
    )

    profile.cleanup()

    assert profile.cleaned is True
    assert profile.name is None
    assert profile.parameters is None
    assert profile.closure is None


def test_component_class_profile_cleanup_cascades_method_profiles() -> None:
    """
    Purpose:
        Validate ClassProfile cleanup cascades to method profiles.
    Contract:
        - Nested MethodProfile instances are cleaned.
        - ClassProfile attributes are nulled.
    Returns:
        None.
    """
    method_profile = MethodProfile(
        name="run",
        qualname="Worker.run",
        module="tests.component",
        id=202,
        type="function",
        repr="repr",
        builtin_mod=False,
        extension_mod=False,
    )
    profile = ClassProfile(
        name="Worker",
        qualname="Worker",
        module="tests.component",
        methods={"run": method_profile},
    )

    profile.cleanup()

    assert method_profile.cleaned is True
    assert method_profile.name is None
    assert profile.cleaned is True
    assert profile.methods is None
    assert profile.name is None


def test_component_spell_validation_result_cleanup_cascades_issues() -> None:
    """
    Purpose:
        Validate SpellValidationResult cleanup clears nested issues.
    Contract:
        - Issues are cleaned and containers are nulled.
    Returns:
        None.
    """
    error = SpellValidationIssue(
        code="missing_node",
        message="Node missing",
        details={"node": "A"},
    )
    warning = SpellValidationIssue(
        code="warn",
        message="Warning",
        details={"note": "check"},
    )
    result = SpellValidationResult(
        is_valid=False,
        errors=[error],
        warnings=[warning],
    )

    result.cleanup()

    assert result.cleaned is True
    assert result.errors is None
    assert result.warnings is None
    assert error.cleaned is True
    assert error.details is None
    assert warning.cleaned is True


def test_component_spell_symbolic_graph_cleanup_cascades_nodes_and_edges() -> None:
    """
    Purpose:
        Validate SpellSymbolicGraph cleanup cascades to nodes and edges.
    Contract:
        - Nodes and edges are cleaned and cleared.
    Returns:
        None.
    """
    node = SpellSymbolicNode("node-1", "root", metadata={"role": "root"})
    edge = SpellSymbolicEdge("node-1", "node-2", via_parameter="dep")
    graph = SpellSymbolicGraph(
        "spell-1",
        nodes=[node],
        edges=[edge],
    )

    graph.cleanup()

    assert graph.cleaned is True
    assert graph.nodes is None
    assert graph.edges is None
    assert node.cleaned is True
    assert edge.cleaned is True


def test_component_spell_resolution_profile_cleanup_cascades_requirements() -> None:
    """
    Purpose:
        Validate SpellResolutionProfile cleanup cascades to phase artifacts.
    Contract:
        - Requirements, graphs, frames, and validation results are cleaned.
    Returns:
        None.
    """
    requirement = _make_requirement()
    requirements = SpellRequirements(
        spell_id="spell-1",
        spell_type=SpellType.SPELL,
        existence=Existence.unique,
        spellframe=None,
        binding_name=None,
        parameters=[requirement],
    )
    graph = SpellSymbolicGraph(
        "spell-1",
        nodes=[SpellSymbolicNode("node-1", "root")],
        edges=[],
    )
    frame = SpellResolutionFrame("spell-1", ordered_node_ids=["node-1"])
    validation = SpellValidationResult(
        is_valid=False,
        errors=[SpellValidationIssue(code="err", message="bad")],
        warnings=[],
    )
    profile = SpellResolutionProfile(
        spell_id="spell-1",
        existence=Existence.unique,
        spellframe=None,
        binding_name=None,
        requirements=requirements,
        symbolic_graph=graph,
        resolution_frame=frame,
        validation=validation,
    )

    profile.cleanup()

    assert profile.cleaned is True
    assert profile.spell_id is None
    assert requirements.cleaned is True
    assert requirement.cleaned is True
    assert graph.cleaned is True
    assert frame.cleaned is True
    assert validation.cleaned is True


def test_component_spell_ai_profile_cleanup_cascades_profiles() -> None:
    """
    Purpose:
        Validate SpellDetailedProfile cleanup cascades to linked profiles.
    Contract:
        - Binding, resolution, and class profiles are cleaned.
        - Metadata is cleared.
    Returns:
        None.
    """
    binding_profile = SpellBindingProfile(
        kind=SpellBindingKind.CLASS,
        original_object=object(),
    )
    requirements = SpellRequirements(
        spell_id="spell-2",
        spell_type=SpellType.SPELL,
        existence=Existence.unique,
        spellframe=None,
        binding_name=None,
        parameters=[_make_requirement("service")],
    )
    resolution_profile = SpellResolutionProfile(
        spell_id="spell-2",
        existence=Existence.unique,
        spellframe=None,
        binding_name=None,
        requirements=requirements,
    )
    class_profile = ClassProfile(
        name="Worker",
        qualname="Worker",
        module="tests.component",
    )
    profile = SpellDetailedProfile(
        binding_profile=binding_profile,
        resolution_profile=resolution_profile,
        class_profile=class_profile,
        metadata={"role": "demo"},
    )

    profile.cleanup()

    assert profile.cleaned is True
    assert binding_profile.cleaned is True
    assert resolution_profile.cleaned is True
    assert class_profile.cleaned is True
    assert profile.metadata is None

