import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.nexus import Nexus
from melder.spellbook.existence.existence import Existence
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.spellbook import Spellbook
from melder.utilities.synchronization.creation_gate_controller import CreationGateController
from melder.utilities.helpers.general_helpers import SpellInputUtils
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.protocols import IService
from tests.mocks.spellbook import scan_bind_module_core


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
    build_aetheric_frame_configuration_for_spellbook_configuration,
    set_frame_ai_native_for_spellbook_configuration,
    set_frame_rift_enabled_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
    set_shared_framewide_spellbook_configuration_for_spellbook_configuration,
)
@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_spellbook() -> None:
    """
    Purpose:
        Ensure component Spellbook tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Nexus._reset_singleton_for_tests()
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
    spellbook._conduit = _ConduitStub(conduit_id="borrower", name="borrower")
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


class _SpellSystemStatesStub:
    """
    Purpose:
        Capture lineage registrations for Spellbook bind operations.
    Contract:
        - register_index records SpellIndex and Spell instances in order.
        - unregister_index records SpellIndex removals during cleanup.
    """
    def __init__(self) -> None:
        """
        Purpose:
            Initialize an empty registry of lineage registrations.
        Contract:
            - registered_lineages starts empty.
            - unregistered_lineages starts empty.
        Returns:
            None.
        """
        self.registered_lineages: list[tuple[object, object]] = []
        self.unregistered_lineages: list[object] = []

    def register_index(self, spell_index: object, spell: object) -> None:
        """
        Purpose:
            Record a lineage registration from Spellbook.bind.
        Contract:
            - Appends (spell_index, spell) to registered_lineages.
        Args:
            spell_index: SpellIndex registered for the lineage.
            spell: Bound Spell instance registered.
        Returns:
            None.
        """
        self.registered_lineages.append((spell_index, spell))

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


class _ConduitStub:
    """
    Purpose:
        Provide a minimal conduit stub for Spellbook bind ownership flows.
    Contract:
        - Tracks registration calls for existing creations.
    """
    def __init__(self, conduit_id: str = "cid", name: str = "cname") -> None:
        """
        Purpose:
            Initialize the conduit stub.
        Contract:
            - Stores identifiers and initializes registration tracking.
        Args:
            conduit_id: Conduit identifier to expose.
            name: Conduit name to expose.
        Returns:
            None.
        """
        self._id = conduit_id
        self._name = name
        self._creations = {}
        self.__dynamic_environment__ = True
        self._creation_gate_controller = CreationGateController()
        self.registered: list[tuple[object, object]] = []

    def _register_to_creations(self, spell: object, obj: object) -> None:
        """
        Purpose:
            Record registration of existing creations.
        Contract:
            - Appends (spell, obj) to the registered list.
        Args:
            spell: Spell instance being registered.
            obj: Existing object bound to the spell.
        Returns:
            None.
        """
        self.registered.append((spell, obj))


def test_component_spellbook_bind_registers_lineage_and_states() -> None:
    """
    Purpose:
        Validate Spellbook.bind registers lineage and uses spell system states.
    Contract:
        - register_index receives the SpellIndex and bound Spell instance.
        - The bound Spell references the injected SpellSystemStates instance.
    Returns:
        None.
    Raises:
        AssertionError: If lineage or state wiring is incorrect.
    """
    spellbook = _make_spellbook()
    states = _SpellSystemStatesStub()
    spellbook._spell_system_states = states

    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )

        assert len(states.registered_lineages) == 1
        registered_index, registered_spell = states.registered_lineages[0]
        assert registered_index in spellbook.spells

        bound_spell = _get_spell_by_version_id(spellbook, spell_id)
        assert bound_spell is not None
        assert registered_spell is bound_spell
        assert registered_spell.spell is BasicService
        assert bound_spell._spell_system_states is states
        assert bound_spell.spell_index.current == spell_id
    finally:
        spellbook.cleanup()


def test_component_spellbook_bind_rejects_duplicate_binding_key() -> None:
    """
    Purpose:
        Validate bind rejects duplicate normalized binding keys.
    Contract:
        - Rebinding a different spell under the same frame/binding raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate bindings are not rejected.
    """
    spellbook = _make_spellbook()

    class ServiceA:
        """
        Purpose:
            Provide a simple spell for duplicate binding tests.
        Contract:
            No behavior beyond type identity.
        """

    class ServiceB:
        """
        Purpose:
            Provide a second spell for duplicate binding tests.
        Contract:
            No behavior beyond type identity.
        """

    try:
        spellbook.bind(
            spell=ServiceA,
            existence=Existence.unique,
            permissions="create",
            spellframe=IService,
            binding_name="primary",
        )

        with pytest.raises(RuntimeError, match="binding key collision"):
            spellbook.bind(
                spell=ServiceB,
                existence=Existence.unique,
                permissions="create",
                spellframe=IService,
                binding_name="primary",
            )
    finally:
        spellbook.cleanup()


def test_component_spellbook_bind_existing_object_registers_to_creations() -> None:
    """
    Purpose:
        Validate binding an existing object registers it to a conjured conduit.
    Contract:
        - _register_to_creations is invoked for existing-object spells.
        - The bound Spell is stamped with owner metadata.
    Returns:
        None.
    Raises:
        AssertionError: If ownership or registration is missing.
    """
    spellbook = _make_spellbook()
    states = _SpellSystemStatesStub()
    spellbook._spell_system_states = states
    conduit = _ConduitStub(conduit_id="owner-id", name="owner-name")
    spellbook._conduit = conduit
    spellbook._conjured = True
    existing = BasicService(marker="existing")

    try:
        spell_id = spellbook.bind(
            spell=existing,
            existence=Existence.unique,
            permissions="create",
        )

        assert len(conduit.registered) == 1
        registered_spell, registered_obj = conduit.registered[0]
        assert registered_obj is existing

        bound_spell = _get_spell_by_version_id(spellbook, spell_id)
        assert bound_spell is not None
        assert registered_spell is bound_spell
        assert bound_spell.user_created_object is existing
        assert bound_spell.owned_spell is True
        assert bound_spell._owner_conduit_id == conduit._id
        assert bound_spell._owner_conduit_name == conduit._name
    finally:
        spellbook.cleanup()


def test_component_spellbook_transaction_context_allows_post_conjure_bind() -> None:
    """
    Purpose:
        Validate change-control bind transactions re-open binding after conjure.
    Contract:
        - Binding after conjure requires an active bind transaction.
        - transaction("bind") opens and closes the binding window.
    Returns:
        None.
    Raises:
        AssertionError: If post-conjure bind gating is incorrect.
    """
    spellbook = _make_spellbook()
    conduit = spellbook.conjure(name="root")
    try:
        with pytest.raises(RuntimeError, match="requires an active binding transaction"):
            spellbook.bind(
                spell=BasicService,
                existence=Existence.unique,
                permissions="create",
            )

        with spellbook.transaction("bind"):
            spellbook.bind(
                spell=BasicService,
                existence=Existence.unique,
                permissions="create",
            )

        with pytest.raises(RuntimeError, match="requires an active binding transaction"):
            spellbook.bind(
                spell=BasicService,
                existence=Existence.unique,
                permissions="create",
            )
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_component_spellbook_conjure_sets_disposal_metadata() -> None:
    """
    Purpose:
        Validate conjure computes per-spell disposal metadata from configuration.
    Contract:
        - Class spells record configured disposal methods present on the class.
        - Non-class spells record an empty disposal method list.
        - has_disposal_methods is True only when the list is non-empty.
    Returns:
        None.
    Raises:
        AssertionError: If disposal metadata is missing or incorrect.
    """
    config = SpellbookConfiguration("default")
    config.set_property("disposal_method_names", ["cleanup", "close", "dispose"])
    config.load_default_dictionary()
    spellbook = Spellbook(configuration=config)
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    class DisposableService:
        """
        Purpose:
            Provide a class with cleanup and close methods.
        Contract:
            - cleanup and close are present for disposal metadata matching.
        """
        def cleanup(self) -> None:
            """
            Purpose:
                Provide a cleanup method for disposal matching.
            Contract:
                No side effects.
            Returns:
                None.
            """
            return None

        def close(self) -> None:
            """
            Purpose:
                Provide a close method for disposal matching.
            Contract:
                No side effects.
            Returns:
                None.
            """
            return None

    def factory() -> object:
        """
        Purpose:
            Provide a callable spell for disposal metadata checks.
        Contract:
            - Returns a new object instance.
        Returns:
            object: A fresh object.
        """
        return object()

    try:
        disposable_id = spellbook.bind(
            spell=DisposableService,
            existence=Existence.unique,
            permissions="create",
        )
        callable_id = spellbook.bind(
            spell=factory,
            existence=Existence.unique,
            permissions="create",
            binding_name="callable",
        )

        conduit = spellbook.conjure(name="root")
        try:
            disposable_spell = _get_spell_by_version_id(spellbook, disposable_id)
            assert disposable_spell is not None
            assert disposable_spell.disposal_method_names == ["cleanup", "close"]
            assert disposable_spell.has_disposal_methods is True

            callable_spell = _get_spell_by_version_id(spellbook, callable_id)
            assert callable_spell is not None
            assert callable_spell.disposal_method_names == []
            assert callable_spell.has_disposal_methods is False
        finally:
            conduit.cleanup()
    finally:
        spellbook.cleanup()


def test_component_spellbook_end_transaction_wrong_type_keeps_binding_active() -> None:
    """
    Purpose:
        Validate end_transaction type mismatches do not close binding windows.
    Contract:
        - end_transaction raises for mismatched transaction types.
        - Binding remains active after the mismatch until the correct end.
    Returns:
        None.
    Raises:
        AssertionError: If binding window closes on a mismatched end.
    """
    spellbook = _make_spellbook()
    conduit = spellbook.conjure(name="root")
    try:
        spellbook.begin_transaction("bind")
        with pytest.raises(RuntimeError, match="does not match"):
            spellbook.end_transaction("link")

        spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )

        spellbook.end_transaction("bind")
        with pytest.raises(RuntimeError, match="requires an active binding transaction"):
            spellbook.bind(
                spell=BasicService,
                existence=Existence.unique,
                permissions="create",
            )
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_component_spellbook_transaction_context_closes_on_exception() -> None:
    """
    Purpose:
        Validate transaction context closes the binding window on errors.
    Contract:
        - Exceptions inside transaction("bind") still close binding access.
    Returns:
        None.
    Raises:
        AssertionError: If binding remains active after an exception.
    """
    spellbook = _make_spellbook()
    conduit = spellbook.conjure(name="root")
    try:
        with pytest.raises(RuntimeError, match="boom"):
            with spellbook.transaction("bind"):
                raise RuntimeError("boom")

        with pytest.raises(RuntimeError, match="requires an active binding transaction"):
            spellbook.bind(
                spell=BasicService,
                existence=Existence.unique,
                permissions="create",
            )
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_component_spellbook_begin_transaction_invalid_type_raises() -> None:
    """
    Purpose:
        Validate invalid transaction types are rejected.
    Contract:
        - begin_transaction raises ValueError for unknown types.
    Returns:
        None.
    Raises:
        AssertionError: If invalid transaction types are accepted.
    """
    spellbook = _make_spellbook()
    try:
        with pytest.raises(ValueError, match="Invalid transaction_type"):
            spellbook.begin_transaction("unknown")
    finally:
        spellbook.cleanup()


def test_component_spellbook_begin_transaction_disabled_change_control_tracks_request() -> None:
    """
    Purpose:
        Validate change-control disabled mode still tracks in-flight requests.
    Contract:
        - begin_transaction admits the request when change-control is disabled.
        - In-flight registry contains the admitted request.
    Returns:
        None.
    Raises:
        AssertionError: If in-flight tracking is missing.
    """
    spellbook = _make_spellbook()
    conduit = spellbook.conjure(name="root")
    change_control = Aether()._get_change_control_manager("default")
    try:
        change_control.disable_change_control()
        spellbook.begin_transaction("bind", scope_keys=["scope:custom"])
        in_flight = change_control.transaction_manager().list_in_flight()
        assert len(in_flight) == 1
        assert spellbook._active_change_request in in_flight
    finally:
        if spellbook._active_change_request is not None:
            spellbook.end_transaction("bind")
        conduit.cleanup()
        spellbook.cleanup()


def test_component_spellbook_begin_transaction_with_conduit_id_tracks_scope() -> None:
    """
    Purpose:
        Validate conduit ids are recorded in change-control requests.
    Contract:
        - begin_transaction stores the initiator conduit id in conduit_ids.
        - Base spellbook scope key is always included.
    Returns:
        None.
    Raises:
        AssertionError: If conduit ids or scopes are missing.
    """
    spellbook = _make_spellbook()
    conduit = spellbook.conjure(name="root")
    change_control = Aether()._get_change_control_manager("default")
    try:
        spellbook.begin_transaction("bind", conduit_id="conduit-1")
        request = change_control.transaction_manager().list_in_flight()[0]
        assert "conduit-1" in request.conduit_ids
        assert f"scope:spellbook:{spellbook._id}" in request.scope_keys
    finally:
        spellbook.end_transaction("bind")
        conduit.cleanup()
        spellbook.cleanup()


def test_component_spellbook_bind_updates_spell_versions_cache() -> None:
    """
    Purpose:
        Validate bind keeps the local spell version cache warm.
    Contract:
        - _spell_versions includes the newly bound spell id.
    Returns:
        None.
    Raises:
        AssertionError: If _spell_versions is not updated.
    """
    spellbook = _make_spellbook()
    states = _SpellSystemStatesStub()
    spellbook._spell_system_states = states

    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        assert spellbook._spell_versions is not None
        assert spell_id in spellbook._spell_versions
    finally:
        spellbook.cleanup()


def test_component_spellbook_conjure_registers_and_cleanup_unregisters_risk_manager_state() -> None:
    """
    Purpose:
        Validate conjure and cleanup wire live conduit state into RiskManager.
    Contract:
        - Conjure registers the root conduit in the per-frame RiskManager.
        - Existing local spell lineages are seeded into the conduit risk state.
        - Conduit cleanup removes the conduit bucket from the RiskManager.
    Returns:
        None.
    Raises:
        AssertionError: If RiskManager runtime state is missing or stale.
    """
    spellbook = _make_spellbook()
    try:
        spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        lineage_id = next(iter(spellbook.spells.keys())).id

        conduit = spellbook.conjure(name="root")
        risk_manager = spellbook._aether._get_devops_manager(
            spellbook._aetheric_frame
        ).risk_manager
        try:
            state = risk_manager._conduit_states.get(conduit.id)
            assert state is not None
            assert state.spellbook is spellbook
            assert lineage_id in state.lineages
            assert spellbook._spellbook_validation_required is False
            conduit_id = conduit.id
        finally:
            conduit.cleanup()

        assert conduit_id not in risk_manager._conduit_states
    finally:
        spellbook.cleanup()


def test_component_spellbook_link_contract_updates_live_transaction_manager_mirror() -> None:
    """
    Purpose:
        Validate link-contract helpers update the live change-control mirror.
    Contract:
        - _create_link_contract registers borrower->provider in the real
          transaction manager mirror.
        - _sever_link_contract clears the live mirror entry again.
    Returns:
        None.
    Raises:
        AssertionError: If the runtime mirror is not updated.
    """
    spellbook = _make_spellbook()
    conduit = spellbook.conjure(name="root")
    transaction_manager = Aether()._get_change_control_manager(
        spellbook._aetheric_frame
    ).transaction_manager()
    try:
        assert transaction_manager.list_borrowers_for_provider("provider-1") == set()

        spellbook._create_link_contract("provider-1")
        assert transaction_manager.list_borrowers_for_provider("provider-1") == {
            conduit.id
        }

        spellbook._sever_link_contract("provider-1")
        assert transaction_manager.list_borrowers_for_provider("provider-1") == set()
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_component_spellbook_describe_spells_runtime_dump_includes_owner_and_shape() -> None:
    """
    Purpose:
        Validate the authoring dump surface against a live post-conjure Spellbook.
    Contract:
        - describe_spells_in_spellbook returns one detached dict per visible spell.
        - owner_conduit_id reflects the live root conduit after post-conjure bind.
        - binding_name defaults to "__default__" when omitted.
        - spellframe values are rendered as user-facing strings.
    Returns:
        None.
    Raises:
        AssertionError: If the runtime dump shape is incorrect.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    conduit = spellbook.conjure(name="root")
    try:
        with spellbook.binding_transaction():
            spellbook.bind(
                spell=BasicService,
                existence=Existence.unique,
                permissions="create",
            )
            spellbook.bind(
                spell=BasicConfig,
                existence=Existence.unique,
                permissions="create",
                spellframe=IService,
                binding_name="secondary",
            )

        descriptions = spellbook.describe_spells_in_spellbook()

        assert len(descriptions) == 2
        assert all(
            set(description.keys()) == {
                "spell_id",
                "spell_name",
                "binding_name",
                "spellframe",
                "existence",
                "owner_conduit_id",
            }
            for description in descriptions
        )
        assert [description["owner_conduit_id"] for description in descriptions] == [
            conduit.id,
            conduit.id,
        ]
        by_name = {description["spell_name"]: description for description in descriptions}
        assert set(by_name.keys()) == {"BasicService", "BasicConfig"}
        assert by_name["BasicService"]["binding_name"] == "__default__"
        assert by_name["BasicService"]["spellframe"] is None
        assert by_name["BasicConfig"]["binding_name"] == "secondary"
        assert by_name["BasicConfig"]["spellframe"] == "IService"
        assert all(description["existence"] == "unique" for description in descriptions)
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_component_spellbook_post_conjure_bind_publishes_incremental_nexus_spell_record() -> None:
    """
    Purpose:
        Validate late binds publish incremental spell records into passive Nexus.
    Contract:
        - A Rift-enabled frame publishes the initial conjure state.
        - A post-conjure bind publishes the newly bound spell record.
        - The late-bound spell record is removed again on conduit cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If incremental Nexus publication is missing.
    """
    configuration = SpellbookConfiguration(aether_frame="ops")
    apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    set_frame_rift_enabled_for_spellbook_configuration(configuration, True)
    spellbook = Spellbook(aetheric_frame="ops", configuration=configuration)
    spellbook_id = spellbook.id

    conduit = spellbook.conjure(name="root")
    late_spell_id = None
    try:
        with spellbook.binding_transaction():
            late_spell_id = spellbook.bind(
                spell=BasicService,
                existence=Existence.unique,
                permissions="create",
                binding_name="late",
            )

        descriptor = Nexus()._get_required_frame_descriptor("ops")
        assert (spellbook_id, late_spell_id) in descriptor.spell_records_by_key
    finally:
        conduit.cleanup()

    descriptor = Nexus()._get_required_frame_descriptor("ops")
    assert (spellbook_id, late_spell_id) not in descriptor.spell_records_by_key
    spellbook.cleanup()


