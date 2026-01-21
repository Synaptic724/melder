import pytest

import melder.spellbook.spell_crafter.spell_crafter as spell_crafter_module
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.mutation_contract import MutationContract
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spellbook import Spellbook
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


class _SpellIndexStub:
    """
    Purpose:
        Provide a minimal SpellIndex-like key for scanner stubs.
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
    def current(self) -> str:
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
        Provide a minimal spell object for scanner stubs.
    Contract:
        - Exposes spell identity and binding metadata.
    """
    def __init__(
        self,
        spell: object,
        spell_name: str,
        spellframe: object | None = None,
        binding_name: str | None = None,
    ) -> None:
        """
        Purpose:
            Capture spell identity for scanner stubs.
        Contract:
            - Stores spell, spell_name, spellframe, and binding_name verbatim.
        Args:
            spell: The underlying spell object or class.
            spell_name: Human-readable spell name.
            spellframe: Optional frame marker for matching.
            binding_name: Optional binding name for matching.
        Returns:
            None.
        """
        self.spell = spell
        self.spell_name = spell_name
        self.spellframe = spellframe
        self.binding_name = binding_name


class _SpellbookScannerStub:
    """
    Purpose:
        Replace SpellbookScanner for component tests.
    Contract:
        - Returns class-level iterators for spell data.
        - Provides frame/binding lookup results as configured by tests.
    """
    iter_all_spells_data: list[tuple[object, object]] = []
    find_by_frame_and_binding_data: dict[object, object] = {}

    def __init__(self, spellbook: Spellbook) -> None:
        """
        Purpose:
            Capture the spellbook reference for parity with the real scanner.
        Contract:
            - Stores the spellbook for diagnostics only.
        Args:
            spellbook: Spellbook passed by SpellCrafter.
        Returns:
            None.
        """
        self._spellbook = spellbook
        self._cleaned = False

    def iter_all_spells(self) -> list[tuple[object, object]]:
        """
        Purpose:
            Yield the configured spell list for scanner consumers.
        Contract:
            - Returns a new list containing the configured data.
        Returns:
            list[tuple[object, object]]: SpellIndex/spell pairs.
        """
        return list(self.iter_all_spells_data)

    def find_by_frame_and_binding(
        self,
        spellframe: object,
        binding_name: str | None,
        include_contracted: bool = True,
    ) -> dict[object, object]:
        """
        Purpose:
            Return the configured frame/binding candidates.
        Contract:
            - Ignores parameters and returns the configured mapping.
        Args:
            spellframe: Frame key requested by the caller.
            binding_name: Binding name requested by the caller.
            include_contracted: Whether contracted spells should be included.
        Returns:
            dict[object, object]: Mapping of SpellIndex-like keys to spell objects.
        """
        return dict(self.find_by_frame_and_binding_data)

    def cleanup(self) -> None:
        """
        Purpose:
            Mark the stub as cleaned for parity with the real scanner.
        Contract:
            - Sets the cleaned flag to True.
        Returns:
            None.
        """
        self._cleaned = True


class _ValidationResultStub:
    """
    Purpose:
        Provide a minimal validation result for SpellCrafter tests.
    Contract:
        - Exposes the has_errors flag.
    """
    def __init__(self, has_errors: bool) -> None:
        """
        Purpose:
            Capture a validation outcome flag.
        Contract:
            - Stores has_errors verbatim.
        Args:
            has_errors: True if the validation result should signal errors.
        Returns:
            None.
        """
        self.has_errors = has_errors


