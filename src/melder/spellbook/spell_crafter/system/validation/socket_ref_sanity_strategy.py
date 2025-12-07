from __future__ import annotations

from typing import Dict, List, Set, Optional

from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import SocketRef
from melder.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.spellbook.spell_crafter.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


class SocketRefSanityStrategy(SpellSystemValidationStrategy):
    """
    Ensures socket_refs and dag_index stay in sync for each root blueprint.

    Checks:
      * No duplicate SocketRef entries.
      * Every socket_ref is reachable via dag_index by path and by name.
      * Every dag_index entry corresponds to a socket_ref present on the blueprint.
    """

    def run(
            self,
            *,
            index,
            blueprints: Dict[str, RootResolutionBlueprint],
            phase4_results: Dict[str, object],
            broken_spell_ids: Set[str],
            diagnostics: List[SystemDiagnostic],
            cancel_event= Optional[CancellationEvent],
    ) -> None:
        for root_id, blueprint in blueprints.items():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            sockets = blueprint.socket_refs
            seen: Set[SocketRef] = set()
            duplicate_found = False

            for ref in sockets:
                if ref in seen:
                    duplicate_found = True
                    diagnostics.append(
                        SystemDiagnostic(
                            code="socket_ref_duplicate",
                            message=f"Duplicate SocketRef detected on root '{root_id}' for path '{'>'.join(ref.param_path)}'.",
                            severity=SystemDiagnosticSeverity.ERROR,
                            spell_id=ref.node_id,
                            root_id=root_id,
                            details={"param_path": ref.param_path, "param_name": ref.param_name},
                        )
                    )
                seen.add(ref)

                # Validate index contains this socket by path and name
                by_path = blueprint.dag_index.get_by_exact_path(ref.param_path)
                if ref not in by_path:
                    diagnostics.append(
                        SystemDiagnostic(
                            code="socket_ref_missing_in_index",
                            message=f"SocketRef '{'>'.join(ref.param_path)}' missing from DagIndex for root '{root_id}'.",
                            severity=SystemDiagnosticSeverity.ERROR,
                            spell_id=ref.node_id,
                            root_id=root_id,
                            details={"param_path": ref.param_path, "param_name": ref.param_name},
                        )
                    )
                by_name = blueprint.dag_index.get_by_name(ref.param_name)
                if ref not in by_name:
                    diagnostics.append(
                        SystemDiagnostic(
                            code="socket_ref_missing_in_index_name",
                            message=f"SocketRef for param '{ref.param_name}' missing in DagIndex name bucket on root '{root_id}'.",
                            severity=SystemDiagnosticSeverity.ERROR,
                            spell_id=ref.node_id,
                            root_id=root_id,
                            details={"param_path": ref.param_path, "param_name": ref.param_name},
                        )
                    )

            # Validate index entries correspond to socket_refs
            for indexed in blueprint.dag_index.iter_all_sockets():
                if indexed not in seen:
                    diagnostics.append(
                        SystemDiagnostic(
                            code="dag_index_orphan_socket",
                            message=f"DagIndex contains socket '{'>'.join(indexed.param_path)}' not present in socket_refs for root '{root_id}'.",
                            severity=SystemDiagnosticSeverity.ERROR,
                            spell_id=indexed.node_id,
                            root_id=root_id,
                            details={"param_path": indexed.param_path, "param_name": indexed.param_name},
                        )
                    )

