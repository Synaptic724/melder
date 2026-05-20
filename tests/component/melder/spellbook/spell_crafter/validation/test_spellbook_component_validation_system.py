import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.validation.validation_system import SpellValidationSystem
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.operation_cancelled_error import OperationCancelledError
from melder.utilities.synchronization.cancellation_event_signal import CancellationEventSignal


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_validation_system() -> None:
    """
    Purpose:
        Ensure component validation system tests start with a clean Aether singleton.
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


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for validation system component tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str) -> object | None:
    """
    Purpose:
        Resolve a local Spell instance by its versioned spell id.
    Contract:
        - Returns the first local spell whose SpellIndex.current matches `spell_id`.
        - Returns None if no matching spell is found.
    Args:
        spellbook: Spellbook holding locally bound spells.
        spell_id: Versioned spell id to locate.
    Returns:
        Spell | None: The resolved spell or None if missing.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell_index.current == spell_id:
            return spell
    return None


def test_component_validation_system_reports_required_holes_and_missing_frame() -> None:
    """
    Purpose:
        Validate builtin validation strategies run against real spell artifacts.
    Contract:
        - Missing resolution frame yields MISSING_RESOLUTION_FRAME error.
        - Required holes yield REQUIRED_HOLE warning.
    Returns:
        None.
    Raises:
        AssertionError: If expected issues are missing or misclassified.
    """
    spellbook = _make_spellbook()
    system = SpellValidationSystem()

    class NeedsInput:
        """
        Purpose:
            Provide a spell with a required plain parameter.
        Contract:
            - Declares an unannotated required parameter.
        Args:
            value: Required plain parameter with no default.
        """

        def __init__(self, value: int) -> None:
            """
            Purpose:
                Capture the required value input.
            Contract:
                Stores the provided value for completeness.
            Args:
                value: Required input for the spell.
            Returns:
                None.
            """
            self.value = value

    try:
        spell_id = spellbook.bind(
            spell=NeedsInput,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spell.run_phase_requirements()
        requirements = spell.requirements

        result = system.validate_spell(
            spell=spell,
            requirements=requirements,
            symbolic_graph=None,
            resolution_frame=None,
        )
        try:
            codes = {issue.code for issue in result.issues}
            assert codes == {"MISSING_RESOLUTION_FRAME", "REQUIRED_HOLE"}
            severity_by_code = {issue.code: issue.severity for issue in result.issues}
            assert severity_by_code["MISSING_RESOLUTION_FRAME"] == "error"
            assert severity_by_code["REQUIRED_HOLE"] == "warning"
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        spellbook.cleanup()


def test_component_validation_system_honors_cancellation_event() -> None:
    """
    Purpose:
        Validate the validation system honors CancellationEvent signals.
    Contract:
        - validate_spell raises OperationCancelledError when cancellation is set.
    Returns:
        None.
    Raises:
        AssertionError: If cancellation does not raise.
    """
    spellbook = _make_spellbook()
    system = SpellValidationSystem()
    signal = CancellationEventSignal()

    class Leaf:
        """
        Purpose:
            Provide a minimal spell for cancellation validation.
        Contract:
            - Declares no constructor parameters.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the leaf spell.
            Contract:
                No side effects beyond construction.
            Returns:
                None.
            """
            return None

    try:
        spell_id = spellbook.bind(
            spell=Leaf,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        signal.cancel()
        cancel_event = signal.event

        with pytest.raises(OperationCancelledError):
            system.validate_spell(
                spell=spell,
                requirements=None,
                symbolic_graph=None,
                resolution_frame=None,
                cancel_event=cancel_event,
            )
    finally:
        signal.cleanup()
        system.cleanup()
        spellbook.cleanup()


def test_component_validation_system_reports_all_issue_types_in_complex_case() -> None:
    """
    Purpose:
        Validate builtin strategies aggregate multiple issue types in one run.
    Contract:
        - Reports required holes, missing dependency graph, dangling deps,
          self deps, circular deps, and duplicate spell names.
    Returns:
        None.
    Raises:
        AssertionError: If any expected issue type is missing.
    """
    spellbook = _make_spellbook()
    system = SpellValidationSystem()

    class ContainerA:
        """
        Purpose:
            Provide a namespace for a Service spell with a required hole.
        Contract:
            Defines a nested Service class for multi-issue validation.
        """

        class Service:
            """
            Purpose:
                Provide a spell with a required plain parameter.
            Contract:
                Declares a required plain parameter to trigger REQUIRED_HOLE.
            Args:
                value: Required plain parameter with no default.
            """

            def __init__(self, value: int) -> None:
                """
                Purpose:
                    Capture the required value input.
                Contract:
                    Stores the provided value for completeness.
                Args:
                    value: Required input for the spell.
                Returns:
                    None.
                """
                self.value = value

    class ContainerB:
        """
        Purpose:
            Provide a second namespace for duplicate spell name detection.
        Contract:
            Defines a nested Service class with the same __name__.
        """

        class Service:
            """
            Purpose:
                Provide a spell with a duplicate name for collision checks.
            Contract:
                No runtime behavior beyond construction.
            """

            def __init__(self) -> None:
                """
                Purpose:
                    Initialize the Service spell.
                Contract:
                    No side effects beyond construction.
                Returns:
                    None.
                """
                return None

    try:
        root_id = spellbook.bind(
            spell=ContainerA.Service,
            existence=Existence.unique,
            permissions="create",
        )
        other_id = spellbook.bind(
            spell=ContainerB.Service,
            existence=Existence.unique,
            permissions="create",
            binding_name="secondary",
        )
        root_spell = _get_spell_by_version_id(spellbook, root_id)
        other_spell = _get_spell_by_version_id(spellbook, other_id)
        assert root_spell is not None
        assert other_spell is not None

        root_spell.run_phase_requirements()
        requirements = root_spell.requirements
        assert requirements is not None

        root_spell.dependencies = [other_id, root_id, "missing-id"]
        other_spell.dependencies = [root_id]

        result = system.validate_spell(
            spell=root_spell,
            requirements=requirements,
            symbolic_graph=None,
            resolution_frame=object(),
        )
        try:
            codes = {issue.code for issue in result.issues}
            expected = {
                "MISSING_DEPENDENCY_GRAPH",
                "DANGLING_DEPENDENCY",
                "SELF_DEPENDENCY",
                "CIRCULAR_DEPENDENCY",
                "REQUIRED_HOLE",
                "DUPLICATE_SPELL_NAME",
            }
            assert expected.issubset(codes)
            severity_by_code = {issue.code: issue.severity for issue in result.issues}
            assert severity_by_code["MISSING_DEPENDENCY_GRAPH"] == "warning"
            assert severity_by_code["REQUIRED_HOLE"] == "warning"
            assert severity_by_code["DANGLING_DEPENDENCY"] == "error"
            assert severity_by_code["SELF_DEPENDENCY"] == "error"
            assert severity_by_code["CIRCULAR_DEPENDENCY"] == "error"
            assert severity_by_code["DUPLICATE_SPELL_NAME"] == "error"
            assert result.has_errors is True
            assert result.has_warnings is True
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        spellbook.cleanup()