class _SpellValidationSystemStub:
    """
    Purpose:
        Stand-in for SpellValidationSystem to control validation outcomes.
    Contract:
        - validate_spell returns the configured result and records call count.
    """
    def __init__(self, result: _ValidationResultStub) -> None:
        """
        Purpose:
            Store the result to return from validate_spell.
        Contract:
            - call_count starts at zero.
        Args:
            result: Validation result to return.
        Returns:
            None.
        """
        self.result = result
        self.call_count = 0

    def validate_spell(
        self,
        spell: object,
        requirements: object,
        symbolic_graph: object,
        resolution_frame: object,
        cancel_event: object | None = None,
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
        Returns:
            _ValidationResultStub: The configured validation result.
        """
        self.call_count += 1
        return self.result


class _SpellSystemStatesStub:
    """
    Purpose:
        Capture SpellSystemStates updates for component tests.
    Contract:
        - update_dependencies records dependencies by SpellIndex.
        - register_local_topology records topology by SpellIndex.
    """
    def __init__(self) -> None:
        """
        Purpose:
            Initialize empty dependency and topology registries.
        Contract:
            - Registries start empty.
        Returns:
            None.
        """
        self.dependencies_by_spell: dict[object, list[str]] = {}
        self.topology_by_spell: dict[object, object] = {}
        self.registered_lineages: list[tuple[object, object]] = []

    def register_lineage(self, spell_index: object, spell: object) -> None:
        """
        Purpose:
            Record a lineage registration call from Spellbook.bind.
        Contract:
            - Stores (spell_index, spell) in registration order.
        Args:
            spell_index: SpellIndex registered for the lineage.
            spell: Underlying spell callable/class registered.
        Returns:
            None.
        """
        self.registered_lineages.append((spell_index, spell))

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

    def get_local_topology(self, spell_index: object) -> object | None:
        """
        Purpose:
            Return the recorded topology for a lineage.
        Contract:
            - Returns None if no topology was recorded.
        Args:
            spell_index: SpellIndex for the lookup.
        Returns:
            object | None: The recorded topology or None.
        """
        return self.topology_by_spell.get(spell_index)


def test_component_spell_crafter_spellmap_default_raises_when_missing_candidates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate missing SpellMap default candidates raise during Phase 3.
    Contract:
        - run_phase_local_frame raises when SpellMap defaults resolve to none.
    Args:
        monkeypatch: Pytest fixture for patching SpellbookScanner.
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

    _SpellbookScannerStub.iter_all_spells_data = []
    _SpellbookScannerStub.find_by_frame_and_binding_data = {}
    monkeypatch.setattr(spell_crafter_module, "SpellbookScanner", _SpellbookScannerStub)

    try:
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        with pytest.raises(RuntimeError, match="SpellMap default could not be resolved"):
            spell.run_phase_local_frame()
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_spellmap_default_raises_on_multiple_candidates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate ambiguous SpellMap defaults raise during Phase 3.
    Contract:
        - run_phase_local_frame raises when SpellMap defaults resolve to multiple candidates.
    Args:
        monkeypatch: Pytest fixture for patching SpellbookScanner.
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

    index_a = _SpellIndexStub("candidate-a")
    index_b = _SpellIndexStub("candidate-b")
    candidate_a = _SpellCandidateStub(spell=object(), spell_name="Alpha")
    candidate_b = _SpellCandidateStub(spell=object(), spell_name="Beta")

    _SpellbookScannerStub.iter_all_spells_data = []
    _SpellbookScannerStub.find_by_frame_and_binding_data = {
        index_a: candidate_a,
        index_b: candidate_b,
    }
    monkeypatch.setattr(spell_crafter_module, "SpellbookScanner", _SpellbookScannerStub)

    try:
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        with pytest.raises(RuntimeError, match="multiple"):
            spell.run_phase_local_frame()
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_spellmap_default_prefers_explicit_spell(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate explicit SpellMap defaults resolve by spell identity.
    Contract:
        - run_phase_local_frame binds the explicit spell only.
    Args:
        monkeypatch: Pytest fixture for patching SpellbookScanner.
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

    explicit_index = _SpellIndexStub("explicit-id")
    explicit_spell = _SpellCandidateStub(
        spell=BasicService,
        spell_name="BasicService",
    )
    other_index = _SpellIndexStub("other-id")
    other_spell = _SpellCandidateStub(
        spell=OtherService,
        spell_name="OtherService",
    )

    _SpellbookScannerStub.iter_all_spells_data = [
        (explicit_index, explicit_spell),
        (other_index, other_spell),
    ]
    _SpellbookScannerStub.find_by_frame_and_binding_data = {}
    monkeypatch.setattr(spell_crafter_module, "SpellbookScanner", _SpellbookScannerStub)

    try:
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()

        assert set(spell.dependencies) == {explicit_index.current}
        topology = spell._spell_system_states.get_local_topology(spell.spell_index)
        assert topology is not None
        sockets = topology.get_sockets_for_param("service")
        assert len(sockets) == 1
        assert set(sockets[0].target_spell_ids) == {explicit_index.current}
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_spellmap_default_resolves_frame_only_candidate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate frame-only SpellMap defaults resolve via frame/binding lookup.
    Contract:
        - run_phase_local_frame binds the frame-only candidate.
        - system states receive dependency updates for the resolved target.
    Args:
        monkeypatch: Pytest fixture for patching SpellbookScanner.
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

    candidate_index = _SpellIndexStub("service-id")
    candidate_spell = _SpellCandidateStub(
        spell=BasicService,
        spell_name="BasicService",
        spellframe=IService,
        binding_name="primary",
    )

    _SpellbookScannerStub.iter_all_spells_data = []
    _SpellbookScannerStub.find_by_frame_and_binding_data = {
        candidate_index: candidate_spell,
    }
    monkeypatch.setattr(spell_crafter_module, "SpellbookScanner", _SpellbookScannerStub)

    try:
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()

        assert set(spell.dependencies) == {candidate_index.current}
        dependencies = states.dependencies_by_spell.get(spell.spell_index)
        assert dependencies is not None
        assert set(dependencies) == {candidate_index.current}
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_spellmap_default_raises_on_duplicate_explicit_matches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate explicit SpellMap defaults raise when duplicates exist.
    Contract:
        - run_phase_local_frame raises when explicit spell resolves to multiple matches.
    Args:
        monkeypatch: Pytest fixture for patching SpellbookScanner.
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

    explicit_index_a = _SpellIndexStub("explicit-a")
    explicit_index_b = _SpellIndexStub("explicit-b")
    explicit_spell_a = _SpellCandidateStub(
        spell=BasicService,
        spell_name="BasicServiceA",
    )
    explicit_spell_b = _SpellCandidateStub(
        spell=BasicService,
        spell_name="BasicServiceB",
    )

    _SpellbookScannerStub.iter_all_spells_data = [
        (explicit_index_a, explicit_spell_a),
        (explicit_index_b, explicit_spell_b),
    ]
    _SpellbookScannerStub.find_by_frame_and_binding_data = {}
    monkeypatch.setattr(spell_crafter_module, "SpellbookScanner", _SpellbookScannerStub)

    try:
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        with pytest.raises(RuntimeError, match="multiple"):
            spell.run_phase_local_frame()
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_contract_sockets_register_topology() -> None:
    """
    Purpose:
        Validate contract sockets register topology without dependencies.
    Contract:
        - dependencies remain empty for contract sockets.
        - topology includes SPELL_CONTRACT and MUTATION_CONTRACT socket kinds.
    Returns:
        None.
    Raises:
        AssertionError: If contract sockets do not register correctly.
    """
    spellbook = _make_spellbook()
    states = _SpellSystemStatesStub()
    spellbook._spell_system_states = states

    class Consumer:
        """
        Purpose:
            Spell that declares contract sockets.
        Contract:
            - Declares SpellContract and MutationContract sockets.
        Args:
            service: SpellContract socket.
            mutation: MutationContract socket.
        """
        def __init__(
            self,
            service: SpellContract = SpellContract(
                spellframe=IService,
                binding_name="primary",
            ),
            mutation: MutationContract = MutationContract(
                spellframe=IService,
                binding_name="primary",
            ),
        ) -> None:
            """
            Purpose:
                Capture contract socket defaults.
            Contract:
                - Stores the sockets for assertions.
            Args:
                service: SpellContract socket.
                mutation: MutationContract socket.
            Returns:
                None.
            """
            self.service = service
            self.mutation = mutation

    consumer_id = spellbook.bind(
        spell=Consumer,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()

        assert spell.dependencies == []
        topology = states.get_local_topology(spell.spell_index)
        assert topology is not None
        service_socket = topology.get_sockets_for_param("service")
        mutation_socket = topology.get_sockets_for_param("mutation")
        assert len(service_socket) == 1
        assert len(mutation_socket) == 1
        assert service_socket[0].socket_kind is SocketKind.SPELL_CONTRACT
        assert mutation_socket[0].socket_kind is SocketKind.MUTATION_CONTRACT
        assert service_socket[0].target_spell_ids == ()
        assert mutation_socket[0].target_spell_ids == ()
    finally:
        spellbook.cleanup()


def test_component_spell_crafter_collection_di_allows_empty_collection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate empty collection DI does not create dependencies.
    Contract:
        - dependencies remain empty when no collection candidates resolve.
        - topology records the collection socket with no targets.
    Args:
        monkeypatch: Pytest fixture for patching SpellbookScanner.
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

    _SpellbookScannerStub.iter_all_spells_data = []
    _SpellbookScannerStub.find_by_frame_and_binding_data = {}
    monkeypatch.setattr(spell_crafter_module, "SpellbookScanner", _SpellbookScannerStub)

    try:
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()

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
    spellbook._spell_validator = validator

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
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()
        spell.run_phase_validation()
        spell.run_phase_validation()

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
    spellbook._spell_validator = validator

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
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()
        spell.run_phase_validation()

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
        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()

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