def test_component_spellbook_post_conjure_scan_publishes_passive_nexus_spell_records() -> None:
    """
    Purpose:
        Validate late scan bindings publish batched spell records into passive Nexus.
    Contract:
        - scan after conjure publishes one spell record per scanned spell id.
        - conduit cleanup removes those scanned spell records again.
    Returns:
        None.
    Raises:
        AssertionError: If passive Nexus does not reflect the scan lifecycle.
    """
    configuration = SpellbookConfiguration(aether_frame="ops")
    apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    set_frame_rift_enabled_for_spellbook_configuration(configuration, True)
    spellbook = Spellbook(aetheric_frame="ops", configuration=configuration)
    spellbook_id = spellbook.id

    conduit = spellbook.conjure(name="root")
    spell_ids = []
    try:
        with spellbook.binding_transaction():
            spell_ids = spellbook.scan(scan_bind_module_core)

        descriptor = Nexus()._get_required_frame_descriptor("ops")
        for spell_id in spell_ids:
            assert (spellbook_id, spell_id) in descriptor.spell_records_by_key
    finally:
        conduit.cleanup()

    descriptor = Nexus()._get_required_frame_descriptor("ops")
    for spell_id in spell_ids:
        assert (spellbook_id, spell_id) not in descriptor.spell_records_by_key
    spellbook.cleanup()


