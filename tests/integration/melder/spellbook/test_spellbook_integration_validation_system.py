from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex
from melder.spellbook.spell_crafter.validation.validation_system import SpellValidationSystem
from melder.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration_validation_system() -> None:
    """
    Purpose:
        Ensure integration validation system tests start with a clean Aether singleton.
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


def _make_dynamic_configuration() -> Configuration:
    """
    Purpose:
        Build a dynamic Configuration for integration validation tests.
    Contract:
        - dynamic_defaults are applied.
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Configuration: Configured integration configuration.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


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


def test_validation_system_resolves_contracted_dependency_without_dangling() -> None:
    """
    Purpose:
        Validate contracted dependencies resolve without dangling errors.
    Contract:
        - A dependency spell_id that is contracted is not flagged as dangling.
    Returns:
        None.
    Raises:
        AssertionError: If dangling dependency issues are produced.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    system = SpellValidationSystem()

    class Consumer:
        """
        Purpose:
            Provide a consumer spell for dependency validation.
        Contract:
            - Declares no constructor parameters.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the consumer spell.
            Contract:
                No side effects beyond construction.
            Returns:
                None.
            """
            return None

    owner = None
    borrower = None
    try:
        service_id = owner_book.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_id = borrower_book.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        owner = owner_book.conjure(automatic=False, name="owner")
        borrower = borrower_book.conjure(automatic=False, name="borrower")
        assert owner.link(borrower) is True
        assert borrower.add_spell_to_contract(
            spell_id=service_id,
            conduit=owner,
            permissions="create",
        )

        consumer_spell = _get_spell_by_version_id(borrower_book, consumer_id)
        assert consumer_spell is not None
        consumer_spell.dependencies = [service_id]
        consumer_spell.dependency_graph = object()

        result = system.validate_spell(
            spell=consumer_spell,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=object(),
        )
        try:
            assert result.issues == []
            assert result.has_errors is False
            assert result.has_warnings is False
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        if borrower is not None:
            borrower.cleanup()
        if owner is not None:
            owner.cleanup()


def test_validation_system_duplicate_spell_name_across_contracted() -> None:
    """
    Purpose:
        Validate duplicate spell names are detected across local and contracted spells.
    Contract:
        - Duplicate spell_name across local and contracted spells yields an error.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate spell names are not reported.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    system = SpellValidationSystem()

    class ContainerA:
        """
        Purpose:
            Provide a namespace for a Service spell.
        Contract:
            Defines a nested Service class for duplicate name testing.
        """

        class Service:
            """
            Purpose:
                Provide a Service spell with a shared name.
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

    class ContainerB:
        """
        Purpose:
            Provide a second namespace for a Service spell.
        Contract:
            Defines a nested Service class for duplicate name testing.
        """

        class Service:
            """
            Purpose:
                Provide a Service spell with a shared name.
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

    owner = None
    borrower = None
    try:
        owner_id = owner_book.bind(
            spell=ContainerB.Service,
            existence=Existence.unique,
            permissions="create",
        )
        borrower_id = borrower_book.bind(
            spell=ContainerA.Service,
            existence=Existence.unique,
            permissions="create",
        )
        owner = owner_book.conjure(automatic=False, name="owner")
        borrower = borrower_book.conjure(automatic=False, name="borrower")
        assert owner.link(borrower) is True
        assert borrower.add_spell_to_contract(
            spell_id=owner_id,
            conduit=owner,
            permissions="create",
        )

        local_spell = _get_spell_by_version_id(borrower_book, borrower_id)
        assert local_spell is not None
        local_spell.dependency_graph = object()

        result = system.validate_spell(
            spell=local_spell,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=object(),
        )
        try:
            assert len(result.issues) == 1
            issue = result.issues[0]
            assert issue.code == "DUPLICATE_SPELL_NAME"
            assert issue.severity == "error"
            assert issue.details["collision_count"] == 2
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        if borrower is not None:
            borrower.cleanup()
        if owner is not None:
            owner.cleanup()


