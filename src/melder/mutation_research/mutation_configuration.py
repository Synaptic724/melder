import threading
from typing import Any, Dict, List, Tuple, Type, Union

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.crystals.mutation_research_crystal import MutationResearchCrystal
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

    Registration:
        MELDER KERNEL - guarded. Obtained through
        `MutationResearch.create_configuration()`, not registered.

    Subsystem Context:
        The policy surface of the mutation-research root, paired with
        `MutationResearchConfigurationBuilder` for fluent assembly. It follows
        the same mutable-then-frozen shape as the Aether, Spellbook, and
        crystallizer configurations, so all four read alike.

    System Context:
        Activation is this object's EMISSION MOMENT, which makes ordering
        load-bearing: config activation necessarily precedes root activation, so
        it must carry the recorded composition forward into its twin. Without
        that, replace-on-emit would wipe the record moments before hydration
        reads it. `lane_type_enforcement` also lives here, propagating to every
        research set at activation, hydration, and set creation.
    """
    _ast_helper_access: str = "public"
    __agent_purpose__: str = (
        "access: public. Research-root policy. with_defaults() covers it; set lane_type_enforcement "
        "to gate cross-type lane joins. activate() is its emission moment."
    )

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
            "lane_type_enforcement": bool,
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

    def finalize(self) -> "MutationResearchConfiguration":
        """
        Validate and freeze the configuration, then return it.

        Returns:
            MutationResearchConfiguration: This configuration instance.
        """
        self.freeze()
        return self

    def activate(self) -> "MutationResearchConfiguration":
        """
        Validate, freeze, and mark the configuration as activated.

        Returns:
            MutationResearchConfiguration: This configuration instance.
        """
        self.freeze()
        with self._lock:
            self._activated = True
        # Configuration activation is the emission factor: pull the
        # crystallizer singleton directly (guarding the pre-boot case,
        # where the singleton is not yet initialized and construction
        # requires the hosting Aether), emit when recording, then drop
        # the local handle.
        if Crystallizer._initialized:
            crystallizer = Crystallizer()
            if crystallizer.activated:
                # DOCKING-LOOP LAW (bug caught by the zero-mock rebirth
                # test 2026-07-12): the profile is REPLACE-ON-EMIT, so a
                # config twin emitted WITHOUT the recorded composition
                # would WIPE it moments before the root's
                # untouched-registry hydration reads it (config
                # activation necessarily
                # precedes root activation). The configuration owns ONLY
                # its property payload - the recorded composition is
                # CARRIED FORWARD, never authored and never destroyed
                # here; the root's next composition re-emission
                # supersedes it as ever.
                prior = crystallizer.describe_mutation_research_record()
                prior_composition = (
                    dict(prior.get("composition_payload", {}))
                    if isinstance(prior, dict)
                    else {}
                )
                crystallizer.emit(
                    MutationResearchCrystal(
                        activated=True,
                        configuration_payload=(
                            self.describe_configuration_payload()
                        ),
                        composition_payload=prior_composition,
                    )
                )
            del crystallizer
        return self

    def describe_configuration_payload(self) -> Dict[str, object]:
        """
        Return the value-coerced configuration surface for recording.

        Purpose:
            The shared twin-payload builder: configuration activation and the
            root's composition re-emissions both record the SAME value-typed
            property mapping, so the persisted configuration surface can
            never drift between emission seams.

        Contract:
            - Plain values (str/int/float/bool/None) pass through; anything
              else records as its string form (records carry values only).

        Returns:
            Dict[str, object]:
                Detached property name -> recorded value mapping.
        """
        self.check_cleaned()
        configuration_payload: Dict[str, object] = {}
        with self._lock:
            for property_name, property_value in self._properties.items():
                if (
                        isinstance(property_value, (str, int, float, bool))
                        or property_value is None
                ):
                    configuration_payload[property_name] = property_value
                else:
                    configuration_payload[property_name] = str(property_value)
        return configuration_payload

    def load_recorded_dictionary(
            self,
            recorded_properties: Dict[str, Any],
    ) -> Dict[str, List[str]]:
        """
        Reload lane: apply one RECORDED property payload as configuration
        truth and seal.

        Purpose:
            The restore counterpart to `with_defaults` (owner reload-lane
            law; MR's original exclusion from the directive is obsolete
            now that the skeleton is a real subsystem). A sealed world's
            research posture rebuilds from its recorded values - never
            from present-day defaults - and the lane loads and seals in
            one motion.

        Contract:
            - Defaults land first as the backfill floor (`with_defaults`),
              then every recorded key OVERWRITES its default (recorded
              truth wins); registry keys the record did not carry are
              returned under "backfilled" so nothing defaults silently.
            - A recorded value the property system refuses is skipped and
              returned under "rejected" as "key: reason" (documented
              best-effort collection for the caller's shortfall
              reporting). The registry's single bool key needs no
              type coercion (JSON round-trips bools natively).
            - SEALS VIA `activate()` on return (freeze + activated): the
              config's activation is its emission factor, so the reload
              re-records into the fresh active profile mid-replay - the
              Nexus-precedent re-recording covenant; replace-on-emit
              means the root's later composition re-emission supersedes
              this twin in the same profile.

        Args:
            recorded_properties:
                Property name -> recorded value mapping (one sealed
                MutationResearchCrystal configuration_payload, as built
                by `describe_configuration_payload`).

        Returns:
            Dict[str, List[str]]:
                {"rejected": ["key: reason", ...],
                 "backfilled": [key, ...]}.

        Raises:
            RuntimeError: If the configuration is cleaned or already
                frozen.
            ValueError: If the reloaded property set fails validation at
                the internal freeze.
        """
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError(
                "MutationResearchConfiguration is already frozen; the "
                "reload lane requires a fresh configuration object."
            )
        self.with_defaults()
        rejected: List[str] = []
        applied: List[str] = []
        for key, value in dict(recorded_properties).items():
            try:
                self.set_property(key, value)
                applied.append(key)
            except Exception as error:
                # Best-effort collection by contract: the refusal reason
                # rides back to the caller for shortfall reporting.
                rejected.append("{0}: {1}".format(key, error))
        backfilled = sorted(
            key for key in self.available_properties.keys()
            if key not in applied
        )
        self.activate()
        return {"rejected": rejected, "backfilled": backfilled}

    def with_defaults(self) -> "MutationResearchConfiguration":
        """
        Apply the default mutation-research posture.

        Contract:
            - Unrestricted module mutation is disabled by default.
            - Lane-type enforcement is disabled by default (the vocabulary
              is always available; the join policy gate is opt-in).

        Returns:
            MutationResearchConfiguration: This configuration instance.
        """
        self.check_cleaned()
        defaults = {
            "unrestricted_module_mutations": False,
            "lane_type_enforcement": False,
        }
        for key, value in defaults.items():
            self.set_property(key, value)
        return self

    def with_unrestricted_module_mutations(
            self,
            enabled: bool,
    ) -> "MutationResearchConfiguration":
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

    def with_lane_type_enforcement(
            self,
            enabled: bool,
    ) -> "MutationResearchConfiguration":
        """
        Set the lane-type-enforcement posture.

        Purpose:
            When enabled, joining two lanes of DIFFERENT types (e.g.
            experiment -> production) requires the explicit force=True
            supersede; the lane-type vocabulary itself is always available.

        Args:
            enabled:
                Whether type-mixing joins require force.

        Returns:
            MutationResearchConfiguration: This configuration instance.
        """
        self.check_cleaned()
        self.set_property("lane_type_enforcement", enabled)
        return self