def test_component_spellbook_cleanup_unregisters_lineages() -> None:
    """
    Purpose:
        Validate Spellbook.cleanup unregisters local lineages from SpellSystemStates.
    Contract:
        - unregister_index is called once per local SpellIndex.
    Returns:
        None.
    Raises:
        AssertionError: If unregister_index is missing or incomplete.
    """
    spellbook = _make_spellbook()
    states = _SpellSystemStatesStub()
    spellbook._spell_system_states = states

    try:
        spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spellbook.bind(
            spell=BasicConfig,
            existence=Existence.unique,
            permissions="create",
        )
        expected = [index for index, _spell in states.registered_lineages]
    finally:
        spellbook.cleanup()

    for spell_index in expected:
        assert spell_index in states.unregistered_lineages
    assert len(states.unregistered_lineages) == len(expected)


def test_component_spellbook_bind_after_conjure_sets_owner_metadata() -> None:
    """
    Purpose:
        Validate binding after conjure stamps owner metadata on new spells.
    Contract:
        - New spells receive owner conduit id/name and owned_spell flag.
        - No creation registration occurs for class-based spells.
    Returns:
        None.
    Raises:
        AssertionError: If ownership metadata is missing or incorrect.
    """
    spellbook = _make_spellbook()
    states = _SpellSystemStatesStub()
    spellbook._spell_system_states = states
    conduit = _ConduitStub(conduit_id="owner-id", name="owner-name")
    spellbook._conduit = conduit
    spellbook._conjured = True

    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        assert conduit.registered == []

        bound_spell = _get_spell_by_version_id(spellbook, spell_id)
        assert bound_spell is not None
        assert bound_spell.user_created_object is None
        assert bound_spell.owned_spell is True
        assert bound_spell._owner_conduit_id == conduit._id
        assert bound_spell._owner_conduit_name == conduit._name
    finally:
        spellbook.cleanup()