def test_validation_system_updates_after_contract_removal_and_readd() -> None:
    """
    Purpose:
        Validate validation results track contract removal and re-addition.
    Contract:
        - Contracted dependencies validate cleanly.
        - Removing the contract yields DANGLING_DEPENDENCY errors.
        - Re-adding the contract clears the dangling dependency.
    Returns:
        None.
    Raises:
        AssertionError: If validation results do not reflect contract changes.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    system = SpellValidationSystem()

    class Consumer:
        """
        Purpose:
            Provide a consumer spell for contract churn validation.
        Contract:
            - Declares no constructor parameters.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the consumer spell.
            Contract:
                No side effects beyond construction.
            Returns:
                None.
            """
            return None

    owner = None
    borrower = None
    try:
        dependency_id = owner_book.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_id = borrower_book.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )

        owner = owner_book.conjure(automatic=False, name="owner")
        borrower = borrower_book.conjure(automatic=False, name="borrower")
        assert owner.link(borrower) is True
        assert borrower.add_spell_to_contract(
            spell_id=dependency_id,
            conduit=owner,
            permissions="create",
        )

        consumer_spell = _get_spell_by_version_id(borrower_book, consumer_id)
        assert consumer_spell is not None
        consumer_spell.dependencies = [dependency_id]
        consumer_spell.dependency_graph = object()

        result = system.validate_spell(
            spell=consumer_spell,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=object(),
        )
        try:
            assert result.issues == []
        finally:
            result.cleanup()

        removed = borrower.remove_spell_from_contract(
            spell_id=dependency_id,
            conduit=owner,
        )
        assert removed is True

        result = system.validate_spell(
            spell=consumer_spell,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=object(),
        )
        try:
            codes = {issue.code for issue in result.issues}
            assert codes == {"DANGLING_DEPENDENCY"}
        finally:
            result.cleanup()

        assert owner.link(borrower) is True
        assert borrower.add_spell_to_contract(
            spell_id=dependency_id,
            conduit=owner,
            permissions="create",
        )

        result = system.validate_spell(
            spell=consumer_spell,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=object(),
        )
        try:
            assert result.issues == []
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        if borrower is not None:
            borrower.cleanup()
        if owner is not None:
            owner.cleanup()


def test_validation_system_reports_dangling_after_sever_link() -> None:
    """
    Purpose:
        Validate severed links update validation results for contracted dependencies.
    Contract:
        - sever_link clears contracted spells.
        - Validation reports DANGLING_DEPENDENCY after unlink.
    Returns:
        None.
    Raises:
        AssertionError: If validation does not reflect the unlink.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    system = SpellValidationSystem()

    class Consumer:
        """
        Purpose:
            Provide a consumer spell for sever_link validation.
        Contract:
            - Declares no constructor parameters.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the consumer spell.
            Contract:
                No side effects beyond construction.
            Returns:
                None.
            """
            return None

    owner = None
    borrower = None
    try:
        dependency_id = owner_book.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_id = borrower_book.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )

        owner = owner_book.conjure(automatic=False, name="owner")
        borrower = borrower_book.conjure(automatic=False, name="borrower")
        assert owner.link(borrower) is True
        assert borrower.add_spell_to_contract(
            spell_id=dependency_id,
            conduit=owner,
            permissions="create",
        )

        consumer_spell = _get_spell_by_version_id(borrower_book, consumer_id)
        assert consumer_spell is not None
        consumer_spell.dependencies = [dependency_id]
        consumer_spell.dependency_graph = object()

        assert owner.sever_link(borrower) is True

        result = system.validate_spell(
            spell=consumer_spell,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=object(),
        )
        try:
            codes = {issue.code for issue in result.issues}
            assert codes == {"DANGLING_DEPENDENCY"}
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        if borrower is not None:
            borrower.cleanup()
        if owner is not None:
            owner.cleanup()


