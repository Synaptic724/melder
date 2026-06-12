"""Unit ring for the DevOps information-strategy catalog.

Covers the builder's default registration, execution counters, the five
catalog strategies (transaction activity view, cluster fanout, transfer
blast radius, frame operational view, registry consistency audit), and the
shared freshness inspector.
"""
from __future__ import annotations

from typing import Dict

import pytest

from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.aetheric_frame.dev_ops.devops_information_strategy import (
    DevopsInformationStrategy,
)
from melder.aether.aetheric_frame.dev_ops.information_strategies.information_strategy_support import (
    InformationFreshnessInspector,
)


def _build_registry() -> DevopsInformationRegistry:
    """Build one empty frame-scoped registry."""
    return DevopsInformationRegistry("frame-info-strategies")


def _build_populated_registry() -> DevopsInformationRegistry:
    """
    Build a registry with one coherent relational world.

    Shape:
        - spellbook-1 owns conduit-1 and conduit-2; spellbook-2 owns conduit-3.
        - conduit-1 provides to borrower conduit-3.
        - conduit-2 provides to borrower conduit-1.
        - cluster-alpha holds conduit-1 and conduit-2; cluster-beta holds
          conduit-1 and conduit-3.
        - txn-1 (bind) touches conduit-1's identity and scope.
        - txn-2 (link) touches conduit-3's scope.
    """
    registry = _build_registry()
    registry.register_spellbook_conduit_ownership(
        spellbook_id="spellbook-1", conduit_id="conduit-1"
    )
    registry.register_spellbook_conduit_ownership(
        spellbook_id="spellbook-1", conduit_id="conduit-2"
    )
    registry.register_spellbook_conduit_ownership(
        spellbook_id="spellbook-2", conduit_id="conduit-3"
    )
    registry.register_conduit_link(
        provider_conduit_id="conduit-1", borrower_conduit_id="conduit-3"
    )
    registry.register_conduit_link(
        provider_conduit_id="conduit-2", borrower_conduit_id="conduit-1"
    )
    registry.register_cluster_membership(
        cluster_id="cluster-alpha", conduit_id="conduit-1"
    )
    registry.register_cluster_membership(
        cluster_id="cluster-alpha", conduit_id="conduit-2"
    )
    registry.register_cluster_membership(
        cluster_id="cluster-beta", conduit_id="conduit-1"
    )
    registry.register_cluster_membership(
        cluster_id="cluster-beta", conduit_id="conduit-3"
    )
    registry.register_transaction(
        transaction_id="txn-1",
        transaction_object=object(),
        transaction_type="bind",
        identity_keys=[("conduit", "conduit-1")],
        scope_keys=["scope:conduit:conduit-1"],
    )
    registry.register_transaction(
        transaction_id="txn-2",
        transaction_object=object(),
        transaction_type="link",
        identity_keys=[("conduit", "conduit-3")],
        scope_keys=["scope:conduit:conduit-3"],
    )
    return registry


# ---------------------------------------------------------------------------
# Builder: default catalog + counters
# ---------------------------------------------------------------------------


def test_builder_registers_default_catalog() -> None:
    """A fresh registry's builder exposes the five default strategies."""
    registry = _build_registry()

    assert registry.information_strategy_builder.list_registered_strategy_names() == (
        "cluster_fanout",
        "frame_operational_view",
        "registry_consistency_audit",
        "transaction_activity_view",
        "transfer_blast_radius",
    )


def test_builder_unknown_strategy_raises_not_implemented() -> None:
    """Executing an unregistered strategy raises NotImplementedError."""
    registry = _build_registry()

    with pytest.raises(NotImplementedError, match="no_such_strategy"):
        registry.information_strategy_builder.execute(
            strategy_name="no_such_strategy", metadata={}
        )


def test_builder_counts_successful_executions_per_strategy() -> None:
    """Successful executions increment the per-name counter."""
    registry = _build_populated_registry()
    builder = registry.information_strategy_builder

    assert builder.get_execution_count("frame_operational_view") == 0
    builder.execute(strategy_name="frame_operational_view", metadata={})
    builder.execute(strategy_name="Frame_Operational_View", metadata={})
    builder.execute(strategy_name="registry_consistency_audit", metadata={})

    assert builder.get_execution_count("frame_operational_view") == 2
    assert builder.get_execution_count("registry_consistency_audit") == 1
    assert builder.list_execution_counts() == {
        "frame_operational_view": 2,
        "registry_consistency_audit": 1,
    }


