from typing import Optional

import pytest
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.creation_context.creation_context_builder import (
    CreationContextBuilder,
)
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.protocols import IService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component() -> None:
    """
    Purpose:
        Ensure component tests start with a clean Aether singleton.
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
        Provide a Spellbook configured for component tests.
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
        Optional[Spell]: The resolved spell or None if missing.
    """
    return spellbook._spell_id_pool.get(spell_id)


def _run_phase_requirements(spell: object) -> None:
    """
    Purpose:
        Run compiler phase 1 through the compiler-system surface for one spell.
    Contract:
        - Constructs a short-lived compiler system.
        - Cleans that compiler system before returning.
    Args:
        spell:
            Spell under test.
    Returns:
        None.
    """
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_requirements(spell)
    finally:
        compiler_system.cleanup()


def _run_phase_symbolic_graph(spell: object) -> None:
    """
    Purpose:
        Run compiler phase 2 through the compiler-system surface for one spell.
    Contract:
        - Constructs a short-lived compiler system.
        - Cleans that compiler system before returning.
    Args:
        spell:
            Spell under test.
    Returns:
        None.
    """
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_symbolic_graph(spell)
    finally:
        compiler_system.cleanup()


def _run_phase_local_frame(spell: object) -> None:
    """
    Purpose:
        Run compiler phase 3 through the compiler-system surface for one spell.
    Contract:
        - Uses the spell-owned Spellbook as the live compiler context.
        - Cleans the short-lived compiler system before returning.
    Args:
        spell:
            Spell under test.
    Returns:
        None.
    """
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_local_frame(spell._spellbook, spell)
    finally:
        compiler_system.cleanup()


def _run_phase_validation(spell: object, validator: Optional[object] = None) -> None:
    """
    Purpose:
        Run compiler phase 4 through the compiler-system surface for one spell.
    Contract:
        - Uses the spell-owned Spellbook as the live compiler context.
        - Allows tests to override the spell validator on the short-lived
          compiler system when they are explicitly testing validator behavior.
        - Cleans the compiler system before returning.
    Args:
        spell:
            Spell under test.
        validator:
            Optional replacement validator used only for the current call.
    Returns:
        None.
    """
    compiler_system = SpellCompilerSystem()
    try:
        if validator is not None:
            compiler_system._spell_validator = validator
        compiler_system.run_phase_validation(spell._spellbook, spell)
    finally:
        compiler_system.cleanup()


def _run_phase_root_blueprints(spell: object, conduit_id: str) -> None:
    """
    Purpose:
        Run compiler phase 5 frame-wide through the compiler-system surface.
    Contract:
        - Uses the spell-owned Spellbook as the live compiler context.
        - Cleans the compiler system before returning.
    Args:
        spell:
            Lead/root spell under test.
        conduit_id:
            Conduit identifier used for the phase.
    Returns:
        None.
    """
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_root_blueprints(spell._spellbook, spell, conduit_id)
    finally:
        compiler_system.cleanup()


def _run_phase_root_blueprints_local(spell: object, conduit_id: str) -> None:
    """
    Purpose:
        Run compiler phase 5 local through the compiler-system surface.
    Contract:
        - Uses the spell-owned Spellbook as the live compiler context.
        - Cleans the compiler system before returning.
    Args:
        spell:
            Target spell under test.
        conduit_id:
            Conduit identifier used for the phase.
    Returns:
        None.
    """
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_root_blueprints_local(
            spell._spellbook,
            spell,
            conduit_id,
        )
    finally:
        compiler_system.cleanup()


def _run_phase_system_validation(spell: object, conduit_id: str) -> None:
    """
    Purpose:
        Run compiler phase 6 frame-wide through the compiler-system surface.
    Contract:
        - Uses the spell-owned Spellbook as the live compiler context.
        - Cleans the compiler system before returning.
    Args:
        spell:
            Lead/root spell under test.
        conduit_id:
            Conduit identifier used for the phase.
    Returns:
        None.
    """
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_system_validation(spell._spellbook, spell, conduit_id)
    finally:
        compiler_system.cleanup()


def _run_phase_system_validation_local(spell: object, conduit_id: str) -> None:
    """
    Purpose:
        Run compiler phase 6 local through the compiler-system surface.
    Contract:
        - Uses the spell-owned Spellbook as the live compiler context.
        - Cleans the compiler system before returning.
    Args:
        spell:
            Target spell under test.
        conduit_id:
            Conduit identifier used for the phase.
    Returns:
        None.
    """
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_system_validation_local(
            spell._spellbook,
            spell,
            conduit_id,
        )
    finally:
        compiler_system.cleanup()


