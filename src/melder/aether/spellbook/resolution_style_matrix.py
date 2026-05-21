from typing import Dict, Mapping, Tuple
from mypy_extensions import mypyc_attr
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_types.spell_types import SpellType

def _expand_spell_type_matrix(
        spell_type_to_family: Mapping[str, str],
        family_policy: Mapping[str, Mapping[str, Tuple[str, ...]]],
) -> Dict[str, Dict[str, Tuple[str, ...]]]:
    """
    Expand binding-family policy into a SpellType-keyed projection.

    Contract:
    - Copies each spell-type row from the owning family policy rather than
      returning references to the source mappings.
    - Requires every spell type to reference a known family entry that exposes
      `supported` and `unsupported` tuples.

    Args:
        spell_type_to_family:
            Mapping from SpellType name to binding family name.
        family_policy:
            Family policy map with `supported` / `unsupported` existence sets.

    Returns:
        Dict[str, Dict[str, Tuple[str, ...]]]:
            SpellType-keyed matrix where each row is inherited from its family.

    Raises:
        KeyError:
            If a spell type points at an unknown family or a family policy row
            is missing required keys.
    """
    matrix: Dict[str, Dict[str, Tuple[str, ...]]] = {}
    for spell_type_name, family_name in spell_type_to_family.items():
        policy = family_policy[family_name]
        matrix[spell_type_name] = {
            "supported": tuple(policy["supported"]),
            "unsupported": tuple(policy["unsupported"]),
        }
    return matrix