def test_component_spellbook_add_hooks_to_spell_attaches_lists() -> None:
    """
    Purpose:
        Validate hook lists are attached to spells via the private hook helper.
    Contract:
        - pre_hooks, activation_hooks, and post_hooks are stored on the Spell.
    Returns:
        None.
    Raises:
        AssertionError: If hooks are not assigned correctly.
    """
    spellbook = _make_spellbook()

    def pre_hook() -> None:
        """
        Purpose:
            Provide a pre-hook for Spellbook hook attachment.
        Contract:
            - No side effects; used for identity checks.
        Returns:
            None.
        """
        return None

    def activation_hook() -> None:
        """
        Purpose:
            Provide an activation hook for Spellbook hook attachment.
        Contract:
            - No side effects; used for identity checks.
        Returns:
            None.
        """
        return None

    def post_hook() -> None:
        """
        Purpose:
            Provide a post-hook for Spellbook hook attachment.
        Contract:
            - No side effects; used for identity checks.
        Returns:
            None.
        """
        return None

    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spellbook._add_hooks_to_spell(
            spell,
            pre_hooks=[pre_hook],
            activation_hooks=[activation_hook],
            post_hooks=[post_hook],
        )

        assert spell._pre_hooks == [pre_hook]
        assert spell._activation_hooks == [activation_hook]
        assert spell._post_hooks == [post_hook]
    finally:
        spellbook.cleanup()