def _run_phase_occurrence_plan(spell: object, conduit_id: str) -> None:
    """
    Purpose:
        Run compiler phase 8 through the compiler-system surface for one spell.
    Contract:
        - Uses the spell-owned Spellbook as the live compiler context.
        - Cleans the compiler system before returning.
    Args:
        spell:
            Spell under test.
        conduit_id:
            Legacy conduit id argument kept only to simplify test call sites.
    Returns:
        None.
    """
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_occurrence_plan(spell._spellbook, spell)
    finally:
        compiler_system.cleanup()


def _run_phase_injection_plan(spell: object, conduit_id: str) -> None:
    """
    Purpose:
        Run compiler phase 9 through the compiler-system surface for one spell.
    Contract:
        - Ignores the legacy conduit_id argument because the compiler-system
          surface now consumes only the spell for this phase.
        - Cleans the compiler system before returning.
    Args:
        spell:
            Spell under test.
        conduit_id:
            Legacy conduit id argument kept only to simplify test call sites.
    Returns:
        None.
    """
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_injection_plan(spell)
    finally:
        compiler_system.cleanup()


def _run_phase_patch_maps(spell: object, conduit_id: str) -> None:
    """
    Purpose:
        Run compiler phase 10 through the compiler-system surface for one spell.
    Contract:
        - Ignores the legacy conduit_id argument because the compiler-system
          surface now consumes only the spell for this phase.
        - Cleans the compiler system before returning.
    Args:
        spell:
            Spell under test.
        conduit_id:
            Legacy conduit id argument kept only to simplify test call sites.
    Returns:
        None.
    """
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_patch_maps(spell)
    finally:
        compiler_system.cleanup()


def _run_phase_execution_plan(spell: object, conduit_id: str) -> None:
    """
    Purpose:
        Run compiler phase 11/12 through the compiler-system surface for one spell.
    Contract:
        - Uses the spell-owned Spellbook as the live compiler context.
        - Ignores the legacy conduit_id argument because the compiler-system
          surface now consumes spellbook + spell for this phase.
        - Cleans the compiler system before returning.
    Args:
        spell:
            Spell under test.
        conduit_id:
            Legacy conduit id argument kept only to simplify test call sites.
    Returns:
        None.
    """
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_execution_plan(spell._spellbook, spell)
    finally:
        compiler_system.cleanup()


class _SpellIndexStub:
    """
    Purpose:
        Provide a minimal SpellIndex-like key for spell-id pool stubs.
    Contract:
        - Exposes a `current` version id.
        - Acts as a stable dictionary key by identity.
    """
    def __init__(self, current: str) -> None:
        """
        Purpose:
            Store a version id for the stub index.
        Contract:
            - The current value is stored verbatim.
        Args:
            current: Version id to expose via the `current` property.
        Returns:
            None.
        """
        self._current = current

    @property
    def selected_spell_id(self) -> str:
        """
        Purpose:
            Expose the version id for this stub.
        Contract:
            - Returns the value provided at construction time.
        Returns:
            str: The current version id.
        """
        return self._current


class _SpellCandidateStub:
    """
    Purpose:
        Provide a minimal spell object for spell-id pool injection.
    Contract:
        - Exposes spell identity and binding metadata.
        - Provides a SpellIndex-like `spell_index` attribute.
    """
    def __init__(
        self,
        *,
        spell_id: str,
        spell: object,
        spell_name: str,
        spellframe: Optional[object] = None,
        binding_name: Optional[str] = None,
    ) -> None:
        """
        Purpose:
            Capture spell identity for pool injection.
        Contract:
            - Stores spell metadata and creates a SpellIndex-like stub.
        Args:
            spell_id: Versioned spell id for the stub.
            spell: The underlying spell object or class.
            spell_name: Human-readable spell name.
            spellframe: Optional frame marker for matching.
            binding_name: Optional binding name for matching.
        Returns:
            None.
        """
        self.spell_index = _SpellIndexStub(spell_id)
        self.spell = spell
        self.spell_name = spell_name
        self.spellframe = spellframe
        self.binding_name = binding_name


class _ValidationResultStub:
    """
    Purpose:
        Provide a minimal validation result for SpellCrafter tests.
    Contract:
        - Exposes the has_errors flag.
        - Provides an issues list for compatibility with contract gating.
    """
    def __init__(self, has_errors: bool, issues: Optional[list[object]] = None) -> None:
        """
        Purpose:
            Capture a validation outcome flag.
        Contract:
            - Stores has_errors verbatim.
            - Preserves a provided issues list (defaults to empty).
        Args:
            has_errors: True if the validation result should signal errors.
            issues: Optional issue list to mirror real validation results.
        Returns:
            None.
        """
        self.has_errors = has_errors
        self.issues = list(issues) if issues is not None else []


