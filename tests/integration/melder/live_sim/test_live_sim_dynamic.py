from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from tests.integration.melder.live_sim.bootstrap import (
    create_live_sim_dynamic_borrower,
    create_live_sim_dynamic_configuration,
    create_live_sim_dynamic_owner,
    link_live_sim_dynamic,
)
from tests.integration.melder.live_sim.mini_application.application import (
    LiveSimApplication,
    LiveSimCache,
    LiveSimHandler,
    LiveSimWorker,
)
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicLogger
from tests.mocks.spellbook.core_classes import RepositoryWithLogger
from tests.mocks.spellbook.core_classes import ServiceWithRepository


def _inbound_spell_ids(spells_by_conduit: dict | None) -> set[str]:
    """
    Purpose:
        Extract inbound spell ids from a contract snapshot.
    Contract:
        - Returns an empty set when snapshot is missing.
    Args:
        spells_by_conduit: Contract snapshot from get_spells_in_contract_by_conduit.
    Returns:
        set[str]: Inbound spell ids.
    """
    if not spells_by_conduit:
        return set()
    inbound = spells_by_conduit.get("inbound", [])
    return {spell_id for spell_id, _spell in inbound}


def test_live_sim_dynamic_bootstrap_links_and_melds_application() -> None:
    """
    Purpose:
        Validate dynamic live-sim bootstrap links conduits and resolves the app.
    Contract:
        - Owner dependencies are contracted into the borrower.
        - Conduit resolution validation passes before meld.
        - Application resolves with interface-typed dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If linking, validation, or melding fails.
    """
    configuration = create_live_sim_dynamic_configuration()
    owner = create_live_sim_dynamic_owner(configuration)
    borrower = create_live_sim_dynamic_borrower(configuration)
    context = link_live_sim_dynamic(owner, borrower)

    try:
        spells_by_conduit = borrower.conduit.get_spells_in_contract_by_conduit(
            owner.conduit.id
        )
        inbound_ids = _inbound_spell_ids(spells_by_conduit)
        assert context.owner_bindings.service_id in inbound_ids
        assert context.owner_bindings.repository_id in inbound_ids
        assert context.owner_bindings.cache_id in inbound_ids
        assert context.owner_bindings.logger_id in inbound_ids
        assert context.owner_bindings.config_id in inbound_ids

        state = borrower.conduit.validate_resolution()
        assert state is not None
        assert state.has_errors() is False
        assert state.get_root_validity(context.application_id) is SpellValidity.valid

        app = borrower.conduit.meld(spell=context.application_id)
        assert isinstance(app, LiveSimApplication)
        assert isinstance(app.worker, LiveSimWorker)
        assert isinstance(app.worker.handler, LiveSimHandler)
        assert isinstance(app.worker.handler.cache, LiveSimCache)
        assert isinstance(app.worker.handler.service, ServiceWithRepository)
        assert isinstance(app.worker.repository, RepositoryWithLogger)
        assert isinstance(app.logger, BasicLogger)
        assert isinstance(app.config, BasicConfig)
    finally:
        borrower.conduit.cleanup()
        owner.conduit.cleanup()
