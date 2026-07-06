from typing import TYPE_CHECKING, Dict, List, Mapping, Optional, Set

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
        RootResolutionBlueprint,
    )
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.system.spell_system_index import (
        SpellSystemIndex,
    )
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.utilities.synchronization.cancellation_event_signal import (
        CancellationEvent,
    )


# Melder imports
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)


class EmptyCollectionStrategy(SpellSystemValidationStrategy):
    """
    Mode-scoped guard for required collection sockets with zero providers.

    Purpose:
        A required list[Frame] dependency that wired zero providers means two
        different things depending on the owning book's runtime mode:
        - AUTOMATIC books: the composition is final at conjure, so zero
          providers is a permanent wiring mistake. The strategy emits an
          ERROR and conjure fails fast (the original guard behavior).
        - DYNAMIC books: members can still arrive through post-conjure
          contract additions, so emptiness at conjure is not final. The
          strategy emits a WARNING for observability and the consumer spawns
          with [] injected for that socket (owner policy 2026-07-06),
          keeping deferred contract provisioning viable.

    Data source (why topology, at Phase 6):
        By Phase 6 the per-spell requirements artifact has already been nulled
        (SpellCompilerArtifact clears _requirements), and the combined DAG
        carries no is-collection flag and emits no edge for an empty list. The
        one Phase-6-durable record that a socket is a collection AND how many
        providers it wired is the local topology held in SpellSystemStates
        (SpellSocketDescriptor.is_collection + target_spell_ids) - the same
        store the Phase-6 visibility-gap guard reads.

    Contract:
        - Reads local topologies from SpellSystemStates for every scoped spell.
        - Emits one collection_socket_no_providers diagnostic per required
          (non-optional) collection socket whose target_spell_ids is empty:
          ERROR when the owning book's system_state is not dynamic (blocks
          conjure via the resolution gate), WARNING when it is dynamic.
        - Mode is read per spell from the owning Spellbook's frame
          configuration (spell._spellbook._aetheric_frame_configuration),
          the same surface the phase-9 contract-override path reads; spells
          without a resolvable mode are treated as non-dynamic (fail-fast).
        - Optional collection sockets are skipped: an optional list[Frame] may
          legitimately wire nothing (the constructor default applies).
        - Reads only; never mutates Phase 5/6 inputs.
        - Honors cancellation between spells.
    """

    __slots__: list[str] = []

    def run(
            self,
            *,
            index: SpellSystemIndex,
            blueprints: Dict[str, RootResolutionBlueprint],
            phase4_results: Mapping[str, object],
            broken_spell_ids: Set[str],
            spell_system_states: SpellSystemStates,
            spell_lookup: Mapping[str, Spell],
            diagnostics: List[SystemDiagnostic],
            cancel_event: Optional[CancellationEvent],
    ) -> None:
        """
        Flag required collection sockets that wired zero providers.

        Purpose:
            Convert a zero-provider required list[Frame] dependency into a
            fail-fast conjure ERROR for automatic books (composition is final,
            so the wiring can never be satisfied) and into an observability
            WARNING for dynamic books (post-conjure contracts can still supply
            members; codegen injects [] so the consumer spawns).

        Contract:
            - Iterates every node in the system index and reads its local
              topology from SpellSystemStates.
            - Emits a collection_socket_no_providers diagnostic for each
              required collection socket whose target_spell_ids tuple is
              empty: ERROR when the owning book is not dynamic, WARNING when
              it is.
            - Skips optional collection sockets and spells without a topology.
            - Reads only; never mutates Phase 5/6 inputs.
            - Honors cancel_event between spells.

        Args:
            index:
                Frame-level spell system index being validated.
            blueprints:
                Root blueprints keyed by root spell id.
            phase4_results:
                Per-spell Phase 4 artifacts keyed by spell id.
            broken_spell_ids:
                Spell ids already known broken at the spell-validation layer.
            spell_system_states:
                Registry providing each spell's durable local topology.
            spell_lookup:
                Visible spell version ids to spell objects for this scope.
            diagnostics:
                Shared list to append new diagnostics into.
            cancel_event:
                Optional cancellation signal honored during the walk.

        Returns:
            None.

        Raises:
            OperationCancelledError:
                If cancel_event is set while iterating.
        """
        for spell_id in index.nodes.keys():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            topology = spell_system_states.get_local_topology_by_id(spell_id)
            if topology is None:
                continue

            # Mode decides severity: dynamic books may receive members via
            # post-conjure contracts (WARNING + [] injection), automatic books
            # cannot (ERROR, conjure fails fast). Missing lookup/config
            # resolves to the fail-fast posture.
            spell_is_dynamic = False
            spell = spell_lookup.get(spell_id)
            if spell is not None:
                spellbook = spell._spellbook
                if spellbook is not None:
                    frame_configuration = spellbook._aetheric_frame_configuration
                    if frame_configuration is not None:
                        spell_is_dynamic = (
                            frame_configuration.system_state is SystemState.dynamic
                        )

            for socket in topology.iter_sockets():
                if not socket.is_collection:
                    continue
                if socket.is_optional:
                    continue
                if socket.target_spell_ids:
                    continue

                if spell_is_dynamic:
                    severity = SystemDiagnosticSeverity.WARNING
                    remediation = (
                        "An empty list will be injected at construction; bind "
                        "implementations under its frame or add them via a "
                        "post-conjure contract to populate it."
                    )
                else:
                    severity = SystemDiagnosticSeverity.ERROR
                    remediation = (
                        "Bind at least one implementation under its frame, "
                        "make the parameter optional, or run the book in "
                        "dynamic mode if members arrive via contracts."
                    )
                diagnostics.append(
                    SystemDiagnostic(
                        code="collection_socket_no_providers",
                        message=(
                            f"Spell '{spell_id}' parameter '{socket.param_name}' "
                            "declares a required collection dependency (list[...]) "
                            "but no providers wired into it in the resolved graph. "
                            f"{remediation}"
                        ),
                        severity=severity,
                        spell_id=spell_id,
                        root_id=spell_id,
                        details={
                            "spell_id": spell_id,
                            "param_name": socket.param_name,
                        },
                    )
                )
