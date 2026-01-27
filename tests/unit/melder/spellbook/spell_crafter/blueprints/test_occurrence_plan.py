import pytest
from typing import Dict, Optional

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.spellbook.existence.existence import Existence
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.spellbook.spell_crafter.blueprints.occurrence_plan import OccurrencePlanBuilder
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.spell_crafter import SpellCrafter


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
        Provide a minimal Spellbook-like container for SpellbookScanner.
    Contract:
        - Exposes `spells` and `contracted_spells` mappings.
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
        self._spells = spells
        self._contracted_spells: Dict[str, Dict[_StubSpellIndex, "_StubSpell"]] = {}
        self._lookup_spells: Dict[tuple, _StubSpellIndex] = {
            spell.key: spell_index for spell_index, spell in spells.items()
        }
        self._lookup_contracted_spells: Dict[str, Dict[tuple, _StubSpellIndex]] = {}

    @property
    def spells(self) -> Dict[_StubSpellIndex, "_StubSpell"]:
        """
        Purpose:
            Expose local spells for SpellbookScanner.
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
            Expose contracted spells for SpellbookScanner.
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
            spellbook: Optional stub spellbook for scanner access.
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
        self._spellbook = spellbook
        self._spell_system_states = None


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
    blueprint = _make_blueprint(root_id, dep_id)

    builder = OccurrencePlanBuilder(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup={
            root_id: root_spell,
            dep_id: dep_spell,
        },
        system_states=None,
    )
    plan = builder.build()

    assert plan.root_spell_id == root_id
    assert plan.execution_order == [dep_id, root_id]
    assert plan.occurrence_graph == {
        (root_id, ()): {"dep": [(dep_id, ("dep",))]},
        (dep_id, ("dep",)): {},
    }
    assert plan.instance_keys_by_spell_id[root_id] == [(root_id, None)]
    assert plan.instance_keys_by_spell_id[dep_id] == [(dep_id, None)]
    assert plan.canonical_occurrences_by_spell_id[root_id] == (root_id, ())
    assert plan.canonical_occurrences_by_spell_id[dep_id] == (dep_id, ("dep",))
    assert plan.root_instance_key == (root_id, None)
    assert plan.shared_spell_ids == {root_id, dep_id}


def test_occurrence_plan_builder_many_instances_preserve_paths() -> None:
    """
    Purpose:
        Verify Existence.many spells preserve occurrence paths.
    Contract:
        - Non-shared spells retain per-occurrence instance keys.
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
        existence=Existence.many,
        spell_callable=_dep_factory,
    )
    blueprint = _make_blueprint(root_id, dep_id)

    builder = OccurrencePlanBuilder(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup={
            root_id: root_spell,
            dep_id: dep_spell,
        },
        system_states=None,
    )
    plan = builder.build()

    assert plan.instance_keys_by_spell_id[dep_id] == [(dep_id, ("dep",))]
    assert dep_id not in plan.shared_spell_ids
    assert dep_id not in plan.canonical_occurrences_by_spell_id


def test_run_phase_occurrence_plan_requires_phase5() -> None:
    """
    Purpose:
        Ensure Phase 8 compilation fails when Phase 5 artifacts are missing.
    Contract:
        - Raises RuntimeError when Phase 5 has not completed.
    """
    root_spell = _StubSpell(
        spell_id="root",
        spell_name="Root",
        existence=Existence.unique,
        spell_callable=_root_factory,
        spellbook=_StubSpellbook({}),
    )
    crafter = SpellCrafter(root_spell)

    with pytest.raises(RuntimeError):
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

    blueprint = _make_blueprint(root_id, dep_id)

    crafter = SpellCrafter(root_spell)
    crafter._root_blueprint_phase5 = blueprint
    crafter._entire_dag_blueprint_phase5 = {root_id: blueprint}

    crafter.run_phase_occurrence_plan(conduit_id="conduit")

    plan = crafter.occurrence_plan_phase8
    assert plan is not None
    assert plan.root_spell_id == root_id
    assert plan.execution_order == [dep_id, root_id]


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
    root_spell = _StubSpell(
        spell_id=root_id,
        spell_name="Root",
        existence=Existence.unique,
        spell_callable=_root_factory_with_contract,
    )
    dep_spell = _StubSpell(
        spell_id=dep_id,
        spell_name="Dep",
        existence=Existence.unique,
        spell_callable=_dep_factory,
    )
    blueprint = _make_blueprint(root_id, dep_id)

    builder = OccurrencePlanBuilder(
        root_spell=root_spell,
        blueprint=blueprint,
        spell_lookup={
            root_id: root_spell,
            dep_id: dep_spell,
        },
        system_states=None,
    )
    plan = builder.build()

    assert plan.occurrence_graph == {
        (root_id, ()): {"dep": [(dep_id, ("dep",))]},
        (dep_id, ("dep",)): {},
    }


def test_occurrence_plan_builder_resolves_spell_contract_when_available() -> None:
    """
    Purpose:
        Verify SpellContract dependencies are added when providers exist.
    Contract:
        - Contract sockets resolve to local providers when available.
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
        provider_spell.spell_index: provider_spell,
    })
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
        system_states=None,
    )
    plan = builder.build()

    assert plan.occurrence_graph == {
        (root_id, ()): {
            "dep": [(dep_id, ("dep",))],
            "contract": [(provider_id, ("contract",))],
        },
        (dep_id, ("dep",)): {},
        (provider_id, ("contract",)): {},
    }
