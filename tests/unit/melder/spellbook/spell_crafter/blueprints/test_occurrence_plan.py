import pytest
from typing import Dict, Optional

from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.aether.spellbook.spell_compiler.blueprints.occurrence_plan import OccurrencePlanBuilder
from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.aether.spellbook.spell_compiler.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)


class _StubSpellIndex:
    """
    Purpose:
        Provide a minimal SpellIndex-like stub for occurrence plan tests.
    Contract:
        - Exposes a stable `current` id.
        - Supplies a deterministic lineage id for diagnostics.
    """

    def __init__(self, current_id: str) -> None:
        """
        Purpose:
            Initialize the stub index with a current id.
        Contract:
            Stores the current id and derives a lineage id.
        Args:
            current_id: Version id to expose via `current`.
        Returns:
            None.
        """
        self._current = current_id
        self.id = f"lineage:{current_id}"

    @property
    def current(self) -> str:
        """
        Purpose:
            Return the current version id.
        Contract:
            Always returns the id passed at construction time.
        Returns:
            str: The current version id.
        """
        return self._current


class _StubSpellbook:
    """
    Purpose:
        Provide a minimal Spellbook-like container for occurrence planning.
    Contract:
        - Exposes local and contracted spell mappings used during planning.
        - Maintains a spell_id -> spell pool for SpellCrafter lookups.
        - Holds a `_spell_validator` attribute for SpellCrafter initialization.
    """

    def __init__(self, spells: Dict[_StubSpellIndex, "_StubSpell"]) -> None:
        """
        Purpose:
            Initialize the stub spellbook with local spell mappings.
        Contract:
            Stores spells and provides an empty contracted map.
        Args:
            spells: Mapping of stub indices to stub spells.
        Returns:
            None.
        """
        self._spell_validator = object()
        self._configuration = _StubConfiguration()
        self._aetheric_frame_configuration = AethericFrameConfiguration(
            origin_spellbook_id="spellbook-stub",
            system_state=SystemState.dynamic,
            ai_native_enabled=False,
            rift_enabled=False,
        )
        self._spells = spells
        self._contracted_spells: Dict[str, Dict[_StubSpellIndex, "_StubSpell"]] = {}
        self._lookup_spells: Dict[tuple, _StubSpellIndex] = {
            spell.key: spell_index for spell_index, spell in spells.items()
        }
        self._lookup_contracted_spells: Dict[str, Dict[tuple, _StubSpellIndex]] = {}
        self._spell_id_pool: Dict[str, "_StubSpell"] = {
            spell_index.current: spell for spell_index, spell in spells.items()
        }

    @property
    def spells(self) -> Dict[_StubSpellIndex, "_StubSpell"]:
        """
        Purpose:
            Expose local spells for occurrence-plan tests.
        Contract:
            Returns the stored spells mapping.
        Returns:
            Dict[_StubSpellIndex, _StubSpell]: Local spells mapping.
        """
        return self._spells

    @property
    def contracted_spells(self) -> Dict[str, Dict[_StubSpellIndex, "_StubSpell"]]:
        """
        Purpose:
            Expose contracted spells for occurrence-plan tests.
        Contract:
            Returns an empty mapping by default.
        Returns:
            Dict[str, Dict[_StubSpellIndex, _StubSpell]]: Contracted spells mapping.
        """
        return self._contracted_spells


class _StubSpell:
    """
    Purpose:
        Provide a minimal ISpell-like object for occurrence plan compilation.
    Contract:
        - Supplies spell metadata required by OccurrencePlanBuilder.
        - Exposes a SpellIndex-like object via `spell_index`.
    """

    def __init__(
            self,
            *,
            spell_id: str,
            spell_name: str,
            existence: Existence,
            spell_callable,
            spellframe: Optional[object] = None,
            binding_name: Optional[str] = None,
            spellbook: Optional[_StubSpellbook] = None,
    ) -> None:
        """
        Purpose:
            Initialize the stub spell with required metadata.
        Contract:
            Stores spell identity, callable, and existence policy.
        Args:
            spell_id: Version id for the spell.
            spell_name: Human-readable name used in diagnostics.
            existence: Existence policy used by instance planning.
            spell_callable: Callable inspected for SpellContract defaults.
            spellbook: Optional stub spellbook for spell_id pool access.
        Returns:
            None.
        """
        self.spell_index = _StubSpellIndex(spell_id)
        self.spell_name = spell_name
        self.spell = spell_callable
        self.existence = existence
        self.spellframe = spellframe
        self.binding_name = binding_name
        self.mutation_override: dict = {}
        self.key = SpellInputUtils.make_spell_key_from_parts(
            spellframe=spellframe,
            spell_name=spell_name,
            binding_name=binding_name,
        )
        if spellbook is None:
            spellbook = _StubSpellbook({})
        self._spellbook = spellbook
        self._spell_system_states = None
        self.is_existing_creation = False
        self.requirements = None


