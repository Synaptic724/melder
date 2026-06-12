from typing import TYPE_CHECKING, Dict, List, Optional, Tuple



from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import (
    SpellValidationStrategy,
)
from melder.utilities.helpers.general_helpers import SpellInputUtils
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import (
        SpellValidationContext,
    )


class ContractProviderPresenceStrategy(SpellValidationStrategy):
    """
    Validate that contract sockets have a resolvable provider in the Spellbook.

    Purpose:
        Surface missing or ambiguous providers for SpellContract
        sockets at Phase 4 so users understand why a
        contracted spell cannot resolve.
    Contract:
        - Emits errors when contract descriptors are malformed.
        - Emits errors when more than one provider matches a contract key.
        - Emits warnings for missing SpellContract providers in dynamic mode.
        - Emits errors for contract sockets in automatic system state.
    """

    __slots__ = SpellValidationStrategy.__slots__

    def __init__(self) -> None:
        """
        Initialize the contract provider presence strategy.
        """
        super().__init__(
            name="contract_provider_presence",
            description="Validates SpellContract provider availability.",
        )

    def validate(self, context: SpellValidationContext) -> None:
        """
        Validate contract sockets against visible providers.

        Purpose:
            Detect contract sockets that cannot be resolved or are ambiguous.
        Contract:
            - Uses the Spellbook's contracted spell maps when available to enumerate providers.
            - Respects system_state to distinguish automatic vs dynamic behavior.
            - Appends one issue per contract socket mismatch.
        Args:
            context: SpellValidationContext for the spell under validation.
        Returns:
            None.
        Raises:
            OperationCancelledError:
                If ``cancel_event`` is set during provider scanning.
        """
        self.check_cleaned()

        cancel_event = context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        requirements = context.requirements
        if requirements is None:
            return

        spell = context.spell
        spellbook = context.spellbook

        system_state: Optional[SystemState] = None
        if spellbook is not None:
            frame_configuration = spellbook._aetheric_frame_configuration
            if frame_configuration is not None:
                try:
                    system_state = frame_configuration.system_state
                except Exception:
                    system_state = None

        # Pass-scoped memo: contracted-spell maps are bind-transactional, so
        # the provider enumeration is pass-invariant and one build serves
        # every spell in the validation pass. Without a pass cache (deferred
        # single-spell paths) the map is built fresh, identical to before.
        pass_cache = context.validation_pass_cache
        provider_map: Optional[Dict[Tuple[str, str], List[str]]] = None
        if pass_cache is not None:
            provider_map = pass_cache.get("contract_provider_map")
        if provider_map is None:
            provider_map = {}
            if spellbook is not None:
                for contracted in spellbook._contracted_spells.values():
                    for index, provider_spell in contracted.items():
                        if cancel_event is not None and cancel_event.is_set:
                            cancel_event.throw_if_set()
                        key = SpellInputUtils.make_spell_key_from_parts(
                            spellframe=provider_spell.spellframe,
                            spell_name=provider_spell.spell_name,
                            binding_name=provider_spell.binding_name,
                        )
                        provider_spell_id = index.current
                        if provider_spell_id is None:
                            provider_spell_id = provider_spell.spell_id
                        provider_map.setdefault(key, []).append(provider_spell_id)
            if pass_cache is not None and spellbook is not None:
                pass_cache["contract_provider_map"] = provider_map

        automatic_mode = system_state is SystemState.automatic
        current_spell_id = spell.spell_index.current
        if current_spell_id is None:
            current_spell_id = spell.spell_id

        for param in requirements.parameters:
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            if param.di_shape is not ParameterDIShape.SPELL_CONTRACT:
                continue

            if param.di_shape is ParameterDIShape.SPELL_CONTRACT and automatic_mode:
                context.issues.append(
                    SpellValidationIssue(
                        severity="error",
                        code="CONTRACT_IN_AUTOMATIC_MODE",
                        message=(
                            f"Spell {spell.spell_name!r} declares a contract socket for "
                            f"parameter {param.name!r} while system_state is automatic. "
                            "Contracts require dynamic mode to resolve."
                        ),
                        details={
                            "spell_id": current_spell_id,
                            "parameter_name": param.name,
                            "system_state": str(system_state),
                        },
                    )
                )
                continue

            if param.di_shape is ParameterDIShape.SPELL_CONTRACT:
                contract = param.default_value
                if not isinstance(contract, SpellContract):
                    context.issues.append(
                        SpellValidationIssue(
                            severity="error",
                            code="SPELL_CONTRACT_INVALID",
                            message=(
                                f"Spell {spell.spell_name!r} parameter {param.name!r} "
                                "is marked as SpellContract but the default is not a SpellContract."
                            ),
                            details={
                                "parameter_name": param.name,
                                "default_value_type": type(contract).__name__,
                            },
                        )
                    )
                    continue

                contract_key = contract.canonical_key
                providers = provider_map.get(contract_key, [])
                if len(providers) > 1:
                    context.issues.append(
                        SpellValidationIssue(
                            severity="error",
                            code="SPELL_CONTRACT_AMBIGUOUS",
                            message=(
                                f"Spell {spell.spell_name!r} parameter {param.name!r} "
                                f"matches multiple providers for contract key {contract_key}."
                            ),
                            details={
                                "parameter_name": param.name,
                                "contract_key": contract_key,
                                "provider_spell_ids": sorted(providers),
                            },
                        )
                    )
                    continue

                if not providers:
                    context.issues.append(
                        SpellValidationIssue(
                            severity="warning",
                            code="SPELL_CONTRACT_MISSING_PROVIDER",
                            message=(
                                f"Spell {spell.spell_name!r} parameter {param.name!r} "
                                f"has no provider for contract key {contract_key}."
                            ),
                            details={
                                "parameter_name": param.name,
                                "contract_key": contract_key,
                            },
                        )
                    )
                continue