def test_builder_failed_executions_do_not_count() -> None:
    """A strategy that raises does not increment its counter."""
    registry = _build_registry()
    builder = registry.information_strategy_builder

    with pytest.raises(ValueError):
        builder.execute(strategy_name="cluster_fanout", metadata={})

    assert builder.get_execution_count("cluster_fanout") == 0
    assert builder.list_execution_counts() == {}


def test_builder_list_execution_counts_returns_detached_copy() -> None:
    """Mutating the returned counts dict never alters builder state."""
    registry = _build_populated_registry()
    builder = registry.information_strategy_builder
    builder.execute(strategy_name="registry_consistency_audit", metadata={})

    counts = builder.list_execution_counts()
    counts["registry_consistency_audit"] = 99

    assert builder.get_execution_count("registry_consistency_audit") == 1


def test_builder_explicit_registration_overrides_default() -> None:
    """Re-registering a default name resolves to the override class."""
    registry = _build_registry()
    builder = registry.information_strategy_builder

    class _Override(DevopsInformationStrategy):
        @staticmethod
        def execute(
                *,
                devops_information_registry: DevopsInformationRegistry,
                metadata: Dict[str, object],
        ) -> Dict[str, object]:
            return {"strategy": "override"}

    builder.register_strategy("cluster_fanout", _Override)

    assert builder.execute(strategy_name="cluster_fanout", metadata={}) == {
        "strategy": "override"
    }


# ---------------------------------------------------------------------------
# Transaction activity view
# ---------------------------------------------------------------------------


def test_activity_view_identity_axis_lists_identity_transactions() -> None:
    """The identity axis returns the identity's transaction ids."""
    registry = _build_populated_registry()

    result = registry.information_strategy_builder.execute(
        strategy_name="transaction_activity_view",
        metadata={"identity_kind": "conduit", "identity_id": "conduit-1"},
    )

    assert result["axis"] == "identity"
    assert result["axis_value"] == "conduit:conduit-1"
    assert result["transaction_ids"] == ("txn-1",)
    assert result["transaction_count"] == 1


def test_activity_view_scope_axis_lists_scope_transactions() -> None:
    """The scope axis returns transactions indexed under one scope key."""
    registry = _build_populated_registry()

    result = registry.information_strategy_builder.execute(
        strategy_name="transaction_activity_view",
        metadata={"scope_key": "scope:conduit:conduit-3"},
    )

    assert result["axis"] == "scope"
    assert result["transaction_ids"] == ("txn-2",)
    assert "conduit:conduit-3" in result["freshness"]["regions"]


def test_activity_view_type_axis_lists_type_transactions() -> None:
    """The type axis returns all transactions of one family."""
    registry = _build_populated_registry()

    result = registry.information_strategy_builder.execute(
        strategy_name="transaction_activity_view",
        metadata={"transaction_type": "bind"},
    )

    assert result["axis"] == "transaction_type"
    assert result["transaction_ids"] == ("txn-1",)


def test_activity_view_without_axis_raises() -> None:
    """Axis-free metadata is rejected with a clear error."""
    registry = _build_populated_registry()

    with pytest.raises(ValueError, match="requires one axis"):
        registry.information_strategy_builder.execute(
            strategy_name="transaction_activity_view", metadata={}
        )


def test_activity_view_freshness_reports_baseline_and_staleness() -> None:
    """Freshness flags a reported region fresh and an unreported one stale."""
    registry = _build_populated_registry()
    registry.report_fact(
        fact_family="bind", region="conduit:conduit-1", reporter="txn-1"
    )

    fresh_result = registry.information_strategy_builder.execute(
        strategy_name="transaction_activity_view",
        metadata={
            "identity_kind": "conduit",
            "identity_id": "conduit-1",
            "max_age_in_seconds": 60.0,
        },
    )
    stale_result = registry.information_strategy_builder.execute(
        strategy_name="transaction_activity_view",
        metadata={
            "identity_kind": "conduit",
            "identity_id": "conduit-3",
            "max_age_in_seconds": 60.0,
        },
    )

    fresh_region = fresh_result["freshness"]["regions"]["conduit:conduit-1"]
    assert fresh_region["baseline_present"] is True
    assert fresh_result["freshness"]["fresh"] is True
    assert fresh_result["freshness"]["stale_regions"] == ()

    stale_region = stale_result["freshness"]["regions"]["conduit:conduit-3"]
    assert stale_region["baseline_present"] is False
    assert stale_result["freshness"]["fresh"] is False
    assert stale_result["freshness"]["stale_regions"] == (
        "conduit:conduit-3",
    )


# ---------------------------------------------------------------------------
# Cluster fanout
# ---------------------------------------------------------------------------


