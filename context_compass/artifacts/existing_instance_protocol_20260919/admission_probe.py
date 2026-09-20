"""Pytest-only admission simulation; never imported by Melder production code.

Run explicitly with pytest -p and keep its results separate from stock tests.
The wrapper adds the current helper's direct-public-member rules for ordinary
supplied instances, then calls the unchanged Bind implementation. Its early
position differs from the proposed production placement and does not qualify
guard ordering or custom examiner profiles.
"""

import inspect
from collections.abc import Sequence
from typing import TYPE_CHECKING, Optional

import pytest

from melder.aether.spellbook.bind.bind import Bind

if TYPE_CHECKING:
    from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
    from melder.aether.spellbook.existence.existence import Existence
    from melder.aether.spellbook.spell import Spell


class InstanceAdmissionProbe:
    """Apply only the existing direct-member contract to an actual supplied value.

    This adapter avoids claiming that an instance is a class merely to call the
    production helper whose current annotation is cls: type. The member rules
    intentionally match that helper; broader Protocol typing is not simulated.
    """

    __slots__ = ()

    @staticmethod
    def validate(candidate: object, protocol: type) -> None:
        """Refuse missing/non-callable declared members without constructing the candidate."""
        missing = []
        for name, member in protocol.__dict__.items():
            if name.startswith("_"):
                continue
            if not hasattr(candidate, name):
                missing.append(name)
                continue
            actual = getattr(candidate, name, None)
            if callable(member) and not callable(actual):
                missing.append(name)
        if missing:
            raise TypeError(
                f"Existing object '{type(candidate).__name__}' does not structurally implement "
                f"Protocol '{protocol.__name__}'. Missing members: {', '.join(sorted(missing))}"
            )


@pytest.fixture(autouse=True)
def simulated_instance_protocol_admission(monkeypatch: pytest.MonkeyPatch) -> None:
    """Install the test-process-only wrapper and restore it automatically after each case."""
    original = Bind._bind_logic

    def guarded_bind(
            binder: Bind,
            spell: object,
            spellframe: Optional[object],
            binding_name: Optional[str],
            existence: Existence,
            permissions: Permissions,
            aetheric_frame: str,
            configured_disposal_method_names: Optional[Sequence[str]] = None,
            profile: str = "general",
            disposal_method_names: Optional[Sequence[str]] = None,
            enforce_priority_disposal_methods: bool = False,
            **kwargs: object,
    ) -> Spell:
        """Add instance admission while preserving all original binding arguments and execution."""
        if (
                not inspect.isclass(spell)
                and not callable(spell)
                and isinstance(spellframe, type)
                and Bind._is_protocol_type(spellframe)
        ):
            InstanceAdmissionProbe.validate(spell, spellframe)
        return original(
            binder, spell, spellframe, binding_name, existence, permissions, aetheric_frame,
            configured_disposal_method_names, profile,
            disposal_method_names=disposal_method_names,
            enforce_priority_disposal_methods=enforce_priority_disposal_methods,
            **kwargs,
        )

    monkeypatch.setattr(Bind, "_bind_logic", guarded_bind)
