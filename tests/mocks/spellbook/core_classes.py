"""
Reusable Spellbook test classes for common DI scenarios.

These classes intentionally keep behavior simple and predictable so tests
can focus on DI wiring, lifetime rules, and spell resolution semantics.
"""
from tests.mocks.spellbook.protocols import ICache
from tests.mocks.spellbook.protocols import IConfig
from tests.mocks.spellbook.protocols import ILogger
from tests.mocks.spellbook.protocols import IRepository
from tests.mocks.spellbook.protocols import IService
from tests.mocks.spellbook.protocols import ITool
from tests.mocks.spellbook.protocols import IWorker


class BasicService:
    """
    Purpose:
        Provide a simple class spell with a stable marker.
    Contract:
        - The marker value is stored verbatim for assertions.
        - No side effects beyond setting attributes.
    """
    def __init__(self, marker: str = "service") -> None:
        """
        Purpose:
            Initialize the service marker.
        Contract:
            Stores the provided marker on the instance.
        Args:
            marker: Stable marker value for assertions.
        Returns:
            None.
        """
        self.marker = marker


class BasicConfig:
    """
    Purpose:
        Provide a simple configuration object for DI tests.
    Contract:
        - Stores a label string for identification.
    """
    def __init__(self, label: str = "config") -> None:
        """
        Purpose:
            Initialize the config label.
        Contract:
            Stores the provided label on the instance.
        Args:
            label: Identifier for the config instance.
        Returns:
            None.
        """
        self.label = label


class ServiceWithConfig:
    """
    Purpose:
        Provide a service that depends on an IConfig instance.
    Contract:
        - Stores the injected config instance for assertions.
    """
    def __init__(self, config: IConfig) -> None:
        """
        Purpose:
            Capture the injected config dependency.
        Contract:
            Stores the config on the instance.
        Args:
            config: Injected configuration instance.
        Returns:
            None.
        """
        self.config = config


class BasicLogger:
    """
    Purpose:
        Provide a basic logger spell for DI graphs.
    Contract:
        - Stores a marker for identity checks.
    """
    def __init__(self, marker: str = "logger") -> None:
        """
        Purpose:
            Initialize the logger marker.
        Contract:
            Stores the provided marker on the instance.
        Args:
            marker: Identifier used in assertions.
        Returns:
            None.
        """
        self.marker = marker


class RepositoryWithLogger:
    """
    Purpose:
        Provide a repository spell that depends on an ILogger.
    Contract:
        - Stores the injected logger for assertions.
    """
    def __init__(self, logger: ILogger) -> None:
        """
        Purpose:
            Capture the logger dependency.
        Contract:
            Stores the logger on the instance.
        Args:
            logger: Injected logger instance.
        Returns:
            None.
        """
        self.logger = logger


class ServiceWithRepository:
    """
    Purpose:
        Provide a service that depends on an IRepository.
    Contract:
        - Stores the repository for assertions.
    """
    def __init__(self, repository: IRepository) -> None:
        """
        Purpose:
            Capture the repository dependency.
        Contract:
            Stores the repository on the instance.
        Args:
            repository: Injected repository instance.
        Returns:
            None.
        """
        self.repository = repository


class CacheClient:
    """
    Purpose:
        Provide a client spell that depends on an ICache.
    Contract:
        - Stores the injected cache instance for assertions.
    """
    def __init__(self, cache: ICache) -> None:
        """
        Purpose:
            Capture the cache dependency.
        Contract:
            Stores the cache on the instance.
        Args:
            cache: Injected cache instance.
        Returns:
            None.
        """
        self.cache = cache


class WorkerService:
    """
    Purpose:
        Provide a service that depends on an IWorker.
    Contract:
        - Stores the injected worker for assertions.
    """
    def __init__(self, worker: IWorker) -> None:
        """
        Purpose:
            Capture the worker dependency.
        Contract:
            Stores the worker on the instance.
        Args:
            worker: Injected worker instance.
        Returns:
            None.
        """
        self.worker = worker


class ToolUser:
    """
    Purpose:
        Provide a service that depends on an ITool.
    Contract:
        - Stores the injected tool for assertions.
    """
    def __init__(self, tool: ITool) -> None:
        """
        Purpose:
            Capture the tool dependency.
        Contract:
            Stores the tool on the instance.
        Args:
            tool: Injected tool instance.
        Returns:
            None.
        """
        self.tool = tool


class ServiceWithInterface:
    """
    Purpose:
        Provide a service that depends on an IService.
    Contract:
        - Stores the injected service for assertions.
    """
    def __init__(self, service: IService) -> None:
        """
        Purpose:
            Capture the injected service dependency.
        Contract:
            Stores the service on the instance.
        Args:
            service: Injected service instance.
        Returns:
            None.
        """
        self.service = service


class NamedService:
    """
    Purpose:
        Provide a service that stores a user-provided name.
    Contract:
        - Stores the provided name verbatim for assertions.
    """
    def __init__(self, name: str) -> None:
        """
        Purpose:
            Initialize the service name.
        Contract:
            Stores the provided name on the instance.
        Args:
            name: Identifier for this service.
        Returns:
            None.
        """
        self.name = name