@mypyc_attr(native_class=True)
class ResolutionStyleMatrix:
    """
    Canonical resolution-style support matrix for Melder.

    Purpose:
        Provide one owner-maintained artifact for resolution-style support, so
        architecture/docs/tests do not infer behaviour from scattered code paths.

    Ownership:
        Runtime maintainers for `spellbook/bind` and `spellbook/spell_types`.

    Update process:
        1) Update family policy entries in this class.
        2) Update expected enum counts when enum shapes change.
        3) Re-run matrix drift tests.
        4) Update architecture/components references if semantics changed.

    Canonical truth:
        `BINDING_FAMILY_POLICY` is the source of truth.

    Derived view:
        `MATRIX_BY_SPELL_TYPE` is an expanded projection for quick lookup only.

    Family-level interpretation:
        - Class spell families support all Existence modes.
        - Callable (method/lambda) families are unique-only.
        - Existing-object families are unique-only.
        - Enum row count does not imply "most binding kinds" are unique-only.
    """

    __melder_internal__ = _mrg.sentinel

    OWNER: str = "melder-runtime-maintainers"
    LAST_UPDATED_ISO: str = "2026-02-13"
    EXPECTED_SPELL_TYPE_COUNT: int = 14
    EXPECTED_EXISTENCE_COUNT: int = 6
    EXPECTED_CONTRACT_ITEM_COUNT: int = 21

    ALL_EXISTENCE_NAMES: Tuple[str, ...] = (
        "unique",
        "unique_per_conduit",
        "many",
        "unique_per_conduit_cluster",
        "unique_per_conduit_lineage",
        "unique_per_spell_space",
    )
    NON_UNIQUE_EXISTENCE_NAMES: Tuple[str, ...] = (
        "unique_per_conduit",
        "many",
        "unique_per_conduit_cluster",
        "unique_per_conduit_lineage",
        "unique_per_spell_space",
    )

    BINDING_FAMILY_POLICY: Dict[str, Dict[str, Tuple[str, ...]]] = {
        "class_based": {
            "spell_types": (
                "SPELL",
                "SPELL_WITH_SPELLFRAME",
                "SPELL_WITH_BINDING_NAME",
                "SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME",
            ),
            "supported": ALL_EXISTENCE_NAMES,
            "unsupported": (),
        },
        "callable_based": {
            "spell_types": (
                "METHOD",
                "METHOD_WITH_BINDING_NAME",
                "METHOD_WITH_SPELLFRAME",
                "METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME",
                "LAMBDA_METHOD_WITH_BINDING_NAME",
                "LAMBDA_METHOD_WITH_SPELLFRAME",
                "LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME",
            ),
            "supported": ("unique",),
            "unsupported": NON_UNIQUE_EXISTENCE_NAMES,
        },
        "existing_object_based": {
            "spell_types": (
                "EXISTING_CREATION",
                "EXISTING_CREATION_WITH_SPELLFRAME",
                "EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME",
            ),
            "supported": ("unique",),
            "unsupported": NON_UNIQUE_EXISTENCE_NAMES,
        },
    }

    SPELL_TYPE_TO_BINDING_FAMILY: Dict[str, str] = {
        "SPELL": "class_based",
        "SPELL_WITH_SPELLFRAME": "class_based",
        "SPELL_WITH_BINDING_NAME": "class_based",
        "SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME": "class_based",
        "METHOD": "callable_based",
        "METHOD_WITH_BINDING_NAME": "callable_based",
        "METHOD_WITH_SPELLFRAME": "callable_based",
        "METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME": "callable_based",
        "LAMBDA_METHOD_WITH_BINDING_NAME": "callable_based",
        "LAMBDA_METHOD_WITH_SPELLFRAME": "callable_based",
        "LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME": "callable_based",
        "EXISTING_CREATION": "existing_object_based",
        "EXISTING_CREATION_WITH_SPELLFRAME": "existing_object_based",
        "EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME": "existing_object_based",
    }

    # SpellType view is a derived projection from family policy.
    # It is not an independent policy table.
    MATRIX_BY_SPELL_TYPE: Dict[str, Dict[str, Tuple[str, ...]]] = (
        _expand_spell_type_matrix(
            SPELL_TYPE_TO_BINDING_FAMILY,
            BINDING_FAMILY_POLICY,
        )
    )

    # Resolution contract status map anchored to the ticket item IDs.
    # This intentionally captures supported runtime behavior and explicit
    # non-supported scope decisions in one source-of-truth artifact.
    CONTRACT_ITEM_STATUS: Dict[str, str] = {
        "A1": "supported",
        "A2": "supported",
        "A3": "supported",
        "A5": "supported",
        "A6": "supported",
        "B1": "supported",
        "B2": "supported",
        "B3": "supported",
        "B4": "out_of_scope",
        "B5": "supported",
        "B6": "supported",
        "C1": "supported",
        "C2": "out_of_scope",
        "D1": "supported",
        "D2": "supported",
        "D3": "supported",
        "E1": "supported",
        "E2": "supported",
        "F": "unsupported",
        "G": "supported",
        "H": "supported",
    }

    @classmethod
    def get_contract_item_status(cls, item_id: str) -> str:
        """
        Return tracked support status for a resolution contract item ID.

        Args:
            item_id:
                Ticket item identifier (for example: A1, B4, F).

        Returns:
            str:
                One of `supported`, `unsupported`, or `out_of_scope`.
        """
        return cls.CONTRACT_ITEM_STATUS[item_id]

    @classmethod
    def get_entry(cls, spell_type: SpellType) -> Mapping[str, Tuple[str, ...]]:
        """
        Return the support-matrix entry for a SpellType.

        Args:
            spell_type:
                SpellType enum value to query.

        Returns:
            Mapping[str, Tuple[str, ...]]:
                Entry containing `supported` and `unsupported` existence names.
        """
        return cls.get_matrix_by_spell_type()[spell_type.name]

    @classmethod
    def get_matrix_by_spell_type(cls) -> Dict[str, Dict[str, Tuple[str, ...]]]:
        """
        Return SpellType policy as a derived family-policy projection.

        Returns:
            Dict[str, Dict[str, Tuple[str, ...]]]:
                SpellType-keyed support matrix generated from family policy.
        """
        return _expand_spell_type_matrix(
            cls.SPELL_TYPE_TO_BINDING_FAMILY,
            cls.BINDING_FAMILY_POLICY,
        )

    @classmethod
    def get_family_policy(cls, family_name: str) -> Mapping[str, Tuple[str, ...]]:
        """
        Return expected existence support policy for a binding family.

        Args:
            family_name:
                One of `class_based`, `callable_based`, or `existing_object_based`.

        Returns:
            Mapping[str, Tuple[str, ...]]:
                Family policy including `spell_types`, `supported`, `unsupported`.
        """
        return cls.BINDING_FAMILY_POLICY[family_name]

    @classmethod
    def get_family_for_spell_type(cls, spell_type: SpellType | str) -> str:
        """
        Return the binding family name for a SpellType.

        Args:
            spell_type:
                SpellType enum value or SpellType name.

        Returns:
            str:
                Binding family identifier.
        """
        if isinstance(spell_type, SpellType):
            return cls.SPELL_TYPE_TO_BINDING_FAMILY[spell_type.name]
        return cls.SPELL_TYPE_TO_BINDING_FAMILY[spell_type]

    @classmethod
    def validate(cls) -> Tuple[str, ...]:
        """
        Validate matrix integrity against enum definitions and matrix contracts.

        Contract:
        - Checks enum count drift for `SpellType` and `Existence`.
        - Verifies family mappings, derived matrix rows, and contract-item ids.
        - Returns every validation problem found in one pass instead of failing
          fast on the first mismatch.

        Returns:
            Tuple[str, ...]:
                Validation errors. Empty tuple means the matrix is valid.
        """
        errors = []
        if len(SpellType) != cls.EXPECTED_SPELL_TYPE_COUNT:
            errors.append(
                "SpellType enum count drift: expected "
                + str(cls.EXPECTED_SPELL_TYPE_COUNT)
                + ", got "
                + str(len(SpellType))
                + "."
            )
        if len(Existence) != cls.EXPECTED_EXISTENCE_COUNT:
            errors.append(
                "Existence enum count drift: expected "
                + str(cls.EXPECTED_EXISTENCE_COUNT)
                + ", got "
                + str(len(Existence))
                + "."
            )
        if len(cls.CONTRACT_ITEM_STATUS) != cls.EXPECTED_CONTRACT_ITEM_COUNT:
            errors.append(
                "Resolution contract item count drift: expected "
                + str(cls.EXPECTED_CONTRACT_ITEM_COUNT)
                + ", got "
                + str(len(cls.CONTRACT_ITEM_STATUS))
                + "."
            )

        enum_spell_type_names = {spell_type.name for spell_type in SpellType}
        mapping_spell_type_names = set(cls.SPELL_TYPE_TO_BINDING_FAMILY.keys())
        matrix_by_spell_type = cls.get_matrix_by_spell_type()
        matrix_spell_type_names = set(matrix_by_spell_type.keys())

        missing_mappings = sorted(enum_spell_type_names - mapping_spell_type_names)
        extra_mappings = sorted(mapping_spell_type_names - enum_spell_type_names)
        if missing_mappings:
            errors.append(
                "SpellType->family map missing SpellType entries: "
                + ", ".join(missing_mappings)
                + "."
            )
        if extra_mappings:
            errors.append(
                "SpellType->family map has unknown SpellType entries: "
                + ", ".join(extra_mappings)
                + "."
            )

        family_names = set(cls.BINDING_FAMILY_POLICY.keys())
        unknown_families = sorted(
            family_name
            for family_name in cls.SPELL_TYPE_TO_BINDING_FAMILY.values()
            if family_name not in family_names
        )
        if unknown_families:
            errors.append(
                "SpellType->family map references unknown families: "
                + ", ".join(unknown_families)
                + "."
            )

        missing_spell_types = sorted(enum_spell_type_names - matrix_spell_type_names)
        extra_spell_types = sorted(matrix_spell_type_names - enum_spell_type_names)
        if missing_spell_types:
            errors.append(
                "Matrix missing SpellType entries: " + ", ".join(missing_spell_types) + "."
            )
        if extra_spell_types:
            errors.append(
                "Matrix has unknown SpellType entries: " + ", ".join(extra_spell_types) + "."
            )

        expected_existence_names = set(cls.ALL_EXISTENCE_NAMES)
        for spell_type_name, entry in matrix_by_spell_type.items():
            supported = set(entry.get("supported", ()))
            unsupported = set(entry.get("unsupported", ()))
            overlap = sorted(supported.intersection(unsupported))
            if overlap:
                errors.append(
                    "Matrix overlap for "
                    + spell_type_name
                    + ": "
                    + ", ".join(overlap)
                    + "."
                )

            unknown_names = sorted((supported.union(unsupported)) - expected_existence_names)
            if unknown_names:
                errors.append(
                    "Matrix contains unknown existence names for "
                    + spell_type_name
                    + ": "
                    + ", ".join(unknown_names)
                    + "."
                )

            uncovered_names = sorted(expected_existence_names - (supported.union(unsupported)))
            if uncovered_names:
                errors.append(
                    "Matrix does not fully classify existence names for "
                    + spell_type_name
                    + ": "
                    + ", ".join(uncovered_names)
                    + "."
                )

        for family_name, policy in cls.BINDING_FAMILY_POLICY.items():
            expected_supported = tuple(policy["supported"])
            expected_unsupported = tuple(policy["unsupported"])
            spell_types = policy["spell_types"]
            for spell_type_name in spell_types:
                policy_entry = matrix_by_spell_type.get(spell_type_name)
                if policy_entry is None:
                    errors.append(
                        "Family policy references unknown spell type in "
                        + family_name
                        + ": "
                        + spell_type_name
                        + "."
                    )
                    continue
                actual_supported = tuple(policy_entry.get("supported", ()))
                actual_unsupported = tuple(policy_entry.get("unsupported", ()))
                if actual_supported != expected_supported:
                    errors.append(
                        "Family policy mismatch for "
                        + spell_type_name
                        + " supported set."
                    )
                if actual_unsupported != expected_unsupported:
                    errors.append(
                        "Family policy mismatch for "
                        + spell_type_name
                        + " unsupported set."
                    )

        valid_statuses = {"supported", "unsupported", "out_of_scope"}
        contract_item_ids = set(cls.CONTRACT_ITEM_STATUS.keys())
        expected_contract_item_ids = {
            "A1",
            "A2",
            "A3",
            "A5",
            "A6",
            "B1",
            "B2",
            "B3",
            "B4",
            "B5",
            "B6",
            "C1",
            "C2",
            "D1",
            "D2",
            "D3",
            "E1",
            "E2",
            "F",
            "G",
            "H",
        }
        missing_contract_items = sorted(expected_contract_item_ids - contract_item_ids)
        extra_contract_items = sorted(contract_item_ids - expected_contract_item_ids)
        if missing_contract_items:
            errors.append(
                "Contract status map missing items: "
                + ", ".join(missing_contract_items)
                + "."
            )
        if extra_contract_items:
            errors.append(
                "Contract status map contains unknown items: "
                + ", ".join(extra_contract_items)
                + "."
            )
        for item_id, status in cls.CONTRACT_ITEM_STATUS.items():
            if status not in valid_statuses:
                errors.append(
                    "Contract status map has invalid status for "
                    + item_id
                    + ": "
                    + str(status)
                    + "."
                )

        return tuple(errors)
