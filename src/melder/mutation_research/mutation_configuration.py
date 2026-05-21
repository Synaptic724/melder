import threading
from typing import Dict, Tuple, Type, Union

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class MutationResearchConfiguration(Cleanable):
    """
    Mutable-to-frozen configuration surface for the mutation-research root.

    Purpose:
        Hold mutation-research-wide policy inputs before the Aether-owned
        mutation-research root is activated.

    Contract:
        - mutable until frozen
        - validates required properties before freeze/activation
        - activation is explicit and implies successful validation/freeze
        - thread-safe mutations are serialized with the instance lock
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frozen",
        "_activated",
        "_properties",
        "available_properties",
    ]

    def __init__(self) -> None:
        """
        Initialize one empty mutation-research configuration.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frozen: bool = False
        self._activated: bool = False
        self._properties: Dict[str, object] = {}
        self.available_properties: Dict[str, Union[Type, Tuple[Type, ...]]] = {
            "unrestricted_module_mutations": bool,
        }

    def cleanup(self) -> None:
        """
        Idempotently clear configuration state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frozen = True
            self._activated = False
            self._properties.clear()
            self.available_properties.clear()

            del self._properties
            del self.available_properties
            del self._id
        del self._lock

    @property
    def id(self) -> str:
        """
        Return the stable configuration id.

        Returns:
            str: Stable configuration id.
        """
        self.check_cleaned()
        return self._id

    @property
    def frozen(self) -> bool:
        """
        Return whether the configuration is frozen.

        Returns:
            bool: True when property mutation is closed.
        """
        self.check_cleaned()
        return self._frozen

    @property
    def activated(self) -> bool:
        """
        Return whether the configuration has been activated.

        Returns:
            bool: True when the config is validated, frozen, and marked ready.
        """
        self.check_cleaned()
        return self._activated

    def set_property(self, key: str, value: object) -> None:
        """
        Set one configuration property before freeze/activation.

        Args:
            key:
                Property name.
            value:
                Candidate property value.

        Returns:
            None.
        """
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError(
                "Cannot modify MutationResearchConfiguration after freeze()."
            )
        if key not in self.available_properties:
            raise ValueError(
                "Unknown MutationResearchConfiguration property: '{0}'.".format(key)
            )
        expected_type = self.available_properties[key]
        if not isinstance(expected_type, tuple):
            expected_type = (expected_type,)
        if not isinstance(value, expected_type):
            expected_names = ", ".join(t.__name__ for t in expected_type)
            raise TypeError(
                "MutationResearchConfiguration property '{0}' must be a {1}.".format(
                    key,
                    expected_names,
                )
            )

        with self._lock:
            if self._frozen:
                raise RuntimeError(
                    "Cannot modify MutationResearchConfiguration after freeze()."
                )
            self._properties[key] = value

    def get_property(self, key: str) -> object:
        """
        Return one stored configuration property.

        Args:
            key:
                Property name.

        Returns:
            object: Stored property value.
        """
        self.check_cleaned()
        return self._properties[key]

    def has_property(self, key: str) -> bool:
        """
        Return whether one property is currently defined.

        Args:
            key:
                Property name.

        Returns:
            bool: True when the property has been set.
        """
        self.check_cleaned()
        return key in self._properties

    def validate(self) -> bool:
        """
        Validate that the mutation-research policy bag is complete and coherent.

        Returns:
            bool: True when the configuration is valid.
        """
        self.check_cleaned()
        for key in self.available_properties.keys():
            if key not in self._properties:
                raise ValueError(
                    "Missing required mutation research configuration property: '{0}'.".format(
                        key
                    )
                )
        return True

    def freeze(self) -> None:
        """
        Validate and freeze the configuration.

        Returns:
            None.
        """
        self.check_cleaned()
        if self._frozen:
            return
        if not self.validate():
            raise ValueError("MutationResearchConfiguration validation failed.")
        with self._lock:
            self._frozen = True

    def finalize(self) -> MutationResearchConfiguration:
        """
        Validate and freeze the configuration, then return it.

        Returns:
            MutationResearchConfiguration: This configuration instance.
        """
        self.freeze()
        return self

    def activate(self) -> MutationResearchConfiguration:
        """
        Validate, freeze, and mark the configuration as activated.

        Returns:
            MutationResearchConfiguration: This configuration instance.
        """
        self.freeze()
        with self._lock:
            self._activated = True
        return self

    def with_defaults(self) -> MutationResearchConfiguration:
        """
        Apply the default mutation-research posture.

        Contract:
            - Unrestricted module mutation is disabled by default.

        Returns:
            MutationResearchConfiguration: This configuration instance.
        """
        self.check_cleaned()
        defaults = {
            "unrestricted_module_mutations": False,
        }
        for key, value in defaults.items():
            self.set_property(key, value)
        return self

    def with_unrestricted_module_mutations(
            self,
            enabled: bool,
    ) -> MutationResearchConfiguration:
        """
        Set the unrestricted-module-mutations posture.

        Args:
            enabled:
                Whether unrestricted module mutation mode is enabled.

        Returns:
            MutationResearchConfiguration: This configuration instance.
        """
        self.check_cleaned()
        self.set_property("unrestricted_module_mutations", enabled)
        return self
