import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def test_meld_overrides_path_targets_root_params() -> None:
    """
    Purpose:
        Validate path overrides target root constructor parameters.
    Contract:
        - spell_override path keys map onto root constructor parameters.
        - Instance fields reflect the provided override values.
    Returns:
        None.
    Raises:
        AssertionError: If override values are not applied.
    """
    class _Service:
        """
        Purpose:
            Provide a class spell with explicit constructor parameters.
        Contract:
            Stores constructor arguments for assertions.
        """
        def __init__(self, value: int, label: str) -> None:
            """
            Purpose:
                Capture constructor arguments for assertions.
            Contract:
                Stores value and label on the instance.
            Args:
                value: Numeric value passed to the constructor.
                label: String label passed to the constructor.
            Returns:
                None.
            """
            self.value = value
            self.label = label

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(
            spell_id=spell_id,
            override={"value": 7, "label": "dict"},
        )
        assert instance.value == 7
        assert instance.label == "dict"
    finally:
        conduit.cleanup()


def test_meld_overrides_unique_targets_dependency() -> None:
    """
    Purpose:
        Validate unique overrides target a dependency socket by name.
    Contract:
        - spell_override uses "*param" to target a single dependency.
        - Instance receives the overridden dependency object.
    Returns:
        None.
    Raises:
        AssertionError: If positional overrides are not applied.
    """
    class _Dependency:
        """
        Purpose:
            Provide a dependency spell that can be overridden.
        Contract:
            Stores the supplied label for assertions.
        """
        def __init__(self, label: str = "default") -> None:
            """
            Purpose:
                Capture a label for assertions.
            Contract:
                Stores the label on the instance.
            Args:
                label: Label assigned to the dependency.
            Returns:
                None.
            """
            self.label = label

    class _Service:
        """
        Purpose:
            Provide a class spell that depends on a single dependency.
        Contract:
            Stores the dependency instance for assertions.
        """
        def __init__(self, dep: _Dependency) -> None:
            """
            Purpose:
                Capture the dependency for assertions.
            Contract:
                Stores the dependency on the instance.
            Args:
                dep: Dependency resolved by the DI system.
            Returns:
                None.
            """
            self.dep = dep

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Dependency,
        existence=Existence.many,
        permissions="create",
    )
    spell_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        override_dep = _Dependency(label="override")
        instance = conduit.meld(
            spell_id=spell_id,
            override={"*dep": override_dep},
        )
        assert instance.dep is override_dep
    finally:
        conduit.cleanup()


def test_meld_overrides_path_targets_nested_dependency_param() -> None:
    """
    Purpose:
        Validate path overrides can target nested dependency parameters.
    Contract:
        - A path of "dep>label" targets the dependency's label socket.
        - The nested dependency receives the overridden label value.
    Returns:
        None.
    Raises:
        AssertionError: If the nested override does not apply.
    """
    class _Dependency:
        """
        Purpose:
            Provide a dependency spell with a required plain parameter.
        Contract:
            Stores the label supplied to the constructor.
        """
        def __init__(self, label: str) -> None:
            """
            Purpose:
                Capture the label for assertions.
            Contract:
                Stores the label on the instance.
            Args:
                label: Label passed by the override.
            Returns:
                None.
            """
            self.label = label

    class _Service:
        """
        Purpose:
            Provide a service spell that depends on _Dependency.
        Contract:
            Stores the dependency instance for assertions.
        """
        def __init__(self, dep: _Dependency) -> None:
            """
            Purpose:
                Capture the dependency for assertions.
            Contract:
                Stores the dependency on the instance.
            Args:
                dep: Dependency resolved by the DI system.
            Returns:
                None.
            """
            self.dep = dep

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Dependency,
        existence=Existence.many,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(
            spell_id=service_id,
            override={"dep>label": "nested"},
        )
        assert instance.dep.label == "nested"
    finally:
        conduit.cleanup()


