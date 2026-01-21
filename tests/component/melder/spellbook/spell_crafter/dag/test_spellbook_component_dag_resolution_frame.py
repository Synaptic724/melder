import threading

import pytest

from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.resolution_frame.resolution_frame import (
    ResolutionFrame,
)


def test_component_resolution_frame_tracks_results_through_dag_execution() -> None:
    """
    Purpose:
        Validate ResolutionFrame stores results produced by DAG tasks.
    Contract:
        - Dependency tasks run before dependents.
        - Results are stored under node ids after execution.
    Returns:
        None.
    """
    frame = ResolutionFrame({"dep": "override"})
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency(parent_key="dep", child_key="root")

    execution_order: list[str] = []

    def dep_task() -> None:
        """
        Purpose:
            Register the dependency result.
        Contract:
            - Uses the override value if present.
        Returns:
            None.
        """
        execution_order.append("dep")
        value = frame.get_override("dep") if frame.has_override("dep") else "default"
        frame.set_result("dep", value)

    def root_task() -> None:
        """
        Purpose:
            Register the root result based on the dependency.
        Contract:
            - Reads dependency result from the frame.
        Returns:
            None.
        """
        execution_order.append("root")
        dep_value = frame.get_result("dep")
        frame.set_result("root", f"root:{dep_value}")

    dep_node = dag.get_node("dep")
    root_node = dag.get_node("root")
    assert dep_node is not None
    assert root_node is not None

    dep_node.add_task(dep_task)
    root_node.add_task(root_task)

    dag.execute()

    assert execution_order == ["dep", "root"]
    assert frame.get_result("dep") == "override"
    assert frame.get_result("root") == "root:override"


def test_component_resolution_frame_records_errors_alongside_results() -> None:
    """
    Purpose:
        Validate ResolutionFrame retains errors and results in a shared run.
    Contract:
        - Errors registered by one node are preserved.
        - Other nodes can still store results.
    Returns:
        None.
    """
    frame = ResolutionFrame()
    dag = DirectedAcyclicWorkGraph()
    dag.add_node("alpha")
    dag.add_node("beta")

    def alpha_task() -> None:
        """
        Purpose:
            Record an error for the alpha node.
        Contract:
            - Error is stored without raising.
        Returns:
            None.
        """
        frame.register_error("alpha", RuntimeError("alpha failed"))

    def beta_task() -> None:
        """
        Purpose:
            Record a successful result for the beta node.
        Contract:
            - Result is stored on the frame.
        Returns:
            None.
        """
        frame.set_result("beta", "ok")

    alpha_node = dag.get_node("alpha")
    beta_node = dag.get_node("beta")
    assert alpha_node is not None
    assert beta_node is not None

    alpha_node.add_task(alpha_task)
    beta_node.add_task(beta_task)

    dag.execute()

    assert frame.get_error("alpha") is not None
    assert frame.get_result("beta") == "ok"


def test_component_resolution_frame_validates_inputs() -> None:
    """
    Purpose:
        Validate ResolutionFrame enforces basic input validation.
    Contract:
        - Empty node ids raise ValueError.
        - None error payloads raise ValueError.
    Returns:
        None.
    """
    frame = ResolutionFrame()

    with pytest.raises(ValueError):
        frame.set_result("", "value")
    with pytest.raises(ValueError):
        frame.register_error("node", None)  # type: ignore[arg-type]


def test_component_resolution_frame_cleanup_blocks_access() -> None:
    """
    Purpose:
        Validate cleanup prevents further access to frame state.
    Contract:
        - Accessing properties after cleanup raises RuntimeError.
    Returns:
        None.
    """
    frame = ResolutionFrame({"root": "override"})
    frame.cleanup()

    with pytest.raises(RuntimeError):
        _ = frame.overrides
    with pytest.raises(RuntimeError):
        _ = frame.results
    with pytest.raises(RuntimeError):
        _ = frame.errors


def test_component_resolution_frame_handles_concurrent_writes() -> None:
    """
    Purpose:
        Validate ResolutionFrame supports concurrent result writes.
    Contract:
        - All threaded writes are recorded without errors.
    Returns:
        None.
    """
    frame = ResolutionFrame()
    total = 25
    errors: list[BaseException] = []

    def worker(idx: int) -> None:
        try:
            frame.set_result(f"node-{idx}", f"value-{idx}")
        except BaseException as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(total)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors
    results = frame.results
    assert len(results) == total
    assert results["node-0"] == "value-0"