def test_validation_system_detects_cross_boundary_cycle() -> None:
    """
    Purpose:
        Validate cycles across local and contracted spells are detected.
    Contract:
        - Circular dependencies spanning local + contracted spells yield errors.
    Returns:
        None.
    Raises:
        AssertionError: If cross-boundary cycles are not reported.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    system = SpellValidationSystem()

    class LocalService:
        """
        Purpose:
            Provide a local spell for cycle detection.
        Contract:
            - Declares no constructor parameters.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the local service.
            Contract:
                No side effects beyond construction.
            Returns:
                None.
            """
            return None

    owner = None
    borrower = None
    try:
        owner_id = owner_book.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        borrower_id = borrower_book.bind(
            spell=LocalService,
            existence=Existence.unique,
            permissions="create",
        )

        owner = owner_book.conjure(automatic=False, name="owner")
        borrower = borrower_book.conjure(automatic=False, name="borrower")
        assert owner.link(borrower) is True
        assert borrower.add_spell_to_contract(
            spell_id=owner_id,
            conduit=owner,
            permissions="create",
        )

        owner_spell = _get_spell_by_version_id(owner_book, owner_id)
        borrower_spell = _get_spell_by_version_id(borrower_book, borrower_id)
        assert owner_spell is not None
        assert borrower_spell is not None

        owner_spell.dependencies = [borrower_id]
        borrower_spell.dependencies = [owner_id]
        borrower_spell.dependency_graph = object()

        result = system.validate_spell(
            spell=borrower_spell,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=object(),
        )
        try:
            codes = {issue.code for issue in result.issues}
            assert codes == {"CIRCULAR_DEPENDENCY"}
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        if borrower is not None:
            borrower.cleanup()
        if owner is not None:
            owner.cleanup()


def test_validation_system_duplicate_name_clears_after_unlink() -> None:
    """
    Purpose:
        Validate duplicate spell names clear after unlinking conduits.
    Contract:
        - Duplicate spell names are reported while contracted.
        - After sever_link, duplicates are no longer reported.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate names persist after unlink.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    system = SpellValidationSystem()

    class ContainerA:
        """
        Purpose:
            Provide a namespace for a Service spell.
        Contract:
            Defines a nested Service class for duplicate name testing.
        """

        class Service:
            """
            Purpose:
                Provide a Service spell with a shared name.
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

    class ContainerB:
        """
        Purpose:
            Provide a second namespace for a Service spell.
        Contract:
            Defines a nested Service class for duplicate name testing.
        """

        class Service:
            """
            Purpose:
                Provide a Service spell with a shared name.
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

    owner = None
    borrower = None
    try:
        owner_id = owner_book.bind(
            spell=ContainerB.Service,
            existence=Existence.unique,
            permissions="create",
        )
        borrower_id = borrower_book.bind(
            spell=ContainerA.Service,
            existence=Existence.unique,
            permissions="create",
        )
        owner = owner_book.conjure(automatic=False, name="owner")
        borrower = borrower_book.conjure(automatic=False, name="borrower")
        assert owner.link(borrower) is True
        assert borrower.add_spell_to_contract(
            spell_id=owner_id,
            conduit=owner,
            permissions="create",
        )

        local_spell = _get_spell_by_version_id(borrower_book, borrower_id)
        assert local_spell is not None
        local_spell.dependency_graph = object()

        result = system.validate_spell(
            spell=local_spell,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=object(),
        )
        try:
            codes = {issue.code for issue in result.issues}
            assert codes == {"DUPLICATE_SPELL_NAME"}
        finally:
            result.cleanup()

        assert owner.sever_link(borrower) is True

        result = system.validate_spell(
            spell=local_spell,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=object(),
        )
        try:
            assert result.issues == []
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        if borrower is not None:
            borrower.cleanup()
        if owner is not None:
            owner.cleanup()


