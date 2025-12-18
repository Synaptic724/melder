import inspect

from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.spell_examiner.profiles.resolution_profile import (
    SpellResolutionFrame,
    SpellResolutionProfile,
    SpellSymbolicEdge,
    SpellSymbolicGraph,
    SpellSymbolicNode,
    SpellValidationIssue,
    SpellValidationResult,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_parameter_requirements import (
    SpellParameterRequirement,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.spellbook.spell_types.spell_types import SpellType


def test_spell_index_identity_and_versions():
    idx = SpellIndex("v1")
    initial_id = idx.id
    assert idx.current == "v1"
    idx.update("v2")
    idx.update("v3")
    assert idx.current == "v3"
    assert idx.has_version("v1")
    assert idx.has_version("v2")
    assert idx.has_version("v3")
    assert idx.get_all_versions() == {"v1", "v2", "v3"}
    assert hash(idx) == hash(idx)  # stable hash
    assert idx == idx
    # inequality on id
    other = SpellIndex("other")
    assert idx != other
    assert idx.id == initial_id


def test_spell_index_cleanup_idempotent_and_nulls():
    idx = SpellIndex("v1")
    idx.cleanup()
    assert idx._cleaned is True
    assert idx._current_id is None
    assert idx._versions is None
    assert idx._lock is None
    idx.cleanup()  # no-op


def _param_req(di_shape: ParameterDIShape, has_default: bool = False, optional: bool = False):
    return SpellParameterRequirement(
        name="p",
        position=0,
        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=int,
        default_value=None if not has_default else 1,
        has_default=has_default,
        is_var_positional=False,
        is_var_keyword=False,
        is_keyword_only=False,
        is_optional=optional,
        di_shape=di_shape,
        collection_element_annotation=None,
        spellmap_default=None,
    )


def test_spell_requirements_iterators_and_holes():
    params = [
        _param_req(ParameterDIShape.PLAIN, has_default=False),  # required hole
        _param_req(ParameterDIShape.PLAIN, has_default=True),
        _param_req(ParameterDIShape.SINGLE_BY_ANNOTATION),
        _param_req(ParameterDIShape.COLLECTION_BY_ANNOTATION),
        _param_req(ParameterDIShape.SPELLMAP_DEFAULT),
    ]
    reqs = SpellRequirements(
        spell_id="spell",
        spell_type=SpellType.SPELL,
        existence=Existence.unique,
        spellframe="frame",
        binding_name="bind",
        parameters=params,
    )

    assert list(reqs.iter_di_parameters()) == params[2:]
    assert list(reqs.iter_plain_parameters()) == params[:2]
    required = list(reqs.iter_required_holes())
    assert required == [params[0]]
    assert reqs.has_required_holes() is True
    assert reqs.spell_id == "spell"
    assert reqs.spell_type is SpellType.SPELL
    assert reqs.existence is Existence.unique
    assert reqs.spellframe == "frame"
    assert reqs.binding_name == "bind"
    assert reqs.parameters == tuple(params)


def test_spell_requirements_cleanup_cascades():
    params = [_param_req(ParameterDIShape.PLAIN)]
    reqs = SpellRequirements(
        spell_id="spell",
        spell_type=SpellType.SPELL,
        existence=Existence.unique,
        spellframe=None,
        binding_name=None,
        parameters=params,
    )
    reqs.cleanup()
    assert reqs._cleaned is True
    assert reqs._parameters == []
    assert params[0]._cleaned is True
    assert reqs._spell_id is None
    assert reqs._lock is None


def test_spell_parameter_requirement_properties_and_cleanup():
    param = _param_req(ParameterDIShape.SINGLE_BY_ANNOTATION, has_default=True, optional=True)
    assert param.name == "p"
    assert param.position == 0
    assert param.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert param.annotation is int
    assert param.default_value == 1
    assert param.has_default is True
    assert param.is_optional is True
    assert param.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    param.cleanup()
    assert param._cleaned is True
    assert param._name is None
    assert param._lock is None


def test_symbolic_node_and_edge_cleanup():
    node = SpellSymbolicNode("n1", "kind", {"k": "v"})
    edge = SpellSymbolicEdge("a", "b", "p")
    node.cleanup()
    edge.cleanup()
    assert node._cleaned is True
    assert node.metadata is None
    assert edge.from_node is None
    assert edge.to_node is None
    assert edge.via_parameter is None


def test_symbolic_graph_cleanup_cleans_children():
    nodes = [SpellSymbolicNode("n1", "kind"), SpellSymbolicNode("n2", "kind")]
    edges = [SpellSymbolicEdge("n1", "n2")]
    graph = SpellSymbolicGraph("spell", nodes=nodes, edges=edges)
    graph.cleanup()
    assert graph._cleaned is True
    assert graph.nodes is None
    assert graph.edges is None
    assert nodes[0]._cleaned is True
    assert edges[0]._cleaned is True


def test_resolution_frame_cleanup():
    frame = SpellResolutionFrame("spell", ["a", "b"])
    frame.cleanup()
    assert frame._cleaned is True
    assert frame.ordered_node_ids is None
    assert frame.spell_id is None


def test_validation_issue_and_result_cleanup():
    issue = SpellValidationIssue("E1", "msg", {"k": "v"})
    warning = SpellValidationIssue("W1", "warn")
    result = SpellValidationResult(
        is_valid=False,
        errors=[issue],
        warnings=[warning],
    )
    result.cleanup()
    assert result._cleaned is True
    assert result.errors is None
    assert result.warnings is None
    assert issue._cleaned is True
    assert warning._cleaned is True


def test_resolution_profile_cleanup_cascades_children():
    requirements = SpellRequirements(
        spell_id="s",
        spell_type=SpellType.SPELL,
        existence=Existence.unique,
        spellframe=None,
        binding_name=None,
        parameters=[],
    )
    graph = SpellSymbolicGraph("s")
    frame = SpellResolutionFrame("s")
    validation = SpellValidationResult(is_valid=True)
    profile = SpellResolutionProfile(
        spell_id="s",
        existence=Existence.unique,
        spellframe=None,
        binding_name=None,
        requirements=requirements,
        symbolic_graph=graph,
        resolution_frame=frame,
        validation=validation,
    )
    profile.cleanup()
    for part in (requirements, graph, frame, validation):
        assert part._cleaned is True
    assert profile.spell_id is None
    assert profile.binding_name is None
    assert profile._cleaned is True