def test_component_spellbook_add_hooks_to_spell_sets_hooks_enabled() -> None:
    """
    Purpose:
        Verify hook attachment enables the spell hook gate.
    Contract:
        - _hooks_enabled is True when any hook list is provided.
    Returns:
        None.
    Raises:
        AssertionError: If hook gating does not enable.
    """
    spellbook = _make_spellbook()

    def pre_hook() -> None:
        """
        Purpose:
            Provide a pre-hook for hook gate checks.
        Contract:
            - No side effects; used for identity checks.
        Returns:
            None.
        """
        return None

    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spellbook._add_hooks_to_spell(spell, pre_hooks=[pre_hook])

        assert spell._hooks_enabled is True
    finally:
        spellbook.cleanup()


def test_component_spellbook_add_hooks_to_spell_partial_update_preserves_existing() -> None:
    """
    Purpose:
        Verify partial hook updates keep existing hook lists intact.
    Contract:
        - Previously set hooks remain when only new lists are supplied.
    Returns:
        None.
    Raises:
        AssertionError: If existing hooks are overwritten.
    """
    spellbook = _make_spellbook()

    def pre_hook() -> None:
        """
        Purpose:
            Provide a pre-hook for partial update checks.
        Contract:
            - No side effects; used for identity checks.
        Returns:
            None.
        """
        return None

    def activation_hook(_: object) -> None:
        """
        Purpose:
            Provide an activation hook for partial update checks.
        Contract:
            - No side effects; used for identity checks.
        Returns:
            None.
        """
        return None

    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spellbook._add_hooks_to_spell(spell, pre_hooks=[pre_hook])
        spellbook._add_hooks_to_spell(spell, activation_hooks=[activation_hook])

        assert spell._pre_hooks == [pre_hook]
        assert spell._activation_hooks == [activation_hook]
        assert spell._hooks_enabled is True
    finally:
        spellbook.cleanup()


