import pytest

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
from melder.utilities.general_base.cleanable import Cleanable


class _CleanableStub(Cleanable):
    __slots__ = Cleanable.__slots__ + ["cleaned_calls"]

    def __init__(self):
        super().__init__()
        self.cleaned_calls = 0

    def cleanup(self):
        if self._cleaned:
            return
        self.cleaned_calls += 1
        self._cleaned = True


class _Boom(Cleanable):
    __slots__ = Cleanable.__slots__

    def cleanup(self):
        raise RuntimeError("boom")


def test_symbolic_node_stores_and_cleans():
    node = SpellSymbolicNode("id", "kind", {"a": 1})
    assert node.node_id == "id"
    assert node.kind == "kind"
    assert node.metadata == {"a": 1}
    node.cleanup()
    assert node.metadata is None
    assert node.cleaned is True
    node.cleanup()  # idempotent


def test_symbolic_node_detaches_metadata_input():
    metadata = {"a": 1}
    node = SpellSymbolicNode("id", "kind", metadata)

    metadata["a"] = 2

    assert node.metadata == {"a": 1}


def test_symbolic_edge_stores_and_cleans():
    edge = SpellSymbolicEdge("from", "to", "param")
    assert edge.from_node == "from"
    edge.cleanup()
    assert edge.from_node is None
    assert edge.cleaned is True
    edge.cleanup()


def test_symbolic_graph_copies_inputs_and_cleans_children():
    n1, n2 = _CleanableStub(), _CleanableStub()
    e1 = _CleanableStub()
    graph = SpellSymbolicGraph("sid", nodes=[n1, n2], edges=[e1])
    assert graph.nodes is not None and len(graph.nodes) == 2
    assert graph.edges is not None and len(graph.edges) == 1
    graph.cleanup()
    assert (getattr(n1, "cleaned", False) or n1.cleaned_calls > 0)
    assert (getattr(n2, "cleaned", False) or n2.cleaned_calls > 0)
    assert (getattr(e1, "cleaned", False) or e1.cleaned_calls > 0)
    assert graph.nodes is None and graph.edges is None and graph.spell_id is None


def test_symbolic_graph_cleanup_swallows_errors():
    bad = _Boom()
    graph = SpellSymbolicGraph("sid", nodes=[bad], edges=[bad])
    graph.cleanup()
    assert graph.cleaned is True
    graph.cleanup()


def test_resolution_frame_copies_and_cleans():
    frame = SpellResolutionFrame("sid", ordered_node_ids=["a", "b"])
    assert frame.ordered_node_ids == ["a", "b"]
    frame.cleanup()
    assert frame.ordered_node_ids is None
    assert frame.spell_id is None
    frame.cleanup()


def test_validation_issue_cleanup():
    issue = SpellValidationIssue("code", "msg", {"d": 1})
    assert issue.code == "code"
    issue.cleanup()
    assert issue.details is None
    assert issue.code is None
    issue.cleanup()


def test_validation_issue_detaches_details_input():
    details = {"d": 1}
    issue = SpellValidationIssue("code", "msg", details)

    details["d"] = 2

    assert issue.details == {"d": 1}


def test_validation_result_cleanup_cascades():
    err = _CleanableStub()
    warn = _CleanableStub()
    result = SpellValidationResult(is_valid=False, errors=[err], warnings=[warn])
    result.cleanup()
    assert (getattr(err, "cleaned", False) or err.cleaned_calls > 0)
    assert (getattr(warn, "cleaned", False) or warn.cleaned_calls > 0)
    assert result.errors is None and result.warnings is None
    result.cleanup()


def test_validation_result_cleanup_swallows_child_errors():
    result = SpellValidationResult(
        is_valid=False,
        errors=[_Boom()],
        warnings=[_Boom()],
    )

    result.cleanup()

    assert result.cleaned is True
    assert result.errors is None
    assert result.warnings is None


def test_resolution_profile_fields_and_cleanup():
    reqs = _CleanableStub()
    sym = _CleanableStub()
    frame = _CleanableStub()
    val = _CleanableStub()
    profile = SpellResolutionProfile(
        spell_id="sid",
        existence=Existence.unique,
        spellframe="frame",
        binding_name="bind",
        requirements=reqs,
        symbolic_graph=sym,
        resolution_frame=frame,
        validation=val,
    )
    assert profile.spell_id == "sid"
    assert profile.existence is Existence.unique
    assert profile.binding_name == "bind"
    profile.cleanup()
    for stub in (reqs, sym, frame, val):
        assert getattr(stub, "cleaned", False) or stub.cleaned_calls > 0
    assert profile.requirements is None
    assert profile.symbolic_graph is None
    assert profile.resolution_frame is None
    assert profile.validation is None
    assert profile.spell_id is None
    profile.cleanup()


def test_resolution_profile_cleanup_swallows_child_errors():
    profile = SpellResolutionProfile(
        spell_id="sid",
        existence=Existence.unique,
        spellframe=None,
        binding_name=None,
        requirements=_Boom(),
        symbolic_graph=_Boom(),
        resolution_frame=_Boom(),
        validation=_Boom(),
    )
    profile.cleanup()
    assert profile.cleaned is True
