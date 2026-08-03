"""
The plane's own transaction families, one per `TransactionType` member.

Dependency rule (epic constraint 4, unchanged here): standard library plus
`melder.utilities` only. NOTHING in this package imports `melder.crystallizer`,
`melder.nexus`, `melder.mutation_research`, or any part of `melder.aether`
outside `aetheric_mediator` itself. That is enforceable by inspection precisely
because `build_start_plan` is PURE over `(submitter, metadata)` - deciding what a
transaction claims needs no subsystem code, only the caller's declared inputs.

WHY THESE LIVE IN THE PLANE, when `strategy_builder.py` says subsystems own the
knowledge of what their operations touch:

    Both are true, at different levels. The six members of `TransactionType` are
    TOP-LEVEL operations the plane itself defined - "one thread takes the world",
    "one thread takes one frame", "one thread enables one subsystem". Their claim
    shape is plane knowledge: it follows from the scope vocabulary
    (`world` / `frame:<name>` / `subsystem:<name>`), not from any subsystem's
    internals. Crystallizer's stage ordering, Nexus's per-Rift fan-out and MR's
    lock order are all BENEATH this layer and stay with their owners.

    A subsystem that later wants a finer family registers it from its own package
    through `Mediator.strategies`. That path is unchanged and this package does
    not close it.

JURISDICTION - the boundary these families must not cross:

    Anything INSIDE a frame belongs to that frame's `ChangeControlManager`, which
    is an admission authority in its own right with its own claim table. This
    plane therefore claims `frame:<name>` as ONE UNIT and never reaches past it.
    No family here emits `spellbook:`, `conduit:`, `spell_index:` or `ward:`
    keys, even though the surveys that produced these families identified real
    mutations at that grain. Claiming them would put two planes on one vocabulary
    with no arbiter between them.

    The consequence is deliberate and worth stating: when this plane holds
    `frame:<name>` as INTENT it is saying "piece-work is happening inside this
    frame", not "I have isolated what that work touches". The frame's own plane
    isolates that. The two compose by nesting, not by overlapping.

SHAPES:

    Five of the six families reduce to two claim shapes, which is the whole
    argument for a shared plane rather than three hand-rolled ones:

        WHOLE-WORLD EXCLUSIVE   `world` x
        PARENT + CHILD          `world` ix  +  <the unit> x

    The sixth, `AGENT_REPAIR`, is the only family whose claim set is supplied by
    the caller rather than derived - see its module for why that is correct and
    not a hole.
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
from melder.aether.aetheric_mediator.strategies.index_graft_transaction_strategy import (
    IndexGraftTransactionStrategy,
)
from melder.aether.aetheric_mediator.strategies.subsystem_disable_transaction_strategy import (
    SubsystemDisableTransactionStrategy,
)
from melder.aether.aetheric_mediator.strategies.subsystem_enable_transaction_strategy import (
    SubsystemEnableTransactionStrategy,
)

__all__ = [
    "AgentRepairTransactionStrategy",
    "CheckpointLoadTransactionStrategy",
    "FormationLoadTransactionStrategy",
    "IndexGraftTransactionStrategy",
    "SubsystemDisableTransactionStrategy",
    "SubsystemEnableTransactionStrategy",
]