def test_component_spellbook_add_hooks_to_spell_no_kwargs_is_noop() -> None:
    """
    Purpose:
        Verify _add_hooks_to_spell is a no-op when no hooks are provided.
    Contract:
        - Existing hook lists are preserved.
    Returns:
        None.
    Raises:
        AssertionError: If existing hooks are modified.
    """
    spellbook = _make_spellbook()

    def pre_hook() -> None:
        """
        Purpose:
            Provide a pre-hook for noop checks.
        Contract:
            - No side effects; used for identity checks.
        Returns:
            None.
        """
        return None

    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spellbook._add_hooks_to_spell(spell, pre_hooks=[pre_hook])
        original_pre = spell._pre_hooks

        spellbook._add_hooks_to_spell(spell)

        assert spell._pre_hooks is original_pre
        assert spell._hooks_enabled is True
    finally:
        spellbook.cleanup()


def test_component_spellbook_add_hooks_to_spell_empty_lists_disable_gate() -> None:
    """
    Purpose:
        Verify empty hook lists disable the hook gate.
    Contract:
        - _hooks_enabled is False when all hook lists are empty.
    Returns:
        None.
    Raises:
        AssertionError: If hook gating remains enabled.
    """
    spellbook = _make_spellbook()

    def pre_hook() -> None:
        """
        Purpose:
            Provide a pre-hook for gate disable checks.
        Contract:
            - No side effects; used for identity checks.
        Returns:
            None.
        """
        return None

    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spellbook._add_hooks_to_spell(spell, pre_hooks=[pre_hook])
        spellbook._add_hooks_to_spell(
            spell,
            pre_hooks=[],
            activation_hooks=[],
            post_hooks=[],
        )

        assert spell._pre_hooks == []
        assert spell._activation_hooks == []
        assert spell._post_hooks == []
        assert spell._hooks_enabled is False
    finally:
        spellbook.cleanup()