def test_spell_validation_phase4_marks_leaf_as_validated() -> None:
    """
    Purpose:
        Validate Phase 4 produces a clean validation result for a leaf spell.
    Contract:
        - run_phase_validation stores a Phase-4 result with no issues.
        - The spell is not marked broken.
        - validated remains Phase-6 gated until system validation runs.
    Returns:
        None.
    Raises:
        AssertionError: If validation flags or issues are unexpected.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    class Leaf:
        """
        Purpose:
            Provide a minimal leaf spell for validation testing.
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

        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()
        spell.run_phase_validation()

        result = spell.validation_result_phase4
        assert result is not None
        assert result.issues == []
        assert result.has_errors is False
        assert result.has_warnings is False
        assert spell.is_broken is False
    finally:
        spellbook.cleanup()


def test_spell_validation_phase4_warns_on_required_hole_not_broken() -> None:
    """
    Purpose:
        Validate required hole warnings do not mark a spell as broken.
    Contract:
        - REQUIRED_HOLE warnings are present.
        - The spell is not marked broken.
    Returns:
        None.
    Raises:
        AssertionError: If warnings are missing or the spell is marked broken.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    class NeedsInput:
        """
        Purpose:
            Provide a spell with a required plain parameter.
        Contract:
            - Declares an unannotated required parameter.
        Args:
            value: Required plain parameter with no default.
        """

        def __init__(self, value) -> None:
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
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()
        spell.run_phase_validation()

        result = spell.validation_result_phase4
        assert result is not None
        codes = {issue.code for issue in result.issues}
        assert "REQUIRED_HOLE" in codes
        assert result.has_errors is False
        assert result.has_warnings is True
        assert spell.is_broken is False
    finally:
        spellbook.cleanup()


def test_spellbook_conjure_raises_validation_error_for_cycle() -> None:
    """
    Purpose:
        Validate conjure raises SpellbookValidationError for broken spells.
    Contract:
        - A circular dependency triggers SpellbookValidationError.
    Returns:
        None.
    Raises:
        AssertionError: If conjure does not raise on a broken spell.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 2)

    class Alpha:
        """
        Purpose:
            Provide a spell that depends on Beta.
        Contract:
            - Declares a Beta dependency via forward reference annotation.
        Args:
            beta: Dependency spelled by the Beta spellframe.
        """

        def __init__(self, beta: Beta) -> None:
            """
            Purpose:
                Capture the injected Beta dependency.
            Contract:
                Stores the dependency for completeness.
            Args:
                beta: Injected Beta dependency.
            Returns:
                None.
            """
            self.beta = beta

    class Beta:
        """
        Purpose:
            Provide a spell that depends on Alpha.
        Contract:
            - Declares an Alpha dependency via forward reference annotation.
        Args:
            alpha: Dependency spelled by the Alpha spellframe.
        """

        def __init__(self, alpha: Alpha) -> None:
            """
            Purpose:
                Capture the injected Alpha dependency.
            Contract:
                Stores the dependency for completeness.
            Args:
                alpha: Injected Alpha dependency.
            Returns:
                None.
            """
            self.alpha = alpha

    try:
        spellbook.bind(
            spell=Alpha,
            existence=Existence.unique,
            permissions="create",
            spellframe="Alpha",
        )
        spellbook.bind(
            spell=Beta,
            existence=Existence.unique,
            permissions="create",
            spellframe="Beta",
        )

        with pytest.raises(SpellbookValidationError, match="Broken spells"):
            spellbook.conjure(name="root")
    finally:
        spellbook.cleanup()


