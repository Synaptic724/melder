from typing import Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import SpellValidationContext
from melder.aether.spellbook.spell_compiler.validation.strategies.annotation_shape_guard_strategy import (
    AnnotationShapeGuardStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.callable_profile_hygiene_strategy import (
    CallableProfileHygieneStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.circular_dependency_strategy import (
    CircularDependencyStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.dangling_dependency_strategy import (
    DanglingDependenciesStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.duplicate_spell_name_strategy import (
    DuplicateSpellNameStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.existing_creation_compatibility_strategy import (
    ExistingCreationCompatibilityStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.parameter_policy_strategy import (
    ParameterPolicyStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.required_holes_strategy import (
    RequiredHolesStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.resolution_frame_presence_strategy import (
    ResolutionFramePresenceStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.self_validation_strategy import (
    SelfDependencyStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.spellmap_shape_validation_strategy import (
    SpellMapShapeValidationStrategy,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
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


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str) -> Optional[object]:
    """
    Purpose:
        Resolve a local Spell instance by its versioned spell id.
    Contract:
        - Returns the spell mapped in the live _spell_id_pool for `spell_id`.
        - Returns None if no matching spell is found.
    Args:
        spellbook: Spellbook holding locally bound spells.
        spell_id: Versioned spell id to locate.
    Returns:
        Spell | None: The resolved spell or None if missing.
    """
    return spellbook._spell_id_pool.get(spell_id)


def _make_context(
    *,
    spell: object,
    spellbook: Spellbook,
    requirements: Optional[object] = None,
    symbolic_graph: Optional[object] = None,
    resolution_frame: Optional[object] = None,
) -> tuple[SpellValidationContext, list]:
    """
    Purpose:
        Build a SpellValidationContext bound to a real Spellbook.
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
    context = SpellValidationContext(
        spell=spell,
        spellbook=spellbook,
        requirements=requirements,
        symbolic_graph=symbolic_graph,
        resolution_frame=resolution_frame,
        cancel_event=None,
        issues=issues,
    )
    return context, issues


def test_component_annotation_shape_guard_flags_unsupported_collection_shape() -> None:
    """
    Purpose:
        Validate AnnotationShapeGuardStrategy flags unsupported collection annotations.
    Contract:
        - set[T] DI annotations yield UNSUPPORTED_COLLECTION_SHAPE errors.
    Returns:
        None.
    Raises:
        AssertionError: If the unsupported collection shape is not reported.
    """
    spellbook = _make_spellbook()
    strategy = AnnotationShapeGuardStrategy()

    class UsesSet:
        """
        Purpose:
            Provide a spell with an unsupported collection DI annotation.
        Contract:
            - Declares set[BasicService] as a DI dependency.
        Args:
            services: Injected services collection.
        """

        def __init__(self, services: set[BasicService]) -> None:
            """
            Purpose:
                Capture the injected services.
            Contract:
                Stores the services on the instance.
            Args:
                services: Collection of services.
            Returns:
                None.
            """
            self.services = services

    try:
        spell_id = spellbook.bind(
            spell=UsesSet,
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
            assert issue.code == "UNSUPPORTED_COLLECTION_SHAPE"
            assert issue.severity == "error"
        finally:
            context.cleanup()
    finally:
        strategy.cleanup()
        spellbook.cleanup()


def test_component_annotation_shape_guard_warns_on_list_non_di_element() -> None:
    """
    Purpose:
        Validate AnnotationShapeGuardStrategy warns on list elements that are not DI targets.
    Contract:
        - list[int] yields LIST_ELEMENT_NOT_DI_TARGET warnings.
    Returns:
        None.
    Raises:
        AssertionError: If the expected warning is not reported.
    """
    spellbook = _make_spellbook()
    strategy = AnnotationShapeGuardStrategy()

    class UsesList:
        """
        Purpose:
            Provide a spell with a list annotation that is not DI-eligible.
        Contract:
            - Declares list[int] as a plain parameter.
        Args:
            values: Plain list of ints.
        """

        def __init__(self, values: list[int]) -> None:
            """
            Purpose:
                Capture the values list.
            Contract:
                Stores the values on the instance.
            Args:
                values: Plain list input.
            Returns:
                None.
            """
            self.values = values

    try:
        spell_id = spellbook.bind(
            spell=UsesList,
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
            assert issue.code == "LIST_ELEMENT_NOT_DI_TARGET"
            assert issue.severity == "warning"
        finally:
            context.cleanup()
    finally:
        strategy.cleanup()
        spellbook.cleanup()


def test_component_spellmap_shape_validation_flags_missing_target() -> None:
    """
    Purpose:
        Validate SpellMapShapeValidationStrategy flags missing SpellMap targets.
    Contract:
        - SpellMap defaults with no spell/spellframe yield SPELLMAP_MISSING_TARGET errors.
    Returns:
        None.
    Raises:
        AssertionError: If the missing target is not reported.
    """
    spellbook = _make_spellbook()
    strategy = SpellMapShapeValidationStrategy()
    spellmap = SpellMap(spell=BasicService)
    spellmap.spell = None
    spellmap.spellframe = None

    class UsesSpellMap:
        """
        Purpose:
            Provide a spell with a malformed SpellMap default.
        Contract:
            - Uses a SpellMap missing both spell and spellframe.
        Args:
            service: SpellMap placeholder.
        """

        def __init__(self, service: SpellMap = spellmap) -> None:
            """
            Purpose:
                Capture the service placeholder.
            Contract:
                Stores the service on the instance.
            Args:
                service: SpellMap placeholder.
            Returns:
                None.
            """
            self.service = service

    try:
        spell_id = spellbook.bind(
            spell=UsesSpellMap,
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
            assert issue.code == "SPELLMAP_MISSING_TARGET"
            assert issue.severity == "error"
        finally:
            context.cleanup()
    finally:
        strategy.cleanup()
        spellbook.cleanup()


def test_component_spellmap_shape_validation_warns_on_non_normalized_binding_name() -> None:
    """
    Purpose:
        Validate SpellMapShapeValidationStrategy warns on non-normalized binding names.
    Contract:
        - Non-normalized binding names yield SPELLMAP_BINDING_NAME_NOT_NORMALIZED warnings.
    Returns:
        None.
    Raises:
        AssertionError: If the expected warning is not reported.
    """
    spellbook = _make_spellbook()
    strategy = SpellMapShapeValidationStrategy()
    spellmap = SpellMap(spell=BasicService, binding_name="primary")
    spellmap.binding_name = "Primary"

    class UsesSpellMap:
        """
        Purpose:
            Provide a spell with a SpellMap using a non-normalized binding name.
        Contract:
            - Uses binding_name with uppercase letters.
        Args:
            service: SpellMap placeholder.
        """

        def __init__(self, service: SpellMap = spellmap) -> None:
            """
            Purpose:
                Capture the service placeholder.
            Contract:
                Stores the service on the instance.
            Args:
                service: SpellMap placeholder.
            Returns:
                None.
            """
            self.service = service

    try:
        spell_id = spellbook.bind(
            spell=UsesSpellMap,
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
            assert issue.code == "SPELLMAP_BINDING_NAME_NOT_NORMALIZED"
            assert issue.severity == "warning"
        finally:
            context.cleanup()
    finally:
        strategy.cleanup()
        spellbook.cleanup()


def test_component_callable_profile_hygiene_flags_missing_profile() -> None:
    """
    Purpose:
        Validate CallableProfileHygieneStrategy flags missing binding profiles.
    Contract:
        - Missing binding profiles yield MISSING_BINDING_PROFILE errors.
    Returns:
        None.
    Raises:
        AssertionError: If the missing profile is not reported.
    """
    spellbook = _make_spellbook()
    strategy = CallableProfileHygieneStrategy()
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spell.profile = None
        context, issues = _make_context(spell=spell, spellbook=spellbook)
        try:
            strategy.validate(context)
            assert len(issues) == 1
            issue = issues[0]
            assert issue.code == "MISSING_BINDING_PROFILE"
            assert issue.severity == "error"
        finally:
            context.cleanup()
    finally:
        strategy.cleanup()
        spellbook.cleanup()


def test_component_parameter_policy_strategy_flags_variadic_di_annotations() -> None:
    """
    Purpose:
        Validate ParameterPolicyStrategy flags variadic DI annotations.
    Contract:
        - Variadic parameters annotated for DI yield VARIADIC_DI_UNSUPPORTED errors.
    Returns:
        None.
    Raises:
        AssertionError: If the variadic DI issue is not reported.
    """
    spellbook = _make_spellbook()
    strategy = ParameterPolicyStrategy()

    class UsesVariadic:
        """
        Purpose:
            Provide a spell with a variadic DI annotation.
        Contract:
            - Declares *handlers: BasicService, which is unsupported for DI.
        Args:
            handlers: Variadic DI annotations.
        """

        def __init__(self, *handlers: BasicService) -> None:
            """
            Purpose:
                Capture the variadic handlers.
            Contract:
                Stores the handlers on the instance.
            Args:
                handlers: Variadic handlers.
            Returns:
                None.
            """
            self.handlers = handlers

    try:
        spell_id = spellbook.bind(
            spell=UsesVariadic,
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
            assert issue.code == "VARIADIC_DI_UNSUPPORTED"
            assert issue.severity == "error"
        finally:
            context.cleanup()
    finally:
        strategy.cleanup()
        spellbook.cleanup()


def test_component_existing_creation_compatibility_flags_missing_instance() -> None:
    """
    Purpose:
        Validate ExistingCreationCompatibilityStrategy flags missing instances.
    Contract:
        - Existing-creation spells with no instance yield EXISTING_CREATION_MISSING_INSTANCE errors.
    Returns:
        None.
    Raises:
        AssertionError: If the missing instance is not reported.
    """
    spellbook = _make_spellbook()
    strategy = ExistingCreationCompatibilityStrategy()
    existing = BasicService()

    try:
        spell_id = spellbook.bind(
            spell=existing,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spell.run_phase_requirements()
        spell.user_created_object = None

        context, issues = _make_context(
            spell=spell,
            spellbook=spellbook,
            requirements=spell.requirements,
        )
        try:
            strategy.validate(context)
            assert len(issues) == 1
            issue = issues[0]
            assert issue.code == "EXISTING_CREATION_MISSING_INSTANCE"
            assert issue.severity == "error"
        finally:
            context.cleanup()
    finally:
        strategy.cleanup()
        spellbook.cleanup()

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


def test_component_required_holes_strategy_ignores_injected_and_defaulted_parameters() -> None:
    """
    Purpose:
        Validate RequiredHolesStrategy reports only caller-required plain parameters.
    Contract:
        - Injected dependencies and defaulted plain parameters are ignored.
        - Only required plain parameters emit REQUIRED_HOLE warnings.
    Returns:
        None.
    Raises:
        AssertionError: If the wrong parameter is reported as a required hole.
    """
    spellbook = _make_spellbook()
    strategy = RequiredHolesStrategy()

    class MixedInputs:
        """
        Purpose:
            Provide a spell with DI, defaulted, and caller-required parameters.
        Contract:
            - `service` is satisfiable through DI when BasicService is bound.
            - `required_value` remains a caller-required plain parameter.
            - `optional_value` is defaulted and must not be reported as a hole.
        Args:
            service: Injected service dependency.
            required_value: Caller-supplied plain parameter with no default.
            optional_value: Defaulted plain parameter.
        """

        def __init__(
                self,
                service: BasicService,
                required_value: int,
                optional_value: int = 7,
        ) -> None:
            """
            Purpose:
                Capture the mixed input set for requirements analysis.
            Contract:
                Stores the provided constructor inputs without mutation.
            Args:
                service: Injected service dependency.
                required_value: Caller-required plain parameter.
                optional_value: Defaulted plain parameter.
            Returns:
                None.
            """
            self.service = service
            self.required_value = required_value
            self.optional_value = optional_value

    try:
        spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell_id = spellbook.bind(
            spell=MixedInputs,
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
            assert issue.details["parameter_name"] == "required_value"
            assert issue.details["position"] == 1
            assert issue.details["annotation"] is int
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
            binding_name="secondary",
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
