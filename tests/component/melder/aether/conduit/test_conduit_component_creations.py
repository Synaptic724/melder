from __future__ import annotations

import pytest
from melder import Aether, Conduit
from melder.aether.conduit.creations.creations import Creations
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_conduit_creations() -> None:
    """
    Purpose:
        Ensure component creations tests start with a clean Aether singleton.
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


def _make_spellbook(
    *,
    dynamic: bool = False,
    disposal: bool = False,
    disposal_methods: list[str] | None = None,
) -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for component creations tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
        - dynamic mode sets system_state to "dynamic".
        - disposal settings are set before defaults to respect idempotency.
    Args:
        dynamic: When True, configure the Spellbook for dynamic mode.
        disposal: Whether disposal behavior is enabled.
        disposal_methods: Optional list of cleanup method names.
    Returns:
        Spellbook: Configured Spellbook instance.
    """
    configuration = SpellbookConfiguration()
    if disposal:
        configuration.set_property("disposal", True)
        configuration.set_property(
            "disposal_method_names",
            list(disposal_methods or ["cleanup"]),
        )
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(
        configuration,
        dynamic=dynamic,
    )
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


class _ManyService:
    """
    Purpose:
        Provide a distinct service type for Existence.many tests.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker for many-scope instances.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()

    def cleanup(self) -> None:
        """
        Purpose:
            Provide a disposal hook for many-scope registration tests.
        Contract:
            - Does not raise.
        Returns:
            None.
        """
        return


class _LineageService:
    """
    Purpose:
        Provide a service type for unique_per_conduit_lineage tests.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker for lineage-scope instances.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()


class _UniqueService:
    """
    Purpose:
        Provide a service type for unique_per_conduit tests.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker for unique-per-conduit instances.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()


class _ClusterService:
    """
    Purpose:
        Provide a service type for unique_per_conduit_cluster tests.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker for cluster-scope instances.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()


class _CountingService:
    """
    Purpose:
        Provide a disposable service that tracks cleanup calls.
    Contract:
        - cleanup increments cleanup_calls.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize cleanup call tracking.
        Contract:
            - cleanup_calls starts at 0.
        Returns:
            None.
        """
        self.cleanup_calls = 0

    def cleanup(self) -> None:
        """
        Purpose:
            Record cleanup calls for disposal verification.
        Contract:
            - Increments cleanup_calls.
        Returns:
            None.
        """
        self.cleanup_calls += 1


class _CountingServiceMany:
    """
    Purpose:
        Provide a distinct disposable service for many-scope cleanup tests.
    Contract:
        - cleanup increments cleanup_calls.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize cleanup call tracking.
        Contract:
            - cleanup_calls starts at 0.
        Returns:
            None.
        """
        self.cleanup_calls = 0

    def cleanup(self) -> None:
        """
        Purpose:
            Record cleanup calls for disposal verification.
        Contract:
            - Increments cleanup_calls.
        Returns:
            None.
        """
        self.cleanup_calls += 1


class _DisposalOrderService:
    """
    Purpose:
        Capture disposal order for LIFO cleanup validation.
    Contract:
        - Each instance records its creation index.
        - cleanup appends the index to the shared order list.
    """

    _counter = 0
    cleanup_order: list[int] = []

    def __init__(self) -> None:
        """
        Purpose:
            Capture creation order for LIFO disposal testing.
        Contract:
            - order_index increments per instance.
        """
        self.order_index = _DisposalOrderService._counter
        _DisposalOrderService._counter += 1

    def cleanup(self) -> None:
        """
        Purpose:
            Record cleanup order for LIFO assertions.
        Contract:
            - Appends order_index to cleanup_order.
        """
        _DisposalOrderService.cleanup_order.append(self.order_index)


