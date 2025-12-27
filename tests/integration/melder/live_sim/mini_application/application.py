"""
Mini application components for live-sim integration tests.

Purpose:
    Provide a small dependency graph that uses interface types throughout.
Contract:
    - All constructor parameters are typed with live-sim interfaces.
    - Instances store dependencies for inspection by integration tests.
"""

from tests.integration.melder.live_sim.interfaces.protocols import ICache
from tests.integration.melder.live_sim.interfaces.protocols import IConfig
from tests.integration.melder.live_sim.interfaces.protocols import IHandler
from tests.integration.melder.live_sim.interfaces.protocols import ILogger
from tests.integration.melder.live_sim.interfaces.protocols import ILiveSimApplication
from tests.integration.melder.live_sim.interfaces.protocols import IRepository
from tests.integration.melder.live_sim.interfaces.protocols import IService
from tests.integration.melder.live_sim.interfaces.protocols import IWorker


class LiveSimCache:
    """
    Purpose:
        Provide a simple cache implementation for live-sim tests.
    Contract:
        - Stores the injected config for assertions.
    """
    def __init__(self, config: IConfig) -> None:
        """
        Purpose:
            Capture the injected config dependency.
        Contract:
            - Stores the config instance for inspection.
        Args:
            config: Injected configuration instance.
        Returns:
            None.
        """
        self.config = config


class LiveSimHandler:
    """
    Purpose:
        Provide a handler implementation for live-sim tests.
    Contract:
        - Stores the injected service and cache dependencies.
    """
    def __init__(self, service: IService, cache: ICache) -> None:
        """
        Purpose:
            Capture handler dependencies.
        Contract:
            - Stores the service and cache instances for inspection.
        Args:
            service: Injected service instance.
            cache: Injected cache instance.
        Returns:
            None.
        """
        self.service = service
        self.cache = cache


class LiveSimWorker:
    """
    Purpose:
        Provide a worker implementation for live-sim tests.
    Contract:
        - Stores the injected handler and repository dependencies.
    """
    def __init__(self, handler: IHandler, repository: IRepository) -> None:
        """
        Purpose:
            Capture worker dependencies.
        Contract:
            - Stores the handler and repository instances for inspection.
        Args:
            handler: Injected handler instance.
            repository: Injected repository instance.
        Returns:
            None.
        """
        self.handler = handler
        self.repository = repository


class LiveSimApplication:
    """
    Purpose:
        Provide the live-sim application root.
    Contract:
        - Stores worker, logger, and config dependencies for inspection.
        - Acts as the root spell for live-sim integration tests.
    """
    def __init__(
        self,
        worker: IWorker,
        logger: ILogger,
        config: IConfig,
    ) -> None:
        """
        Purpose:
            Capture application dependencies.
        Contract:
            - Stores worker, logger, and config instances for inspection.
        Args:
            worker: Injected worker instance.
            logger: Injected logger instance.
            config: Injected configuration instance.
        Returns:
            None.
        """
        self.worker = worker
        self.logger = logger
        self.config = config

