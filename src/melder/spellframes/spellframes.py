import threading
from typing import Optional, Type, Dict, Any

import ulid

from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.general_base.cleanable import Cleanable

# ─────────────────────────────────────────────────────────────────────────────
# TODO: Implement SpellFrame-based SpellMaps
#
# 📌 Objective:
#   Each spellframe (interface or grouping class) should manage its own map
#   of spells and methods bound to it, enabling localized resolution, inspection,
#   and version control.
#
# 🧩 Core Tasks:
#   - [ ] Create a `SpellFrame` object or class to encapsulate:
#         - spell_map: Dict[str, Spell]
#         - method_map: Dict[str, Spell]
#   - [ ] On each `bind(...)`, if a `spellframe` is provided:
#         - Retrieve or create the corresponding `SpellFrame`
#         - Register the spell into the appropriate map
#   - [ ] Add resolution helpers:
#         - frame.resolve(name=None, method=False) → Spell
#         - frame.all_spells() → List[Spell]
#   - [ ] Store these `SpellFrame` containers in a global SpellFrameRegistry
#         for quick access by frame class/type
#
# ✅ Benefits:
#   - Isolated resolution per frame
#   - Support for multiple named spells
#   - Clean introspection of spellframe capabilities
# ─────────────────────────────────────────────────────────────────────────────

class SpellFrame(Cleanable):
    """
    SpellFrame is a runtime-only registry used to bind, track, and validate AI-generated or
    dynamically resolved interface classes. It supports storing metadata like UUIDs, method/property maps,
    and module information, enabling runtime introspection, dependency injection, or agentic behavior modeling.

    Common use cases:
        - AI-generated service contracts
        - Runtime-defined plugin schemas
        - Dynamic behavior trees or agent frameworks
        - Code synthesis systems that evolve structure during runtime

    Design Rationale:
        - Not compatible with static typing tools or linters (e.g., Pyright, MyPy)
        - Designed for frameworks where class structures are generated or mutated at runtime
        - Enables systems to reason about available capabilities, even if the code is fluid
        - Avoids traditional interface inheritance patterns, and instead tracks class structure reflectively

    Features:
        - Uses the class `__name__` as a unique key
        - Prevents duplicate bindings
        - Generates and stores UUIDs for each frame
        - Inspects and tracks public methods and properties
        - Supports metadata injection for downstream introspection or serialization
        - Can be cleaned up to disable further registrations (for safety or immutability)

    ⚠️ Developers working on typical business applications, libraries, or team-based codebases should NOT
       rely on SpellFrame for interface management. Prefer static interfaces, `abc.ABC`, or formal DI frameworks instead.

    SpellFrame is built for the future — for AI-native runtimes that change and grow.
    """
    def __init__(self):
        super().__init__()
        self._frame_map: ConcurrentDict[str, Dict[str, Any]] = ConcurrentDict()
        self._lock = threading.RLock()

    def cleanup(self):
        """
        Cleans the registry and clears all entries.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frame_map.cleanup()


    def bind(self, frame_type: Type, extra_metadata: Optional[Dict[str, Any]] = None):
        """
        Registers a SpellFrame class.

        Args:
            frame_type (Type): Class to register.
            extra_metadata (dict, optional): Additional metadata to attach.

        Raises:
            TypeError: If frame_type is not a class.
            ValueError: If already registered or disabled.
        """
        self.check_cleaned()

        if not isinstance(frame_type, type):
            raise TypeError("Only class types can be registered as SpellFrames.")

        if getattr(frame_type, "__spell_disabled__", False):
            raise ValueError(f"SpellFrame '{frame_type.__name__}' is disabled.")

        name = frame_type.__name__
        if name in self._frame_map:
            raise ValueError(f"SpellFrame '{name}' is already registered.")

        metadata = {
            "uuid": str(ulid.ULID()),
            "name": name,
            "module": frame_type.__module__,
            "qualname": frame_type.__qualname__,
            "methods": [m for m in dir(frame_type) if callable(getattr(frame_type, m)) and not m.startswith("__")],
            "properties": [a for a in dir(frame_type) if not callable(getattr(frame_type, a)) and not a.startswith("__")],
            "type": frame_type,
        }

        if extra_metadata:
            metadata.update(extra_metadata)

        self._frame_map[name] = metadata

    def validate(self, obj: Any, frame_type: Type) -> bool:
        """
        Validates that `obj` is an instance of a registered frame_type.

        Raises:
            ValueError: If the frame_type is not registered.
            TypeError: If the object is not a valid instance.
        """
        name = frame_type.__name__

        if name not in self._frame_map:
            raise ValueError(f"SpellFrame '{name}' is not registered.")

        if not isinstance(obj, frame_type):
            raise TypeError(f"Object does not conform to SpellFrame '{name}'.")

        return True

    def meld(self, frame_type: Type) -> Optional[Dict[str, Any]]:
        """
        Retrieves metadata for a registered SpellFrame.

        Returns:
            Metadata dict or None if not found.
        """
        return self._frame_map.get(frame_type.__name__)