def test_component_spellbook_add_hooks_to_spell_rejects_non_callable() -> None:
    """
    Purpose:
        Validate hook attachment rejects non-callable hooks.
    Contract:
        - _add_hooks_to_spell raises TypeError for non-callable hook entries.
    Returns:
        None.
    Raises:
        AssertionError: If non-callable hooks are accepted.
    """
    spellbook = _make_spellbook()
    bad_hook = object()

    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        with pytest.raises(TypeError, match="pre_hooks"):
            spellbook._add_hooks_to_spell(spell, pre_hooks=[bad_hook])
    finally:
        spellbook.cleanup()


def test_component_spellbook_add_hooks_to_spell_rejects_non_spell() -> None:
    """
    Purpose:
        Validate hook attachment rejects non-Spell inputs.
    Contract:
        - _add_hooks_to_spell raises TypeError when the target is not an ISpell.
    Returns:
        None.
    Raises:
        AssertionError: If non-Spell inputs are accepted.
    """
    spellbook = _make_spellbook()
    try:
        with pytest.raises(TypeError, match="spell must be an instance"):
            spellbook._add_hooks_to_spell(object(), pre_hooks=[])
    finally:
        spellbook.cleanup()


def test_component_spellbook_make_spell_key_normalizes_inputs() -> None:
    """
    Purpose:
        Validate _make_spell_key uses normalized spell key parts.
    Contract:
        - Returned key matches SpellInputUtils.make_spell_key_from_parts.
    Returns:
        None.
    Raises:
        AssertionError: If key normalization does not match helper behavior.
    """
    spellbook = _make_spellbook()
    try:
        key = spellbook._make_spell_key("ISERVICE", "BasicService", "PRIMARY")
        expected = SpellInputUtils.make_spell_key_from_parts(
            spellframe="ISERVICE",
            spell_name="BasicService",
            binding_name="PRIMARY",
        )
        assert key == expected
    finally:
        spellbook.cleanup()


