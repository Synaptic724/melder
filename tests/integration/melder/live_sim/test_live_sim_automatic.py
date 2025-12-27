from tests.integration.melder.live_sim.bootstrap import bootstrap_live_sim_automatic
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


def test_live_sim_automatic_bootstrap_melds_application() -> None:
    """
    Purpose:
        Validate automatic live-sim bootstrap can meld the application root.
    Contract:
        - The application resolves with interface-typed dependencies.
        - Shared dependencies reuse the same instances in automatic mode.
    Returns:
        None.
    Raises:
        AssertionError: If the application graph is not wired correctly.
    """
    context = bootstrap_live_sim_automatic()
    try:
        app = context.conduit.meld(spell=context.application_id)

        assert isinstance(app, LiveSimApplication)
        assert isinstance(app.worker, LiveSimWorker)
        assert isinstance(app.worker.handler, LiveSimHandler)
        assert isinstance(app.worker.handler.cache, LiveSimCache)
        assert isinstance(app.worker.handler.service, ServiceWithRepository)
        assert isinstance(app.worker.repository, RepositoryWithLogger)
        assert isinstance(app.logger, BasicLogger)
        assert isinstance(app.config, BasicConfig)

        assert app.worker.repository is app.worker.handler.service.repository
        assert app.worker.handler.cache.config is app.config
    finally:
        context.conduit.cleanup()