def test_meld_overrides_broadcast_targets_multiple_labels() -> None:
    """
    Purpose:
        Validate broadcast overrides apply to all matching socket names.
    Contract:
        - "**label" targets every label socket in the root DAG.
        - Both dependencies receive the broadcast label override.
    Returns:
        None.
    Raises:
        AssertionError: If the broadcast override does not apply.
    """
    class _DepA:
        """
        Purpose:
            Provide a dependency spell with a label parameter.
        Contract:
            Stores the label supplied to the constructor.
        """
        def __init__(self, label: str) -> None:
            """
            Purpose:
                Capture the label for assertions.
            Contract:
                Stores the label on the instance.
            Args:
                label: Label supplied by the override.
            Returns:
                None.
            """
            self.label = label

    class _DepB:
        """
        Purpose:
            Provide a second dependency spell with a label parameter.
        Contract:
            Stores the label supplied to the constructor.
        """
        def __init__(self, label: str) -> None:
            """
            Purpose:
                Capture the label for assertions.
            Contract:
                Stores the label on the instance.
            Args:
                label: Label supplied by the override.
            Returns:
                None.
            """
            self.label = label

    class _Service:
        """
        Purpose:
            Provide a service spell with two labeled dependencies.
        Contract:
            Stores both dependencies for assertions.
        """
        def __init__(self, dep_a: _DepA, dep_b: _DepB) -> None:
            """
            Purpose:
                Capture dependencies for assertions.
            Contract:
                Stores both dependencies on the instance.
            Args:
                dep_a: First dependency instance.
                dep_b: Second dependency instance.
            Returns:
                None.
            """
            self.dep_a = dep_a
            self.dep_b = dep_b

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_DepA,
        existence=Existence.many,
        permissions="create",
    )
    spellbook.bind(
        spell=_DepB,
        existence=Existence.many,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(
            spell_id=service_id,
            override={"**label": "shared"},
        )
        assert instance.dep_a.label == "shared"
        assert instance.dep_b.label == "shared"
    finally:
        conduit.cleanup()


def test_meld_overrides_path_precedes_broadcast_for_root_params() -> None:
    """
    Purpose:
        Validate PATH overrides take precedence over BROADCAST overrides.
    Contract:
        - A root PATH override wins over a broadcast override for that socket.
        - Broadcast continues to apply to other matching sockets.
    Returns:
        None.
    Raises:
        AssertionError: If precedence is not respected.
    """
    class _Dependency:
        """
        Purpose:
            Provide a dependency spell with a label parameter.
        Contract:
            Stores the label supplied to the constructor.
        """
        def __init__(self, label: str) -> None:
            """
            Purpose:
                Capture the label for assertions.
            Contract:
                Stores the label on the instance.
            Args:
                label: Label supplied by the override.
            Returns:
                None.
            """
            self.label = label

    class _Service:
        """
        Purpose:
            Provide a service spell with a root label and a dependency.
        Contract:
            Stores both the root label and the dependency instance.
        """
        def __init__(self, label: str, dep: _Dependency) -> None:
            """
            Purpose:
                Capture the label and dependency for assertions.
            Contract:
                Stores the label and dependency on the instance.
            Args:
                label: Root label assigned to the service.
                dep: Dependency resolved by the DI system.
            Returns:
                None.
            """
            self.label = label
            self.dep = dep

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Dependency,
        existence=Existence.many,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        instance = conduit.meld(
            spell_id=service_id,
            override={
                "**label": "broadcast",
                "label": "root",
            },
        )
        assert instance.label == "root"
        assert instance.dep.label == "broadcast"
    finally:
        conduit.cleanup()


def test_meld_overrides_unique_raises_on_multiple_matches() -> None:
    """
    Purpose:
        Validate unique overrides raise when multiple sockets match.
    Contract:
        - Using "*label" with multiple label sockets raises MeldExecutionError.
    Returns:
        None.
    Raises:
        AssertionError: If the unique override does not raise.
    """
    class _DepA:
        """
        Purpose:
            Provide a dependency spell with a label parameter.
        Contract:
            Stores the label supplied to the constructor.
        """
        def __init__(self, label: str) -> None:
            """
            Purpose:
                Capture the label for assertions.
            Contract:
                Stores the label on the instance.
            Args:
                label: Label supplied by the constructor.
            Returns:
                None.
            """
            self.label = label

    class _DepB:
        """
        Purpose:
            Provide a second dependency spell with a label parameter.
        Contract:
            Stores the label supplied to the constructor.
        """
        def __init__(self, label: str) -> None:
            """
            Purpose:
                Capture the label for assertions.
            Contract:
                Stores the label on the instance.
            Args:
                label: Label supplied by the constructor.
            Returns:
                None.
            """
            self.label = label

    class _Service:
        """
        Purpose:
            Provide a service spell with two labeled dependencies.
        Contract:
            Stores both dependencies for assertions.
        """
        def __init__(self, dep_a: _DepA, dep_b: _DepB) -> None:
            """
            Purpose:
                Capture dependencies for assertions.
            Contract:
                Stores both dependencies on the instance.
            Args:
                dep_a: First dependency instance.
                dep_b: Second dependency instance.
            Returns:
                None.
            """
            self.dep_a = dep_a
            self.dep_b = dep_b

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_DepA,
        existence=Existence.many,
        permissions="create",
    )
    spellbook.bind(
        spell=_DepB,
        existence=Existence.many,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        with pytest.raises(
            MeldExecutionError,
            match=r"Unique override '\*label' matched 2 sockets; expected exactly one\.",
        ):
            conduit.meld(
                spell_id=service_id,
                override={"*label": "override"},
            )
    finally:
        conduit.cleanup()


def test_meld_overrides_broadcast_raises_when_missing_param() -> None:
    """
    Purpose:
        Validate broadcast overrides raise when no sockets match.
    Contract:
        - Using "**missing" without a matching socket raises MeldExecutionError.
    Returns:
        None.
    Raises:
        AssertionError: If the broadcast override does not raise.
    """
    class _Dependency:
        """
        Purpose:
            Provide a dependency spell without a matching socket.
        Contract:
            Stores a stable marker for assertions.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the dependency marker.
            Contract:
                Sets marker to "dep".
            Returns:
                None.
            """
            self.marker = "dep"

    class _Service:
        """
        Purpose:
            Provide a service spell that depends on _Dependency.
        Contract:
            Stores the dependency instance for assertions.
        """
        def __init__(self, dep: _Dependency) -> None:
            """
            Purpose:
                Capture the dependency for assertions.
            Contract:
                Stores the dependency on the instance.
            Args:
                dep: Dependency resolved by the DI system.
            Returns:
                None.
            """
            self.dep = dep

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(
        spell=_Dependency,
        existence=Existence.many,
        permissions="create",
    )
    service_id = spellbook.bind(
        spell=_Service,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        with pytest.raises(
            MeldExecutionError,
            match=r"No sockets found for broadcast override '\*\*missing'\.",
        ):
            conduit.meld(
                spell_id=service_id,
                override={"**missing": "value"},
            )
    finally:
        conduit.cleanup()