class _StubConfiguration:
    """
    Purpose:
        Provide configuration access for system_state.
    Contract:
        Returns a dynamic system_state by default.
    """

    def get_property(self, _name: str) -> SystemState:
        return SystemState.dynamic


class _SystemStatesStub:
    """
    Purpose:
        Provide minimal system states surface for occurrence planning.
    Contract:
        - Exposes _local_topologies for topology lookup.
    """

    def __init__(self) -> None:
        self._local_topologies: Dict[str, object] = {}


def _root_factory(dep: object) -> object:
    """
    Purpose:
        Provide a root callable with a dependency parameter.
    Contract:
        Returns a new object instance.
    Args:
        dep: Injected dependency (unused).
    Returns:
        object: A new object instance.
    """
    return object()


def _root_factory_with_contract(
        dep: object,
        contract: object = SpellContract(spellframe="Service", binding_name="primary"),
) -> object:
    """
    Purpose:
        Provide a root callable with a SpellContract default.
    Contract:
        Returns a new object instance.
    Args:
        dep: Injected dependency (unused).
        contract: Contract placeholder (unused).
    Returns:
        object: A new object instance.
    """
    return object()


def _dep_factory() -> object:
    """
    Purpose:
        Provide a dependency callable with no parameters.
    Contract:
        Returns a new object instance.
    Returns:
        object: A new object instance.
    """
    return object()


