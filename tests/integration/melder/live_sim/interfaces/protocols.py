"""
Live-sim integration interfaces.

Purpose:
    Provide interface definitions for live-sim integration tests without
    redefining the shared mock protocols in multiple places.
Contract:
    - Re-exports existing mock protocols for consistency.
    - Adds a root application protocol for live-sim wiring assertions.
"""

from typing import Protocol

from tests.mocks.spellbook.protocols import ICache
from tests.mocks.spellbook.protocols import IConfig
from tests.mocks.spellbook.protocols import IHandler
from tests.mocks.spellbook.protocols import ILogger
from tests.mocks.spellbook.protocols import IRepository
from tests.mocks.spellbook.protocols import IService
from tests.mocks.spellbook.protocols import ITool
from tests.mocks.spellbook.protocols import IWorker


class ILiveSimApplication(Protocol):
    """
    Purpose:
        Provide a protocol for the live-sim application root.
    Contract:
        - Exposes the core dependencies for validation and inspection.
    """
    worker: IWorker
    logger: ILogger
    config: IConfig