def test_component_conduit_meld_many_registers_multiple_creations() -> None:
    """
    Purpose:
        Validate Existence.many melds are tracked in Creations.
    Contract:
        - Each meld call produces a distinct instance.
        - Creations._creations stores all many instances for the spell_id.
    Returns:
        None.
    Raises:
        AssertionError: If instances are reused or not recorded.
    """
    spellbook = _make_spellbook(disposal=True)
    spell_id = spellbook.bind(
        spell=_ManyService,
        existence=Existence.many,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        creations = conduit._creations
        instance_a = conduit.meld(spell=spell_id)
        instance_b = conduit.meld(spell=spell_id)

        assert instance_a is not instance_b
        bucket = creations._creations.get(spell_id)
        assert bucket is not None
        assert [creation.value for creation in bucket] == [instance_a, instance_b]
    finally:
        conduit.cleanup()


def test_component_conduit_meld_unique_per_conduit_lineage_registers_in_lineage_bucket() -> None:
    """
    Purpose:
        Validate unique_per_conduit_lineage melds register in lineage storage.
    Contract:
        - Creations._creations stores the created instance under spell_id.
    Returns:
        None.
    Raises:
        AssertionError: If lineage storage does not retain the instance.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_LineageService,
        existence=Existence.unique_per_conduit_lineage,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        creations = conduit._creations
        instance = conduit.meld(spell=spell_id)
        entry = creations._creations.get(spell_id)
        assert entry is not None
        assert entry.value is instance
    finally:
        conduit.cleanup()


def test_component_conduit_meld_unique_per_conduit_cluster_registers_in_cluster_bucket() -> None:
    """
    Purpose:
        Validate unique_per_conduit_cluster melds register in cluster storage.
    Contract:
        - Creations._creations stores the created instance under spell_id.
    Returns:
        None.
    Raises:
        AssertionError: If cluster storage does not retain the instance.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=_ClusterService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        creations = conduit._creations
        instance = conduit.meld(spell=spell_id)
        entry = creations._creations.get(spell_id)
        assert entry is not None
        assert entry.value is instance
    finally:
        conduit.cleanup()


def test_component_conduit_cleanup_disposes_across_scopes() -> None:
    """
    Purpose:
        Validate Conduit cleanup disposes instances across scopes.
    Contract:
        - Disposal methods are invoked for unique-per-conduit and many scopes.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not invoked for created instances.
    """
    spellbook = _make_spellbook(disposal=True, disposal_methods=["cleanup"])
    unique_id = spellbook.bind(
        spell=_CountingService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    many_id = spellbook.bind(
        spell=_CountingServiceMany,
        existence=Existence.many,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        unique_instance = conduit.meld(spell=unique_id)
        many_instance_a = conduit.meld(spell=many_id)
        many_instance_b = conduit.meld(spell=many_id)

        conduit.cleanup()

        assert unique_instance.cleanup_calls == 1
        assert many_instance_a.cleanup_calls == 1
        assert many_instance_b.cleanup_calls == 1
    finally:
        conduit.cleanup()


def test_component_conduit_upgrade_transfers_lesser_creations_and_reuses_unique() -> None:
    """
    Purpose:
        Validate lesser upgrade transfers creations and preserves reuse.
    Contract:
        - Unique-per-conduit creations are preserved across upgrade.
        - Many creations remain tracked after upgrade.
    Returns:
        None.
    Raises:
        AssertionError: If creations are not transferred or reused correctly.
    """
    spellbook = _make_spellbook(dynamic=True, disposal=True)
    unique_id = spellbook.bind(
        spell=_UniqueService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    many_id = spellbook.bind(
        spell=_ManyService,
        existence=Existence.many,
        permissions="create",
    )
    root = spellbook.conjure(automatic=False, name="root")
    lesser = root.create_lesser_conduit()
    try:
        unique_instance = lesser.meld(spell=unique_id)
        many_instance = lesser.meld(spell=many_id)

        lesser.upgrade_to_normal(name="upgraded")

        assert isinstance(lesser._creations, Creations)
        reused_unique = lesser.meld(spell=unique_id)
        assert reused_unique is unique_instance

        many_instance_after = lesser.meld(spell=many_id)
        assert many_instance_after is not many_instance

        bucket = lesser._creations._creations.get(many_id)
        assert bucket is not None
        values = [creation.value for creation in bucket]
        assert many_instance in values
        assert many_instance_after in values
    finally:
        lesser.cleanup()
        root.cleanup()


def test_component_conduit_cleanup_disposes_lifo() -> None:
    """
    Purpose:
        Validate cleanup disposes creations in LIFO order.
    Contract:
        - Later created instances are disposed before earlier ones.
    Returns:
        None.
    Raises:
        AssertionError: If disposal order is not LIFO.
    """
    _DisposalOrderService._counter = 0
    _DisposalOrderService.cleanup_order = []
    spellbook = _make_spellbook(disposal=True, disposal_methods=["cleanup"])
    spell_id = spellbook.bind(
        spell=_DisposalOrderService,
        existence=Existence.many,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        conduit.meld(spell=spell_id)
        conduit.meld(spell=spell_id)
        conduit.meld(spell=spell_id)

        conduit.cleanup()

        assert _DisposalOrderService.cleanup_order == [2, 1, 0]
    finally:
        conduit.cleanup()