def test_cluster_fanout_for_conduit_unions_cluster_siblings() -> None:
    """A conduit's fanout unions every member across its clusters."""
    registry = _build_populated_registry()

    result = registry.information_strategy_builder.execute(
        strategy_name="cluster_fanout",
        metadata={"conduit_id": "conduit-1"},
    )

    assert result["cluster_ids"] == ("cluster-alpha", "cluster-beta")
    assert result["sibling_conduit_ids"] == ("conduit-2", "conduit-3")
    assert result["fanout_size"] == 2


def test_cluster_fanout_for_cluster_lists_members() -> None:
    """A cluster's fanout lists its member conduits."""
    registry = _build_populated_registry()

    result = registry.information_strategy_builder.execute(
        strategy_name="cluster_fanout",
        metadata={"cluster_id": "cluster-beta"},
    )

    assert result["member_conduit_ids"] == ("conduit-1", "conduit-3")
    assert result["fanout_size"] == 2


def test_cluster_fanout_rejects_zero_or_two_axes() -> None:
    """Exactly one of conduit_id/cluster_id must be supplied."""
    registry = _build_populated_registry()

    with pytest.raises(ValueError, match="exactly one"):
        registry.information_strategy_builder.execute(
            strategy_name="cluster_fanout", metadata={}
        )
    with pytest.raises(ValueError, match="exactly one"):
        registry.information_strategy_builder.execute(
            strategy_name="cluster_fanout",
            metadata={"conduit_id": "conduit-1", "cluster_id": "cluster-alpha"},
        )


# ---------------------------------------------------------------------------
# Transfer blast radius
# ---------------------------------------------------------------------------


def test_transfer_blast_radius_enumerates_full_impact_set() -> None:
    """The radius names owner, siblings, link partners, and clusters."""
    registry = _build_populated_registry()

    result = registry.information_strategy_builder.execute(
        strategy_name="transfer_blast_radius",
        metadata={"conduit_id": "conduit-1"},
    )

    assert result["owning_spellbook_id"] == "spellbook-1"
    assert result["sibling_conduit_ids"] == ("conduit-2",)
    assert result["borrower_conduit_ids"] == ("conduit-3",)
    assert result["provider_conduit_ids"] == ("conduit-2",)
    assert result["cluster_ids"] == ("cluster-alpha", "cluster-beta")
    # related conduits {2, 3} + clusters {alpha, beta} + owner
    assert result["blast_radius_size"] == 5
    assert "spellbook:spellbook-1" in result["freshness"]["regions"]
    assert "conduit:conduit-3" in result["freshness"]["regions"]


def test_transfer_blast_radius_for_unknown_conduit_is_empty() -> None:
    """An unmapped conduit yields an empty radius, not an error."""
    registry = _build_registry()

    result = registry.information_strategy_builder.execute(
        strategy_name="transfer_blast_radius",
        metadata={"conduit_id": "conduit-ghost"},
    )

    assert result["owning_spellbook_id"] is None
    assert result["sibling_conduit_ids"] == ()
    assert result["borrower_conduit_ids"] == ()
    assert result["provider_conduit_ids"] == ()
    assert result["cluster_ids"] == ()
    assert result["blast_radius_size"] == 0


def test_transfer_blast_radius_requires_conduit_id() -> None:
    """Missing conduit_id is rejected."""
    registry = _build_registry()

    with pytest.raises(ValueError, match="requires conduit_id"):
        registry.information_strategy_builder.execute(
            strategy_name="transfer_blast_radius", metadata={}
        )


# ---------------------------------------------------------------------------
# Frame operational view
# ---------------------------------------------------------------------------


def test_frame_operational_view_rolls_up_population_and_pressure() -> None:
    """The rollup reports ownership, link, cluster, and transaction shape."""
    registry = _build_populated_registry()
    registry.report_fact(
        fact_family="bind", region="conduit:conduit-1", reporter="txn-1"
    )
    registry.report_fact(
        fact_family="link", region="conduit:conduit-3", reporter="txn-2"
    )

    result = registry.information_strategy_builder.execute(
        strategy_name="frame_operational_view", metadata={}
    )

    assert result["aetheric_frame_name"] == "frame-info-strategies"
    assert result["spellbook_count"] == 2
    assert result["owned_conduit_count"] == 3
    assert result["link_edge_count"] == 2
    assert result["cluster_count"] == 2
    assert result["live_transaction_count"] == 2
    assert result["transaction_counts_by_type"] == {"bind": 1, "link": 1}
    assert result["fact_record_count"] == 2
    assert result["fact_record_counts_by_family"] == {"bind": 1, "link": 1}


