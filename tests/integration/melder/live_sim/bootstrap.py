"""
Live-sim bootstrap helpers for integration tests.

Purpose:
    Provide reusable helpers that bind and conjure live-sim conduits for
    automatic and dynamic modes.
Contract:
    - Binding helpers always use interface spellframes.
    - Automatic bootstrap returns a single conduit plus application id.
    - Dynamic bootstrap exposes separate owner/borrower creation and a final
      linking helper that returns the conduits.
"""

from dataclasses import dataclass

from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.integration.melder.live_sim.interfaces.protocols import ICache
from tests.integration.melder.live_sim.interfaces.protocols import IConfig
from tests.integration.melder.live_sim.interfaces.protocols import IHandler
from tests.integration.melder.live_sim.interfaces.protocols import ILogger
from tests.integration.melder.live_sim.interfaces.protocols import ILiveSimApplication
from tests.integration.melder.live_sim.interfaces.protocols import IRepository
from tests.integration.melder.live_sim.interfaces.protocols import IService
from tests.integration.melder.live_sim.interfaces.protocols import IWorker
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


@dataclass(frozen=True)
class LiveSimBindings:
    """
    Purpose:
        Bundle spell ids for the live-sim dependency graph.
    Contract:
        - Stores ids for all non-application dependencies.
        - Used to contract dependencies in dynamic mode.
    """
    config_id: str
    logger_id: str
    repository_id: str
    cache_id: str
    service_id: str
    handler_id: str
    worker_id: str


@dataclass(frozen=True)
class LiveSimAutomaticContext:
    """
    Purpose:
        Container for automatic-mode live-sim bootstrap output.
    Contract:
        - Exposes the conjured conduit and application spell id.
    """
    spellbook: Spellbook
    conduit: Conduit
    application_id: str
    bindings: LiveSimBindings


@dataclass(frozen=True)
class LiveSimDynamicOwner:
    """
    Purpose:
        Container for the owner side of a dynamic live-sim bootstrap.
    Contract:
        - Holds the owner spellbook, conduit, and dependency bindings.
    """
    spellbook: Spellbook
    conduit: Conduit
    bindings: LiveSimBindings


@dataclass(frozen=True)
class LiveSimDynamicBorrower:
    """
    Purpose:
        Container for the borrower side of a dynamic live-sim bootstrap.
    Contract:
        - Holds the borrower spellbook, conduit, and application spell id.
    """
    spellbook: Spellbook
    conduit: Conduit
    application_id: str


@dataclass(frozen=True)
class LiveSimDynamicContext:
    """
    Purpose:
        Container for linked dynamic live-sim conduits.
    Contract:
        - Exposes the linked owner/borrower conduits and application id.
    """
    owner_conduit: Conduit
    borrower_conduit: Conduit
    application_id: str
    owner_bindings: LiveSimBindings


