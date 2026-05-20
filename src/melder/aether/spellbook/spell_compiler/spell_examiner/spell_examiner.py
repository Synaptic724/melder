from typing import Any, Callable, Dict, List

from mypy_extensions import mypyc_attr

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.detailed_profile import (
    SpellDetailedProfile,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.general_profile import (
    SpellGeneralProfile,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder

@mypyc_attr(native_class=True)
class SpellExaminer(Cleanable):
    """
    Purpose:
        Act as the registry-backed front door for spell-examination profiles.

    Contract:
        - This class does not inspect raw candidates itself; it routes requests
          to named builder callables.
        - Callers can ask for a profile by stable name instead of depending on
          concrete profile classes directly.
        - The runtime seeds only the built-in `general` and `detailed`
          builders, but the registry remains open for explicit extension.
        - Builders receive the original target object unchanged plus the shared
          formatting knobs (`show_dunders`, `max_repr`).
        - The returned object is whatever the resolved builder produces. For a
          raw candidate that may be a partial examination view; for a bound
          `Spell` it may be a fuller runtime-aware profile.
        - Registry mutation is explicit through
          `register_profile_builder(...)` and uses plain dictionary semantics:
          later registrations replace earlier ones for the same name.

    Lifecycle:
        The examiner owns its builder registry and stable id only. Cleanup is
        idempotent, clears the registry, and leaves the object unusable.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_profile_builders_by_name",
    ]

    def __init__(self) -> None:
        """
        Initialize one registry-driven SpellExaminer instance.

        Contract:
            - Allocates a stable examiner id for tracing/introspection.
            - Creates an empty mutable builder registry.
            - Seeds the built-in runtime builders through
              `_register_default_profile_builders()`.

        Returns:
            None.
        """
        super().__init__()
        self._id = IDBuilder.create_id()
        self._profile_builders_by_name: Dict[str, Callable[[Any, bool, int], Any]] = {}
        self._register_default_profile_builders()

    def cleanup(self) -> None:
        """
        Idempotently release examiner-owned registry state.

        Contract:
            - Clears the examiner-owned builder registry.
            - Does not invoke or clean the registered builders; they are
              treated as external callables rather than owned child objects.
            - Leaves the examiner unusable after cleanup.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._profile_builders_by_name.clear()
        del self._profile_builders_by_name
        del self._id

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
        Register or replace one named examination-profile builder.

        Args:
            profile_name:
                Stable profile name exposed to `create_profile(...)`.
            builder:
                Callable accepting `(target, show_dunders, max_repr)` and
                returning the profile object for that target.

        Contract:
            - Replaces any existing builder registered under the same profile
              name.
            - Does not normalize or wrap the supplied callable.
            - Serves as the extension seam for new spell-examination views.

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

        Contract:
            Performs an existence check only; it does not validate builder
            behavior, call the builder, or imply that the builder will succeed
            for a specific target.

        Returns:
            bool: True when the builder is registered.
        """
        self.check_cleaned()
        return profile_name in self._profile_builders_by_name

    def list_profile_builder_names(self) -> List[str]:
        """
        Return the current registered profile-builder names in insertion order.

        Contract:
            Returns a snapshot list of the current builder-registry keys, so
            later registry mutation does not retroactively change the returned
            list object.

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
        Build one examination profile through the named registered builder.

        Args:
            target:
                Raw candidate object or fully formed `Spell` to examine.
            profile:
                Registered profile-builder name to resolve.
            show_dunders:
                Dunder-inspection preference for builders that honor it.
            max_repr:
                Maximum representation length for builders that honor it.

        Contract:
            - Resolves the requested builder from the current registry.
            - Delegates all examination work to that builder.
            - Does not reinterpret the target or verify the builder's return
              type.
            - Provides one stable front door for binding-time and post-binding
              profile creation so callers do not have to know which concrete
              profile class to instantiate themselves.

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
        Seed the built-in examination profiles used by the runtime.

        Contract:
            - Registers the built-in `general` and `detailed` builders into the
              mutable registry used by `create_profile()`.
            - Defines the default public profile surface for a fresh examiner.
            - Leaves room for callers to replace or extend that surface later
              through `register_profile_builder(...)`.

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
