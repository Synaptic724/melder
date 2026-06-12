"""
Slotted runtime step rows for the generalized family.

Replaces the per-load `SimpleNamespace` step adapters with one family-owned
`__slots__` class: faster attribute access on the hot construction path,
cheaper hydration, and an explicit attribute contract instead of an ad-hoc
namespace bag.

The attribute surface mirrors exactly what the emitted source and the family
runtime helpers (`construct_spell_instance`, `get_existing_creation`,
registration) read off a plan step.

Ownership:
    Runtime rows REFERENCE the live spell; they never own it. Rows are owned
    by the hydrated executor bindings that close over them and live for the
    executor's lifetime. `cleanup()` drops the row's reference surface for
    deterministic teardown by that owner.
"""

from typing import Any, Dict, Optional, Sequence, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable

_REQUIRED_ROW_FIELDS = (
    "instance_key",
    "spell_id",
    "existence",
    "creations_target_kind",
    "dependency_resolution_order",
    "uses_positional_override",
    "contract_positional_override",
    "has_contract_payload",
    "contract_payload_items",
    "use_spell_lock_hint",
    "must_register",
    "shared_instance",
    "override_match_prefix",
    "override_match_prefix_len",
)


class CodegenStepRuntimeRow(Cleanable):
    """
    One hydrated, slotted runtime step row.

    Contract:
        - Carries exactly the attributes emitted source and family runtime
          helpers consume from a plan step.
        - `spell` is a REFERENCE to the live spell, not an owned resource;
          every other field is manifest row data.

    Lifecycle / Cleanup:
        - Owned by the executor bindings that close over the row tuple.
        - `cleanup()` is idempotent and deletes every field so the row stops
          exposing stale state after teardown. No child object owns cleanup
          here because the spell is referenced, never owned.
    """

    __slots__ = Cleanable.__slots__ + [
        "instance_key",
        "spell",
        "existence",
        "creations_target_kind",
        "dependency_resolution_order",
        "uses_positional_override",
        "contract_positional_override",
        "has_contract_payload",
        "contract_payload",
        "use_spell_lock_hint",
        "must_register",
        "shared_instance",
        "override_match_prefix",
        "override_match_prefix_len",
    ]

    def __init__(
            self,
            *,
            instance_key: Tuple[str, Optional[int]],
            spell: Any,
            existence: Existence,
            creations_target_kind: int,
            dependency_resolution_order: Tuple[Tuple[str, Tuple[Any, ...]], ...],
            uses_positional_override: bool,
            contract_positional_override: Any,
            has_contract_payload: bool,
            contract_payload: Optional[Dict[str, Any]],
            use_spell_lock_hint: bool,
            must_register: bool,
            shared_instance: bool,
            override_match_prefix: Any,
            override_match_prefix_len: int,
    ) -> None:
        """
        Build one slotted runtime row.
        """
        super().__init__()
        self.instance_key = instance_key
        self.spell = spell
        self.existence = existence
        self.creations_target_kind = creations_target_kind
        self.dependency_resolution_order = dependency_resolution_order
        self.uses_positional_override = uses_positional_override
        self.contract_positional_override = contract_positional_override
        self.has_contract_payload = has_contract_payload
        self.contract_payload = contract_payload
        self.use_spell_lock_hint = use_spell_lock_hint
        self.must_register = must_register
        self.shared_instance = shared_instance
        self.override_match_prefix = override_match_prefix
        self.override_match_prefix_len = override_match_prefix_len

    def cleanup(self) -> None:
        """
        Deterministically release this row's reference surface.

        Contract:
            - Idempotent.
            - The spell is referenced, not owned, so no child cleanup runs;
              every field is deleted so post-cleanup access raises.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self.instance_key
        del self.spell
        del self.existence
        del self.creations_target_kind
        del self.dependency_resolution_order
        del self.uses_positional_override
        del self.contract_positional_override
        del self.has_contract_payload
        del self.contract_payload
        del self.use_spell_lock_hint
        del self.must_register
        del self.shared_instance
        del self.override_match_prefix
        del self.override_match_prefix_len


def build_runtime_rows(
        *,
        rows: Sequence[Dict[str, Any]],
        spell_lookup: Dict[str, Any],
) -> Tuple[CodegenStepRuntimeRow, ...]:
    """
    Hydrate slotted runtime rows from manifest rows plus resolved spells.

    Contract:
        - Validates required row fields and existence names with explicit
          error messages. Family manifest rows always carry the full field
          set (both lane variants of `build_phase11_step_ir_row` emit every
          field), so access below is direct, not defensive.
        - The only live resolution performed is the spell_id -> Spell mapping
          supplied by the caller; everything else is pure row data.

    Raises:
        RuntimeError:
            On missing fields, unknown existence names, or unknown spell ids.
    """
    runtime_rows = []
    for row_index, row in enumerate(rows):
        for field_name in _REQUIRED_ROW_FIELDS:
            if field_name not in row:
                raise RuntimeError(
                    "generalized runtime row is missing required field "
                    f"'{field_name}' at index {row_index}."
                )
        spell_id = row["spell_id"]
        spell = spell_lookup.get(spell_id)
        if spell is None:
            raise RuntimeError(
                "generalized runtime row references unknown spell_id "
                f"'{spell_id}'."
            )
        existence_name = row["existence"]
        try:
            existence = Existence[existence_name]
        except KeyError as exc:
            raise RuntimeError(
                "generalized runtime row contains unknown existence "
                f"'{existence_name}' at index {row_index}."
            ) from exc

        dependency_resolution_order = tuple(
            (
                param_name,
                tuple(dependency_keys),
            )
            for param_name, dependency_keys in row["dependency_resolution_order"]
        )
        contract_payload: Optional[Dict[str, Any]] = None
        if row["has_contract_payload"]:
            contract_payload = {
                param_name: value
                for param_name, value in row["contract_payload_items"]
            }

        runtime_rows.append(
            CodegenStepRuntimeRow(
                instance_key=(row["instance_key"][0], row["instance_key"][1]),
                spell=spell,
                existence=existence,
                creations_target_kind=row["creations_target_kind"],
                dependency_resolution_order=dependency_resolution_order,
                uses_positional_override=bool(row["uses_positional_override"]),
                contract_positional_override=row["contract_positional_override"],
                has_contract_payload=bool(row["has_contract_payload"]),
                contract_payload=contract_payload,
                use_spell_lock_hint=bool(row["use_spell_lock_hint"]),
                must_register=bool(row["must_register"]),
                shared_instance=bool(row["shared_instance"]),
                override_match_prefix=row["override_match_prefix"],
                override_match_prefix_len=int(row["override_match_prefix_len"]),
            )
        )
    return tuple(runtime_rows)