def test_frame_operational_view_freshness_covers_reported_regions() -> None:
    """The freshness verdict spans every region with a baseline."""
    registry = _build_populated_registry()
    registry.report_fact(
        fact_family="bind", region="conduit:conduit-1", reporter="txn-1"
    )

    result = registry.information_strategy_builder.execute(
        strategy_name="frame_operational_view",
        metadata={"max_age_in_seconds": 60.0},
    )

    assert result["freshness"]["fresh"] is True
    assert tuple(result["freshness"]["regions"].keys()) == (
        "conduit:conduit-1",
    )


# ---------------------------------------------------------------------------
# Registry consistency audit
# ---------------------------------------------------------------------------


def test_consistency_audit_passes_on_public_api_state() -> None:
    """All maps populated through the public API audit clean."""
    registry = _build_populated_registry()

    result = registry.information_strategy_builder.execute(
        strategy_name="registry_consistency_audit", metadata={}
    )

    assert result["consistent"] is True
    assert result["finding_count"] == 0
    assert result["findings"] == ()


def test_consistency_audit_detects_injected_relationship_drift() -> None:
    """One-sided edges in cluster and ownership maps surface as findings."""
    registry = _build_populated_registry()
    # Reverse-only cluster edge: conduit claims a cluster that does not
    # claim it back.
    registry._conduit_to_clusters.setdefault("conduit-2", set()).add(
        "cluster-ghost"
    )
    # Ownership value drift: conduit points at a spellbook whose forward set
    # does not contain it.
    registry._conduit_to_spellbook["conduit-drift"] = "spellbook-1"

    result = registry.information_strategy_builder.execute(
        strategy_name="registry_consistency_audit", metadata={}
    )

    assert result["consistent"] is False
    assert result["finding_count"] == 2
    checks = {finding["check"] for finding in result["findings"]}
    assert "conduit_to_clusters/cluster_to_conduits" in checks
    assert "spellbook_to_conduits/conduit_to_spellbook" in checks


def test_consistency_audit_detects_transaction_index_drift() -> None:
    """A scope index entry without its per-id twin surfaces as a finding."""
    registry = _build_populated_registry()
    registry._transaction_ids_by_scope.setdefault(
        "scope:conduit:conduit-9", set()
    ).add("txn-ghost")

    result = registry.information_strategy_builder.execute(
        strategy_name="registry_consistency_audit", metadata={}
    )

    assert result["consistent"] is False
    assert any(
        finding["check"]
        == "transaction_ids_by_scope/transaction_scope_keys_by_id"
        for finding in result["findings"]
    )


# ---------------------------------------------------------------------------
# Freshness inspector
# ---------------------------------------------------------------------------


def test_normalize_region_strips_scope_prefix_and_validates() -> None:
    """Scope keys fold onto region form; junk inputs are rejected."""
    assert (
        InformationFreshnessInspector.normalize_region("scope:conduit:c1")
        == "conduit:c1"
    )
    assert (
        InformationFreshnessInspector.normalize_region("spellbook:s1")
        == "spellbook:s1"
    )
    with pytest.raises(TypeError):
        InformationFreshnessInspector.normalize_region(7)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        InformationFreshnessInspector.normalize_region("scope:")


def test_read_optional_max_age_validates_values() -> None:
    """The optional tolerance must be a positive number when present."""
    assert InformationFreshnessInspector.read_optional_max_age({}) is None
    assert (
        InformationFreshnessInspector.read_optional_max_age(
            {"max_age_in_seconds": 5}
        )
        == 5.0
    )
    with pytest.raises(TypeError):
        InformationFreshnessInspector.read_optional_max_age(
            {"max_age_in_seconds": True}
        )
    with pytest.raises(ValueError):
        InformationFreshnessInspector.read_optional_max_age(
            {"max_age_in_seconds": 0}
        )


def test_build_freshness_view_reports_generations_and_reporters() -> None:
    """The per-region view carries family, generation, and reporter."""
    registry = _build_registry()
    registry.report_fact(
        fact_family="bind", region="conduit:c1", reporter="txn-a"
    )
    registry.report_fact(
        fact_family="bind", region="conduit:c1", reporter="txn-b"
    )

    view = InformationFreshnessInspector.build_freshness_view(
        devops_information_registry=registry,
        regions=["scope:conduit:c1", "conduit:c1"],
    )

    assert tuple(view["regions"].keys()) == ("conduit:c1",)
    records = view["regions"]["conduit:c1"]["fact_records"]
    assert len(records) == 1
    assert records[0]["fact_family"] == "bind"
    assert records[0]["generation"] == 2
    assert records[0]["last_reporter"] == "txn-b"