def _make_blueprint(root_id: str, dep_id: str) -> RootResolutionBlueprint:
    """
    Purpose:
        Build a minimal RootResolutionBlueprint for a root -> dep DAG.
    Contract:
        - The dependency edge is tagged with param name "dep".
        - The ordered node ids are dependency-first.
    Args:
        root_id: Root spell id.
        dep_id: Dependency spell id.
    Returns:
        RootResolutionBlueprint: Blueprint containing the DAG and order.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency(dep_id, root_id, param_name="dep")
    return RootResolutionBlueprint(
        root_spell_id=root_id,
        root_lineage_id=f"lineage:{root_id}",
        dag=dag,
        ordered_node_ids=(dep_id, root_id),
    )


def test_occurrence_plan_builder_shared_instances() -> None:
    """
    Purpose:
        Verify occurrence planning for shared-existence spells.
    Contract:
        - Occurrence graph includes root and dependency occurrences.
        - Shared spells collapse to a single instance key.
    """
    root_id = "root"
    dep_id = "dep"
    spellbook = _StubSpellbook({})
    root_spell = _StubSpell(
        spell_id=root_id,
        spell_name="Root",
        existence=Existence.unique,
        spell_callable=_root_factory,
        spellbook=spellbook,
    )
    dep_spell = _StubSpell(
        spell_id=dep_id,
        spell_name="Dep",
        existence=Existence.unique,
        spell_callable=_dep_factory,
        spellbook=spellbook,
    )
    blueprint = _make_blueprint(root_id, dep_id)

    builder = OccurrencePlanBuilder(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup={
            root_id: root_spell,
            dep_id: dep_spell,
        },
        system_states=_SystemStatesStub(),
    )
    plan = builder.build()

    path_registry = plan.path_registry
    root_path_id = path_registry.root_path_id
    dep_path_id = path_registry.extend_path(root_path_id, "dep")
    assert plan.root_spell_id == root_id
    assert plan.execution_order == [dep_id, root_id]
    assert plan.occurrence_graph == {
        (root_id, root_path_id): {"dep": [(dep_id, dep_path_id)]},
        (dep_id, dep_path_id): {},
    }
    assert plan.instance_keys_by_spell_id[root_id] == [(root_id, None)]
    assert plan.instance_keys_by_spell_id[dep_id] == [(dep_id, None)]
    assert plan.canonical_occurrences_by_spell_id[root_id] == (root_id, root_path_id)
    assert plan.canonical_occurrences_by_spell_id[dep_id] == (dep_id, dep_path_id)
    assert plan.root_instance_key == (root_id, None)
    assert plan.shared_spell_ids == {root_id, dep_id}
    assert plan.contract_overrides_by_occurrence == {}
    assert plan.contract_overrides_by_spell_id == {}
    assert plan.contract_dependencies_complete is True


def test_normalize_contract_override_payload_none_returns_empty_dict() -> None:
    """
    Verify None contract payloads normalize to an empty dict.

    Contract:
        - None payloads are treated as no overrides.

    Raises:
        AssertionError: If None payloads do not normalize to {}.
    """
    normalized = OccurrencePlanBuilder._normalize_contract_override_payload(
        payload=None,
        consumer_spell_id="spell-1",
        consumer_spell_name="spell-name",
        param_name="param",
    )
    assert normalized == {}


def test_occurrence_plan_builder_many_instances_preserve_paths() -> None:
    """
    Purpose:
        Verify Existence.many spells preserve occurrence paths.
    Contract:
        - Non-shared spells retain per-occurrence instance keys.
    """
    root_id = "root"
    dep_id = "dep"
    spellbook = _StubSpellbook({})
    root_spell = _StubSpell(
        spell_id=root_id,
        spell_name="Root",
        existence=Existence.unique,
        spell_callable=_root_factory,
        spellbook=spellbook,
    )
    dep_spell = _StubSpell(
        spell_id=dep_id,
        spell_name="Dep",
        existence=Existence.many,
        spell_callable=_dep_factory,
        spellbook=spellbook,
    )
    blueprint = _make_blueprint(root_id, dep_id)

    builder = OccurrencePlanBuilder(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup={
            root_id: root_spell,
            dep_id: dep_spell,
        },
        system_states=_SystemStatesStub(),
    )
    plan = builder.build()

    dep_path_id = plan.path_registry.extend_path(plan.path_registry.root_path_id, "dep")
    assert plan.instance_keys_by_spell_id[dep_id] == [(dep_id, dep_path_id)]
    assert dep_id not in plan.shared_spell_ids
    assert dep_id not in plan.canonical_occurrences_by_spell_id
    assert plan.contract_overrides_by_occurrence == {}
    assert plan.contract_overrides_by_spell_id == {}
    assert plan.contract_dependencies_complete is True


def test_run_phase_occurrence_plan_requires_phase5() -> None:
    """
    Purpose:
        Ensure Phase 8 compilation fails when Phase 5 artifacts are missing.
    Contract:
        - Raises a deterministic ValueError when Phase 5 has not completed.
    """
    root_spell = _StubSpell(
        spell_id="root",
        spell_name="Root",
        existence=Existence.unique,
        spell_callable=_root_factory,
        spellbook=_StubSpellbook({}),
    )
    crafter = SpellCrafter(root_spell)

    with pytest.raises(RuntimeError, match="Phase 5 root blueprint is required"):
        crafter.run_phase_occurrence_plan(conduit_id="conduit")


def test_run_phase_occurrence_plan_compiles_for_root() -> None:
    """
    Purpose:
        Validate Phase 8 compilation attaches an OccurrencePlan for roots.
    Contract:
        - OccurrencePlan is stored on the SpellCrafter when blueprint exists.
    """
    root_id = "root"
    dep_id = "dep"
    root_spell = _StubSpell(
        spell_id=root_id,
        spell_name="Root",
        existence=Existence.unique,
        spell_callable=_root_factory,
    )
    dep_spell = _StubSpell(
        spell_id=dep_id,
        spell_name="Dep",
        existence=Existence.unique,
        spell_callable=_dep_factory,
    )
    spellbook = _StubSpellbook({
        root_spell.spell_index: root_spell,
        dep_spell.spell_index: dep_spell,
    })
    root_spell._spellbook = spellbook
    dep_spell._spellbook = spellbook
    root_spell._spell_system_states = _SystemStatesStub()

    blueprint = _make_blueprint(root_id, dep_id)

    crafter = SpellCrafter(root_spell)
    crafter._spell_system_states = _SystemStatesStub()
    crafter._root_blueprint_phase5 = blueprint
    crafter._entire_dag_blueprint_phase5 = {root_id: blueprint}

    crafter.run_phase_occurrence_plan(conduit_id="conduit")

    plan = crafter.occurrence_plan_phase8
    assert plan is not None
    assert plan.root_spell_id == root_id
    assert plan.execution_order == [dep_id, root_id]
    assert plan.contract_dependencies_complete is True


def test_occurrence_plan_builder_defers_spell_contracts() -> None:
    """
    Purpose:
        Verify SpellContract defaults do not add dependencies in Phase 8.
    Contract:
        - Occurrence planning ignores SpellContract sockets.
        - DAG dependencies remain intact.
    """
    root_id = "root"
    dep_id = "dep"
    spellbook = _StubSpellbook({})
    root_spell = _StubSpell(
        spell_id=root_id,
        spell_name="Root",
        existence=Existence.unique,
        spell_callable=_root_factory_with_contract,
        spellbook=spellbook,
    )
    dep_spell = _StubSpell(
        spell_id=dep_id,
        spell_name="Dep",
        existence=Existence.unique,
        spell_callable=_dep_factory,
        spellbook=spellbook,
    )
    blueprint = _make_blueprint(root_id, dep_id)

    builder = OccurrencePlanBuilder(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup={
            root_id: root_spell,
            dep_id: dep_spell,
        },
        system_states=_SystemStatesStub(),
    )
    plan = builder.build()

    path_registry = plan.path_registry
    root_path_id = path_registry.root_path_id
    dep_path_id = path_registry.extend_path(root_path_id, "dep")
    assert plan.occurrence_graph == {
        (root_id, root_path_id): {"dep": [(dep_id, dep_path_id)]},
        (dep_id, dep_path_id): {},
    }
    assert plan.contract_overrides_by_occurrence == {}
    assert plan.contract_overrides_by_spell_id == {}
    assert plan.contract_dependencies_complete is False


def test_occurrence_plan_builder_resolves_spell_contract_when_available() -> None:
    """
    Purpose:
        Verify SpellContract dependencies are added when providers exist.
    Contract:
        - Contract sockets resolve to contracted providers when available.
        - The resolved provider occurrence is included in the graph.
    """
    root_id = "root"
    dep_id = "dep"
    provider_id = "provider"
    root_spell = _StubSpell(
        spell_id=root_id,
        spell_name="Root",
        existence=Existence.unique,
        spell_callable=_root_factory_with_contract,
        spellframe="Root",
        binding_name="primary",
    )
    dep_spell = _StubSpell(
        spell_id=dep_id,
        spell_name="Dep",
        existence=Existence.unique,
        spell_callable=_dep_factory,
        spellframe="Dep",
        binding_name="primary",
    )
    provider_spell = _StubSpell(
        spell_id=provider_id,
        spell_name="ServiceProvider",
        existence=Existence.unique,
        spell_callable=_dep_factory,
        spellframe="Service",
        binding_name="primary",
    )
    spellbook = _StubSpellbook({
        root_spell.spell_index: root_spell,
        dep_spell.spell_index: dep_spell,
    })
    spellbook._contracted_spells = {
        "conduit-a": {provider_spell.spell_index: provider_spell},
    }
    spellbook._lookup_contracted_spells = {
        "conduit-a": {provider_spell.key: provider_spell.spell_index},
    }
    root_spell._spellbook = spellbook
    dep_spell._spellbook = spellbook
    provider_spell._spellbook = spellbook

    blueprint = _make_blueprint(root_id, dep_id)

    builder = OccurrencePlanBuilder(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup={
            root_id: root_spell,
            dep_id: dep_spell,
            provider_id: provider_spell,
        },
        system_states=_SystemStatesStub(),
    )
    plan = builder.build()

    path_registry = plan.path_registry
    root_path_id = path_registry.root_path_id
    dep_path_id = path_registry.extend_path(root_path_id, "dep")
    contract_path_id = path_registry.extend_path(root_path_id, "contract")
    assert plan.occurrence_graph == {
        (root_id, root_path_id): {
            "dep": [(dep_id, dep_path_id)],
            "contract": [(provider_id, contract_path_id)],
        },
        (dep_id, dep_path_id): {},
        (provider_id, contract_path_id): {},
    }
    assert plan.contract_overrides_by_occurrence == {}
    assert plan.contract_overrides_by_spell_id == {}
    assert plan.contract_dependencies_complete is True


def test_build_instance_plan_is_stable_across_occurrence_graph_insertion_orders() -> None:
    """
    Purpose:
        Ensure instance planning is deterministic across equivalent map orders.
    Contract:
        - Canonical occurrence selection is stable for shared spells.
        - Many-existence instance-key ordering is stable.
    """
    root_id = "root"
    shared_id = "shared"
    many_id = "many"
    spellbook = _StubSpellbook({})
    root_spell = _StubSpell(
        spell_id=root_id,
        spell_name="Root",
        existence=Existence.unique,
        spell_callable=_root_factory,
        spellbook=spellbook,
    )
    shared_spell = _StubSpell(
        spell_id=shared_id,
        spell_name="Shared",
        existence=Existence.unique,
        spell_callable=_dep_factory,
        spellbook=spellbook,
    )
    many_spell = _StubSpell(
        spell_id=many_id,
        spell_name="Many",
        existence=Existence.many,
        spell_callable=_dep_factory,
        spellbook=spellbook,
    )
    builder = OccurrencePlanBuilder(
        root_spell=root_spell,
        blueprint=_make_blueprint(root_id, shared_id),
        spell_lookup={
            root_id: root_spell,
            shared_id: shared_spell,
            many_id: many_spell,
        },
        system_states=_SystemStatesStub(),
    )

    occurrence_graph_first = {
        (shared_id, 7): {},
        (many_id, 5): {},
        (root_id, 0): {},
        (many_id, 1): {},
        (shared_id, 2): {},
    }
    occurrence_graph_second = {
        (root_id, 0): {},
        (shared_id, 2): {},
        (many_id, 1): {},
        (shared_id, 7): {},
        (many_id, 5): {},
    }

    first_result = builder._build_instance_plan(
        occurrence_graph=occurrence_graph_first,
        root_spell_id=root_id,
    )
    second_result = builder._build_instance_plan(
        occurrence_graph=occurrence_graph_second,
        root_spell_id=root_id,
    )

    assert first_result == second_result
    first_instance_keys, first_canonical, first_root_key, first_shared = first_result
    assert first_instance_keys[many_id] == [(many_id, 1), (many_id, 5)]
    assert first_canonical[shared_id] == (shared_id, 2)
    assert first_root_key == (root_id, None)
    assert first_shared == {root_id, shared_id}


def test_compile_contract_overrides_is_stable_across_occurrence_map_orders() -> None:
    """
    Purpose:
        Ensure contract override compilation is deterministic for equivalent maps.
    Contract:
        - Provider occurrence keys are stable across occurrence-map insertion order.
        - Spell-id grouped override rows are stable across equivalent inputs.
    """

    def _root_factory_with_override_contract(
            contract: object = SpellContract(
                spellframe="Service",
                binding_name="primary",
                spell_override={"value": "x"},
            ),
    ) -> object:
        return object()

    root_id = "root"
    provider_id = "provider"

    root_spell = _StubSpell(
        spell_id=root_id,
        spell_name="Root",
        existence=Existence.unique,
        spell_callable=_root_factory_with_override_contract,
        spellframe="Root",
        binding_name="primary",
    )
    provider_spell = _StubSpell(
        spell_id=provider_id,
        spell_name="Provider",
        existence=Existence.unique,
        spell_callable=_dep_factory,
        spellframe="Service",
        binding_name="primary",
    )
    spellbook = _StubSpellbook({
        root_spell.spell_index: root_spell,
    })
    spellbook._contracted_spells = {
        "conduit-a": {provider_spell.spell_index: provider_spell},
    }
    spellbook._lookup_contracted_spells = {
        "conduit-a": {provider_spell.key: provider_spell.spell_index},
    }
    root_spell._spellbook = spellbook
    provider_spell._spellbook = spellbook

    blueprint = _make_blueprint(root_id, provider_id)

    builder_one = OccurrencePlanBuilder(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup={
            root_id: root_spell,
            provider_id: provider_spell,
        },
        system_states=_SystemStatesStub(),
    )
    branch_path_one = builder_one._path_registry.extend_path(
        builder_one._path_registry.root_path_id,
        "branch",
    )
    first_occurrence_graph = {
        (root_id, branch_path_one): {},
        (root_id, builder_one._path_registry.root_path_id): {},
    }
    first_occurrence_map, first_spell_map, first_complete = (
        builder_one._compile_contract_overrides(
            occurrence_graph=first_occurrence_graph,
        )
    )

    builder_two = OccurrencePlanBuilder(
        root_spell=root_spell,
        blueprint=_make_blueprint(root_id, provider_id),
        spell_lookup={
            root_id: root_spell,
            provider_id: provider_spell,
        },
        system_states=_SystemStatesStub(),
    )
    branch_path_two = builder_two._path_registry.extend_path(
        builder_two._path_registry.root_path_id,
        "branch",
    )
    second_occurrence_graph = {
        (root_id, builder_two._path_registry.root_path_id): {},
        (root_id, branch_path_two): {},
    }
    second_occurrence_map, second_spell_map, second_complete = (
        builder_two._compile_contract_overrides(
            occurrence_graph=second_occurrence_graph,
        )
    )

    assert first_complete is True
    assert second_complete is True
    assert first_occurrence_map == second_occurrence_map
    assert first_spell_map == second_spell_map

