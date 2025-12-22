from typing import Protocol


class IService(Protocol):
    """
    Purpose:
        Provide a protocol spellframe for service DI tests.
    Contract:
        Acts as a DI grouping key for service-like dependencies.
    """


class IConfig(Protocol):
    """
    Purpose:
        Provide a protocol spellframe for configuration DI tests.
    Contract:
        Acts as a DI grouping key for configuration dependencies.
    """


class ILogger(Protocol):
    """
    Purpose:
        Provide a protocol spellframe for logger DI tests.
    Contract:
        Acts as a DI grouping key for logging dependencies.
    """


class IRepository(Protocol):
    """
    Purpose:
        Provide a protocol spellframe for repository DI tests.
    Contract:
        Acts as a DI grouping key for repository dependencies.
    """


class ICache(Protocol):
    """
    Purpose:
        Provide a protocol spellframe for cache DI tests.
    Contract:
        Acts as a DI grouping key for cache dependencies.
    """


class IHandler(Protocol):
    """
    Purpose:
        Provide a protocol spellframe for handler DI tests.
    Contract:
        Acts as a DI grouping key for handler collections.
    """


class IWorker(Protocol):
    """
    Purpose:
        Provide a protocol spellframe for worker DI tests.
    Contract:
        Acts as a DI grouping key for worker dependencies.
    """


class ITool(Protocol):
    """
    Purpose:
        Provide a protocol spellframe for tool DI tests.
    Contract:
        Acts as a DI grouping key for tool dependencies.
    """
