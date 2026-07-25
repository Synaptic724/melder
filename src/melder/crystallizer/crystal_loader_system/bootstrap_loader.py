
from typing import ClassVar, Dict, List, Optional

from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.asset_management.external_persistence_manager_configuration import (
    ExternalPersistenceManagerConfiguration,
)
from melder.utilities.general_base.cleanable import Cleanable


class CrystallizerBootstrap(Cleanable):
    """
    Fluent pod-boot lane: from a fresh process to a rebuilt world.

    Purpose:
        Compose the restart sequence for a fresh process: activate the
        crystallizer, attach optional external assets, recover local and remote
        history, verify the selected profile's chain, and load its newest
        checkpoint. A process with no history is valid and starts an empty
        recording world.

    Usage:
        Choose this object for process/pod restart orchestration. Use direct
        `Crystallizer` facade verbs when the process is already configured and
        only one checkpoint, formation, or graft operation is needed. The
        builder is single-use because it transfers configuration ownership and
        may create a live world.

        Remote history is written back through the normal flush lane so the
        local cache is repopulated. Consequently, attached write handlers must
        tolerate idempotent re-storage of an existing checkpoint id.

    Contract:
        - Composes ONLY Crystallizer facades (the crystallizer owns its
          internals; the bootstrap owns the ORDER).
        - Single-use: bootstrap() consumes the builder.
        - A fresh-ever pod is LEGAL: no history anywhere boots an empty
          recording world (restored_checkpoint_id None, no error).
        - Remote-pulled checkpoints re-flush through the facade so the
          local cache holds them; remote write handlers may therefore receive
          the same checkpoint id again and must be upsert-safe.
        - The chain verdict GATES the load: "broken" refuses loudly
          (bootstrapping a wrong world is worse than not booting);
          "truncated_prefix" boots and rides the report.

    Threading:
        Builder-thread confined; not shared.

    Lifecycle / Cleanup:
        Cleanup releases configurations that were never consumed. After
        `bootstrap()` begins, configuration ownership transfers downstream and
        cleanup never tears down the resulting crystallizer world.

    Registration:
        MELDER KERNEL - guarded (internal manifest). access=public: a deploy/pod
        constructs and drives it for restart orchestration; guarding only refuses it as a bind
        target (Melder never injects it) - it is still user-driven.

    Subsystem Context:
        The pod-restart lane of THE UNFOLD: a single-use fluent builder that composes ONLY
        `Crystallizer` facades in order - activate -> attach external assets -> reload local
        cache -> pull remote history + re-flush -> chain-verify gate -> load newest checkpoint
        -> report. The crystallizer owns its internals; the bootstrap owns the ORDER.

    System Context:
        Crystallizer layer (position 2), the entry point for bringing a fresh process back to a
        recorded world. A fresh-ever pod is LEGAL (no history boots an empty recording world, no
        error); the chain verdict GATES the load - "broken" refuses loudly because booting a
        wrong world is worse than not booting, while "truncated_prefix" boots and rides the
        report.
    """
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Fluent single-use pod-boot chain: activate, attach the external manager, "
        "reload cache, pull remote, verify the chain, restore the newest checkpoint. Use this to "
        "bring a fresh process back to a recorded world in one expression."
    )


    __slots__ = Cleanable.__slots__ + [
        "_crystallizer_configuration",
        "_manager_configuration",
        "_profile_name",
        "_pull_remote",
        "_reload_formations",
        "_preflight_gate",
        "_consumed",
    ]

    def __init__(self) -> None:
        """
        Initialize an empty bootstrap chain (defaults everywhere).

        Contract:
            Holds no crystallizer singleton or runtime object. Optional
            configurations remain owned by this builder until `bootstrap()`
            transfers them downstream; remote pulls and formation reloads
            default on, and the profile defaults to `default`.

        Returns:
            None.

        Threading:
            Builder-thread confined; fluent mutation is unsynchronized.
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
        # Mesh-aware boot (asset CRUD completion, 2026-07-11): formation
        # FILES pull back beside the checkpoint history; mirrors
        # _pull_remote's default-on-when-a-manager-is-attached posture.
        self._reload_formations: bool = True
        # Compatibility-only storage for with_preflight_gate(). The
        # value no longer changes behavior: mediated loads always refuse a
        # folded blocker verdict before replay inside standard admission.
        self._preflight_gate: bool = False
        self._consumed: bool = False

    def cleanup(self) -> None:
        """
        Release unconsumed configurations and mark the builder cleaned.

        Contract:
            - Idempotent and terminal; unconsumed configurations clean before
              builder fields are deleted.
            - Configurations consumed by `bootstrap()` transferred downstream
              and are not cleaned here.
            - Does not deactivate or clean the crystallizer world produced by
              a successful bootstrap.

        Threading:
            Must run on the builder thread after fluent/bootstrap activity has
            stopped.

        Lifecycle / Cleanup:
            Safe in `finally` on both successful and failed boot chains; the
            consumed flag determines whether configuration ownership moved.

        Returns:
            None.
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
        del self._reload_formations
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
        Supply an external transport configuration and return `self`.

        Guidance:
            Use the generic mesh handlers for complete checkpoint/formation/
            graft support. A checkpoint-only legacy handler trio is valid, but
            remote formation reload is then skipped because that capability is
            absent.

        Args:
            manager_configuration:
                Handler-bearing configuration; ownership transfers to this
                builder until bootstrap consumes it.

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

    def with_formation_reload(
            self,
            enabled: bool,
    ) -> "CrystallizerBootstrap":
        """
        Set whether bootstrap pulls remote FORMATIONS, and return `self`.

        Purpose:
            Mesh-aware boot (asset CRUD completion, 2026-07-11): a pod
            that rebuilds from the user's DB gets its named formation
            slices back beside the checkpoint history, so the
            restore-a-slice verbs work immediately after boot.

        Contract:
            - Runs only when a manager is attached AND its configuration
              carries the generic fetch + list-units lanes; legacy-only
              managers (upload/download/list trio) have no formation
              transport, so the step SKIPS silently (report key None)
              rather than tripping the generic lanes' loud-refusal.
            - Tolerates a mesh with no formations (empty summary).
            - Default is True, mirroring with_pull_remote's posture.

        Args:
            enabled:
                False skips the formation pull even when a manager is
                attached.

        Returns:
            CrystallizerBootstrap: This builder (fluent).

        Raises:
            RuntimeError: If the builder has been cleaned or consumed.
            TypeError: If `enabled` is not a bool.
        """
        self.check_cleaned()
        self._require_unconsumed()
        if not isinstance(enabled, bool):
            raise TypeError("formation_reload must be a bool.")
        self._reload_formations = enabled
        return self

    def with_preflight_gate(self, enabled: bool) -> "CrystallizerBootstrap":
        """
        Accepted no-op knob: blocker refusal is standard admission now.

        Purpose:
            Preserve compatibility with older fluent chains. Every mediated load
            now refuses folded blocker verdicts before replay regardless of this
            value.

        Guidance:
            Omit this method in new code. It communicates no current policy and
            exists only so previously authored bootstrap chains remain valid.

        Args:
            enabled:
                Accepted and recorded; admission refuses blockers
                regardless.

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
            5. Pull the profile's REMOTE formations (mesh-aware boot;
               default-on when the attached manager carries the generic
               fetch+list lanes - legacy-only managers skip silently;
               with_formation_reload(False) also skips) so slice
               restores work on the rebuilt pod.
            6. Verify the chain: "broken" REFUSES loudly; anything else
               rides the report.
            7. Load the profile's most recent checkpoint by exact ledger
               insertion order; a history-less process boots an empty world
               (`restored_checkpoint_id` is None).

        Returns:
            Dict[str, object]:
                {"activated": True,
                 "profile_name": str,
                 "cache_reload": summary | None,
                 "remote_reload": summary | None,
                 "formation_reload": summary | None,
                 "chain_report": report | None,
                 "restored_checkpoint_id": str | None,
                 "restore_report": report | None}.

        Raises:
            RuntimeError:
                If cleaned, already consumed, chain verification is broken,
                folded admission finds blockers, or replay fails.
            ValueError/TypeError/KeyError:
                Propagated from configuration activation, transport setup, or
                selected profile/history operations.
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
        formation_reload: Optional[Dict[str, object]] = None
        if (
                self._manager_configuration is not None
                and self._reload_formations
                # Capability gate (triage 2026-07-11): formations ride
                # the GENERIC lanes only. Legacy-only managers (the
                # upload/download/list trio, no quartet) are legal and
                # carry checkpoints fine - they simply have no formation
                # transport, so the step SKIPS instead of tripping the
                # generic lanes' deliberate loud-refusal.
                and self._manager_configuration.list_units_handler is not None
                and self._manager_configuration.fetch_handler is not None
        ):
            # Mesh-aware boot: named formation slices land as local
            # FILES beside the pulled checkpoints, so slice restores
            # work immediately on the rebuilt pod.
            formation_reload = crystallizer.reload_formations_from_external(
                self._profile_name
            )
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
            # S4: the facade's loader admission refuses "blockers"
            # verdicts BEFORE any replay (standard verdict law), so the
            # old post-restore gate check is gone - a blocked world never
            # gets this far.
            restore_report = crystallizer.load_checkpoint(newest)
            restored_checkpoint_id = newest
        return {
            "activated": True,
            "profile_name": self._profile_name,
            "cache_reload": cache_reload,
            "remote_reload": remote_reload,
            "formation_reload": formation_reload,
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
            - `list_checkpoint_ids()` returns exact ledger insertion order,
              including checkpoints minted in the same millisecond. The newest
              matching profile id is therefore the last one encountered.

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
