import threading
from typing import Any, Callable, Dict, List

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.spell import Spell
from melder.spellbook.spell_crafter.spell_examiner.profiles.ai_profile import (
    SpellAIProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import (
    SpellBindingProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.profiles.resolution_profile import (
    SpellResolutionProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.ai_profile_strategy import (
    AIProfileStrategy,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.binding_profile_strategy import (
    BindingProfileStrategy,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.resolution_profile_strategy import (
    ResolutionProfileStrategy,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class SpellExaminer(Cleanable):
    """
    Purpose:
        Provide one registry-driven profile factory for spell and object
        examination.

    Contract:
        - Default builders for `binding`, `resolution`, and `ai` are
          registered at construction time.
        - `create_profile(...)` is the primary entrypoint for producing
          examination output.
        - Binding creation accepts raw objects or `Spell` instances.
        - Resolution and AI creation require a `Spell` instance.
        - AI creation preserves the prior contract of always enabling dunder
          inspection inside the AI strategy.

    Threading:
        Uses one instance `threading.RLock` to serialize registry mutation and
        cleanup.

    Lifecycle:
        Cleanup is idempotent and clears the registered builder registry.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_profile_builders_by_name",
    ]

    def __init__(self) -> None:
        """
        Initialize one registry-driven SpellExaminer.

        Purpose:
            Construct the spell examiner and register the default profile
            builders used by the runtime.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
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
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._profile_builders_by_name.clear()
            self._profile_builders_by_name = None
            self._id = None
        self._lock = None

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
        with self._lock:
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
        with self._lock:
            return profile_name in self._profile_builders_by_name

    def list_profile_builder_names(self) -> List[str]:
        """
        Return the current registered profile-builder names in insertion order.

        Returns:
            List[str]: Current builder names.
        """
        self.check_cleaned()
        with self._lock:
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
                Raw object for binding profiles or `Spell` for resolution/AI
                profiles.
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
        with self._lock:
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
        self.register_profile_builder("binding", self._create_binding_profile)
        self.register_profile_builder("resolution", self._create_resolution_profile)
        self.register_profile_builder("ai", self._create_ai_profile)

    def _create_binding_profile(
            self,
            target: Any,
            show_dunders: bool,
            max_repr: int,
    ) -> SpellBindingProfile:
        """
        Build a binding profile for a raw object or `Spell`.

        Args:
            target:
                Raw candidate object or `Spell`.
            show_dunders:
                Whether dunder members should be included.
            max_repr:
                Maximum repr length.

        Returns:
            SpellBindingProfile: Built binding profile.
        """
        if isinstance(target, Spell):
            target = target.spell
        strategy = BindingProfileStrategy(
            show_dunders=show_dunders,
            max_repr=max_repr,
        )
        return strategy.build_profile(target)

    def _create_resolution_profile(
            self,
            target: Any,
            show_dunders: bool,
            max_repr: int,
    ) -> SpellResolutionProfile:
        """
        Build a resolution profile for a `Spell`.

        Args:
            target:
                Target `Spell`.
            show_dunders:
                Unused in this builder; accepted for uniform registry shape.
            max_repr:
                Unused in this builder; accepted for uniform registry shape.

        Returns:
            SpellResolutionProfile: Built resolution profile.

        Raises:
            TypeError:
                If `target` is not a `Spell`.
        """
        if not isinstance(target, Spell):
            raise TypeError(
                "Resolution profile creation requires a Spell instance."
            )
        _ = show_dunders
        _ = max_repr
        strategy = ResolutionProfileStrategy()
        return strategy.build_profile(target)

    def _create_ai_profile(
            self,
            target: Any,
            show_dunders: bool,
            max_repr: int,
    ) -> SpellAIProfile:
        """
        Build an AI profile for a `Spell`.

        Args:
            target:
                Target `Spell`.
            show_dunders:
                Dunder preference supplied by the caller. The current AI path
                intentionally forces dunders on to preserve the previous
                contract.
            max_repr:
                Maximum repr length for deep reflection.

        Returns:
            SpellAIProfile: Built AI profile.

        Raises:
            TypeError:
                If `target` is not a `Spell`.
        """
        if not isinstance(target, Spell):
            raise TypeError(
                "AI profile creation requires a Spell instance."
            )
        _ = show_dunders
        binding_profile = self._create_binding_profile(target, show_dunders, max_repr)
        resolution_profile = self._create_resolution_profile(target, show_dunders, max_repr)
        strategy = AIProfileStrategy(
            show_dunders=True,
            max_repr=max_repr,
        )
        return strategy.build_profile(
            spell=target,
            binding_profile=binding_profile,
            resolution_profile=resolution_profile,
        )
