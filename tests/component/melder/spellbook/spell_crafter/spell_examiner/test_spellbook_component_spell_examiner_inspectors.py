from melder.spellbook.spell_crafter.spell_examiner.inspectors.class_inspector import (
    ClassInspector,
)
from melder.spellbook.spell_crafter.spell_examiner.inspectors.inspector_utility import (
    InspectorUtility,
)
from melder.spellbook.spell_crafter.spell_examiner.inspectors.method_inspector import (
    MethodInspector,
)


def test_component_inspector_utility_safe_repr_truncates_long_payload() -> None:
    """
    Purpose:
        Validate safe_repr truncates large representations.
    Contract:
        - The representation is shortened.
        - The original length marker is included.
    Returns:
        None.
    """
    payload = "x" * 200
    result = InspectorUtility.safe_repr(payload, max_len=40)
    assert result != repr(payload)
    assert "... (len " in result
    assert result.startswith("'x")


def test_component_inspector_utility_safe_repr_handles_repr_failure() -> None:
    """
    Purpose:
        Validate safe_repr handles repr failures gracefully.
    Contract:
        - An error-safe placeholder is returned.
    Returns:
        None.
    """

    class Boom:
        def __repr__(self) -> str:
            raise RuntimeError("boom")

    result = InspectorUtility.safe_repr(Boom(), max_len=30)
    assert result == "<unrepr-able Boom>"


def test_component_inspector_utility_unwraps_closure_decorators() -> None:
    """
    Purpose:
        Validate unwrap_callable finds closure-wrapped originals.
    Contract:
        - The returned callable is the original target.
    Returns:
        None.
    """
    def decorator(fn):
        def inner(*args, **kwargs):
            return fn(*args, **kwargs)

        return inner

    @decorator
    def target(value: int) -> int:
        return value + 1

    unwrapped = InspectorUtility.unwrap_callable(target)
    assert unwrapped is not target
    assert unwrapped(1) == 2


def test_component_class_inspector_tracks_members_and_protocols() -> None:
    """
    Purpose:
        Validate ClassInspector captures members and protocol flags.
    Contract:
        - Non-dunder members are present when show_dunders is False.
        - Protocol flags reflect dunder availability.
    Returns:
        None.
    """

    class Gadget:
        label = "gizmo"

        def __init__(self, value: int) -> None:
            self.value = value

        def __len__(self) -> int:
            return 1

        def ping(self, count: int = 1) -> str:
            return f"pong:{count}"

        @property
        def status(self) -> str:
            return "ok"

    data = ClassInspector(Gadget, show_dunders=False).inspect()
    members = data["members"]

    assert "ping" in members
    assert "status" in members
    assert members["status"]["property"] is True
    assert members["label"]["callable"] is False
    assert "__len__" not in members
    assert data["protocols"]["len"] is True


def test_component_class_inspector_includes_dunders_when_enabled() -> None:
    """
    Purpose:
        Validate ClassInspector includes dunders when requested.
    Contract:
        - Dunder methods appear when show_dunders is True.
    Returns:
        None.
    """

    class Gadget:
        def __init__(self, value: int) -> None:
            self.value = value

        def __len__(self) -> int:
            return 1

    members = ClassInspector(Gadget, show_dunders=True).inspect()["members"]
    assert "__init__" in members
    assert "__len__" in members
    assert members["__init__"]["signature"].startswith("(self")


def test_component_method_inspector_unwraps_decorated_signature() -> None:
    """
    Purpose:
        Validate MethodInspector reports original signatures for wrapped callables.
    Contract:
        - Signature includes the original parameter names.
        - Decoration metadata is recorded for the wrapper.
    Returns:
        None.
    """
    def decorator(fn):
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    @decorator
    def compute(x: int, y: int = 3) -> int:
        return x + y

    data = MethodInspector(compute).inspect()
    assert data["decorated"] is True
    assert data["signature"] is not None
    assert "x" in data["signature"]
    assert "y" in data["signature"]
    assert "*args" not in data["signature"]
    assert data["wrapped_repr"] is not None
