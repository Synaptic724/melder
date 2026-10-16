"""S5 seams: per-path managed sites, solo decline, manifest route key, door rows, specializer decline."""
import pathlib
import sys

SC = "src/melder/aether/spellbook/spell_compiler"
CCS = f"{SC}/codegen_creation_system"

SHARED_DOC = '''        """
        Determine whether an existence policy yields a shared instance.

        Contract:
            - `many` and `managed_spell_quantity` are per path: each occurrence
              keeps its own instance key, so every injection of a managed spell
              is its own lease (managed_spell_quantity S5, 2026-10-15).
            - Every slotted existence shares one instance per spell.
        """
        return existence is not Existence.many and existence is not Existence.managed_spell_quantity
'''

EDITS = [
    (f"{SC}/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py", [(
        '''    def _is_shared_existence(
            existence: Existence,
    ) -> bool:
        """
        Determine whether an existence policy yields a shared instance.
        """
        return existence is not Existence.many
''',
        '''    def _is_shared_existence(
            existence: Existence,
    ) -> bool:
''' + SHARED_DOC,
    )]),
    (f"{SC}/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py", [(
        '''    def _is_shared_existence(existence: Existence) -> bool:
        """
        Determine whether an existence policy yields a shared instance.
        """
        return existence is not Existence.many
''',
        '''    def _is_shared_existence(existence: Existence) -> bool:
''' + SHARED_DOC,
    )]),
    (f"{SC}/codegen_planner/codegen_plan_discovery_system/strategies/solo_codegen_plan_discovery_strategy.py", [
        (
            '''from typing import Optional

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (''',
            '''from typing import Optional

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (''',
        ),
        (
            '''        Claim any model whose visible spell set contains exactly one spell,
        regardless of existence policy, so phase 10 can emit the dedicated
        solo planning family.''',
            '''        Claim any model whose visible spell set contains exactly one spell,
        of any existence policy but `managed_spell_quantity`, so phase 10 can
        emit the dedicated solo planning family.''',
        ),
        (
            '''              models route to the collection-aware families instead.
        """''',
            '''              models route to the collection-aware families instead.
            - Declines a model holding a `managed_spell_quantity` spell: its
              objects are leased through the generalized family's site plan
              (managed_spell_quantity S5, 2026-10-15), which the solo lowering
              does not dispense.
        """''',
        ),
        (
            '''        if existence_occurrence_shape.total_spell_count != 1:
            return None
        injection_shape = spell_codegen_model.injection_shape''',
            '''        if existence_occurrence_shape.total_spell_count != 1:
            return None
        for existence, _count in existence_occurrence_shape.existence_counts:
            if existence is Existence.managed_spell_quantity:
                return None
        injection_shape = spell_codegen_model.injection_shape''',
        ),
    ]),
    (f"{CCS}/strategies/generalized/manifest/generalized_manifest.py", [
        (
            '''    """
    Resolve the runtime route key from processor-owned model truth.
    """''',
            '''    """
    Resolve the runtime route key from processor-owned model truth.

    Contract:
        Route family "managed" (managed_spell_quantity S5, 2026-10-15) is a
        route key of its own; its doors are the `many` doors.
    """''',
        ),
        (
            '''            "lineage",
            "cluster",
    ):
        return route_family''',
            '''            "lineage",
            "cluster",
            "managed",
    ):
        return route_family''',
        ),
    ]),
    (f"{CCS}/shared_assets/creation_runtime_door_compiler.py", [
        (
            '''    "cluster": _TEMPLATE_CLUSTER_INSTANCE_OVERRIDES_ONLY,
}''',
            '''    "cluster": _TEMPLATE_CLUSTER_INSTANCE_OVERRIDES_ONLY,
    # A managed root's doors are the `many` doors (managed_spell_quantity S5):
    # the plan leases, and the hooks lane reports `created=True` on every lease.
    "managed": _TEMPLATE_MANY_INSTANCE_OVERRIDES_ONLY,
}''',
        ),
        (
            '''    "cluster": _TEMPLATE_CLUSTER_OVERRIDES_ONLY,
}''',
            '''    "cluster": _TEMPLATE_CLUSTER_OVERRIDES_ONLY,
    "managed": _TEMPLATE_MANY_OVERRIDES_ONLY,
}''',
        ),
        (
            '''    ("cluster", True): _TEMPLATE_CLUSTER_INSTANCE_NO_OVERRIDES_ONLY,
}''',
            '''    ("cluster", True): _TEMPLATE_CLUSTER_INSTANCE_NO_OVERRIDES_ONLY,
    # Managed roots never take the fast-transient door: both bits select the
    # plain `many` template (managed_spell_quantity S5).
    ("managed", False): _TEMPLATE_MANY_INSTANCE_NO_OVERRIDES_ONLY,
    ("managed", True): _TEMPLATE_MANY_INSTANCE_NO_OVERRIDES_ONLY,
}''',
        ),
        (
            '''    ("cluster", True): _TEMPLATE_CLUSTER_NO_OVERRIDES_ONLY,
}''',
            '''    ("cluster", True): _TEMPLATE_CLUSTER_NO_OVERRIDES_ONLY,
    ("managed", False): _TEMPLATE_MANY_NO_OVERRIDES_ONLY,
    ("managed", True): _TEMPLATE_MANY_NO_OVERRIDES_ONLY,
}''',
        ),
    ]),
    (f"{CCS}/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py", [(
        '''                if (dependency_key[0], dependency_key[1]) in many_keys:
                    return True
    return False
''',
        '''                if (dependency_key[0], dependency_key[1]) in many_keys:
                    return True
    return False


def rows_contain_managed_step(
        rows: Sequence[Dict[str, Any]],
) -> bool:
    """
    Return True when any manifest row is an `Existence.managed_spell_quantity` step.

    Purpose:
        Decide whether the singleton warm-tail specializer can express a graph.
        A managed step is leased from its pool through the site plan (an inline
        pop, a reserve-first miss, children recorded with the object, leases
        returned when their holder is never built); the straight-line body has
        no such lowering, so a graph with a managed row keeps the plain door
        (managed_spell_quantity S5, 2026-10-15).

    Contract:
        - Pure function of manifest row data; no live spells consulted.

    Args:
        rows:
            Manifest step rows for the no-overrides lane.

    Returns:
        bool: True when some row's `existence` is `managed_spell_quantity`.
    """
    managed_name = Existence.managed_spell_quantity.name
    return any(row["existence"] == managed_name for row in rows)
''',
    )]),
    (f"{CCS}/strategies/generalized/hydration/generalized_hydrator.py", [
        (
            '''    resolve_root_instance_key_from_rows,
    rows_feed_many_into_non_many_step,
    select_specializable_step_indexes,
)''',
            '''    resolve_root_instance_key_from_rows,
    rows_contain_managed_step,
    rows_feed_many_into_non_many_step,
    select_specializable_step_indexes,
)''',
        ),
        (
            '''        # cannot do that, so the plain door (site plan) keeps serving.
        return plain_instance_door
''',
            '''        # cannot do that, so the plain door (site plan) keeps serving.
        return plain_instance_door
    if rows_contain_managed_step(rows):
        # A managed step is leased through the site plan (pop, reserve-first
        # miss, returns); the straight-line body has no lease lowering.
        return plain_instance_door
''',
        ),
        (
            '''        only its root on a short-circuiting route, or feeds a `many` step into
        a non-`many` step.''',
            '''        only its root on a short-circuiting route, feeds a `many` step into
        a non-`many` step, or holds a `managed_spell_quantity` step.''',
        ),
    ]),
]


def main() -> int:
    for path, edits in EDITS:
        file = pathlib.Path(path)
        text = file.read_text(encoding="utf-8")
        for old, new in edits:
            if text.count(old) != 1:
                print("NOT UNIQUE", path, text.count(old), old[:80])
                return 1
            text = text.replace(old, new)
        file.write_text(text, encoding="utf-8", newline="")
        print("edited", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