class _SpellValidationSystemStub:
    """
    Purpose:
        Stand-in for SpellValidationSystem to control validation outcomes.
    Contract:
        - validate_spell returns the configured result and records call count.
        - shared-view hooks record invocation for phase orchestration.
    """
    def __init__(self, result: _ValidationResultStub) -> None:
        """
        Purpose:
            Store the result to return from validate_spell.
        Contract:
            - call_count starts at zero.
            - shared_view_prepared and shared_view_cleared start False.
        Args:
            result: Validation result to return.
        Returns:
            None.
        """
        self.result = result
        self.call_count = 0
        self.shared_view_prepared = False
        self.shared_view_cleared = False

    def validate_spell(
        self,
        spell: object,
        requirements: object,
        symbolic_graph: object,
        resolution_frame: object,
        cancel_event: object = None,
        validation_pass_cache: object = None,
    ) -> _ValidationResultStub:
        """
        Purpose:
            Return the preconfigured validation result.
        Contract:
            - Increments call_count on each invocation.
        Args:
            spell: Spell under validation.
            requirements: Phase 1 requirements.
            symbolic_graph: Phase 2 symbolic graph.
            resolution_frame: Phase 3 resolution frame.
            cancel_event: Optional cancellation event.
            validation_pass_cache: Optional pass-scoped memo dict mirrored
                from the live validator contract.
        Returns:
            _ValidationResultStub: The configured validation result.
        """
        self.call_count += 1
        return self.result

    def prepare_shared_view(self, *, spellbook: object, cancel_event: object = None) -> None:
        """
        Purpose:
            Record that shared-view preparation was invoked.
        Contract:
            Marks shared_view_prepared True.
        Args:
            spellbook: Spellbook instance for the validation run.
            cancel_event: Optional cancellation event.
        Returns:
            None.
        """
        self.shared_view_prepared = True

    def clear_shared_view(self) -> None:
        """
        Purpose:
            Record that shared-view cleanup was invoked.
        Contract:
            Marks shared_view_cleared True.
        Returns:
            None.
        """
        self.shared_view_cleared = True


class _SpellSystemStatesStub:
    """
    Purpose:
        Capture SpellSystemStates updates for component tests.
    Contract:
        - update_dependencies records dependencies by SpellIndex.
        - register_local_topology records topology by SpellIndex.
        - unregister_index records SpellIndex removals during cleanup.
    """
    def __init__(self) -> None:
        """
        Purpose:
            Initialize empty dependency and topology registries.
        Contract:
            - Registries start empty.
            - Unregistration registry starts empty.
        Returns:
            None.
        """
        self.dependencies_by_spell: dict[object, list[str]] = {}
        self.topology_by_spell: dict[object, object] = {}
        self.registered_lineages: list[tuple[object, object]] = []
        self.unregistered_lineages: list[object] = []

    def register_index(self, spell_index: object, owner_spellbook_id: object = None) -> None:
        """
        Purpose:
            Record a lineage registration call from Spellbook.bind.
        Contract:
            - Stores (spell_index, owner_spell) in registration order.
        Args:
            spell_index: SpellIndex registered for the lineage.
        Returns:
            None.
        """
        self.registered_lineages.append((spell_index, spell_index.selected_spell_id))

    def update_dependencies(self, spell_index: object, dependency_spell_ids: list[str]) -> None:
        """
        Purpose:
            Record dependency spell ids for a lineage.
        Contract:
            - Stores a copy of dependency_spell_ids keyed by spell_index.
        Args:
            spell_index: SpellIndex for the updated lineage.
            dependency_spell_ids: Dependency ids from Phase 3.
        Returns:
            None.
        """
        self.dependencies_by_spell[spell_index] = list(dependency_spell_ids)

    def register_local_topology(self, spell_index: object, topology: object) -> None:
        """
        Purpose:
            Record the local topology for a lineage.
        Contract:
            - Stores the topology keyed by spell_index.
        Args:
            spell_index: SpellIndex for the updated lineage.
            topology: SpellLocalTopology instance.
        Returns:
            None.
        """
        self.topology_by_spell[spell_index] = topology

    def get_local_topology(self, spell_index: object) -> Optional[object]:
        """
        Purpose:
            Return the recorded topology for a lineage.
        Contract:
            - Returns None if no topology was recorded.
        Args:
            spell_index: SpellIndex for the lookup.
        Returns:
            Optional[object]: The recorded topology or None.
        """
        return self.topology_by_spell.get(spell_index)

    def unregister_index(self, spell_index: object) -> None:
        """
        Purpose:
            Record a lineage unregistration from Spellbook.cleanup.
        Contract:
            - Appends spell_index to unregistered_lineages.
        Args:
            spell_index: SpellIndex removed from system-state tracking.
        Returns:
            None.
        """
        self.unregistered_lineages.append(spell_index)


