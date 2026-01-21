import pytest

from melder.spellbook.spell_crafter.dag.dag_node import DagNode


def test_add_dependency_records_both_directions_and_params():
    parent = DagNode("parent")
    child = DagNode("child")

    child.add_dependency(parent, param_name="repo")

    assert parent in child.dependencies
    assert child in parent.dependents
    assert child in parent.children_by_param["repo"]
    assert child.incoming_params[parent] == "repo"


def test_add_dependency_rejects_self_and_conflicting_param():
    node = DagNode("n")
    with pytest.raises(ValueError):
        node.add_dependency(node)

    parent = DagNode("p")
    node.add_dependency(parent, param_name="first")
    # Second registration is ignored (idempotent) rather than erroring
    node.add_dependency(parent, param_name="second")
    assert node.incoming_params[parent] == "first"


def test_tasks_validate_and_run_in_order():
    node = DagNode("n")
    calls = []
    node.add_task(lambda: calls.append("a"))
    node.add_task(lambda: calls.append("b"))
    node.run_tasks()
    assert calls == ["a", "b"]
    with pytest.raises(TypeError):
        node.add_task("not-callable")  # type: ignore[arg-type]


def test_cleanup_clears_graph_and_blocks_mutation():
    parent = DagNode("p")
    child = DagNode("c")
    child.add_dependency(parent, param_name="x")
    child.add_task(lambda: None)

    child.cleanup()
    assert child.dependencies == set()
    assert child.dependents == set()
    assert child.children_by_param == {}
    assert child.incoming_params == {}
    child.cleanup()  # idempotent

    with pytest.raises(RuntimeError):
        child.payload = object()


def test_add_dependency_without_param_updates_sets_only():
    parent = DagNode("p")
    child = DagNode("c")
    child.add_dependency(parent)

    assert child in parent.dependents
    assert parent in child.dependencies
    assert parent.children_by_param == {}
    assert child.incoming_params == {}


def test_add_dependency_duplicate_same_param_keeps_single_edge():
    parent = DagNode("p")
    child = DagNode("c")
    child.add_dependency(parent, param_name="repo")
    child.add_dependency(parent, param_name="repo")

    assert len(child.dependencies) == 1
    assert len(parent.dependents) == 1
    assert parent.children_by_param["repo"] == {child}


def test_add_dependency_multiple_parents_track_incoming_params():
    p1 = DagNode("p1")
    p2 = DagNode("p2")
    child = DagNode("c")

    child.add_dependency(p1, param_name="alpha")
    child.add_dependency(p2, param_name="beta")

    assert child.incoming_params[p1] == "alpha"
    assert child.incoming_params[p2] == "beta"
    assert child in p1.children_by_param["alpha"]
    assert child in p2.children_by_param["beta"]


def test_children_by_param_multiple_children_same_param():
    parent = DagNode("parent")
    c1 = DagNode("c1")
    c2 = DagNode("c2")

    c1.add_dependency(parent, param_name="svc")
    c2.add_dependency(parent, param_name="svc")

    assert parent.children_by_param["svc"] == {c1, c2}


def test_children_by_param_different_params_isolated_sets():
    parent = DagNode("parent")
    c1 = DagNode("c1")
    c2 = DagNode("c2")

    c1.add_dependency(parent, param_name="a")
    c2.add_dependency(parent, param_name="b")

    assert parent.children_by_param["a"] == {c1}
    assert parent.children_by_param["b"] == {c2}


def test_add_dependency_after_cleanup_raises():
    node = DagNode("n")
    node.cleanup()
    with pytest.raises(RuntimeError):
        node.add_dependency(DagNode("other"))


def test_add_task_after_cleanup_raises():
    node = DagNode("n")
    node.cleanup()
    with pytest.raises(RuntimeError):
        node.add_task(lambda: None)


def test_run_tasks_after_cleanup_raises():
    node = DagNode("n")
    node.add_task(lambda: None)
    node.cleanup()
    with pytest.raises(RuntimeError):
        node.run_tasks()


