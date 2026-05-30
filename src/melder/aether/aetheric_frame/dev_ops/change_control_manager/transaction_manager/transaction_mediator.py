import threading
import time
import sys
from enum import Enum
from typing import (
    Iterable,
    Optional,
    Dict,
    List,
    Callable,
    TYPE_CHECKING,
    ClassVar,
    Any,
)

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.conflict_manager.conflict_manager import (
    ChangeControlConflictManager,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import (
    DevopsIdentity,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_session import (
    TransactionSession,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transaction_strategy_builder import (
    TransactionStrategyBuilder,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlAdmissionResult,
    ChangeTransactionType,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
        ChangeControlEmbargoManager,
    )
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.orchestrator import (
        ChangeControlOrchestrator,
    )
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.staged_mutation import (
        ChangeControlStagedMutation,
    )
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
        ChangeControlTransactionManager,
    )
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
        ChangeControlTransactionRequest,
    )

class TransactionMediator(Cleanable):
    """
    Frame-local live transaction session mediator.

    Purpose:
        Own the runtime session layer that sits above immutable request/staged
        payloads. This mediator tracks same-thread recursion, root-session
        ownership, and root commit/abort finalization without replacing the
        existing request builder, embargo manager, or orchestrator.

    Contract:
        - Root sessions are keyed by admitted request id.
        - Same-thread nested work joins the active root session.
        - Cross-thread root starts are allowed by default unless coarse
          queueing is explicitly enabled.
        - Only the outermost frame finalizes commit or abort through the
          existing orchestrator path.

    Threading:
        - Shared mediator state is guarded by an internal `RLock`.
        - Active execution frame stacks are stored in `threading.local()`.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_wait_condition",
        "_transaction_manager",
        "_conflict_manager",
        "_embargo_manager",
        "_orchestrator",
        "_devops_information_registry",
        "_queue_competing_root_transactions",
        "_max_transaction_wait_time_in_seconds",
        "_admit_request",
        "_strategy_builder",
        "_sessions_by_request_id",
        "_pending_root_starts",
        "_thread_local",
    ]

    def __init__(
            self,
            *,
            transaction_manager: "ChangeControlTransactionManager",
            conflict_manager: "ChangeControlConflictManager",
            embargo_manager: "ChangeControlEmbargoManager",
            orchestrator: "ChangeControlOrchestrator",
            devops_information_registry: Optional[DevopsInformationRegistry],
            queue_competing_root_transactions: bool = False,
            max_transaction_wait_time_in_seconds: float = 30.0,
            admit_request_fn: Optional[Callable[["ChangeControlTransactionRequest"], ChangeControlAdmissionResult]] = None,
    ) -> None:
        """
        Initialize the live transaction mediator.

        Args:
            transaction_manager:
                In-flight request registry helper.
            conflict_manager:
                Conflict helper used during admission.
            embargo_manager:
                Embargo helper used by orchestrator commit/abort paths.
            orchestrator:
                Admission/commit/abort orchestration helper.
            queue_competing_root_transactions:
                Whether competing root starts should wait in FIFO order.
            max_transaction_wait_time_in_seconds:
                Maximum seconds a competing root start may wait for the slot.
            admit_request_fn:
                Optional frame-owned admission facade. When supplied, root
                transaction admission goes through that facade instead of
                calling the orchestrator directly so manager-level policy like
                change-control disablement still applies.

        Raises:
            ValueError: If required collaborators are missing.
        """
        super().__init__()
        if transaction_manager is None:
            raise ValueError("transaction_manager must not be None.")
        if conflict_manager is None:
            raise ValueError("conflict_manager must not be None.")
        if embargo_manager is None:
            raise ValueError("embargo_manager must not be None.")
        if orchestrator is None:
            raise ValueError("orchestrator must not be None.")
        if not isinstance(queue_competing_root_transactions, bool):
            raise TypeError("queue_competing_root_transactions must be a bool.")
        if (
            not isinstance(max_transaction_wait_time_in_seconds, (int, float))
            or isinstance(max_transaction_wait_time_in_seconds, bool)
        ):
            raise TypeError(
                "max_transaction_wait_time_in_seconds must be a float or int."
            )
        if max_transaction_wait_time_in_seconds <= 0:
            raise ValueError(
                "max_transaction_wait_time_in_seconds must be greater than 0."
            )

        self._lock: threading.RLock = threading.RLock()
        self._wait_condition: threading.Condition = threading.Condition(self._lock)
        self._transaction_manager: ChangeControlTransactionManager = transaction_manager
        self._conflict_manager: ChangeControlConflictManager = conflict_manager
        self._embargo_manager: ChangeControlEmbargoManager = embargo_manager
        self._orchestrator: ChangeControlOrchestrator = orchestrator
        self._devops_information_registry: Optional[DevopsInformationRegistry] = (
            devops_information_registry
        )
        self._queue_competing_root_transactions: bool = (
            queue_competing_root_transactions
        )
        self._max_transaction_wait_time_in_seconds: float = float(
            max_transaction_wait_time_in_seconds
        )
        self._admit_request = admit_request_fn
        self._strategy_builder: TransactionStrategyBuilder = (
            TransactionStrategyBuilder(
                transaction_manager,
                devops_information_registry,
            )
        )
        self._sessions_by_request_id: Dict[str, TransactionSession] = {}
        self._pending_root_starts: List[int] = []
        self._thread_local: threading.local = threading.local()

    def cleanup(self) -> None:
        """
        Idempotently clear mediator-owned live session state.

        Contract:
            - Does not commit or abort in-flight requests implicitly.
            - Drops local session references and thread-local stacks only.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._sessions_by_request_id is not None:
                for session in list(self._sessions_by_request_id.values()):
                    try:
                        session.cleanup()
                    except Exception:
                        pass
                self._sessions_by_request_id.clear()
            if self._pending_root_starts is not None:
                self._pending_root_starts.clear()
            del self._sessions_by_request_id
            del self._pending_root_starts
            del self._transaction_manager
            del self._conflict_manager
            del self._embargo_manager
            del self._orchestrator
            del self._queue_competing_root_transactions
            del self._max_transaction_wait_time_in_seconds
            del self._admit_request
            del self._strategy_builder
            del self._thread_local
            del self._wait_condition
        del self._lock

    def configure(
            self,
            *,
            queue_competing_root_transactions: bool,
            max_transaction_wait_time_in_seconds: float,
    ) -> None:
        """
        Update mediator root-session policy.

        Args:
            queue_competing_root_transactions:
                Whether competing root starts queue for their turn.
            max_transaction_wait_time_in_seconds:
                Maximum seconds a queued root start may wait.
        """
        if not isinstance(queue_competing_root_transactions, bool):
            raise TypeError("queue_competing_root_transactions must be a bool.")
        if (
            not isinstance(max_transaction_wait_time_in_seconds, (int, float))
            or isinstance(max_transaction_wait_time_in_seconds, bool)
        ):
            raise TypeError(
                "max_transaction_wait_time_in_seconds must be a float or int."
            )
        if max_transaction_wait_time_in_seconds <= 0:
            raise ValueError(
                "max_transaction_wait_time_in_seconds must be greater than 0."
            )
        with self._lock:
            self._queue_competing_root_transactions = (
                queue_competing_root_transactions
            )
            self._max_transaction_wait_time_in_seconds = float(
                max_transaction_wait_time_in_seconds
            )

    def begin_frame(
            self,
            *,
            request: Optional["ChangeControlTransactionRequest"] = None,
            staged: Optional["ChangeControlStagedMutation"] = None,
            capabilities: Optional[Iterable[str]] = None,
            required_capabilities: Optional[Iterable[str]] = None,
    ) -> TransactionSession:
        """
        Begin one root session or join the active root session on the current thread.

        Args:
            request:
                Root admitted request for a new root session.
            staged:
                Root staged payload for a new root session.
            capabilities:
                Granted capabilities for a new root session or required
                capabilities for a nested join.
            required_capabilities:
                Explicit nested-join capability requirement. When provided, this
                is used for same-thread join checks instead of `capabilities`.

        Returns:
            TransactionSession: The active root session for this frame.

        Raises:
            RuntimeError: If nested different-root start is attempted.
            RuntimeError: If strict mode rejects a cross-thread root collision.
        """
        
        current_thread_id = threading.get_ident()
        active = self.get_active_session()
        if active is not None:
            if request is not None and request.request_id != active.request.request_id:
                raise RuntimeError(
                    "Nested root transaction is not allowed while a session is already active on this thread."
                )
            join_requirements = required_capabilities
            if join_requirements is None:
                join_requirements = capabilities
            active.join(
                thread_id=current_thread_id,
                required_capabilities=join_requirements,
            )
            self._get_stack().append(active.request.request_id)
            return active

        if request is None:
            raise ValueError(
                "request must be supplied when starting a new root transaction session."
            )
        if staged is None:
            raise ValueError(
                "staged must be supplied when starting a new root transaction session."
            )

        with self._lock:
            self._wait_for_turn_locked(current_thread_id)
            session = TransactionSession(
                request=request,
                staged=staged,
                submitter_identity=None,
                owner_thread_id=current_thread_id,
                capabilities=capabilities,
            )
            self._sessions_by_request_id[request.request_id] = session
            self._register_transaction_session_locked(session)
        self._get_stack().append(request.request_id)
        return session

    def begin_transaction(
            self,
            *,
            identity: DevopsIdentity,
            transaction_type: Any,
            existing_request_id: Optional[str] = None,
            initiator_conduit_id: Optional[str] = None,
            spellbook_id: Optional[str] = None,
            conduit_ids: Optional[Iterable[str]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, object]] = None,
            capabilities: Optional[Iterable[str]] = None,
            required_capabilities: Optional[Iterable[str]] = None,
    ) -> TransactionSession:
        """
        Route one transaction start through root-session creation or same-thread join.

        Purpose:
            Provide the first live transaction ingress surface that callers can
            use without manually building and admitting requests outside the
            mediator. This method handles:
            - identity validation
            - same-thread nested joins for one already-active local request
            - queued waiting for competing root starts
            - request building
            - orchestrator admission
            - root session creation

        Args:
            identity:
                Submitter identity entering the frame mutation domain.
            transaction_type:
                Requested transaction kind (enum or string).
            existing_request_id:
                Existing root request id to join for same-owner recursion.
            initiator_conduit_id:
                Optional explicit initiator id used when the submitter
                identity is not itself the conduit id that should appear on the
                request payload.
            spellbook_id:
                Optional spellbook id associated with the request.
            conduit_ids:
                Optional participating conduits.
            scope_keys:
                Optional normalized scope keys.
            scope_hashes:
                Optional normalized scope hashes.
            binding_keys:
                Optional binding keys.
            contract_keys:
                Optional contract keys.
            metadata:
                Optional structured metadata.
            capabilities:
                Granted capabilities for a new root session.
            required_capabilities:
                Capability requirements for nested same-thread joins.

        Returns:
            TransactionSession: The active root session for this frame.
        """
        
        if identity is None:
            raise ValueError("identity must not be None.")

        transaction_name = self._normalize_transaction_name(transaction_type)
        if not identity.supports_transaction(transaction_name):
            raise RuntimeError(
                f"DevopsIdentity does not declare support for '{transaction_name}'."
            )

        current_thread_id = threading.get_ident()
        normalized_metadata: Dict[str, object] = {}
        if metadata is not None:
            normalized_metadata.update(metadata)
        normalized_metadata.setdefault("transaction_identity", identity.describe())

        if existing_request_id is not None:
            active = self._get_session_or_raise(existing_request_id)
            join_requirements = required_capabilities
            if join_requirements is None:
                join_requirements = capabilities
            # Same-thread recursion is explicit. Callers must pass the current
            # local request id when they intend to keep working inside the same
            # root transaction instead of starting a parallel root.
            active.join(
                thread_id=current_thread_id,
                required_capabilities=join_requirements,
            )
            self._get_stack().append(active.request.request_id)
            self._update_active_staged_metadata(
                session=active,
                scope_keys=scope_keys,
                binding_keys=binding_keys,
                contract_keys=contract_keys,
                metadata=normalized_metadata,
            )
            return active

        with self._lock:
            self._wait_for_turn_locked(
                current_thread_id,
                allow_same_thread_parallel=True,
            )
            request = self._transaction_manager.build_request(
                request_type=transaction_type,
                initiator_conduit_id=(
                    initiator_conduit_id
                    if initiator_conduit_id is not None
                    else identity.owner_id
                ),
                spellbook_id=spellbook_id,
                conduit_ids=conduit_ids,
                scope_keys=scope_keys,
                scope_hashes=scope_hashes,
                binding_keys=binding_keys,
                contract_keys=contract_keys,
                metadata=normalized_metadata,
            )
            if self._admit_request is not None:
                admission = self._admit_request(request)
            else:
                admission = self._orchestrator.admit_request(
                    request,
                    transaction_manager=self._transaction_manager,
                    conflict_manager=self._conflict_manager,
                    embargo_manager=self._embargo_manager,
                )
            if not admission.admitted:
                details: list[str] = []
                if admission.conflicts:
                    details.append(f"conflicts={admission.conflicts}")
                if admission.embargoes:
                    details.append(f"embargoes={admission.embargoes}")
                detail_msg = "; ".join(details) if details else "no conflict metadata available"
                raise RuntimeError(
                    "[TRANSACTION_MEDIATOR] Change-control admission denied "
                    f"(reasons={admission.reasons}). {detail_msg}"
                )
            staged = self._orchestrator.get_staged(request.request_id)
            if staged is None:
                from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.staged_mutation import (
                    ChangeControlStagedMutation,
                )
                staged = ChangeControlStagedMutation.from_request(
                    request_id=request.request_id,
                    request_type=request.request_type,
                    initiator_conduit_id=request.initiator_conduit_id,
                    spellbook_id=request.spellbook_id,
                    conduit_ids=request.conduit_ids,
                    scope_keys=request.scope_keys,
                    binding_keys=request.binding_keys,
                    contract_keys=request.contract_keys,
                    metadata=request.metadata,
                )
            session = TransactionSession(
                request=request,
                staged=staged,
                submitter_identity=identity,
                owner_thread_id=current_thread_id,
                capabilities=capabilities,
            )
            self._sessions_by_request_id[request.request_id] = session
            self._register_transaction_session_locked(session)
        self._get_stack().append(request.request_id)
        return session

    def get_session_for_identity(
            self,
            *,
            identity: DevopsIdentity,
            transaction_type: Any,
    ) -> Optional[TransactionSession]:
        """
        Return the newest local session matching one identity and transaction kind.
        """
        
        if identity is None:
            raise ValueError("identity must not be None.")
        transaction_name = self._normalize_transaction_name(transaction_type)
        stack = self._get_stack()
        for request_id in reversed(stack):
            session = self.get_session_by_request_id(request_id)
            if session is None:
                continue
            submitter_identity = session.submitter_identity
            if submitter_identity is None:
                continue
            if submitter_identity.owner_id != identity.owner_id:
                continue
            if submitter_identity.owner_kind != identity.owner_kind:
                continue
            session_transaction_name = self._normalize_transaction_name(
                session.request.request_type,
            )
            if session_transaction_name != transaction_name:
                continue
            return session
        return None

    def update_transaction_for_identity(
            self,
            *,
            identity: DevopsIdentity,
            transaction_type: Any,
            scope_keys: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> bool:
        """
        Update staged metadata for the active session matching one identity.

        Purpose:
            Give thin runtime callers a mediator-owned way to extend staged
            metadata for an already-active transaction without reaching through
            to `ChangeControlManager` directly.

        Contract:
            - Returns `False` when no matching session is active.
            - Delegates staged metadata and embargo extension through the same
              internal path used for same-thread join widening.
            - Does not create or end sessions.

        Args:
            identity:
                Submitter identity that owns the active transaction.
            transaction_type:
                Transaction kind whose active session should be updated.
            scope_keys:
                Optional additional normalized scope keys.
            binding_keys:
                Optional additional binding keys.
            contract_keys:
                Optional additional contract keys.
            metadata:
                Optional metadata merged into the staged request.

        Returns:
            bool:
                `True` when an active matching session was found and updated,
                otherwise `False`.
        """
        
        if identity is None:
            raise ValueError("identity must not be None.")
        session = self.get_session_for_identity(
            identity=identity,
            transaction_type=transaction_type,
        )
        if session is None:
            return False
        self._update_active_staged_metadata(
            session=session,
            scope_keys=scope_keys,
            binding_keys=binding_keys,
            contract_keys=contract_keys,
            metadata=metadata,
        )
        return True

    def start_transaction(
            self,
            *,
            identity: DevopsIdentity,
            transaction_type: Any,
            metadata: Optional[Dict[str, object]] = None,
    ) -> TransactionSession:
        """
        Start one high-level transaction using mediator-owned resolution logic.

        Purpose:
            Provide the thin generic API callers should use. Resolver-specific
            request shaping and bind lifecycle registration stay in the
            mediator rather than in the caller.
        """
        
        transaction_name = self._normalize_transaction_name(transaction_type)
        if transaction_name in (
                "bind",
                "link",
                "cluster_link",
                "transfer_ownership",
        ):
            return self._start_strategy_transaction(
                identity=identity,
                transaction_type=ChangeTransactionType(transaction_name),
                metadata=dict(metadata) if metadata is not None else {},
            )
        raise NotImplementedError(
            f"High-level mediator resolution is not implemented for '{transaction_name}'."
        )

    def end_transaction_for_identity(
            self,
            *,
            identity: DevopsIdentity,
            transaction_type: Any,
    ) -> TransactionSession:
        """
        End one high-level transaction by identity and transaction kind.
        """
        
        session = self.get_session_for_identity(
            identity=identity,
            transaction_type=transaction_type,
        )
        if session is None:
            raise RuntimeError("No active transaction session exists for this identity.")
        transaction_name = self._normalize_transaction_name(transaction_type)
        exc_type, _exc, _tb = sys.exc_info()
        success = exc_type is None and session.status != TransactionSession.STATUS_ABORT_ONLY
        try:
            return self.end_transaction_by_request_id(
                session.request.request_id,
                expected_type=transaction_type,
                success=success,
            )
        finally:
            self._strategy_builder.on_end(
                transaction_type=transaction_name,
                identity=identity,
                metadata=dict(session.request.metadata),
            )

    def get_session_by_request_id(
            self,
            request_id: str,
    ) -> Optional[TransactionSession]:
        """
        Return one live session by request id, if present.
        """
        
        if not isinstance(request_id, str):
            raise TypeError("request_id must be a string.")
        if not request_id.strip():
            raise ValueError("request_id must not be empty.")
        with self._lock:
            return self._sessions_by_request_id.get(request_id)

    def end_transaction(
            self,
            *,
            expected_type: Optional[Any] = None,
            success: bool = True,
    ) -> TransactionSession:
        """
        End the active transaction frame for the current thread.

        Args:
            expected_type:
                Optional transaction kind assertion for the active root request.
            success:
                Whether the current frame exited successfully.

        Returns:
            TransactionSession: The session whose frame was ended.
        """
        
        session = self.get_active_session()
        if session is None:
            raise RuntimeError("No active transaction session exists on this thread.")
        if expected_type is not None:
            expected_name = self._normalize_transaction_name(expected_type)
            active_name = self._normalize_transaction_name(
                session.request.request_type
            )
            if active_name != expected_name:
                raise RuntimeError(
                    "Active transaction session does not match the requested type."
                )
        return self.end_frame(success=success)

    def end_transaction_by_request_id(
            self,
            request_id: str,
            *,
            expected_type: Optional[Any] = None,
            success: bool = True,
    ) -> TransactionSession:
        """
        End one specific active transaction frame identified by request id.
        """
        
        session = self._get_session_or_raise(request_id)
        current_thread_id = threading.get_ident()
        if session.owner_thread_id != current_thread_id:
            raise RuntimeError(
                "Only the owner thread may end an active transaction session."
            )
        if expected_type is not None:
            expected_name = self._normalize_transaction_name(expected_type)
            active_name = self._normalize_transaction_name(
                session.request.request_type
            )
            if active_name != expected_name:
                raise RuntimeError(
                    "Active transaction session does not match the requested type."
                )
        self._remove_request_id_from_stack(request_id)
        if not success:
            session.mark_abort_only("Nested transaction frame exited with failure.")
        remaining_depth = session.leave()
        if remaining_depth > 0:
            return session
        try:
            self._finalize_root_session(session)
        finally:
            with self._lock:
                self._unregister_transaction_session_locked(request_id)
                self._sessions_by_request_id.pop(request_id, None)
                self._wait_condition.notify_all()
        return session

    def end_frame(self, *, success: bool = True) -> TransactionSession:
        """
        End the current execution frame and finalize the root session if outermost.

        Args:
            success:
                Whether the current frame exited successfully.

        Returns:
            TransactionSession: The session that owned the exiting frame.

        Raises:
            RuntimeError: If no active session exists on the current thread.
            Exception: Propagates commit pipeline failures after abort cleanup.
        """
        
        stack = self._get_stack()
        if not stack:
            raise RuntimeError("No active transaction session exists on this thread.")
        request_id = stack.pop()
        session = self._get_session_or_raise(request_id)
        if not success:
            session.mark_abort_only("Nested transaction frame exited with failure.")
        remaining_depth = session.leave()
        if remaining_depth > 0:
            return session
        try:
            self._finalize_root_session(session)
        finally:
            with self._lock:
                self._unregister_transaction_session_locked(request_id)
                self._sessions_by_request_id.pop(request_id, None)
                self._wait_condition.notify_all()
        return session

    def mark_active_session_abort_only(
            self,
            *,
            reason: str,
            error: Optional[BaseException] = None,
    ) -> None:
        """
        Mark the current active session abort-only on the current thread.
        """
        
        session = self.get_active_session()
        if session is None:
            raise RuntimeError("No active transaction session exists on this thread.")
        session.mark_abort_only(reason, error)

    def get_active_session(self) -> Optional[TransactionSession]:
        """
        Return the active session for the current thread, if any.
        """
        
        stack = self._get_stack()
        if not stack:
            return None
        request_id = stack[-1]
        with self._lock:
            return self._sessions_by_request_id.get(request_id)

    def get_active_request(self) -> Optional["ChangeControlTransactionRequest"]:
        """
        Return the active root request for the current thread, if any.
        """
        
        session = self.get_active_session()
        if session is None:
            return None
        return session.request

    def has_active_session(self) -> bool:
        """
        Return whether the current thread has an active session frame.
        """
        
        return self.get_active_session() is not None

    def describe(self) -> dict:
        """
        Return a detached diagnostic snapshot of mediator state.
        """
        
        with self._lock:
            return {
                "queue_competing_root_transactions": (
                    self._queue_competing_root_transactions
                ),
                "max_transaction_wait_time_in_seconds": (
                    self._max_transaction_wait_time_in_seconds
                ),
                "active_session_count": len(self._sessions_by_request_id),
                "request_ids": tuple(sorted(self._sessions_by_request_id.keys())),
            }

    def _finalize_root_session(self, session: TransactionSession) -> None:
        """
        Commit or abort one root session through the existing orchestrator path.
        """
        if session.status == TransactionSession.STATUS_ABORT_ONLY:
            session.run_abort_pipeline()
            session.mark_aborted()
            self._orchestrator.abort_request(
                session.request.request_id,
                transaction_manager=self._transaction_manager,
                embargo_manager=self._embargo_manager,
            )
            return

        session.mark_committing()
        try:
            session.run_commit_pipeline()
            self._orchestrator.commit_request(
                session.request.request_id,
                transaction_manager=self._transaction_manager,
                embargo_manager=self._embargo_manager,
            )
        except Exception as exc:
            session.mark_abort_only("Commit pipeline failed.", exc)
            session.run_abort_pipeline()
            session.mark_aborted()
            self._orchestrator.abort_request(
                session.request.request_id,
                transaction_manager=self._transaction_manager,
                embargo_manager=self._embargo_manager,
            )
            raise
        else:
            session.mark_committed()

    def _get_stack(self) -> List[str]:
        """
        Return the thread-local request-id stack for the current thread.
        """
        try:
            stack = self._thread_local.request_stack
        except AttributeError:
            stack = []
            self._thread_local.request_stack = stack
        return stack

    def _wait_for_turn_locked(
            self,
            thread_id: int,
            *,
            allow_same_thread_parallel: bool = False,
    ) -> None:
        """
        Wait in FIFO order for a root-session slot when queueing is enabled.

        Contract:
            - Returns immediately when no root session is active.
            - Returns immediately when queueing is disabled.
            - When queueing is enabled, waits until this thread is the queue
              head and no root sessions remain active.
        """
        if not self._sessions_by_request_id:
            return
        if allow_same_thread_parallel:
            # Distinct local roots on the same thread should still be allowed
            # to reach normal admission/conflict handling. The block/wait
            # policy only applies when another thread currently owns the frame
            # mutation domain.
            owner_thread_ids = {
                session.owner_thread_id
                for session in self._sessions_by_request_id.values()
            }
            if owner_thread_ids == {thread_id}:
                return
        if not self._queue_competing_root_transactions:
            return

        self._pending_root_starts.append(thread_id)
        deadline = time.monotonic() + self._max_transaction_wait_time_in_seconds
        try:
            while True:
                is_head = bool(self._pending_root_starts) and self._pending_root_starts[0] == thread_id
                if is_head and not self._sessions_by_request_id:
                    self._pending_root_starts.pop(0)
                    return
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    self._pending_root_starts = [
                        pending_id
                        for pending_id in self._pending_root_starts
                        if pending_id != thread_id
                    ]
                    raise RuntimeError(
                        "Timed out waiting for the active root transaction session to finish."
                    )
                self._wait_condition.wait(timeout=remaining)
        except Exception:
            self._wait_condition.notify_all()
            raise

    def _remove_request_id_from_stack(self, request_id: str) -> None:
        """
        Remove the most recent occurrence of one request id from the thread stack.
        """
        stack = self._get_stack()
        for index in range(len(stack) - 1, -1, -1):
            if stack[index] == request_id:
                del stack[index]
                return
        raise RuntimeError(
            "Active transaction request id is not present on this thread stack."
        )

    def _update_active_staged_metadata(
            self,
            *,
            session: TransactionSession,
            scope_keys: Optional[Iterable[str]],
            binding_keys: Optional[Iterable[tuple[str, str]]],
            contract_keys: Optional[Iterable[tuple[str, str, str]]],
            metadata: Optional[Dict[str, object]],
    ) -> None:
        """
        Extend staged metadata for the current root request after a same-thread join.
        """
        request_id = session.request.request_id
        normalized_scope_keys = tuple(scope_keys) if scope_keys is not None else None
        normalized_binding_keys = tuple(binding_keys) if binding_keys is not None else None
        normalized_contract_keys = tuple(contract_keys) if contract_keys is not None else None
        updated = self._orchestrator.update_staged(
            request_id,
            scope_keys=normalized_scope_keys,
            binding_keys=normalized_binding_keys,
            contract_keys=normalized_contract_keys,
            metadata=metadata,
        )
        if not updated:
            return
        staged = self._orchestrator.get_staged(request_id)
        if staged is None:
            return
        with session._lock:
            session._staged = staged
        scope_key_values = self._embargo_manager.collect_scope_keys_from_staged(staged)
        if scope_key_values:
            self._embargo_manager.extend_embargoes(
                owner_request_id=request_id,
                scope_keys=scope_key_values,
                reason_tag=(
                    staged.request_type.value
                    if hasattr(staged.request_type, "value")
                    else str(staged.request_type)
                ),
            )

    def _get_session_or_raise(self, request_id: str) -> TransactionSession:
        """
        Resolve one session by request id or raise if missing.
        """
        with self._lock:
            session = self._sessions_by_request_id.get(request_id)
        if session is None:
            raise RuntimeError("Active transaction session could not be resolved.")
        return session

    def _register_transaction_session_locked(
            self,
            session: TransactionSession,
    ) -> None:
        """
        Register one live root session in the dev-ops information registry.

        Caller contract:
            The mediator lock must already be held.
        """
        registry = self._devops_information_registry
        if registry is None:
            return
        identity_keys = set()
        submitter_identity = session.submitter_identity
        if submitter_identity is not None:
            identity_keys.add(
                (submitter_identity.owner_kind, submitter_identity.owner_id)
            )
        registry.register_transaction(
            transaction_id=session.request.request_id,
            transaction_object=session,
            transaction_type=self._normalize_transaction_name(
                session.request.request_type,
            ),
            identity_keys=identity_keys,
        )

    def _unregister_transaction_session_locked(self, request_id: str) -> None:
        """
        Remove one live root session from the dev-ops information registry.

        Caller contract:
            The mediator lock must already be held.
        """
        registry = self._devops_information_registry
        if registry is None:
            return
        registry.unregister_transaction(request_id)

    @staticmethod
    def _normalize_transaction_name(transaction_type: Any) -> str:
        """
        Normalize one transaction type value into a lowercase string name.
        """
        value = transaction_type
        if not isinstance(transaction_type, str):
            if isinstance(transaction_type, Enum):
                value = transaction_type.value
            else:
                try:
                    value = transaction_type.value
                except AttributeError as exc:
                    raise TypeError(
                        "transaction_type must be a string-like value."
                    ) from exc
        if not isinstance(value, str):
            raise TypeError("transaction_type must be a string-like value.")
        normalized_value = value.strip().lower()
        if not normalized_value:
            raise ValueError("transaction_type must not be empty.")
        return normalized_value

    def _start_strategy_transaction(
            self,
            *,
            identity: DevopsIdentity,
            transaction_type: ChangeTransactionType,
            metadata: Dict[str, object],
    ) -> TransactionSession:
        """
        Resolve and start one strategy-owned transaction.
        """
        
        active = self.get_session_for_identity(
            identity=identity,
            transaction_type=transaction_type,
        )
        if active is not None:
            active.join(
                thread_id=threading.get_ident(),
                required_capabilities=None,
            )
            self._get_stack().append(active.request.request_id)
            return active

        bind_request = self._strategy_builder.build_start_plan(
            transaction_type=transaction_type,
            identity=identity,
            metadata=metadata,
        )
        session = self.begin_transaction(
            identity=identity,
            transaction_type=transaction_type,
            initiator_conduit_id=bind_request["initiator_conduit_id"],
            spellbook_id=bind_request["spellbook_id"],
            conduit_ids=bind_request["conduit_ids"],
            scope_keys=bind_request["scope_keys"],
            scope_hashes=bind_request["scope_hashes"],
            binding_keys=bind_request["binding_keys"],
            contract_keys=bind_request["contract_keys"],
            metadata=bind_request["metadata"],
            capabilities=bind_request.get("granted_capabilities"),
            required_capabilities=bind_request.get("required_capabilities"),
        )
        try:
            self._strategy_builder.on_start(
                transaction_type=transaction_type,
                identity=identity,
                metadata=dict(bind_request["metadata"]),
            )
            return session
        except Exception:
            session.mark_abort_only(
                f"{transaction_type.value} transaction start strategy failed.",
            )
            self.end_transaction_by_request_id(
                session.request.request_id,
                expected_type=transaction_type,
                success=False,
            )
            self._strategy_builder.on_end(
                transaction_type=transaction_type,
                identity=identity,
                metadata=dict(bind_request["metadata"]),
            )
            raise