def create_live_sim_dynamic_configuration() -> Configuration:
    """
    Purpose:
        Build a configuration for dynamic live-sim integration tests.
    Contract:
        - Uses dynamic defaults.
        - Sets phase_scheduler_workers_per_spellbook to 1.
    Returns:
        Configuration: Configured dynamic configuration.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _configure_automatic_spellbook(spellbook: Spellbook) -> None:
    """
    Purpose:
        Apply deterministic configuration for automatic live-sim tests.
    Contract:
        - Sets the phase scheduler worker count to 1.
    Args:
        spellbook: Spellbook to configure.
    Returns:
        None.
    """
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)


def bind_live_sim_dependencies(spellbook: Spellbook) -> LiveSimBindings:
    """
    Purpose:
        Bind live-sim dependency spells to a spellbook.
    Contract:
        - All bindings use interface spellframes.
        - All bindings use Existence.unique and create permissions.
    Args:
        spellbook: Spellbook to populate with dependencies.
    Returns:
        LiveSimBindings: Spell ids for dependency spells.
    """
    config_id = spellbook.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
        spellframe=IConfig,
    )
    logger_id = spellbook.bind(
        spell=BasicLogger,
        existence=Existence.unique,
        permissions="create",
        spellframe=ILogger,
    )
    repository_id = spellbook.bind(
        spell=RepositoryWithLogger,
        existence=Existence.unique,
        permissions="create",
        spellframe=IRepository,
    )
    cache_id = spellbook.bind(
        spell=LiveSimCache,
        existence=Existence.unique,
        permissions="create",
        spellframe=ICache,
    )
    service_id = spellbook.bind(
        spell=ServiceWithRepository,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
    )
    handler_id = spellbook.bind(
        spell=LiveSimHandler,
        existence=Existence.unique,
        permissions="create",
        spellframe=IHandler,
    )
    worker_id = spellbook.bind(
        spell=LiveSimWorker,
        existence=Existence.unique,
        permissions="create",
        spellframe=IWorker,
    )

    return LiveSimBindings(
        config_id=config_id,
        logger_id=logger_id,
        repository_id=repository_id,
        cache_id=cache_id,
        service_id=service_id,
        handler_id=handler_id,
        worker_id=worker_id,
    )


def bind_live_sim_application(spellbook: Spellbook) -> str:
    """
    Purpose:
        Bind the live-sim application root spell.
    Contract:
        - Uses the live-sim application interface spellframe.
    Args:
        spellbook: Spellbook to bind the application spell into.
    Returns:
        str: Spell id for the application root.
    """
    return spellbook.bind(
        spell=LiveSimApplication,
        existence=Existence.unique,
        permissions="create",
        spellframe=ILiveSimApplication,
    )


def bootstrap_live_sim_automatic(*, name: str = "live-sim-auto") -> LiveSimAutomaticContext:
    """
    Purpose:
        Bootstrap a live-sim environment in automatic mode.
    Contract:
        - Uses a single spellbook and conduit.
        - Returns the conduit and application spell id.
    Args:
        name: Conduit name to use for the automatic bootstrap.
    Returns:
        LiveSimAutomaticContext: Bootstrap result for automatic mode.
    """
    spellbook = Spellbook()
    _configure_automatic_spellbook(spellbook)
    bindings = bind_live_sim_dependencies(spellbook)
    application_id = bind_live_sim_application(spellbook)
    conduit = spellbook.conjure(name=name)

    return LiveSimAutomaticContext(
        spellbook=spellbook,
        conduit=conduit,
        application_id=application_id,
        bindings=bindings,
    )


def create_live_sim_dynamic_owner(
    configuration: Configuration,
    *,
    name: str = "live-sim-owner",
) -> LiveSimDynamicOwner:
    """
    Purpose:
        Create the owner side of a dynamic live-sim environment.
    Contract:
        - Uses the provided configuration.
        - Binds dependency spells and conjures a normal conduit.
    Args:
        configuration: Shared configuration for dynamic spellbooks.
        name: Conduit name to assign to the owner.
    Returns:
        LiveSimDynamicOwner: Owner bootstrap context.
    """
    spellbook = Spellbook(configuration=configuration)
    bindings = bind_live_sim_dependencies(spellbook)
    conduit = spellbook.conjure(automatic=False, name=name)
    return LiveSimDynamicOwner(
        spellbook=spellbook,
        conduit=conduit,
        bindings=bindings,
    )


def create_live_sim_dynamic_borrower(
    configuration: Configuration,
    *,
    name: str = "live-sim-borrower",
) -> LiveSimDynamicBorrower:
    """
    Purpose:
        Create the borrower side of a dynamic live-sim environment.
    Contract:
        - Uses the provided configuration.
        - Binds the application spell and conjures a normal conduit.
    Args:
        configuration: Shared configuration for dynamic spellbooks.
        name: Conduit name to assign to the borrower.
    Returns:
        LiveSimDynamicBorrower: Borrower bootstrap context.
    """
    spellbook = Spellbook(configuration=configuration)
    application_id = bind_live_sim_application(spellbook)
    conduit = spellbook.conjure(automatic=False, name=name)
    return LiveSimDynamicBorrower(
        spellbook=spellbook,
        conduit=conduit,
        application_id=application_id,
    )


def link_live_sim_dynamic(
    owner: LiveSimDynamicOwner,
    borrower: LiveSimDynamicBorrower,
) -> LiveSimDynamicContext:
    """
    Purpose:
        Link dynamic live-sim conduits and contract dependencies.
    Contract:
        - Links the owner and borrower conduits.
        - Contracts all owner dependencies into the borrower.
        - Returns the linked conduits and application id.
    Args:
        owner: Owner bootstrap context.
        borrower: Borrower bootstrap context.
    Returns:
        LiveSimDynamicContext: Linked conduit context.
    Raises:
        AssertionError: If linking or contracting fails.
    """
    assert owner.conduit.link(borrower.conduit) is True

    report = borrower.conduit.add_spells_to_contract(
        spell_ids=[
            owner.bindings.config_id,
            owner.bindings.logger_id,
            owner.bindings.repository_id,
            owner.bindings.cache_id,
            owner.bindings.service_id,
            owner.bindings.handler_id,
            owner.bindings.worker_id,
        ],
        conduit=owner.conduit,
        permissions="create",
        link_dependencies=True,
    )
    assert all(value is True for value in report.values())

    return LiveSimDynamicContext(
        owner_conduit=owner.conduit,
        borrower_conduit=borrower.conduit,
        application_id=borrower.application_id,
        owner_bindings=owner.bindings,
    )


def bootstrap_live_sim_dynamic() -> LiveSimDynamicContext:
    """
    Purpose:
        Convenience bootstrap for dynamic live-sim integration tests.
    Contract:
        - Creates owner/borrower conduits using a shared configuration.
        - Links and contracts dependencies.
        - Returns the linked conduits.
    Returns:
        LiveSimDynamicContext: Linked conduit context for dynamic mode.
    """
    configuration = create_live_sim_dynamic_configuration()
    owner = create_live_sim_dynamic_owner(configuration)
    borrower = create_live_sim_dynamic_borrower(configuration)
    return link_live_sim_dynamic(owner, borrower)