def test_component_spellbook_create_link_contract_raises_on_inconsistent_state() -> None:
    """
    Purpose:
        Validate inconsistent contract maps raise on creation.
    Contract:
        - _create_link_contract raises RuntimeError when maps are inconsistent.
    Returns:
        None.
    Raises:
        AssertionError: If inconsistent state does not raise.
    """
    spellbook = _make_spellbook()
    conduit_id = "peer"
    spellbook._contracted_spells[conduit_id] = {}

    try:
        with pytest.raises(RuntimeError, match="Inconsistent link contract state"):
            spellbook._create_link_contract(conduit_id)
    finally:
        spellbook.cleanup()


def test_component_spellbook_remove_contracted_spell_raises_when_missing_version() -> None:
    """
    Purpose:
        Validate removal raises when the version id is not present.
    Contract:
        - _remove_contracted_spell raises RuntimeError for unknown version ids.
    Returns:
        None.
    Raises:
        AssertionError: If removal does not raise for missing version ids.
    """
    spellbook = _make_spellbook()
    conduit_id = "peer"

    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    try:
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None
        spellbook._add_contracted_spell(spell, conduit_id)

        with pytest.raises(RuntimeError, match="not found"):
            spellbook._remove_contracted_spell("missing-version", conduit_id)
    finally:
        spellbook.cleanup()