def test_run_tasks_propagates_exception():
    node = DagNode("n")

    def boom():
        raise RuntimeError("fail")

    node.add_task(lambda: None)
    node.add_task(boom)
    with pytest.raises(RuntimeError):
        node.run_tasks()


def test_payload_property_round_trip():
    node = DagNode("n")
    obj = object()
    node.payload = obj
    assert node.payload is obj


def test_payload_set_after_cleanup_raises():
    node = DagNode("n")
    node.cleanup()
    with pytest.raises(RuntimeError):
        node.payload = "x"


def test_dependencies_and_dependents_are_live_sets():
    a = DagNode("a")
    b = DagNode("b")
    b.add_dependency(a)
    a.dependencies.add(DagNode("extra"))
    assert any(n.id == "extra" for n in a.dependencies)


def test_repr_contains_id_and_counts():
    a = DagNode("a")
    b = DagNode("b")
    b.add_dependency(a)
    text = repr(b)
    assert "b" in text and "deps=1" in text and "dependents=0" in text


def test_cleanup_removes_edges_from_neighbors():
    a = DagNode("a")
    b = DagNode("b")
    c = DagNode("c")
    b.add_dependency(a, param_name="x")
    c.add_dependency(b, param_name="y")

    b.cleanup()

    assert b not in a.dependents
    assert b not in c.dependencies
    assert b.children_by_param == {}
    assert b.incoming_params == {}


def test_cleanup_is_idempotent_with_neighbors():
    a = DagNode("a")
    b = DagNode("b")
    b.add_dependency(a, param_name="x")
    b.cleanup()
    b.cleanup()  # second call no-op
    assert b.cleaned


def test_check_cleaned_raises_when_cleaned():
    node = DagNode("n")
    node.cleanup()
    with pytest.raises(RuntimeError):
        node.check_cleaned()


def test_add_dependency_conflict_detected_on_child():
    parent = DagNode("p")
    child = DagNode("c")
    child.add_dependency(parent, param_name="one")
    # Duplicate registration keeps original mapping
    child.add_dependency(parent, param_name="two")
    assert child.incoming_params[parent] == "one"


def test_add_dependency_reusing_parent_same_param_no_error():
    parent = DagNode("p")
    child = DagNode("c")
    child.add_dependency(parent, param_name="one")
    child.add_dependency(parent, param_name="one")
    assert child.incoming_params[parent] == "one"


def test_add_dependency_rejects_self_reference():
    node = DagNode("n")
    with pytest.raises(ValueError):
        node.add_dependency(node)


def test_add_dependency_multiple_layers_preserve_sets():
    root = DagNode("root")
    mid = DagNode("mid")
    leaf = DagNode("leaf")

    mid.add_dependency(root, param_name="mid_param")
    leaf.add_dependency(mid, param_name="leaf_param")

    assert root in mid.dependencies
    assert mid in leaf.dependencies
    assert mid in root.dependents
    assert leaf in mid.dependents


def test_incoming_params_records_each_parent_only_once():
    p = DagNode("p")
    c = DagNode("c")
    c.add_dependency(p, param_name="a")
    c.add_dependency(p, param_name="a")
    assert list(c.incoming_params.keys()) == [p]


def test_children_by_param_not_created_when_param_none():
    p = DagNode("p")
    c = DagNode("c")
    c.add_dependency(p, param_name=None)
    assert p.children_by_param == {}


def test_run_tasks_no_tasks_is_noop():
    node = DagNode("n")
    node.run_tasks()


def test_add_task_validates_callable_type():
    node = DagNode("n")
    with pytest.raises(TypeError):
        node.add_task(123)  # type: ignore[arg-type]


def test_dependents_and_dependencies_sets_are_same_objects():
    a = DagNode("a")
    b = DagNode("b")
    b.add_dependency(a)
    # Mutate via property and see effect locally on the child's set
    b.dependencies.clear()
    assert a not in b.dependencies
    # Parent dependents are not auto-synchronized by raw set mutation
    assert b in a.dependents