def test_spellbook_conjure_succeeds_with_required_hole_warning() -> None:
    """
    Purpose:
        Validate conjure succeeds when validation reports only warnings.
    Contract:
        - Required-hole warnings do not block Conduit creation.
    Returns:
        None.
    Raises:
        AssertionError: If conjure raises on warnings.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    class NeedsInput:
        """
        Purpose:
            Provide a spell with a required plain parameter.
        Contract:
            - Declares a required plain parameter to trigger REQUIRED_HOLE.
        Args:
            value: Required plain parameter with no default.
        """

        def __init__(self, value) -> None:
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

    conduit = None
    try:
        spellbook.bind(
            spell=NeedsInput,
            existence=Existence.unique,
            permissions="create",
        )

        conduit = spellbook.conjure(name="root")
        assert conduit is not None
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def test_validation_system_reports_missing_resolution_frame() -> None:
    """
    Purpose:
        Validate missing resolution frames surface as validation errors.
    Contract:
        - MISSING_RESOLUTION_FRAME is emitted when resolution_frame is None.
    Returns:
        None.
    Raises:
        AssertionError: If the missing resolution frame error is absent.
    """
    spellbook = Spellbook()
    system = SpellValidationSystem()

    class Leaf:
        """
        Purpose:
            Provide a minimal spell for resolution-frame tests.
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

        result = system.validate_spell(
            spell=spell,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=None,
        )
        try:
            codes = {issue.code for issue in result.issues}
            assert codes == {"MISSING_RESOLUTION_FRAME"}
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        spellbook.cleanup()


