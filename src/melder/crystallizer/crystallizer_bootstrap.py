
from typing import ClassVar, Dict, List, Optional

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.persistence.external_persistence_manager_configuration import (
    ExternalPersistenceManagerConfiguration,
)
from melder.utilities.general_base.cleanable import Cleanable


class CrystallizerBootstrap(Cleanable):
    """
    Fluent pod-boot lane: from a fresh process to a rebuilt world.

    Purpose:
        The restart story (owner charter, kube scenario): a rebuilt pod
        always needs to set up the crystallizer + persistence system,
        attach its external transport, pull its history (local cache
        first, then the user's DB), pick the MOST RECENT checkpoint, and
        load it - then the whole system bootstraps. This builder is that
        flow as one fluent chain:

            report = (CrystallizerBootstrap()
                      .with_external_persistence_manager(pm_configuration)
                      .with_profile("default")
                      .bootstrap())

    Contract:
        - Composes ONLY Crystallizer facades (the crystallizer owns its
          internals; the bootstrap owns the ORDER).
        - Single-use: bootstrap() consumes the builder.
        - A fresh-ever pod is LEGAL: no history anywhere boots an empty
          recording world (restored_checkpoint_id None, no error).
        - Remote-pulled checkpoints re-flush through the facade so the
          local cache holds them ("store it if it needs to be done");
          consequence: the flush upload hook re-upserts those ids, so
          user upload handlers must be upsert-safe (documented).
        - The chain verdict GATES the load: "broken" refuses loudly
          (bootstrapping a wrong world is worse than not booting);
          "truncated_prefix" boots and rides the report.

    Threading:
        Builder-thread confined; not shared.

    Lifecycle:
        cleanup() releases held configurations that bootstrap() did not
        consume; idempotent.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    __slots__ = Cleanable.__slots__ + [
        "_crystallizer_configuration",
        "_manager_configuration",
        "_profile_name",
        "_pull_remote",
        "_preflight_gate",
        "_consumed",
    ]

    def __init__(self) -> None:
        """
        Initialize an empty bootstrap chain (defaults everywhere).

        Returns:
            None.
        """
        super().__init__()
        # Optional inputs: None means "use the documented default" at
        # bootstrap() time (defaults-lane crystallizer configuration; no
        # external manager; the guaranteed default profile).
        self._crystallizer_configuration: Optional[
            CrystallizerConfiguration
        ] = None
        self._manager_configuration: Optional[
            ExternalPersistenceManagerConfiguration
        ] = None
        self._profile_name: str = "default"
        self._pull_remote: bool = True
        # Opt-in strictness: when True, a "blockers" verdict in the
        # restore report's load-time preflight refuses the boot AFTER
        # the all-or-nothing restore already protected the world (the
        # engine never gates; the boot lane may).
        self._preflight_gate: bool = False
        self._consumed: bool = False

    def cleanup(self) -> None:
        """
        Release unconsumed configurations and mark the builder cleaned.

        Contract:
            - Idempotent; children first, then del posture.
            - Configurations consumed by bootstrap() are owned downstream
              (crystallizer/manager) and are NOT cleaned here.
        """
        if self._cleaned:
            return
        self._cleaned = True
        if not self._consumed:
            if (
                    self._crystallizer_configuration is not None
                    and not self._crystallizer_configuration.cleaned
            ):
                self._crystallizer_configuration.cleanup()
            if (
                    self._manager_configuration is not None
                    and not self._manager_configuration.cleaned
            ):
                self._manager_configuration.cleanup()
        del self._crystallizer_configuration
        del self._manager_configuration
        del self._profile_name
        del self._pull_remote
        del self._preflight_gate
        del self._consumed

    def with_crystallizer_configuration(
            self,
            configuration: CrystallizerConfiguration,
    ) -> "CrystallizerBootstrap":
        """
        Supply the crystallizer configuration and return `self`.

        Contract:
            - Omitting this uses CrystallizerConfiguration().with_defaults()
              at bootstrap() time. To boot the RECORDED policy, reload it
              first (CrystallizerConfiguration().load_recorded_dictionary
              on the head checkpoint's crystallizer payload) and pass it
              here.

        Args:
            configuration:
                The (possibly reloaded) crystallizer configuration;
                ownership transfers to this builder until consumed.

        Returns:
            CrystallizerBootstrap: This builder (fluent).

        Raises:
            RuntimeError: If the builder has been cleaned or consumed.
        """
        self.check_cleaned()
        self._require_unconsumed()
        self._crystallizer_configuration = configuration
        return self

    def with_external_persistence_manager(
            self,
            manager_configuration: ExternalPersistenceManagerConfiguration,
    ) -> "CrystallizerBootstrap":
        """
        Supply the user's external transport configuration, return `self`.

        Args:
            manager_configuration:
                Handler-bearing configuration (the user's DB callables);
                ownership transfers to this builder until consumed.

        Returns:
            CrystallizerBootstrap: This builder (fluent).

        Raises:
            RuntimeError: If the builder has been cleaned or consumed.
        """
        self.check_cleaned()
        self._require_unconsumed()
        self._manager_configuration = manager_configuration
        return self

    def with_profile(self, profile_name: str) -> "CrystallizerBootstrap":
        """
        Pick the profile to rebuild and return `self`.

        Args:
            profile_name:
                Profile whose history boots (default "default").

        Returns:
            CrystallizerBootstrap: This builder (fluent).

        Raises:
            RuntimeError: If the builder has been cleaned or consumed.
            ValueError: If `profile_name` is empty.
        """
        self.check_cleaned()
        self._require_unconsumed()
        if not profile_name:
            raise ValueError("with_profile requires a non-empty name.")
        self._profile_name = profile_name
        return self

    def with_pull_remote(self, enabled: bool) -> "CrystallizerBootstrap":
        """
        Set whether bootstrap pulls remote history, and return `self`.

        Args:
            enabled:
                False skips the remote pull even when a manager is
                attached (local-cache-only boot).

        Returns:
            CrystallizerBootstrap: This builder (fluent).

        Raises:
            RuntimeError: If the builder has been cleaned or consumed.
            TypeError: If `enabled` is not a bool.
        """
        self.check_cleaned()
        self._require_unconsumed()
        if not isinstance(enabled, bool):
            raise TypeError("pull_remote must be a bool.")
        self._pull_remote = enabled
        return self

    def with_preflight_gate(self, enabled: bool) -> "CrystallizerBootstrap":
        """
        Set whether load-time preflight blockers refuse the boot.

        Purpose:
            The restore engine runs the analysis strategies AS it loads
            (owner ruling) and files them in the report; this knob makes
            a "blockers" verdict fatal to the boot instead of advisory.

        Args:
            enabled:
                True refuses the boot on preflight blockers (the restore
                itself completed or rolled back before the gate fires).

        Returns:
            CrystallizerBootstrap: This builder (fluent).

        Raises:
            RuntimeError: If the builder has been cleaned or consumed.
            TypeError: If `enabled` is not a bool.
        """
        self.check_cleaned()
        self._require_unconsumed()
        if not isinstance(enabled, bool):
            raise TypeError("preflight_gate must be a bool.")
        self._preflight_gate = enabled
        return self

    def bootstrap(self) -> Dict[str, object]:
        """
        Run the pod-boot flow and return the bootstrap report.

        Contract (the ORDER is the product):
            1. Activate the crystallizer (supplied or defaults-lane
               configuration; the persistence system comes up with it).
            2. Attach the external manager when configured.
            3. Reload the profile's LOCAL cache (empty tolerated).
            4. Pull the profile's REMOTE history when enabled and a
               manager is attached; re-flush pulled ids so the local
               cache holds them.
            5. Verify the chain: "broken" REFUSES loudly; anything else
               rides the report.
            6. Load the MOST RECENT checkpoint (last ULID in the
               profile's ledger); a history-less pod boots an empty
               world (restored_checkpoint_id None).

        Returns:
            Dict[str, object]:
                {"activated": True,
                 "profile_name": str,
                 "cache_reload": summary | None,
                 "remote_reload": summary | None,
                 "chain_report": report | None,
                 "restored_checkpoint_id": str | None,
                 "restore_report": report | None}.

        Raises:
            RuntimeError: If cleaned, already consumed, or the chain
                verdict is "broken".
        """
        self.check_cleaned()
        self._require_unconsumed()
        self._consumed = True
        configuration = self._crystallizer_configuration
        if configuration is None:
            configuration = CrystallizerConfiguration().with_defaults()
        configuration.activate()
        crystallizer = Crystallizer()
        crystallizer.activate(configuration)
        if self._manager_configuration is not None:
            crystallizer.configure_external_persistence_manager(
                self._manager_configuration
            )
        cache_reload: Optional[Dict[str, object]] = None
        try:
            cache_reload = crystallizer.reload_profile_from_cache(
                self._profile_name
            )
        except KeyError:
            # Fresh-ever pod: no local history is a legal boot state.
            cache_reload = None
        remote_reload: Optional[Dict[str, object]] = None
        if self._manager_configuration is not None and self._pull_remote:
            remote_reload = crystallizer.reload_profile_from_external(
                self._profile_name
            )
            # "Store it if it needs to be done": remote-pulled ids land
            # in the local cache too (the flush upload hook re-upserts
            # them remotely; user handlers must be upsert-safe).
            for checkpoint_id in list(remote_reload["inserted"]):
                crystallizer.flush_checkpoint(checkpoint_id)
        chain_report: Optional[Dict[str, object]] = None
        restored_checkpoint_id: Optional[str] = None
        restore_report: Optional[Dict[str, object]] = None
        newest = self._newest_profile_checkpoint(crystallizer)
        if newest is not None:
            chain_report = crystallizer.verify_checkpoint_chain(
                self._profile_name
            )
            if str(chain_report["verdict"]) == "broken":
                raise RuntimeError(
                    "Bootstrap refused: profile {0!r} has a BROKEN "
                    "checkpoint chain ({1} break(s)). Booting a wrong "
                    "world is worse than not booting - repair or purge "
                    "the damaged history first (see the chain report's "
                    "break entries).".format(
                        self._profile_name,
                        len(list(chain_report["breaks"])),
                    )
                )
            restore_report = crystallizer.load_checkpoint(newest)
            restored_checkpoint_id = newest
            if self._preflight_gate:
                preflight = dict(restore_report.get("preflight", {}))
                if str(preflight.get("verdict")) == "blockers":
                    raise RuntimeError(
                        "Bootstrap refused by the preflight gate: the "
                        "load-time analysis found {0} blocker(s) for "
                        "profile {1!r} (see the restore report's "
                        "preflight findings). The restore itself "
                        "honored all-or-nothing; the gate refuses to "
                        "hand over a world with known-unbuildable "
                        "elements.".format(
                            dict(preflight.get("counts", {})).get(
                                "blocker", 0
                            ),
                            self._profile_name,
                        )
                    )
        return {
            "activated": True,
            "profile_name": self._profile_name,
            "cache_reload": cache_reload,
            "remote_reload": remote_reload,
            "chain_report": chain_report,
            "restored_checkpoint_id": restored_checkpoint_id,
            "restore_report": restore_report,
        }

    def _newest_profile_checkpoint(
            self,
            crystallizer: Crystallizer,
    ) -> Optional[str]:
        """
        Return the profile's most recent ledger checkpoint id.

        Contract:
            - Checkpoint ids are ULIDs, so id order IS time order; the
              newest is the last profile-owned id.

        Args:
            crystallizer:
                The activated crystallizer (facade reads only).

        Returns:
            Optional[str]: Newest id, or None when the profile holds no
            checkpoints (fresh-ever boot).
        """
        newest: Optional[str] = None
        checkpoint_ids: List[str] = crystallizer.list_checkpoint_ids()
        for checkpoint_id in checkpoint_ids:
            described = crystallizer.describe_checkpoint(checkpoint_id)
            if str(described.get("profile_name")) == self._profile_name:
                newest = checkpoint_id
        return newest

    def _require_unconsumed(self) -> None:
        """
        Refuse fluent mutation or re-run after bootstrap() consumed this.

        Returns:
            None.

        Raises:
            RuntimeError: If bootstrap() already ran.
        """
        if self._consumed:
            raise RuntimeError(
                "CrystallizerBootstrap is single-use and was already "
                "consumed; build a fresh one for another boot."
            )
