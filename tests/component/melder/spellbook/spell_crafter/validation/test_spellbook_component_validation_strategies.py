import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.spellbook_scanner import SpellbookScanner
from melder.spellbook.spell_crafter.validation.spell_validation_context import SpellValidationContext
from melder.spellbook.spell_crafter.validation.strategies.circular_dependency_strategy import (
    CircularDependencyStrategy,
)
from melder.spellbook.spell_crafter.validation.strategies.dangling_dependency_strategy import (
    DanglingDependenciesStrategy,
)
from melder.spellbook.spell_crafter.validation.strategies.duplicate_spell_name_strategy import (
    DuplicateSpellNameStrategy,
)
from melder.spellbook.spell_crafter.validation.strategies.required_holes_strategy import (
    RequiredHolesStrategy,
)
from melder.spellbook.spell_crafter.validation.strategies.resolution_frame_presence_strategy import (
    ResolutionFramePresenceStrategy,
)
from melder.spellbook.spell_crafter.validation.strategies.self_validation_strategy import (
    SelfDependencyStrategy,
)
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_validation_strategies() -> None:
    """
    Purpose:
        Ensure component validation strategy tests start with a clean Aether singleton.
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
        Provide a Spellbook configured for validation strategy component tests.
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


def _make_context(
    *,
    spell: object,
    spellbook: Spellbook,
    requirements: object | None = None,
    symbolic_graph: object | None = None,
    resolution_frame: object | None = None,
) -> tuple[SpellValidationContext, list]:
    """
    Purpose:
        Build a SpellValidationContext bound to a real SpellbookScanner.
    Contract:
        - Returns the context and the shared issues list.
    Args:
        spell: Spell instance under validation.
        spellbook: Spellbook owning the spell.
        requirements: Phase 1 requirements artifact, if any.
        symbolic_graph: Phase 2 symbolic graph artifact, if any.
        resolution_frame: Phase 3 resolution frame artifact, if any.
    Returns:
        tuple[SpellValidationContext, list]: The context and issues list.
    """
    issues: list = []
    scanner = SpellbookScanner(spellbook)
    context = SpellValidationContext(
        spell=spell,
        spellbook=spellbook,
        requirements=requirements,
        symbolic_graph=symbolic_graph,
        resolution_frame=resolution_frame,
        scanner=scanner,
        cancel_event=None,
        issues=issues,
    )
    return context, issues


def test_component_resolution_frame_presence_strategy_flags_missing_frame() -> None:
    """
    Purpose:
        Validate ResolutionFramePresenceStrategy emits an error when Phase 3 is missing.
    Contract:
        - Missing resolution_frame yields a MISSING_RESOLUTION_FRAME error.
    Returns:
        None.
    Raises:
        AssertionError: If the expected issue is not reported.
    """
    spellbook = _make_spellbook()
    strategy = ResolutionFramePresenceStrategy()
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        context, issues = _make_context(spell=spell, spellbook=spellbook)
        try:
            strategy.validate(context)
            assert len(issues) == 1
            issue = issues[0]
            assert issue.code == "MISSING_RESOLUTION_FRAME"
            assert issue.severity == "error"
        finally:
            context.cleanup()
    finally:
        strategy.cleanup()
        spellbook.cleanup()


def test_component_resolution_frame_presence_strategy_warns_on_missing_graph() -> None:
    """
    Purpose:
        Validate ResolutionFramePresenceStrategy warns when dependency graph is missing.
    Contract:
        - Missing dependency_graph yields a MISSING_DEPENDENCY_GRAPH warning.
    Returns:
        None.
    Raises:
        AssertionError: If the expected warning is not reported.
    """
    spellbook = _make_spellbook()
    strategy = ResolutionFramePresenceStrategy()
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        context, issues = _make_context(
            spell=spell,
            spellbook=spellbook,
            resolution_frame=object(),
        )
        try:
            strategy.validate(context)
            assert len(issues) == 1
            issue = issues[0]
            assert issue.code == "MISSING_DEPENDENCY_GRAPH"
            assert issue.severity == "warning"
        finally:
            context.cleanup()
    finally:
        strategy.cleanup()
        spellbook.cleanup()


def test_component_required_holes_strategy_reports_plain_required_parameters() -> None:
    """
    Purpose:
        Validate RequiredHolesStrategy reports required plain parameters.
    Contract:
        - Required holes yield REQUIRED_HOLE warnings with parameter metadata.
    Returns:
        None.
    Raises:
        AssertionError: If the required hole is not reported.
    """
    spellbook = _make_spellbook()
    strategy = RequiredHolesStrategy()

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

        context, issues = _make_context(
            spell=spell,
            spellbook=spellbook,
            requirements=requirements,
        )
        try:
            strategy.validate(context)
            assert len(issues) == 1
            issue = issues[0]
            assert issue.code == "REQUIRED_HOLE"
            assert issue.severity == "warning"
            assert issue.details["parameter_name"] == "value"
        finally:
            context.cleanup()
    finally:
        strategy.cleanup()
        spellbook.cleanup()


def test_component_dangling_dependencies_strategy_ignores_resolved_dependencies() -> None:
    """
    Purpose:
        Validate DanglingDependenciesStrategy ignores resolved dependency ids.
    Contract:
        - No issues are emitted when dependency ids are present in the spellbook.
    Returns:
        None.
    Raises:
        AssertionError: If issues are emitted for resolved dependencies.
    """
    spellbook = _make_spellbook()
    strategy = DanglingDependenciesStrategy()
    try:
        service_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        config_id = spellbook.bind(
            spell=BasicConfig,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, service_id)
        assert spell is not None

        spell.dependencies = [config_id]

        context, issues = _make_context(spell=spell, spellbook=spellbook)
        try:
            strategy.validate(context)
            assert issues == []
        finally:
            context.cleanup()
    finally:
        strategy.cleanup()
        spellbook.cleanup()


def test_component_dangling_dependencies_strategy_reports_missing_dependency() -> None:
    """
    Purpose:
        Validate DanglingDependenciesStrategy reports missing dependency ids.
    Contract:
        - Missing dependency ids yield DANGLING_DEPENDENCY errors.
    Returns:
        None.
    Raises:
        AssertionError: If missing dependencies are not reported.
    """
    spellbook = _make_spellbook()
    strategy = DanglingDependenciesStrategy()
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spell.dependencies = ["missing-id"]

        context, issues = _make_context(spell=spell, spellbook=spellbook)
        try:
            strategy.validate(context)
            assert len(issues) == 1
            issue = issues[0]
            assert issue.code == "DANGLING_DEPENDENCY"
            assert issue.severity == "error"
            assert issue.details["missing_spell_id"] == "missing-id"
        finally:
            context.cleanup()
    finally:
        strategy.cleanup()
        spellbook.cleanup()


def test_component_self_dependency_strategy_reports_self_reference() -> None:
    """
    Purpose:
        Validate SelfDependencyStrategy reports direct self-dependencies.
    Contract:
        - Self dependencies yield SELF_DEPENDENCY errors.
    Returns:
        None.
    Raises:
        AssertionError: If self dependencies are not reported.
    """
    spellbook = _make_spellbook()
    strategy = SelfDependencyStrategy()
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spell.dependencies = [spell_id]

        context, issues = _make_context(spell=spell, spellbook=spellbook)
        try:
            strategy.validate(context)
            assert len(issues) == 1
            issue = issues[0]
            assert issue.code == "SELF_DEPENDENCY"
            assert issue.severity == "error"
        finally:
            context.cleanup()
    finally:
        strategy.cleanup()
        spellbook.cleanup()


def test_component_circular_dependency_strategy_detects_cycle() -> None:
    """
    Purpose:
        Validate CircularDependencyStrategy reports dependency cycles.
    Contract:
        - A simple two-node cycle yields CIRCULAR_DEPENDENCY errors.
    Returns:
        None.
    Raises:
        AssertionError: If cycles are not reported.
    """
    spellbook = _make_spellbook()
    strategy = CircularDependencyStrategy()

    class Alpha:
        """
        Purpose:
            Provide a simple spell for cycle detection.
        Contract:
            - No runtime behavior beyond construction.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the Alpha spell.
            Contract:
                No side effects beyond construction.
            Returns:
                None.
            """
            return None

    class Beta:
        """
        Purpose:
            Provide a second spell for cycle detection.
        Contract:
            - No runtime behavior beyond construction.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the Beta spell.
            Contract:
                No side effects beyond construction.
            Returns:
                None.
            """
            return None

    try:
        alpha_id = spellbook.bind(
            spell=Alpha,
            existence=Existence.unique,
            permissions="create",
        )
        beta_id = spellbook.bind(
            spell=Beta,
            existence=Existence.unique,
            permissions="create",
        )
        alpha_spell = _get_spell_by_version_id(spellbook, alpha_id)
        beta_spell = _get_spell_by_version_id(spellbook, beta_id)
        assert alpha_spell is not None
        assert beta_spell is not None

        alpha_spell.dependencies = [beta_id]
        beta_spell.dependencies = [alpha_id]

        context, issues = _make_context(spell=alpha_spell, spellbook=spellbook)
        try:
            strategy.validate(context)
            assert len(issues) == 1
            issue = issues[0]
            assert issue.code == "CIRCULAR_DEPENDENCY"
            assert issue.severity == "error"
            cycle = issue.details["cycle"]
            assert alpha_id in cycle
            assert beta_id in cycle
        finally:
            context.cleanup()
    finally:
        strategy.cleanup()
        spellbook.cleanup()


def test_component_duplicate_spell_name_strategy_flags_collision() -> None:
    """
    Purpose:
        Validate DuplicateSpellNameStrategy reports same-name collisions.
    Contract:
        - Two visible spells with the same name yield DUPLICATE_SPELL_NAME errors.
    Returns:
        None.
    Raises:
        AssertionError: If collisions are not reported.
    """
    spellbook = _make_spellbook()
    strategy = DuplicateSpellNameStrategy()

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
        first_id = spellbook.bind(
            spell=ContainerA.Service,
            existence=Existence.unique,
            permissions="create",
        )
        spellbook.bind(
            spell=ContainerB.Service,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, first_id)
        assert spell is not None

        context, issues = _make_context(spell=spell, spellbook=spellbook)
        try:
            strategy.validate(context)
            assert len(issues) == 1
            issue = issues[0]
            assert issue.code == "DUPLICATE_SPELL_NAME"
            assert issue.severity == "error"
            assert issue.details["collision_count"] == 2
        finally:
            context.cleanup()
    finally:
        strategy.cleanup()
        spellbook.cleanup()