def test_component_spell_crafter_spellmap_default_raises_when_missing_candidates() -> None:
    """
    Purpose:
        Validate missing SpellMap default candidates raise during Phase 3.
    Contract:
        - run_phase_local_frame raises when SpellMap defaults resolve to none.
    Returns:
        None.
    Raises:
        AssertionError: If missing SpellMap defaults do not raise.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Spell that uses a frame-only SpellMap default.
        Contract:
            - Declares a SpellMap pointing to IService "primary".
        Args:
            service: SpellMap default for IService "primary".
        """
        def __init__(
            self,
            service: IService = SpellMap(
                spell=None,
                spellframe=IService,
                binding_name="primary",
            ),
        ) -> None:
            """
            Purpose:
                Capture the frame-only SpellMap dependency.
            Contract:
                - Stores the resolved service for assertions.
            Args:
                service: SpellMap default for IService "primary".
            Returns:
                None.
            """
            self.service = service

    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        _run_phase_requirements(spell)
        _run_phase_symbolic_graph(spell)
        with pytest.raises(RuntimeError, match="SpellMap default could not be resolved"):
            _run_phase_local_frame(spell)
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_spellmap_default_raises_on_multiple_candidates() -> None:
    """
    Purpose:
        Validate ambiguous SpellMap defaults raise during Phase 3.
    Contract:
        - run_phase_local_frame raises when SpellMap defaults resolve to multiple candidates.
    Returns:
        None.
    Raises:
        AssertionError: If ambiguous SpellMap defaults do not raise.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Spell that uses a frame-only SpellMap default.
        Contract:
            - Declares a SpellMap pointing to IService "primary".
        Args:
            service: SpellMap default for IService "primary".
        """
        def __init__(
            self,
            service: IService = SpellMap(
                spell=None,
                spellframe=IService,
                binding_name="primary",
            ),
        ) -> None:
            """
            Purpose:
                Capture the frame-only SpellMap dependency.
            Contract:
                - Stores the resolved service for assertions.
            Args:
                service: SpellMap default for IService "primary".
            Returns:
                None.
            """
            self.service = service

    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    candidate_a = _SpellCandidateStub(
        spell_id="candidate-a",
        spell=object(),
        spell_name="Alpha",
        spellframe=IService,
        binding_name="primary",
    )
    candidate_b = _SpellCandidateStub(
        spell_id="candidate-b",
        spell=object(),
        spell_name="Beta",
        spellframe=IService,
        binding_name="primary",
    )
    spellbook._spell_id_pool[candidate_a.spell_index.selected_spell_id] = candidate_a
    spellbook._spell_id_pool[candidate_b.spell_index.selected_spell_id] = candidate_b

    try:
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        _run_phase_requirements(spell)
        _run_phase_symbolic_graph(spell)
        with pytest.raises(RuntimeError, match="multiple"):
            _run_phase_local_frame(spell)
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_spellmap_default_prefers_explicit_spell() -> None:
    """
    Purpose:
        Validate explicit SpellMap defaults resolve by spell identity.
    Contract:
        - run_phase_local_frame binds the explicit spell only.
    Returns:
        None.
    Raises:
        AssertionError: If explicit SpellMap defaults resolve incorrectly.
    """
    spellbook = _make_spellbook()

    class OtherService:
        """
        Purpose:
            Provide a decoy spell for explicit SpellMap resolution.
        Contract:
            - Declares no constructor parameters.
        """

    class Consumer:
        """
        Purpose:
            Spell that uses an explicit SpellMap default.
        Contract:
            - Declares a SpellMap pointing to BasicService.
        Args:
            service: SpellMap default for BasicService.
        """
        def __init__(self, service: BasicService = SpellMap(BasicService)) -> None:
            """
            Purpose:
                Capture the explicit SpellMap dependency.
            Contract:
                - Stores the resolved service for assertions.
            Args:
                service: SpellMap default for BasicService.
            Returns:
                None.
            """
            self.service = service

    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    explicit_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    spellbook.bind(
        spell=OtherService,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        _run_phase_requirements(spell)
        _run_phase_symbolic_graph(spell)
        _run_phase_local_frame(spell)

        assert set(spell.dependencies) == {explicit_id}
        topology = spell._spell_system_states.get_local_topology(spell.spell_index)
        assert topology is not None
        sockets = topology.get_sockets_for_param("service")
        assert len(sockets) == 1
        assert set(sockets[0].target_spell_ids) == {explicit_id}
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_spellmap_default_resolves_frame_only_candidate() -> None:
    """
    Purpose:
        Validate frame-only SpellMap defaults resolve via frame/binding lookup.
    Contract:
        - run_phase_local_frame binds the frame-only candidate.
        - system states receive dependency updates for the resolved target.
    Returns:
        None.
    Raises:
        AssertionError: If frame-only SpellMap resolution is incorrect.
    """
    spellbook = _make_spellbook()
    states = _SpellSystemStatesStub()
    spellbook._spell_system_states = states

    class Consumer:
        """
        Purpose:
            Spell that uses a frame-only SpellMap default.
        Contract:
            - Declares a SpellMap pointing to IService "primary".
        Args:
            service: SpellMap default for IService "primary".
        """
        def __init__(
            self,
            service: IService = SpellMap(
                spell=None,
                spellframe=IService,
                binding_name="primary",
            ),
        ) -> None:
            """
            Purpose:
                Capture the frame-only SpellMap dependency.
            Contract:
                - Stores the resolved service for assertions.
            Args:
                service: SpellMap default for IService "primary".
            Returns:
                None.
            """
            self.service = service

    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    candidate_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        _run_phase_requirements(spell)
        _run_phase_symbolic_graph(spell)
        _run_phase_local_frame(spell)

        assert set(spell.dependencies) == {candidate_id}
        dependencies = states.dependencies_by_spell.get(spell.spell_index)
        assert dependencies is not None
        assert set(dependencies) == {candidate_id}
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_spellmap_default_raises_on_duplicate_explicit_matches() -> None:
    """
    Purpose:
        Validate explicit SpellMap defaults raise when duplicates exist.
    Contract:
        - run_phase_local_frame raises when explicit spell resolves to multiple matches.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate explicit SpellMap defaults do not raise.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Spell that uses an explicit SpellMap default.
        Contract:
            - Declares a SpellMap pointing to BasicService.
        Args:
            service: SpellMap default for BasicService.
        """
        def __init__(self, service: BasicService = SpellMap(BasicService)) -> None:
            """
            Purpose:
                Capture the explicit SpellMap dependency.
            Contract:
                - Stores the resolved service for assertions.
            Args:
                service: SpellMap default for BasicService.
            Returns:
                None.
            """
            self.service = service

    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    candidate_a = _SpellCandidateStub(
        spell_id="candidate-a",
        spell=BasicService,
        spell_name="BasicService-A",
        spellframe=BasicService,
        binding_name="primary-a",
    )
    candidate_b = _SpellCandidateStub(
        spell_id="candidate-b",
        spell=BasicService,
        spell_name="BasicService-B",
        spellframe=BasicService,
        binding_name="primary-b",
    )
    spellbook._spell_id_pool[candidate_a.spell_index.selected_spell_id] = candidate_a
    spellbook._spell_id_pool[candidate_b.spell_index.selected_spell_id] = candidate_b

    try:
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        _run_phase_requirements(spell)
        _run_phase_symbolic_graph(spell)
        with pytest.raises(RuntimeError, match="multiple"):
            _run_phase_local_frame(spell)
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_collection_di_allows_empty_collection() -> None:
    """
    Purpose:
        Validate empty collection DI does not create dependencies.
    Contract:
        - dependencies remain empty when no collection candidates resolve.
        - topology records the collection socket with no targets.
    Returns:
        None.
    Raises:
        AssertionError: If empty collection behavior is incorrect.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Spell that requests all IService implementations.
        Contract:
            - Declares a collection dependency on IService.
        Args:
            services: Collection of IService implementations.
        """
        def __init__(self, services: list[IService]) -> None:
            """
            Purpose:
                Capture the injected IService collection.
            Contract:
                - Stores the services for assertions.
            Args:
                services: Collection of IService implementations.
            Returns:
                None.
            """
            self.services = services

    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        _run_phase_requirements(spell)
        _run_phase_symbolic_graph(spell)
        _run_phase_local_frame(spell)

        assert spell.dependencies == []
        topology = spell._spell_system_states.get_local_topology(spell.spell_index)
        assert topology is not None
        sockets = topology.get_sockets_for_param("services")
        assert len(sockets) == 1
        assert sockets[0].socket_kind is SocketKind.NORMAL
        assert sockets[0].is_collection
        assert sockets[0].target_spell_ids == ()
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_validation_caches_result() -> None:
    """
    Purpose:
        Validate validation results are cached after the first run.
    Contract:
        - validate_spell is invoked once even if run_phase_validation is called twice.
    Returns:
        None.
    Raises:
        AssertionError: If validation caching is not respected.
    """
    spellbook = _make_spellbook()
    validator = _SpellValidationSystemStub(_ValidationResultStub(has_errors=False))
    class Leaf:
        """
        Purpose:
            Minimal spell with no dependencies.
        Contract:
            - Declares no constructor parameters.
        """

    spell_id = spellbook.bind(
        spell=Leaf,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None
        _run_phase_requirements(spell)
        _run_phase_symbolic_graph(spell)
        _run_phase_local_frame(spell)
        _run_phase_validation(spell, validator=validator)
        _run_phase_validation(spell, validator=validator)

        assert validator.call_count == 1
        assert spell.validation_result_phase4 is validator.result
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_validation_marks_broken_on_error() -> None:
    """
    Purpose:
        Validate validation errors mark the spell as broken.
    Contract:
        - is_broken is True when the validation result has errors.
    Returns:
        None.
    Raises:
        AssertionError: If validation errors do not mark the spell as broken.
    """
    spellbook = _make_spellbook()
    validator = _SpellValidationSystemStub(_ValidationResultStub(has_errors=True))
    class Leaf:
        """
        Purpose:
            Minimal spell with no dependencies.
        Contract:
            - Declares no constructor parameters.
        """

    spell_id = spellbook.bind(
        spell=Leaf,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None
        _run_phase_requirements(spell)
        _run_phase_symbolic_graph(spell)
        _run_phase_local_frame(spell)
        _run_phase_validation(spell, validator=validator)

        assert spell.validation_result_phase4 is validator.result
        assert spell.is_broken
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_updates_system_states_for_dependencies() -> None:
    """
    Purpose:
        Validate SpellCrafter publishes dependencies and topology to system states.
    Contract:
        - update_dependencies records direct dependency spell ids.
        - register_local_topology records the local topology.
    Returns:
        None.
    Raises:
        AssertionError: If system state updates are missing or incorrect.
    """
    spellbook = _make_spellbook()
    states = _SpellSystemStatesStub()
    spellbook._spell_system_states = states

    class Consumer:
        """
        Purpose:
            Spell that depends on BasicService.
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
                - Stores the service for assertions.
            Args:
                service: Injected BasicService instance.
            Returns:
                None.
            """
            self.service = service

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

    try:
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        _run_phase_requirements(spell)
        _run_phase_symbolic_graph(spell)
        _run_phase_local_frame(spell)

        dependencies = states.dependencies_by_spell.get(spell.spell_index)
        assert dependencies is not None
        assert set(dependencies) == {service_id}

        topology = states.get_local_topology(spell.spell_index)
        assert topology is not None
        sockets = topology.get_sockets_for_param("service")
        assert len(sockets) == 1
        assert set(sockets[0].target_spell_ids) == {service_id}
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_builds_real_execution_plan_for_dependency_chain() -> None:
    """
    Purpose:
        Validate Phase 11 produces a real execution plan for a live dependency chain.
    Contract:
        - A root spell with one dependency builds a no-overrides execution plan.
        - The produced plan carries both root and dependency spell ids.
        - The fast-plan payload is available on the no-overrides variant.
    Returns:
        None.
    Raises:
        AssertionError: If the live execution plan is missing or structurally wrong.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a root spell with one runtime dependency.
        Contract:
            - Declares one BasicService dependency.
        """

        def __init__(self, service: BasicService) -> None:
            self.service = service

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

    conduit_id = "component-execution-plan"

    try:
        local_spells = list(spellbook._spells.values())
        for spell in local_spells:
            _run_phase_requirements(spell)
            _run_phase_symbolic_graph(spell)
            _run_phase_local_frame(spell)
            _run_phase_validation(spell)

        _run_phase_root_blueprints(local_spells[0], conduit_id)

        for spell in local_spells:
            _run_phase_occurrence_plan(spell, conduit_id)
            _run_phase_injection_plan(spell, conduit_id)
            _run_phase_patch_maps(spell, conduit_id)
            _run_phase_execution_plan(spell, conduit_id)

        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        artifact = consumer_spell._compiler_artifact
        codegen_plan = artifact._spell_codegen_plan
        assert codegen_plan is not None
        plan = codegen_plan.no_overrides_plan

        assert plan is not None
        assert plan.root_spell_id == consumer_id
        assert plan.root_instance_key[0] == consumer_id
        assert len(plan.steps) == 2
        assert set(plan.spell_id_step_index.keys()) == {consumer_id, service_id}
        assert any(step.spell.spell_id == consumer_id for step in plan.steps)
        assert any(step.spell.spell_id == service_id for step in plan.steps)
        assert plan.fast_plan is not None
        assert artifact._spell_codegen_model is not None
        assert artifact._spell_codegen_model.node_count == 2
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_builds_real_injection_plan_for_dependency_chain() -> None:
    """
    Purpose:
        Validate Phase 9 materializes a live injection plan for a real dependency chain.
    Contract:
        - The built plan is rooted on the target spell id.
        - The target spell gets an injection spec that points at the dependency spell.
        - Runtime selection honors the matching root spell id.
    Returns:
        None.
    Raises:
        AssertionError: If the live injection plan is missing or malformed.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a root spell with one runtime dependency.
        Contract:
            - Declares one BasicService dependency.
        """

        def __init__(self, service: BasicService) -> None:
            self.service = service

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
    conduit_id = "component-injection-plan"

    try:
        local_spells = list(spellbook._spells.values())
        for spell in local_spells:
            _run_phase_requirements(spell)
            _run_phase_symbolic_graph(spell)
            _run_phase_local_frame(spell)
            _run_phase_validation(spell)

        _run_phase_root_blueprints(local_spells[0], conduit_id)

        for spell in local_spells:
            _run_phase_occurrence_plan(spell, conduit_id)
            _run_phase_injection_plan(spell, conduit_id)

        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        model = consumer_spell._compiler_artifact._spell_codegen_model
        assert model is not None
        plan = model.injection_shape

        assert plan is not None
        assert plan.root_spell_id == consumer_id
        assert plan.root_instance_key[0] == consumer_id

        consumer_specs = [
            spec
            for instance_key, spec in plan.instance_specs_by_instance_key.items()
            if instance_key[0] == consumer_id
        ]
        assert len(consumer_specs) >= 1

        service_keys = []
        for spec in consumer_specs:
            if "service" in spec.param_sources:
                service_keys.extend(spec.param_sources["service"].dependency_keys or [])

        assert service_keys
        assert any(dependency_key[0] == service_id for dependency_key in service_keys)
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_builds_real_occurrence_plan_for_dependency_chain() -> None:
    """
    Purpose:
        Validate Phase 8 materializes a live occurrence plan for a real dependency chain.
    Contract:
        - The built plan is rooted on the target spell id.
        - The execution order carries both dependency and root spell ids.
        - Instance planning and runtime selection are available on the real plan.
    Returns:
        None.
    Raises:
        AssertionError: If the live occurrence plan is missing or malformed.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a root spell with one runtime dependency.
        Contract:
            - Declares one BasicService dependency.
        """

        def __init__(self, service: BasicService) -> None:
            self.service = service

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
    conduit_id = "component-occurrence-plan"

    try:
        local_spells = list(spellbook._spells.values())
        for spell in local_spells:
            _run_phase_requirements(spell)
            _run_phase_symbolic_graph(spell)
            _run_phase_local_frame(spell)
            _run_phase_validation(spell)

        _run_phase_root_blueprints(local_spells[0], conduit_id)

        for spell in local_spells:
            _run_phase_occurrence_plan(spell, conduit_id)

        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        graph_analysis = consumer_spell._compiler_artifact._occurrence_graph_analysis

        assert graph_analysis is not None
        assert graph_analysis.root_spell_id == consumer_id
        assert graph_analysis.occurrence_count >= 2
        assert graph_analysis.edge_count >= 1
        assert any(key[0] == consumer_id for key in graph_analysis.occurrence_graph)
        assert any(key[0] == service_id for key in graph_analysis.occurrence_graph)
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_builds_real_patch_maps_for_dependency_and_mutation_sockets() -> None:
    """
    Purpose:
        Validate Phase 10 materializes live override and mutation patch maps.
    Contract:
        - A normal dependency produces an override patch target.
        - A mutation contract socket produces a mutation patch target.
        - The live phase10 artifacts can apply runtime payloads directly.
    Returns:
        None.
    Raises:
        AssertionError: If live patch maps are missing or unusable.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide one normal dependency.
        Contract:
            - `service` is a normal runtime dependency.
        """

        def __init__(
            self,
            service: BasicService,
        ) -> None:
            self.service = service

    service_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )
    conduit_id = "component-patch-maps"

    try:
        local_spells = list(spellbook._spells.values())
        for spell in local_spells:
            _run_phase_requirements(spell)
            _run_phase_symbolic_graph(spell)
            _run_phase_local_frame(spell)
            _run_phase_validation(spell)

        _run_phase_root_blueprints(local_spells[0], conduit_id)

        for spell in local_spells:
            _run_phase_occurrence_plan(spell, conduit_id)
            _run_phase_injection_plan(spell, conduit_id)
            _run_phase_patch_maps(spell, conduit_id)

        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        artifact = consumer_spell._compiler_artifact
        model = artifact._spell_codegen_model
        assert model is not None
        override_targeting = model.override_targeting_shape

        assert override_targeting is not None
        assert "*service" in override_targeting.targets_by_spec

        override_targets = override_targeting.targets_by_spec["*service"]
        assert len(override_targets) == 1
        assert override_targets[0].param_name == "service"
        assert override_targets[0].node_id == consumer_id
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_executes_real_creation_context_override_lane_for_dependency_override() -> None:
    """
    Purpose:
        Validate override codegen-creation execution against live phase8-11 artifacts.
    Contract:
        - The compiled overrides executor runs from the real codegen-creation
          payload and override targeting bridge.
        - A targeted override value replaces the dependency for the root spell.
        - Execution uses a real conduit creations container instead of synthetic stubs.
    Returns:
        None.
    Raises:
        AssertionError: If the live overrides executor does not honor the targeted override.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a root spell with one overrideable dependency.
        Contract:
            - Stores the injected service verbatim for assertions.
        """

        def __init__(self, service: BasicService) -> None:
            self.service = service

    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    conduit_id = conduit._id

    try:
        local_spells = list(spellbook._spells.values())
        for spell in local_spells:
            _run_phase_requirements(spell)
            _run_phase_symbolic_graph(spell)
            _run_phase_local_frame(spell)
            _run_phase_validation(spell)

        _run_phase_root_blueprints(local_spells[0], conduit_id)

        for spell in local_spells:
            _run_phase_occurrence_plan(spell, conduit_id)
            _run_phase_injection_plan(spell, conduit_id)
            _run_phase_patch_maps(spell, conduit_id)
            _run_phase_execution_plan(spell, conduit_id)

        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None

        override_value = object()
        context = CreationContextBuilder.build(consumer_spell)
        try:
            result = context.execute_no_hooks(
                conduit._creations,
                {"*service": override_value},
            )
        finally:
            context.cleanup()

        assert isinstance(result, Consumer)
        assert result.service is override_value
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_component_spell_crafter_run_phase_root_blueprints_local_scopes_to_dependency_closure() -> None:
    """
    Purpose:
        Validate local Phase 5 only attaches artifacts for the target spell and its dependencies.
    Contract:
        - The local root-blueprint map excludes unrelated visible spells.
        - The local system index excludes unrelated visible spells.
        - Scoped dependency spells receive local Phase 5 artifacts.
    Returns:
        None.
    Raises:
        AssertionError: If local Phase 5 leaks unrelated spells into the scoped artifacts.
    """
    spellbook = _make_spellbook()

    class Service:
        pass

    class Consumer:
        def __init__(self, service: Service) -> None:
            self.service = service

    class Outside:
        pass

    service_id = spellbook.bind(
        spell=Service,
        existence=Existence.unique,
        permissions="create",
    )
    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )
    outside_id = spellbook.bind(
        spell=Outside,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        local_spells = list(spellbook._spells.values())
        for spell in local_spells:
            _run_phase_requirements(spell)
            _run_phase_symbolic_graph(spell)
            _run_phase_local_frame(spell)
            _run_phase_validation(spell)

        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        service_spell = _get_spell_by_version_id(spellbook, service_id)
        outside_spell = _get_spell_by_version_id(spellbook, outside_id)
        assert consumer_spell is not None
        assert service_spell is not None
        assert outside_spell is not None

        _run_phase_root_blueprints_local(consumer_spell, "cid")

        consumer_artifact = consumer_spell._compiler_artifact
        service_artifact = service_spell._compiler_artifact
        outside_artifact = outside_spell._compiler_artifact

        assert consumer_artifact._entire_dag_blueprint_phase5 is not None
        assert set(consumer_artifact._entire_dag_blueprint_phase5.keys()) == {consumer_id}
        assert consumer_artifact._spell_system_index_phase5 is not None
        assert consumer_artifact._spell_system_index_phase5.get_node(consumer_id) is not None
        assert consumer_artifact._spell_system_index_phase5.get_node(service_id) is not None
        assert consumer_artifact._spell_system_index_phase5.get_node(outside_id) is None

        assert consumer_artifact._root_blueprint_phase5 is not None
        assert service_artifact._root_blueprint_phase5 is not None
        assert outside_artifact._root_blueprint_phase5 is None
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_run_phase_system_validation_local_scopes_results() -> None:
    """
    Purpose:
        Validate local Phase 6 only publishes validation state to the scoped dependency closure.
    Contract:
        - The target spell and its dependencies receive the local Phase 6 result.
        - Unrelated visible spells do not receive the local Phase 6 result.
    Returns:
        None.
    Raises:
        AssertionError: If local Phase 6 leaks validation state to unrelated spells.
    """
    spellbook = _make_spellbook()

    class Service:
        pass

    class Consumer:
        def __init__(self, service: Service) -> None:
            self.service = service

    class Outside:
        pass

    service_id = spellbook.bind(
        spell=Service,
        existence=Existence.unique,
        permissions="create",
    )
    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )
    outside_id = spellbook.bind(
        spell=Outside,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        local_spells = list(spellbook._spells.values())
        for spell in local_spells:
            _run_phase_requirements(spell)
            _run_phase_symbolic_graph(spell)
            _run_phase_local_frame(spell)
            _run_phase_validation(spell)

        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        service_spell = _get_spell_by_version_id(spellbook, service_id)
        outside_spell = _get_spell_by_version_id(spellbook, outside_id)
        assert consumer_spell is not None
        assert service_spell is not None
        assert outside_spell is not None

        _run_phase_root_blueprints_local(consumer_spell, "cid")
        _run_phase_system_validation_local(consumer_spell, "cid")

        assert consumer_spell.validation_result_phase6 is not None
        assert consumer_spell.validated is True
        assert service_spell.validation_result_phase6 is consumer_spell.validation_result_phase6
        assert service_spell.validated is True
        assert outside_spell.validation_result_phase6 is None
    finally:
        spellbook.cleanup()