def test_validation_system_reports_self_dependency_errors() -> None:
    """
    Purpose:
        Validate self-dependencies surface as validation errors.
    Contract:
        - SELF_DEPENDENCY is reported for a spell depending on itself.
        - CIRCULAR_DEPENDENCY is also reported for the trivial cycle.
    Returns:
        None.
    Raises:
        AssertionError: If expected self-cycle diagnostics are missing.
    """
    spellbook = Spellbook()
    system = SpellValidationSystem()

    class Loop:
        """
        Purpose:
            Provide a spell for self-dependency validation.
        Contract:
            - Declares no constructor parameters.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the loop spell.
            Contract:
                No side effects beyond construction.
            Returns:
                None.
            """
            return None

    try:
        spell_id = spellbook.bind(
            spell=Loop,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spell.dependencies = [spell_id]
        spell.dependency_graph = object()

        result = system.validate_spell(
            spell=spell,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=object(),
        )
        try:
            codes = {issue.code for issue in result.issues}
            assert codes == {"SELF_DEPENDENCY", "CIRCULAR_DEPENDENCY"}
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        spellbook.cleanup()


def test_validation_system_duplicate_spell_name_local_only() -> None:
    """
    Purpose:
        Validate duplicate spell names are detected within a single Spellbook.
    Contract:
        - Duplicate spell_name across local spells yields DUPLICATE_SPELL_NAME.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate spell names are not reported.
    """
    spellbook = Spellbook()
    system = SpellValidationSystem()

    class ContainerA:
        """
        Purpose:
            Provide a namespace for a Service spell.
        Contract:
            Defines a nested Service class for duplicate name testing.
        """

        class Service:
            """
            Purpose:
                Provide a Service spell with a shared name.
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

    class ContainerB:
        """
        Purpose:
            Provide a second namespace for a Service spell.
        Contract:
            Defines a nested Service class for duplicate name testing.
        """

        class Service:
            """
            Purpose:
                Provide a Service spell with a shared name.
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
        spellbook.bind(
            spell=ContainerA.Service,
            existence=Existence.unique,
            permissions="create",
        )
        target_id = spellbook.bind(
            spell=ContainerB.Service,
            existence=Existence.unique,
            permissions="create",
        )

        spell = _get_spell_by_version_id(spellbook, target_id)
        assert spell is not None
        spell.dependency_graph = object()

        result = system.validate_spell(
            spell=spell,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=object(),
        )
        try:
            codes = {issue.code for issue in result.issues}
            assert codes == {"DUPLICATE_SPELL_NAME"}
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        spellbook.cleanup()


def test_spell_validation_phase4_marks_broken_on_dangling_dependency() -> None:
    """
    Purpose:
        Validate Phase 4 marks a spell as broken when dangling dependencies exist.
    Contract:
        - DANGLING_DEPENDENCY errors are present.
        - The spell is marked broken after Phase 4.
        - validated remains Phase-6 gated until system validation runs.
    Returns:
        None.
    Raises:
        AssertionError: If the error is missing or the spell is not marked broken.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    class Leaf:
        """
        Purpose:
            Provide a minimal leaf spell for dangling dependency testing.
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

        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()

        spell.dependencies = ["missing-id"]
        spell.run_phase_validation()

        result = spell.validation_result_phase4
        assert result is not None
        codes = {issue.code for issue in result.issues}
        assert codes == {"DANGLING_DEPENDENCY"}
        assert result.has_errors is True
        assert spell.is_broken is True
    finally:
        spellbook.cleanup()


def test_spell_validation_phase4_warns_on_missing_dependency_graph_not_broken() -> None:
    """
    Purpose:
        Validate missing dependency graph emits warnings without breaking spells.
    Contract:
        - MISSING_DEPENDENCY_GRAPH warning is present.
        - The spell is not marked broken after Phase 4.
        - validated remains Phase-6 gated until system validation runs.
    Returns:
        None.
    Raises:
        AssertionError: If warnings are missing or the spell is marked broken.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    class Leaf:
        """
        Purpose:
            Provide a minimal leaf spell for dependency graph testing.
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

        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()

        spell.dependency_graph = None
        spell.run_phase_validation()

        result = spell.validation_result_phase4
        assert result is not None
        codes = {issue.code for issue in result.issues}
        assert "MISSING_DEPENDENCY_GRAPH" in codes
        assert result.has_errors is False
        assert result.has_warnings is True
        assert spell.is_broken is False
    finally:
        spellbook.cleanup()


def test_validation_system_local_dependency_not_dangling() -> None:
    """
    Purpose:
        Validate local spell dependencies are not flagged as dangling.
    Contract:
        - A dependency spell_id bound in the same Spellbook is not reported.
    Returns:
        None.
    Raises:
        AssertionError: If local dependencies are marked as dangling.
    """
    spellbook = Spellbook()
    system = SpellValidationSystem()

    class Consumer:
        """
        Purpose:
            Provide a consumer spell for local dependency checks.
        Contract:
            - Declares no constructor parameters.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the consumer spell.
            Contract:
                No side effects beyond construction.
            Returns:
                None.
            """
            return None

    try:
        service_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )

        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None
        consumer_spell.dependencies = [service_id]
        consumer_spell.dependency_graph = object()

        result = system.validate_spell(
            spell=consumer_spell,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=object(),
        )
        try:
            assert result.issues == []
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        spellbook.cleanup()


def test_spell_validation_phase6_marks_valid_and_updates_system_state() -> None:
    """
    Purpose:
        Validate Phase 6 marks a clean spell as system-valid.
    Contract:
        - Phase 6 validation result reports is_valid True.
        - SpellSystemStates marks the lineage as SpellValidity.valid.
    Returns:
        None.
    Raises:
        AssertionError: If Phase 6 validation or system state is incorrect.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    class Leaf:
        """
        Purpose:
            Provide a minimal leaf spell for system validation.
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

        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()
        spell.run_phase_validation()
        spell.run_phase_root_blueprints()
        spell.run_phase_system_validation()

        result = spell.validation_result_phase6
        assert result is not None
        assert result.is_valid is True
        assert result.errors == []

        state = spellbook._spell_system_states.get_by_spell_id(spell_id)
        assert state is not None
        assert state.validity is SpellValidity.valid
    finally:
        spellbook.cleanup()


