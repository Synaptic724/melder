from typing import Any, Callable, Dict, List

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.spell_crafter.spell_examiner.profiles.detailed_profile import (
    SpellDetailedProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.profiles.general_profile import (
    SpellGeneralProfile,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class SpellExaminer(Cleanable):
    """
    Purpose:
        Provide one registry-driven profile factory for spell examination.

    Contract:
        - `create_profile(...)` is the only public profile-creation entrypoint.
        - The default registry exposes only `general` and `detailed`.
        - Both profile kinds support a two-step lifecycle:
          phase 1 from a raw candidate, phase 2 completion after `Spell`
          exists.
        - `create_profile(...)` returns a partial or complete profile depending
          on whether the supplied target is a raw candidate or a fully formed
          `Spell`.
        - The registry is mutable through explicit `register_profile_builder(...)`
          calls without carrying an additional explicit mutex on the examiner.

    Lifecycle:
        Cleanup is idempotent and clears the registered builder registry.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_profile_builders_by_name",
    ]

    def __init__(self) -> None:
        """
        Initialize one registry-driven SpellExaminer.

        Returns:
            None.
        """
        super().__init__()
        self._id = IDBuilder.create_id()
        self._profile_builders_by_name: Dict[str, Callable[[Any, bool, int], Any]] = {}
        self._register_default_profile_builders()

    def cleanup(self) -> None:
        """
        Idempotently clear the profile-builder registry.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._profile_builders_by_name.clear()
        self._profile_builders_by_name = None
        self._id = None

    @property
    def id(self) -> str:
        """
        Return the stable spell examiner identifier.

        Returns:
            str: Stable spell examiner id.
        """
        self.check_cleaned()
        return self._id

    def register_profile_builder(
            self,
            profile_name: str,
            builder: Callable[[Any, bool, int], Any],
    ) -> None:
        """
        Register or replace one named profile builder.

        Args:
            profile_name:
                Stable profile-builder name.
            builder:
                Callable accepting `(target, show_dunders, max_repr)`.

        Returns:
            None.

        Raises:
            ValueError:
                If `profile_name` is empty.
            TypeError:
                If `builder` is not callable.
        """
        self.check_cleaned()
        if not profile_name:
            raise ValueError("profile_name cannot be empty.")
        if not callable(builder):
            raise TypeError("builder must be callable.")
        self._profile_builders_by_name[profile_name] = builder

    def has_profile_builder(self, profile_name: str) -> bool:
        """
        Return whether the named profile builder is registered.

        Args:
            profile_name:
                Profile-builder name to inspect.

        Returns:
            bool: True when the builder is registered.
        """
        self.check_cleaned()
        return profile_name in self._profile_builders_by_name

    def list_profile_builder_names(self) -> List[str]:
        """
        Return the current registered profile-builder names in insertion order.

        Returns:
            List[str]: Current builder names.
        """
        self.check_cleaned()
        return list(self._profile_builders_by_name.keys())

    def create_profile(
            self,
            target: Any,
            profile: str,
            show_dunders: bool = False,
            max_repr: int = 120,
    ) -> Any:
        """
        Create one profile using the named registered builder.

        Args:
            target:
                Raw candidate object or fully formed `Spell`.
            profile:
                Registered profile-builder name.
            show_dunders:
                Dunder-inspection preference for builders that honor it.
            max_repr:
                Maximum representation length for builders that honor it.

        Returns:
            Any: Profile object returned by the resolved builder.

        Raises:
            ValueError:
                If the requested profile name is not registered.
        """
        self.check_cleaned()
        builder = self._profile_builders_by_name.get(profile)
        if builder is None:
            raise ValueError(
                "Profile '{0}' is not registered on SpellExaminer.".format(
                    profile
                )
            )
        return builder(target, show_dunders, max_repr)

    def _register_default_profile_builders(self) -> None:
        """
        Register the default profile builders used by the runtime.

        Returns:
            None.
        """
        self.register_profile_builder(
            "general",
            lambda target, show_dunders, max_repr: SpellGeneralProfile.create_from_target(
                target,
                show_dunders=show_dunders,
                max_repr=max_repr,
            ),
        )
        self.register_profile_builder(
            "detailed",
            lambda target, show_dunders, max_repr: SpellDetailedProfile.create_from_target(
                target,
                show_dunders=show_dunders,
                max_repr=max_repr,
            ),
        )
