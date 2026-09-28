"""
The registry that resolves a transaction type to its strategy class.

Dependency rule: standard library plus `melder.utilities` only.

Mirrors `TransactionStrategyBuilder`. The registry is CLOSED in the sense that
every member of the transaction vocabulary must resolve; it is OPEN in the sense
that each subsystem registers its own families rather than the plane shipping
them. That split is deliberate: the plane owns the CONTRACT, the subsystems own
the KNOWLEDGE of what their operations touch.
"""

import threading
from typing import Dict, Optional, Tuple, Type

from melder.aether.aetheric_mediator.transaction_strategy import TransactionStrategy
from melder.aether.aetheric_mediator.transaction_type import TransactionType
from melder.utilities.general_base.cleanable import Cleanable


class StrategyBuilder(Cleanable):
    """
    Registry-backed resolver from transaction type to strategy class.

    Purpose:
        Give the mediator exactly one way to answer "who decides what this
        transaction claims", and make a missing answer a loud, early failure
        rather than a silent default.

    Contract:
        - STRATEGIES ARE REGISTERED AS CLASSES, never instances, matching the
          contract in `TransactionStrategy`. The registry stores the type
          object itself.
        - REGISTRATION IS EXPLICIT AND REPLACEABLE. Re-registering a type
          REPLACES the previous class and is legal, so a subsystem can
          override a default. Replacement is deliberate rather than an error
          because the alternative - silently keeping the first registration -
          hides a real conflict.
        - AN UNREGISTERED TYPE IS AN ERROR, NOT A DEFAULT. There is no
          fallback strategy. A default would have to guess a claim set, and a
          guessed claim set is precisely how isolation is lost quietly. If a
          type has no strategy, the transaction must not run.
        - VALIDATION IS AVAILABLE BUT NOT AUTOMATIC. `missing_types()` reports
          which vocabulary members have no strategy, so a caller can assert
          completeness at boot instead of discovering a gap at runtime.

    Owned State:
        `_strategies` (type -> strategy class) and one lock.

    Threading:
        One `RLock`. Registration is expected at boot; resolution is a read on
        the transaction path and takes the lock only briefly.

    Registration:
        MELDER KERNEL - guarded. Constructed by the plane; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Resolves a transaction type to its registered
        strategy class. Seeded with the plane's own family for every vocabulary
        member at construction; a type with no registration raises rather than
        guessing.
    """

    __slots__ = Cleanable.__slots__ + ["_lock", "_strategies"]

    def __init__(self) -> None:
        """
        Build one strategy registry, seeded with the plane's own families.

        Contract:
            - Every `TransactionType` member resolves immediately after
              construction, so `missing_types()` is empty on a fresh registry.
              That is the same posture `TransactionStrategyBuilder` takes in the
              DevOps plane: a vocabulary member without a strategy is a build
              error, not a runtime surprise.
            - Seeding happens LAST, after the lock and the map exist, because
              `_register_default_strategies` goes through the public `register`
              verb and that verb takes the lock.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._strategies: Dict[TransactionType, Type[TransactionStrategy]] = {}
        self._register_default_strategies()

    def _register_default_strategies(self) -> None:
        """
        Internal

        Register the plane's own family for every transaction type.

        Contract:
            - Registers EVERY member of `TransactionType`. A new member added to
              the vocabulary without a line here leaves `missing_types()`
              non-empty, which is the intended way to notice.
            - Imports the families INSIDE the method rather than at module
              scope. Each family module imports `transaction_strategy`, which
              this module also imports - a module-scope import here would make
              that latent relationship a real import cycle.
            - Imports each family module DIRECTLY. There is no
              `strategies/__init__.py` to import from: every melder subpackage
              is a PEP 420 namespace package by explicit design (`pyproject`
              sets `namespaces = true`) and the repo keeps exactly ONE
              `__init__.py`, at the package root.
            - Registration stays REPLACEABLE: a subsystem may override any of
              these afterwards through `Mediator.strategies` by registering its
              own class against the same type. Seeding does not close that path.

        Returns:
            None.
        """
        from melder.aether.aetheric_mediator.strategies.agent_repair_transaction_strategy import (
            AgentRepairTransactionStrategy,
        )
        from melder.aether.aetheric_mediator.strategies.checkpoint_load_transaction_strategy import (
            CheckpointLoadTransactionStrategy,
        )
        from melder.aether.aetheric_mediator.strategies.formation_load_transaction_strategy import (
            FormationLoadTransactionStrategy,
        )
        from melder.aether.aetheric_mediator.strategies.frame_create_transaction_strategy import (
            FrameCreateTransactionStrategy,
        )
        from melder.aether.aetheric_mediator.strategies.index_graft_transaction_strategy import (
            IndexGraftTransactionStrategy,
        )
        from melder.aether.aetheric_mediator.strategies.subsystem_configure_transaction_strategy import (
            SubsystemConfigureTransactionStrategy,
        )
        from melder.aether.aetheric_mediator.strategies.subsystem_deactivate_transaction_strategy import (
            SubsystemDeactivateTransactionStrategy,
        )
        from melder.aether.aetheric_mediator.strategies.subsystem_activate_transaction_strategy import (
            SubsystemActivateTransactionStrategy,
        )

        self.register(
            transaction_type=TransactionType.FRAME_CREATE,
            strategy=FrameCreateTransactionStrategy,
        )
        self.register(
            transaction_type=TransactionType.CHECKPOINT_LOAD,
            strategy=CheckpointLoadTransactionStrategy,
        )
        self.register(
            transaction_type=TransactionType.FORMATION_LOAD,
            strategy=FormationLoadTransactionStrategy,
        )
        self.register(
            transaction_type=TransactionType.INDEX_GRAFT,
            strategy=IndexGraftTransactionStrategy,
        )
        self.register(
            transaction_type=TransactionType.SUBSYSTEM_CONFIGURE,
            strategy=SubsystemConfigureTransactionStrategy,
        )
        self.register(
            transaction_type=TransactionType.SUBSYSTEM_ACTIVATE,
            strategy=SubsystemActivateTransactionStrategy,
        )
        self.register(
            transaction_type=TransactionType.SUBSYSTEM_DEACTIVATE,
            strategy=SubsystemDeactivateTransactionStrategy,
        )
        self.register(
            transaction_type=TransactionType.AGENT_REPAIR,
            strategy=AgentRepairTransactionStrategy,
        )

    def cleanup(self) -> None:
        """
        Idempotently drop all registrations.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            # Re-check under the lock; the outer check is a fast path only.
            if self._cleaned:
                return
            self._cleaned = True
            self._strategies.clear()
        del self._strategies
        del self._lock

    def register(
            self,
            *,
            transaction_type: TransactionType,
            strategy: Type[TransactionStrategy],
    ) -> None:
        """
        Register the strategy class for one transaction type.

        Args:
            transaction_type: The vocabulary member being served.
            strategy: The strategy CLASS (not an instance).

        Returns:
            None.

        Raises:
            RuntimeError: If the registry has been cleaned.
            TypeError: If `strategy` is not a `TransactionStrategy` subclass,
                or an instance was passed where a class was required.
        """
        self.check_cleaned()
        if not isinstance(strategy, type) or not issubclass(
            strategy, TransactionStrategy
        ):
            raise TypeError(
                "strategy must be a TransactionStrategy SUBCLASS, not an "
                "instance or unrelated type; got {0!r}.".format(strategy)
            )
        with self._lock:
            self._strategies[transaction_type] = strategy

    def resolve(
            self,
            transaction_type: TransactionType,
    ) -> Type[TransactionStrategy]:
        """
        Return the strategy class for one transaction type.

        Args:
            transaction_type: The vocabulary member to resolve.

        Returns:
            Type[TransactionStrategy]: The registered class.

        Raises:
            RuntimeError: If the registry has been cleaned.
            KeyError: If no strategy is registered. Deliberately fatal - a
                transaction whose claim set nobody can compute must not run.
        """
        self.check_cleaned()
        with self._lock:
            strategy = self._strategies.get(transaction_type)
        if strategy is None:
            raise KeyError(
                "no strategy registered for transaction type {0!r}; a "
                "transaction whose claim set cannot be computed must not "
                "run.".format(transaction_type.value)
            )
        return strategy

    def is_registered(self, transaction_type: TransactionType) -> bool:
        """
        Report whether a strategy is registered for one type.

        Args:
            transaction_type: The vocabulary member to test.

        Returns:
            bool: True when a strategy is registered.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return transaction_type in self._strategies

    def missing_types(self) -> Tuple[TransactionType, ...]:
        """
        Return vocabulary members that have no registered strategy.

        Contract:
            Lets a caller assert completeness AT BOOT rather than discovering
            a gap when the first transaction of that type is attempted.

        Returns:
            Tuple[TransactionType, ...]: Unserved types, in vocabulary order.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            registered = set(self._strategies.keys())
        return tuple(
            member for member in TransactionType if member not in registered
        )

    def describe(self) -> Dict[str, Optional[str]]:
        """
        Return a detached view of the registration table.

        Returns:
            Dict[str, Optional[str]]: Type value to strategy class name, with
                None for unserved members so gaps are visible at a glance.

        Raises:
            RuntimeError: If the registry has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            table = dict(self._strategies)
        return {
            member.value: (
                table[member].__name__ if member in table else None
            )
            for member in TransactionType
        }