def test_spell_validation_phase6_gates_broken_spell_in_system_state() -> None:
    """
    Purpose:
        Validate Phase 6 gates lineages when Phase 4 marks a spell broken.
    Contract:
        - Phase 6 validation result reports is_valid False.
        - broken_spell_in_dag is reported in system diagnostics.
        - SpellSystemStates marks the lineage as SpellValidity.gated.
    Returns:
        None.
    Raises:
        AssertionError: If Phase 6 gating or diagnostics are incorrect.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    class Leaf:
        """
        Purpose:
            Provide a minimal leaf spell for gating tests.
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

        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()

        spell.dependencies = ["missing-id"]
        spell.run_phase_validation()
        spell.run_phase_root_blueprints()
        spell.run_phase_system_validation()

        result = spell.validation_result_phase6
        assert result is not None
        assert result.is_valid is False

        codes = {diag.code for diag in result.errors}
        assert "broken_spell_in_dag" in codes

        state = spellbook._spell_system_states.get_by_spell_id(spell_id)
        assert state is not None
        assert state.validity is SpellValidity.gated
    finally:
        spellbook.cleanup()


def test_spell_validation_phase6_reports_missing_phase4_validation_and_root_not_viable() -> None:
    """
    Purpose:
        Validate missing Phase-4 results are surfaced at system validation.
    Contract:
        - missing_phase4_validation is reported for unvalidated nodes.
        - root_not_viable is emitted for the affected root.
    Returns:
        None.
    Raises:
        AssertionError: If missing Phase-4 diagnostics are not reported.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    class Consumer:
        """
        Purpose:
            Provide a spell that depends on BasicService.
        Contract:
            - Declares a BasicService dependency.
        Args:
            service: Injected BasicService instance.
        """

        def __init__(self, service: BasicService) -> None:
            """
            Purpose:
                Capture the injected BasicService dependency.
            Contract:
                Stores the dependency for completeness.
            Args:
                service: Injected BasicService dependency.
            Returns:
                None.
            """
            self.service = service

    try:
        spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
            spellframe="BasicService",
        )
        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        consumer_spell.run_phase_requirements()
        consumer_spell.run_phase_symbolic_graph()
        consumer_spell.run_phase_local_frame()
        consumer_spell.run_phase_validation()
        consumer_spell.run_phase_root_blueprints()
        consumer_spell.run_phase_system_validation()

        result = consumer_spell.validation_result_phase6
        assert result is not None
        codes = {diag.code for diag in result.errors}
        assert "missing_phase4_validation" in codes
        assert "root_not_viable" in codes
    finally:
        spellbook.cleanup()


def test_spell_validation_phase6_detects_cycle_in_index_and_graph_mismatch() -> None:
    """
    Purpose:
        Validate system validation detects index cycles and graph mismatches.
    Contract:
        - cycle_detected is reported for cyclic dependencies in the index.
        - edge_missing_from_blueprint is reported for index edges without blueprints.
    Returns:
        None.
    Raises:
        AssertionError: If cycle or graph-consistency diagnostics are missing.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    class Root:
        """
        Purpose:
            Provide a root spell isolated from the cycle.
        Contract:
            - Declares no constructor parameters.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the root spell.
            Contract:
                No side effects beyond construction.
            Returns:
                None.
            """
            return None

    class Alpha:
        """
        Purpose:
            Provide one half of a dependency cycle.
        Contract:
            - Declares a Beta dependency via forward reference annotation.
        Args:
            beta: Injected Beta dependency.
        """

        def __init__(self, beta: Beta) -> None:
            """
            Purpose:
                Capture the injected Beta dependency.
            Contract:
                Stores the dependency for completeness.
            Args:
                beta: Injected Beta dependency.
            Returns:
                None.
            """
            self.beta = beta

    class Beta:
        """
        Purpose:
            Provide the other half of a dependency cycle.
        Contract:
            - Declares an Alpha dependency via forward reference annotation.
        Args:
            alpha: Injected Alpha dependency.
        """

        def __init__(self, alpha: Alpha) -> None:
            """
            Purpose:
                Capture the injected Alpha dependency.
            Contract:
                Stores the dependency for completeness.
            Args:
                alpha: Injected Alpha dependency.
            Returns:
                None.
            """
            self.alpha = alpha

    try:
        root_id = spellbook.bind(
            spell=Root,
            existence=Existence.unique,
            permissions="create",
        )
        alpha_id = spellbook.bind(
            spell=Alpha,
            existence=Existence.unique,
            permissions="create",
            spellframe="Alpha",
        )
        beta_id = spellbook.bind(
            spell=Beta,
            existence=Existence.unique,
            permissions="create",
            spellframe="Beta",
        )

        root_spell = _get_spell_by_version_id(spellbook, root_id)
        alpha_spell = _get_spell_by_version_id(spellbook, alpha_id)
        beta_spell = _get_spell_by_version_id(spellbook, beta_id)
        assert root_spell is not None
        assert alpha_spell is not None
        assert beta_spell is not None

        for spell in (alpha_spell, beta_spell):
            spell.run_phase_requirements()
            spell.run_phase_symbolic_graph()
            spell.run_phase_local_frame()
            spell.run_phase_validation()

        root_spell.run_phase_requirements()
        root_spell.run_phase_symbolic_graph()
        root_spell.run_phase_local_frame()
        root_spell.run_phase_validation()
        root_spell.run_phase_root_blueprints()
        root_spell.run_phase_system_validation()

        result = root_spell.validation_result_phase6
        assert result is not None
        codes = {diag.code for diag in result.errors}
        assert "cycle_detected" in codes
        assert "edge_missing_from_blueprint" in codes
    finally:
        spellbook.cleanup()


