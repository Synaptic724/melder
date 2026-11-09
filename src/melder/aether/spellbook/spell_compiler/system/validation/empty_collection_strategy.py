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
    from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
        SpellSocketDescriptor,
    )


# Melder imports
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.spell_compiler.validation.hidden_provider_report import (
    HiddenProviderReport,
)
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.utilities.helpers.general_helpers import SpellInputUtils
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
        - A `list[Class]` left empty because its class is bound only under a
          spellframe or a binding name carries Phase 3's hidden candidates
          (`SpellSocketDescriptor.hidden_spell_ids`, 2026-11-07); its message
          names where the class is bound and the list that gathers it
          (`_diagnostic_for`), at the same severity.
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
                Visible spell_ids to spell objects for this scope.
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

                diagnostics.append(
                    self._diagnostic_for(
                        spell_id=spell_id,
                        socket=socket,
                        spell_lookup=spell_lookup,
                        spell_is_dynamic=spell_is_dynamic,
                    )
                )

    @staticmethod
    def _diagnostic_for(
            *,
            spell_id: str,
            socket: SpellSocketDescriptor,
            spell_lookup: Mapping[str, Spell],
            spell_is_dynamic: bool,
    ) -> SystemDiagnostic:
        """
        Build the collection_socket_no_providers diagnostic for one empty required collection socket.

        Purpose:
            Keep the mode-scoped wording in one place and, since 2026-11-07
            (patch hidden_provider_2026_11_07), name where the class of a
            `list[Class]` is bound when Phase 3 recorded hidden candidates: the
            class IS registered, under a spellframe or a binding name, where a
            class lookup does not gather it, and "bind implementations under its
            frame" would send the user the wrong way.

        Contract:
            - Severity: WARNING in a dynamic Book (`[]` is injected), ERROR
              otherwise - unchanged by hidden candidates (the owner's D3).
            - Without hidden candidates (or none of them found in
              `spell_lookup`) the message is byte-identical to the text before
              2026-11-07.
            - With them: "... but no provider is wired into it: list[T] gathers
              T only where it is bound bare (no spellframe, the default
              binding), and T is bound only <where>: <entries>." followed by
              "Gather it where it is bound, as shown, bind T bare, or make the
              parameter optional." (ERROR) or "An empty list will be injected at
              construction; gather it where it is bound, as shown, or bind T
              bare to populate it." (WARNING); `details` gains
              "hidden_candidates" (the described candidates with their `use`).
            - Candidates are rendered from `spell_lookup`, the visible spells of
              this scope; an id it does not hold renders as `spell id <id>`.

        Args:
            spell_id: The consumer spell id.
            socket: Its empty required collection socket.
            spell_lookup: Visible spell_ids to spell objects for this scope.
            spell_is_dynamic: Whether the consumer's Book is dynamic.

        Returns:
            SystemDiagnostic: The diagnostic to append.
        """
        candidates = [
            HiddenProviderReport.describe(candidate_id, spell_lookup.get(candidate_id))
            for candidate_id in socket.hidden_spell_ids
        ]
        clause, type_name = HiddenProviderReport.collection_clause(candidates)
        details: Dict[str, object] = {
            "spell_id": spell_id,
            "param_name": socket.param_name,
        }
        if type_name is not None:
            details["hidden_candidates"] = HiddenProviderReport.with_uses(
                candidates, shape=HiddenProviderReport.SHAPE_LIST,
            )
        if spell_is_dynamic:
            severity = SystemDiagnosticSeverity.WARNING
            if type_name is None:
                remediation = (
                    " An empty list will be injected at construction; bind "
                    "implementations under its frame or add them via a "
                    "post-conjure contract to populate it."
                )
            else:
                remediation = (
                    " An empty list will be injected at construction; gather it where it is bound, as shown, "
                    f"or bind {type_name} bare to populate it."
                )
        else:
            severity = SystemDiagnosticSeverity.ERROR
            if type_name is None:
                remediation = (
                    " Bind at least one implementation under its frame, "
                    "make the parameter optional, or run the book in "
                    "dynamic mode if members arrive via contracts."
                )
            else:
                remediation = (
                    f" Gather it where it is bound, as shown, bind {type_name} bare, or make the parameter optional."
                )
        return SystemDiagnostic(
            code="collection_socket_no_providers",
            message=(
                f"Spell {SpellInputUtils.describe_spell_id(spell_id, spell_lookup)} "
                f"parameter '{socket.param_name}' is a required list[...] "
                f"dependency, but no provider is wired into it{clause or '.'}"
                f"{remediation}"
            ),
            severity=severity,
            spell_id=spell_id,
            root_id=spell_id,
            details=details,
        )