def test_spell_validation_phase6_reports_socket_ref_index_mismatch() -> None:
    """
    Purpose:
        Validate socket-ref sanity checks catch index mismatches.
    Contract:
        - socket_ref_missing_in_index is reported when the DagIndex is empty.
        - socket_ref_missing_in_index_name is also reported for name buckets.
    Returns:
        None.
    Raises:
        AssertionError: If socket-ref diagnostics are missing.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    class Consumer:
        """
        Purpose:
            Provide a spell with a dependency socket for blueprint tests.
        Contract:
            - Declares a BasicService dependency.
        Args:
            service: Injected BasicService dependency.
        """

        def __init__(self, service: BasicService) -> None:
            """
            Purpose:
                Capture the injected BasicService dependency.
            Contract:
                Stores the dependency for completeness.
            Args:
                service: Injected BasicService dependency.
            Returns:
                None.
            """
            self.service = service

    try:
        service_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
            spellframe="BasicService",
        )
        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )

        service_spell = _get_spell_by_version_id(spellbook, service_id)
        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert service_spell is not None
        assert consumer_spell is not None

        service_spell.run_phase_requirements()
        service_spell.run_phase_symbolic_graph()
        service_spell.run_phase_local_frame()
        service_spell.run_phase_validation()

        consumer_spell.run_phase_requirements()
        consumer_spell.run_phase_symbolic_graph()
        consumer_spell.run_phase_local_frame()
        consumer_spell.run_phase_validation()
        consumer_spell.run_phase_root_blueprints()

        crafter = consumer_spell._crafter
        assert crafter is not None
        blueprints = crafter._entire_dag_blueprint_phase5
        assert blueprints is not None
        root_blueprint = blueprints.get(consumer_id)
        assert root_blueprint is not None
        root_blueprint._dag_index = DagIndex()

        consumer_spell.run_phase_system_validation()

        result = consumer_spell.validation_result_phase6
        assert result is not None
        codes = {diag.code for diag in result.errors}
        assert "socket_ref_missing_in_index" in codes
        assert "socket_ref_missing_in_index_name" in codes
    finally:
        spellbook.cleanup()
