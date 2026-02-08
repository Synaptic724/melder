import time
from typing import Any, Callable, List, Tuple


class _SharedDependencies:
    """
    Hold a fixed dependency payload for attribute-access micro-benchmarks.

    Contract:
        - Stores four integer dependency fields.
        - Exposes direct attribute access only.
    """

    __slots__ = ("dep1", "dep2", "dep3", "dep4")

    def __init__(self) -> None:
        """
        Initialize deterministic dependency values.
        """
        self.dep1 = 1
        self.dep2 = 2
        self.dep3 = 3
        self.dep4 = 4


class _ChainLevel4:
    """
    Provide depth-4 dependency payload fields.

    Contract:
        - Stores four integer dependency fields.
    """

    __slots__ = ("dep1", "dep2", "dep3", "dep4")

    def __init__(self) -> None:
        """
        Initialize deterministic dependency values.
        """
        self.dep1 = 1
        self.dep2 = 2
        self.dep3 = 3
        self.dep4 = 4


class _ChainLevel3:
    """
    Provide depth-3 dependency payload fields and link to level 4.

    Contract:
        - Stores four integer dependency fields.
        - Owns one level-4 child under ``l4``.
    """

    __slots__ = ("dep1", "dep2", "dep3", "dep4", "l4")

    def __init__(self) -> None:
        """
        Initialize deterministic dependency values and nested level-4 node.
        """
        self.dep1 = 1
        self.dep2 = 2
        self.dep3 = 3
        self.dep4 = 4
        self.l4 = _ChainLevel4()


class _ChainLevel2:
    """
    Provide depth-2 dependency payload fields and link to level 3.

    Contract:
        - Stores four integer dependency fields.
        - Owns one level-3 child under ``l3``.
    """

    __slots__ = ("dep1", "dep2", "dep3", "dep4", "l3")

    def __init__(self) -> None:
        """
        Initialize deterministic dependency values and nested level-3 node.
        """
        self.dep1 = 1
        self.dep2 = 2
        self.dep3 = 3
        self.dep4 = 4
        self.l3 = _ChainLevel3()


class _ChainRoot:
    """
    Root object for chain-depth attribute benchmarks.

    Contract:
        - Owns one level-2 child under ``l2``.
    """

    __slots__ = ("l2",)

    def __init__(self) -> None:
        """
        Initialize the chain root with deterministic nested children.
        """
        self.l2 = _ChainLevel2()


class _Owner:
    """
    Provide benchmark methods for direct and aliased attribute access.

    Contract:
        - Owns a single shared dependency object.
        - Each method runs a tight loop and returns an integer checksum.
        - No mutation occurs during benchmark loops.
    """

    __slots__ = ("_shared",)

    def __init__(self, shared: _SharedDependencies) -> None:
        """
        Initialize the owner with a shared dependency object.

        Args:
            shared: Shared dependency object used by benchmark methods.
        """
        self._shared = shared

    def run_direct(self, *, iterations: int, access_count: int) -> int:
        """
        Execute direct ``self._shared`` attribute access in a tight loop.

        Args:
            iterations: Loop iterations to execute.
            access_count: Number of dependency fields to read per iteration.

        Returns:
            int: Deterministic checksum for correctness validation.
        """
        total = 0
        if access_count == 1:
            for _ in range(iterations):
                total += self._shared.dep1
            return total
        if access_count == 2:
            for _ in range(iterations):
                total += self._shared.dep1 + self._shared.dep2
            return total
        if access_count == 3:
            for _ in range(iterations):
                total += self._shared.dep1 + self._shared.dep2 + self._shared.dep3
            return total
        if access_count == 4:
            for _ in range(iterations):
                total += (
                    self._shared.dep1
                    + self._shared.dep2
                    + self._shared.dep3
                    + self._shared.dep4
                )
            return total
        raise ValueError("access_count must be between 1 and 4.")

    def run_alias(self, *, iterations: int, access_count: int) -> int:
        """
        Execute local-alias attribute access in a tight loop.

        Args:
            iterations: Loop iterations to execute.
            access_count: Number of dependency fields to read per iteration.

        Returns:
            int: Deterministic checksum for correctness validation.
        """
        total = 0
        shared = self._shared
        if access_count == 1:
            for _ in range(iterations):
                total += shared.dep1
            return total
        if access_count == 2:
            for _ in range(iterations):
                total += shared.dep1 + shared.dep2
            return total
        if access_count == 3:
            for _ in range(iterations):
                total += shared.dep1 + shared.dep2 + shared.dep3
            return total
        if access_count == 4:
            for _ in range(iterations):
                total += (
                    shared.dep1
                    + shared.dep2
                    + shared.dep3
                    + shared.dep4
                )
            return total
        raise ValueError("access_count must be between 1 and 4.")


class _OwnerWithChain:
    """
    Provide benchmark methods for chained self-attribute access.

    Contract:
        - Owns one chain root object.
        - Compares direct chain traversal versus local alias to the leaf node.
        - Supports depth 2, 3, and 4 with access counts 1..4.
    """

    __slots__ = ("_chain_root",)

    def __init__(self, chain_root: _ChainRoot) -> None:
        """
        Initialize owner with a nested chain root object.

        Args:
            chain_root: Root object containing nested benchmark chain levels.
        """
        self._chain_root = chain_root

    def run_direct_chain(self, *, iterations: int, access_count: int, depth: int) -> int:
        """
        Execute direct chained self-attribute access in a tight loop.

        Args:
            iterations: Loop iterations to execute.
            access_count: Number of dependency fields to read per iteration.
            depth: Chain depth to resolve (2, 3, or 4).

        Returns:
            int: Deterministic checksum for correctness validation.
        """
        total = 0
        if depth == 2:
            if access_count == 1:
                for _ in range(iterations):
                    total += self._chain_root.l2.dep1
                return total
            if access_count == 2:
                for _ in range(iterations):
                    total += self._chain_root.l2.dep1 + self._chain_root.l2.dep2
                return total
            if access_count == 3:
                for _ in range(iterations):
                    total += (
                        self._chain_root.l2.dep1
                        + self._chain_root.l2.dep2
                        + self._chain_root.l2.dep3
                    )
                return total
            if access_count == 4:
                for _ in range(iterations):
                    total += (
                        self._chain_root.l2.dep1
                        + self._chain_root.l2.dep2
                        + self._chain_root.l2.dep3
                        + self._chain_root.l2.dep4
                    )
                return total
        if depth == 3:
            if access_count == 1:
                for _ in range(iterations):
                    total += self._chain_root.l2.l3.dep1
                return total
            if access_count == 2:
                for _ in range(iterations):
                    total += self._chain_root.l2.l3.dep1 + self._chain_root.l2.l3.dep2
                return total
            if access_count == 3:
                for _ in range(iterations):
                    total += (
                        self._chain_root.l2.l3.dep1
                        + self._chain_root.l2.l3.dep2
                        + self._chain_root.l2.l3.dep3
                    )
                return total
            if access_count == 4:
                for _ in range(iterations):
                    total += (
                        self._chain_root.l2.l3.dep1
                        + self._chain_root.l2.l3.dep2
                        + self._chain_root.l2.l3.dep3
                        + self._chain_root.l2.l3.dep4
                    )
                return total
        if depth == 4:
            if access_count == 1:
                for _ in range(iterations):
                    total += self._chain_root.l2.l3.l4.dep1
                return total
            if access_count == 2:
                for _ in range(iterations):
                    total += self._chain_root.l2.l3.l4.dep1 + self._chain_root.l2.l3.l4.dep2
                return total
            if access_count == 3:
                for _ in range(iterations):
                    total += (
                        self._chain_root.l2.l3.l4.dep1
                        + self._chain_root.l2.l3.l4.dep2
                        + self._chain_root.l2.l3.l4.dep3
                    )
                return total
            if access_count == 4:
                for _ in range(iterations):
                    total += (
                        self._chain_root.l2.l3.l4.dep1
                        + self._chain_root.l2.l3.l4.dep2
                        + self._chain_root.l2.l3.l4.dep3
                        + self._chain_root.l2.l3.l4.dep4
                    )
                return total
        raise ValueError("depth must be 2, 3, or 4 and access_count must be 1..4.")

    def run_alias_chain(self, *, iterations: int, access_count: int, depth: int) -> int:
        """
        Execute local-alias chained self-attribute access in a tight loop.

        Args:
            iterations: Loop iterations to execute.
            access_count: Number of dependency fields to read per iteration.
            depth: Chain depth to resolve (2, 3, or 4).

        Returns:
            int: Deterministic checksum for correctness validation.
        """
        if depth == 2:
            leaf = self._chain_root.l2
        elif depth == 3:
            leaf = self._chain_root.l2.l3
        elif depth == 4:
            leaf = self._chain_root.l2.l3.l4
        else:
            raise ValueError("depth must be 2, 3, or 4.")

        total = 0
        if access_count == 1:
            for _ in range(iterations):
                total += leaf.dep1
            return total
        if access_count == 2:
            for _ in range(iterations):
                total += leaf.dep1 + leaf.dep2
            return total
        if access_count == 3:
            for _ in range(iterations):
                total += leaf.dep1 + leaf.dep2 + leaf.dep3
            return total
        if access_count == 4:
            for _ in range(iterations):
                total += leaf.dep1 + leaf.dep2 + leaf.dep3 + leaf.dep4
            return total
        raise ValueError("access_count must be between 1 and 4.")


def _run_param_direct(*, shared: _SharedDependencies, iterations: int, access_count: int) -> int:
    """
    Execute direct parameter-attribute access in a tight loop.

    Args:
        shared: Dependency object passed as a method/function parameter.
        iterations: Loop iterations to execute.
        access_count: Number of dependency fields to read per iteration.

    Returns:
        int: Deterministic checksum for correctness validation.
    """
    total = 0
    if access_count == 1:
        for _ in range(iterations):
            total += shared.dep1
        return total
    if access_count == 2:
        for _ in range(iterations):
            total += shared.dep1 + shared.dep2
        return total
    if access_count == 3:
        for _ in range(iterations):
            total += shared.dep1 + shared.dep2 + shared.dep3
        return total
    if access_count == 4:
        for _ in range(iterations):
            total += shared.dep1 + shared.dep2 + shared.dep3 + shared.dep4
        return total
    raise ValueError("access_count must be between 1 and 4.")


def _run_param_alias(*, shared: _SharedDependencies, iterations: int, access_count: int) -> int:
    """
    Execute local-alias parameter-attribute access in a tight loop.

    Args:
        shared: Dependency object passed as a method/function parameter.
        iterations: Loop iterations to execute.
        access_count: Number of dependency fields to read per iteration.

    Returns:
        int: Deterministic checksum for correctness validation.
    """
    local_shared = shared
    total = 0
    if access_count == 1:
        for _ in range(iterations):
            total += local_shared.dep1
        return total
    if access_count == 2:
        for _ in range(iterations):
            total += local_shared.dep1 + local_shared.dep2
        return total
    if access_count == 3:
        for _ in range(iterations):
            total += local_shared.dep1 + local_shared.dep2 + local_shared.dep3
        return total
    if access_count == 4:
        for _ in range(iterations):
            total += (
                local_shared.dep1
                + local_shared.dep2
                + local_shared.dep3
                + local_shared.dep4
            )
        return total
    raise ValueError("access_count must be between 1 and 4.")


def _run_param_chain_direct(
        *,
        chain_root: _ChainRoot,
        iterations: int,
        access_count: int,
        depth: int,
) -> int:
    """
    Execute direct chained parameter-attribute access in a tight loop.

    Args:
        chain_root: Root object passed as a parameter.
        iterations: Loop iterations to execute.
        access_count: Number of dependency fields to read per iteration.
        depth: Chain depth to resolve (2, 3, or 4).

    Returns:
        int: Deterministic checksum for correctness validation.
    """
    total = 0
    if depth == 2:
        if access_count == 1:
            for _ in range(iterations):
                total += chain_root.l2.dep1
            return total
        if access_count == 2:
            for _ in range(iterations):
                total += chain_root.l2.dep1 + chain_root.l2.dep2
            return total
        if access_count == 3:
            for _ in range(iterations):
                total += chain_root.l2.dep1 + chain_root.l2.dep2 + chain_root.l2.dep3
            return total
        if access_count == 4:
            for _ in range(iterations):
                total += (
                    chain_root.l2.dep1
                    + chain_root.l2.dep2
                    + chain_root.l2.dep3
                    + chain_root.l2.dep4
                )
            return total
    if depth == 3:
        if access_count == 1:
            for _ in range(iterations):
                total += chain_root.l2.l3.dep1
            return total
        if access_count == 2:
            for _ in range(iterations):
                total += chain_root.l2.l3.dep1 + chain_root.l2.l3.dep2
            return total
        if access_count == 3:
            for _ in range(iterations):
                total += chain_root.l2.l3.dep1 + chain_root.l2.l3.dep2 + chain_root.l2.l3.dep3
            return total
        if access_count == 4:
            for _ in range(iterations):
                total += (
                    chain_root.l2.l3.dep1
                    + chain_root.l2.l3.dep2
                    + chain_root.l2.l3.dep3
                    + chain_root.l2.l3.dep4
                )
            return total
    if depth == 4:
        if access_count == 1:
            for _ in range(iterations):
                total += chain_root.l2.l3.l4.dep1
            return total
        if access_count == 2:
            for _ in range(iterations):
                total += chain_root.l2.l3.l4.dep1 + chain_root.l2.l3.l4.dep2
            return total
        if access_count == 3:
            for _ in range(iterations):
                total += (
                    chain_root.l2.l3.l4.dep1
                    + chain_root.l2.l3.l4.dep2
                    + chain_root.l2.l3.l4.dep3
                )
            return total
        if access_count == 4:
            for _ in range(iterations):
                total += (
                    chain_root.l2.l3.l4.dep1
                    + chain_root.l2.l3.l4.dep2
                    + chain_root.l2.l3.l4.dep3
                    + chain_root.l2.l3.l4.dep4
                )
            return total
    raise ValueError("depth must be 2, 3, or 4 and access_count must be 1..4.")


def _run_param_chain_alias(
        *,
        chain_root: _ChainRoot,
        iterations: int,
        access_count: int,
        depth: int,
) -> int:
    """
    Execute local-alias chained parameter-attribute access in a tight loop.

    Args:
        chain_root: Root object passed as a parameter.
        iterations: Loop iterations to execute.
        access_count: Number of dependency fields to read per iteration.
        depth: Chain depth to resolve (2, 3, or 4).

    Returns:
        int: Deterministic checksum for correctness validation.
    """
    if depth == 2:
        leaf = chain_root.l2
    elif depth == 3:
        leaf = chain_root.l2.l3
    elif depth == 4:
        leaf = chain_root.l2.l3.l4
    else:
        raise ValueError("depth must be 2, 3, or 4.")

    total = 0
    if access_count == 1:
        for _ in range(iterations):
            total += leaf.dep1
        return total
    if access_count == 2:
        for _ in range(iterations):
            total += leaf.dep1 + leaf.dep2
        return total
    if access_count == 3:
        for _ in range(iterations):
            total += leaf.dep1 + leaf.dep2 + leaf.dep3
        return total
    if access_count == 4:
        for _ in range(iterations):
            total += leaf.dep1 + leaf.dep2 + leaf.dep3 + leaf.dep4
        return total
    raise ValueError("access_count must be between 1 and 4.")


class _HookFlags:
    """
    Hold conduit-like hook flags for real-world call-shape benchmarks.

    Contract:
        - Stores one boolean flag used by singleton resolve paths.
    """

    __slots__ = ("has_meld_phase_hooks",)

    def __init__(self, has_meld_phase_hooks: bool) -> None:
        """
        Initialize hook-flag state.

        Args:
            has_meld_phase_hooks: Whether conduit-level meld hooks are active.
        """
        self.has_meld_phase_hooks = has_meld_phase_hooks


class _ValidationFlags:
    """
    Hold spellbook-like validation flags for real-world call-shape benchmarks.

    Contract:
        - Stores one boolean validation gate flag.
    """

    __slots__ = ("spellbook_validation_required",)

    def __init__(self, spellbook_validation_required: bool) -> None:
        """
        Initialize validation-flag state.

        Args:
            spellbook_validation_required:
                Whether lineage validation gates are active.
        """
        self.spellbook_validation_required = spellbook_validation_required


class _RuntimeCounter:
    """
    Provide deterministic runtime-construction behavior for miss-path checks.

    Contract:
        - Tracks build invocations through ``counter``.
        - Returns deterministic integer payloads for one spell id.
    """

    __slots__ = ("counter",)

    def __init__(self) -> None:
        """
        Initialize runtime counter to zero.
        """
        self.counter = 0

    def build_value(self, spell_id: str) -> int:
        """
        Build one deterministic value and increment build count.

        Args:
            spell_id: Spell identifier used to derive payload value.

        Returns:
            int: Deterministic integer payload.
        """
        self.counter += 1
        return len(spell_id) + self.counter


class _SingletonCallShapeBench:
    """
    Model one real-world singleton resolve call shape.

    Contract:
        - Performs hook gate checks.
        - Performs spellbook validation gate checks.
        - Performs one singleton cache lookup and optional build on miss.
        - Returns deterministic checksum-compatible integers.
    """

    __slots__ = (
        "_hook_flags",
        "_validation_flags",
        "_cache",
        "_runtime",
        "_spell_id",
    )

    def __init__(
            self,
            *,
            preload_cache: bool,
            hooks_enabled: bool,
            validation_required: bool,
            spell_id: str = "service-spell-id",
    ) -> None:
        """
        Initialize call-shape benchmark state.

        Args:
            preload_cache:
                When True, cache-hit path is used for all timed calls.
            hooks_enabled:
                Hook gate state for timed calls.
            validation_required:
                Validation gate state for timed calls.
            spell_id:
                Spell id used as singleton cache key.
        """
        self._hook_flags = _HookFlags(hooks_enabled)
        self._validation_flags = _ValidationFlags(validation_required)
        self._cache: dict[str, int] = {}
        self._runtime = _RuntimeCounter()
        self._spell_id = spell_id
        if preload_cache:
            self._cache[spell_id] = 101

    def resolve_direct_once(self) -> int:
        """
        Resolve one singleton-like call using direct chained access.

        Returns:
            int: Deterministic payload with branch checksum.
        """
        branch_score = 0
        if self._hook_flags.has_meld_phase_hooks:
            branch_score += 1
        if self._validation_flags.spellbook_validation_required:
            branch_score += 1

        cached = self._cache.get(self._spell_id)
        if cached is None:
            cached = self._runtime.build_value(self._spell_id)
            self._cache[self._spell_id] = cached
        return cached + branch_score

    def resolve_alias_once(self) -> int:
        """
        Resolve one singleton-like call using local aliases.

        Returns:
            int: Deterministic payload with branch checksum.
        """
        hook_flags = self._hook_flags
        validation_flags = self._validation_flags
        cache = self._cache
        runtime = self._runtime
        spell_id = self._spell_id

        branch_score = 0
        if hook_flags.has_meld_phase_hooks:
            branch_score += 1
        if validation_flags.spellbook_validation_required:
            branch_score += 1

        cached = cache.get(spell_id)
        if cached is None:
            cached = runtime.build_value(spell_id)
            cache[spell_id] = cached
        return cached + branch_score


class _SocketKindValue:
    """
    Hold socket-kind enum-like values for row-build benchmarks.

    Contract:
        - Exposes one ``value`` field.
    """

    __slots__ = ("value",)

    def __init__(self, value: str) -> None:
        """
        Initialize socket-kind value.

        Args:
            value: Socket-kind string label.
        """
        self.value = value


class _SocketRefRow:
    """
    Hold deterministic socket-ref payload values for row-build benchmarks.

    Contract:
        - Stores node id, param path id, param name, and socket kind.
    """

    __slots__ = ("node_id", "param_path_id", "param_name", "socket_kind")

    def __init__(
            self,
            *,
            node_id: str,
            param_path_id: int,
            param_name: str,
            socket_kind: str,
    ) -> None:
        """
        Initialize one socket-ref row payload.

        Args:
            node_id: Node identifier.
            param_path_id: Path position integer.
            param_name: Parameter name label.
            socket_kind: Socket kind label.
        """
        self.node_id = node_id
        self.param_path_id = param_path_id
        self.param_name = param_name
        self.socket_kind = _SocketKindValue(socket_kind)


class _SocketShapeBench:
    """
    Model one runtime-like socket-shape row build call.

    Contract:
        - Builds tuple rows from fixed socket-ref inputs.
        - Returns deterministic checksum per call.
        - Uses no sorting; focuses on chained field-read cost.
    """

    __slots__ = ("_refs",)

    def __init__(self, *, ref_count: int) -> None:
        """
        Initialize deterministic socket-ref rows.

        Args:
            ref_count: Number of socket refs included in each call.
        """
        refs: list[_SocketRefRow] = []
        for index in range(ref_count):
            refs.append(
                _SocketRefRow(
                    node_id="n{0}".format(index % 3),
                    param_path_id=index,
                    param_name="p{0}".format(index),
                    socket_kind="normal" if (index % 2 == 0) else "optional",
                )
            )
        self._refs = refs

    def build_rows_direct_once(self) -> int:
        """
        Build one socket-shape payload with direct chained field reads.

        Returns:
            int: Deterministic checksum from payload rows.
        """
        rows: list[Tuple[Any, ...]] = []
        checksum = 0
        for socket_ref in self._refs:
            rows.append(
                (
                    socket_ref.node_id,
                    socket_ref.param_path_id,
                    socket_ref.param_name,
                    socket_ref.socket_kind.value,
                )
            )
            checksum += socket_ref.param_path_id
        return checksum + len(rows)

    def build_rows_alias_once(self) -> int:
        """
        Build one socket-shape payload with local aliased field reads.

        Returns:
            int: Deterministic checksum from payload rows.
        """
        rows: list[Tuple[Any, ...]] = []
        checksum = 0
        for socket_ref in self._refs:
            node_id = socket_ref.node_id
            param_path_id = socket_ref.param_path_id
            param_name = socket_ref.param_name
            socket_kind_value = socket_ref.socket_kind.value
            rows.append(
                (
                    node_id,
                    param_path_id,
                    param_name,
                    socket_kind_value,
                )
            )
            checksum += param_path_id
        return checksum + len(rows)


class _PointerMethodCallBench:
    """
    Benchmark one-copy accessor units for self and chained-self shapes.

    Contract:
        - Each benchmark unit performs one indexed read, one local copy, then
          returns.
        - No inner access loops are used inside the unit methods.
        - Supports one method per shape for flat and chained depths 2..4.
    """

    __slots__ = ("_shared", "_chain_root")

    def __init__(self) -> None:
        """
        Initialize shared flat and chained payload roots.
        """
        self._shared = _SharedDependencies()
        self._chain_root = _ChainRoot()

    def call_self_flat_direct_copy_once(self) -> int:
        """
        Execute one flat self direct-index + copy unit.

        Returns:
            int: Copied value.
        """
        indexed = self._shared.dep1
        copied = indexed
        return copied

    def call_self_flat_alias_copy_once(self) -> int:
        """
        Execute one flat self alias-index + copy unit.

        Returns:
            int: Copied value.
        """
        shared = self._shared
        indexed = shared.dep1
        copied = indexed
        return copied

    def call_self_chain_depth2_direct_copy_once(self) -> int:
        """
        Execute one chained self direct-index + copy unit at depth 2.

        Returns:
            int: Copied value.
        """
        indexed = self._chain_root.l2.dep1
        copied = indexed
        return copied

    def call_self_chain_depth2_alias_copy_once(self) -> int:
        """
        Execute one chained self alias-index + copy unit at depth 2.

        Returns:
            int: Copied value.
        """
        leaf = self._chain_root.l2
        indexed = leaf.dep1
        copied = indexed
        return copied

    def call_self_chain_depth3_direct_copy_once(self) -> int:
        """
        Execute one chained self direct-index + copy unit at depth 3.

        Returns:
            int: Copied value.
        """
        indexed = self._chain_root.l2.l3.dep1
        copied = indexed
        return copied

    def call_self_chain_depth3_alias_copy_once(self) -> int:
        """
        Execute one chained self alias-index + copy unit at depth 3.

        Returns:
            int: Copied value.
        """
        leaf = self._chain_root.l2.l3
        indexed = leaf.dep1
        copied = indexed
        return copied

    def call_self_chain_depth4_direct_copy_once(self) -> int:
        """
        Execute one chained self direct-index + copy unit at depth 4.

        Returns:
            int: Copied value.
        """
        indexed = self._chain_root.l2.l3.l4.dep1
        copied = indexed
        return copied

    def call_self_chain_depth4_alias_copy_once(self) -> int:
        """
        Execute one chained self alias-index + copy unit at depth 4.

        Returns:
            int: Copied value.
        """
        leaf = self._chain_root.l2.l3.l4
        indexed = leaf.dep1
        copied = indexed
        return copied


def _call_param_flat_direct_copy_once(
        shared: _SharedDependencies,
) -> int:
    """
    Execute one flat param direct-index + copy unit.

    Args:
        shared: Flat parameter payload.

    Returns:
        int: Copied value.
    """
    indexed = shared.dep1
    copied = indexed
    return copied


def _call_param_flat_alias_copy_once(
        shared: _SharedDependencies,
) -> int:
    """
    Execute one flat param alias-index + copy unit.

    Args:
        shared: Flat parameter payload.

    Returns:
        int: Copied value.
    """
    local_shared = shared
    indexed = local_shared.dep1
    copied = indexed
    return copied


def _call_param_chain_direct_copy_once(
        chain_root: _ChainRoot,
) -> int:
    """
    Execute one chained param direct-index + copy unit at depth 2.

    Args:
        chain_root: Root parameter containing chain payloads.

    Returns:
        int: Copied value.
    """
    indexed = chain_root.l2.dep1
    copied = indexed
    return copied


def _call_param_chain_alias_copy_once(
        chain_root: _ChainRoot,
) -> int:
    """
    Execute one chained param alias-index + copy unit at depth 2.

    Args:
        chain_root: Root parameter containing chain payloads.

    Returns:
        int: Copied value.
    """
    leaf = chain_root.l2
    indexed = leaf.dep1
    copied = indexed
    return copied


def _call_param_chain_depth3_direct_copy_once(chain_root: _ChainRoot) -> int:
    """
    Execute one chained param direct-index + copy unit at depth 3.

    Args:
        chain_root: Root parameter containing chain payloads.

    Returns:
        int: Copied value.
    """
    indexed = chain_root.l2.l3.dep1
    copied = indexed
    return copied


def _call_param_chain_depth3_alias_copy_once(chain_root: _ChainRoot) -> int:
    """
    Execute one chained param alias-index + copy unit at depth 3.

    Args:
        chain_root: Root parameter containing chain payloads.

    Returns:
        int: Copied value.
    """
    leaf = chain_root.l2.l3
    indexed = leaf.dep1
    copied = indexed
    return copied


def _call_param_chain_depth4_direct_copy_once(chain_root: _ChainRoot) -> int:
    """
    Execute one chained param direct-index + copy unit at depth 4.

    Args:
        chain_root: Root parameter containing chain payloads.

    Returns:
        int: Copied value.
    """
    indexed = chain_root.l2.l3.l4.dep1
    copied = indexed
    return copied


def _call_param_chain_depth4_alias_copy_once(chain_root: _ChainRoot) -> int:
    """
    Execute one chained param alias-index + copy unit at depth 4.

    Args:
        chain_root: Root parameter containing chain payloads.

    Returns:
        int: Copied value.
    """
    leaf = chain_root.l2.l3.l4
    indexed = leaf.dep1
    copied = indexed
    return copied


def _measure_call_only_loop_ns(
        *,
        fn: Callable[..., int],
        args: Tuple[Any, ...],
        warmup: int,
        iterations: int,
) -> int:
    """
    Measure call-only loop cost for a one-unit benchmark method.

    Args:
        fn: Callable benchmark unit.
        args: Positional arguments passed to ``fn``.
        warmup: Warmup invocation count before the timed loop.
        iterations: Timed invocation count.

    Returns:
        int: Elapsed nanoseconds for the timed loop only.
    """
    for _ in range(warmup):
        fn(*args)
    start_ns = time.perf_counter_ns()
    for _ in range(iterations):
        fn(*args)
    end_ns = time.perf_counter_ns()
    return end_ns - start_ns


def _average_call_only_loop_ns(
        *,
        fn: Callable[..., int],
        args: Tuple[Any, ...],
        warmup: int,
        iterations: int,
        repeats: int,
) -> float:
    """
    Measure averaged call-only loop cost.

    Args:
        fn: Callable benchmark unit.
        args: Positional arguments passed to ``fn``.
        warmup: Warmup invocation count before each timed repeat.
        iterations: Timed invocation count per repeat.
        repeats: Number of timed repeats.

    Returns:
        float: Average elapsed nanoseconds across repeats.
    """
    elapsed_runs: List[int] = []
    for _ in range(repeats):
        elapsed_runs.append(
            _measure_call_only_loop_ns(
                fn=fn,
                args=args,
                warmup=warmup,
                iterations=iterations,
            )
        )
    return sum(elapsed_runs) / float(repeats)


def _median(values: List[float]) -> float:
    """
    Return the median for a non-empty numeric sample list.

    Args:
        values: Numeric samples.

    Returns:
        float: Median sample value, or 0.0 for empty input.
    """
    if not values:
        return 0.0
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def _paired_order_call_only_avg_ns(
        *,
        direct_fn: Callable[..., int],
        direct_args: Tuple[Any, ...],
        alias_fn: Callable[..., int],
        alias_args: Tuple[Any, ...],
        warmup: int,
        iterations: int,
        pair_repeats: int,
) -> Tuple[float, float, float]:
    """
    Measure direct vs alias with paired alternating run order.

    Contract:
        - Executes one direct and one alias run per pair.
        - Alternates run order each pair to reduce fixed-order bias.
        - Returns average totals and median alias-minus-direct delta per iter.

    Args:
        direct_fn: Direct-access benchmark callable.
        direct_args: Positional args for ``direct_fn``.
        alias_fn: Alias-access benchmark callable.
        alias_args: Positional args for ``alias_fn``.
        warmup: Warmup invocation count before each timed run.
        iterations: Timed invocation count per run.
        pair_repeats: Number of direct/alias pairs.

    Returns:
        Tuple[float, float, float]:
            - direct average total elapsed ns
            - alias average total elapsed ns
            - median alias-minus-direct delta ns/iter
    """
    direct_runs_ns: List[int] = []
    alias_runs_ns: List[int] = []
    per_pair_delta_ns_per_iter: List[float] = []

    for pair_index in range(pair_repeats):
        if pair_index % 2 == 0:
            direct_elapsed_ns = _measure_call_only_loop_ns(
                fn=direct_fn,
                args=direct_args,
                warmup=warmup,
                iterations=iterations,
            )
            alias_elapsed_ns = _measure_call_only_loop_ns(
                fn=alias_fn,
                args=alias_args,
                warmup=warmup,
                iterations=iterations,
            )
        else:
            alias_elapsed_ns = _measure_call_only_loop_ns(
                fn=alias_fn,
                args=alias_args,
                warmup=warmup,
                iterations=iterations,
            )
            direct_elapsed_ns = _measure_call_only_loop_ns(
                fn=direct_fn,
                args=direct_args,
                warmup=warmup,
                iterations=iterations,
            )

        direct_runs_ns.append(direct_elapsed_ns)
        alias_runs_ns.append(alias_elapsed_ns)
        per_pair_delta_ns_per_iter.append(
            (alias_elapsed_ns - direct_elapsed_ns) / float(iterations)
        )

    return (
        sum(direct_runs_ns) / float(pair_repeats),
        sum(alias_runs_ns) / float(pair_repeats),
        _median(per_pair_delta_ns_per_iter),
    )


def _aa_noise_floor_ns_per_iter(
        *,
        fn: Callable[..., int],
        args: Tuple[Any, ...],
        warmup: int,
        iterations: int,
        pair_repeats: int,
) -> float:
    """
    Measure A/A same-callable noise floor in ns per iteration.

    Contract:
        - Runs the same callable twice per pair.
        - Reports median absolute delta ns/iter across pairs.

    Args:
        fn: Benchmark callable used for both A/A runs.
        args: Positional args for ``fn``.
        warmup: Warmup invocation count before each timed run.
        iterations: Timed invocation count per run.
        pair_repeats: Number of A/A pairs.

    Returns:
        float: Median absolute A/A delta in ns per iteration.
    """
    absolute_deltas_ns_per_iter: List[float] = []
    for _ in range(pair_repeats):
        first_elapsed_ns = _measure_call_only_loop_ns(
            fn=fn,
            args=args,
            warmup=warmup,
            iterations=iterations,
        )
        second_elapsed_ns = _measure_call_only_loop_ns(
            fn=fn,
            args=args,
            warmup=warmup,
            iterations=iterations,
        )
        absolute_deltas_ns_per_iter.append(
            abs(second_elapsed_ns - first_elapsed_ns) / float(iterations)
        )
    return _median(absolute_deltas_ns_per_iter)


def _measure_ns(fn: Callable[..., int], *args: Any, **kwargs: Any) -> Tuple[int, int]:
    """
    Measure one callable execution in nanoseconds.

    Args:
        fn: Callable to execute.
        *args: Positional args passed to fn.
        **kwargs: Keyword args passed to fn.

    Returns:
        Tuple[int, int]: (elapsed_ns, fn_result).
    """
    start_ns = time.perf_counter_ns()
    result = fn(*args, **kwargs)
    end_ns = time.perf_counter_ns()
    return end_ns - start_ns, result


def _measure_invoke_loop_ns(
        *,
        fn: Callable[[], int],
        warmup: int,
        iterations: int,
) -> Tuple[int, int]:
    """
    Measure per-call invocation cost over a fixed loop.

    Args:
        fn: Zero-argument callable invoked once per iteration.
        warmup: Warmup invocation count before timed loop.
        iterations: Timed invocation count.

    Returns:
        Tuple[int, int]: (elapsed_ns, checksum_across_calls).
    """
    for _ in range(warmup):
        fn()
    checksum = 0
    start_ns = time.perf_counter_ns()
    for _ in range(iterations):
        checksum += fn()
    end_ns = time.perf_counter_ns()
    return end_ns - start_ns, checksum


def _average_invoke_loop_ns(
        *,
        fn: Callable[[], int],
        warmup: int,
        iterations: int,
        repeats: int,
) -> Tuple[float, int]:
    """
    Measure averaged per-call invocation loop cost.

    Args:
        fn: Zero-argument callable invoked once per iteration.
        warmup: Warmup invocation count before each timed repeat.
        iterations: Timed invocation count per repeat.
        repeats: Number of timed repeats.

    Returns:
        Tuple[float, int]: (average_total_ns, final_checksum).
    """
    elapsed_runs: List[int] = []
    final_checksum = 0
    for _ in range(repeats):
        elapsed_ns, checksum = _measure_invoke_loop_ns(
            fn=fn,
            warmup=warmup,
            iterations=iterations,
        )
        elapsed_runs.append(elapsed_ns)
        final_checksum = checksum
    return sum(elapsed_runs) / float(repeats), final_checksum


def _average_mode_ns(
        *,
        owner: _Owner,
        mode: str,
        iterations: int,
        access_count: int,
        repeats: int,
) -> Tuple[float, int]:
    """
    Measure average elapsed nanoseconds for one mode.

    Args:
        owner: Benchmark owner object.
        mode: Either ``"direct"`` or ``"alias"``.
        iterations: Loop iterations per run.
        access_count: Number of dependency accesses per iteration.
        repeats: Number of repeated timed runs to average.

    Returns:
        Tuple[float, int]: (average_total_ns, final_checksum_result).
    """
    elapsed_runs: List[int] = []
    final_result = 0
    for _ in range(repeats):
        if mode == "direct":
            elapsed_ns, result = _measure_ns(
                owner.run_direct,
                iterations=iterations,
                access_count=access_count,
            )
        elif mode == "alias":
            elapsed_ns, result = _measure_ns(
                owner.run_alias,
                iterations=iterations,
                access_count=access_count,
            )
        else:
            raise ValueError("mode must be either 'direct' or 'alias'.")
        elapsed_runs.append(elapsed_ns)
        final_result = result
    return sum(elapsed_runs) / float(repeats), final_result


def _average_param_mode_ns(
        *,
        shared: _SharedDependencies,
        mode: str,
        iterations: int,
        access_count: int,
        repeats: int,
) -> Tuple[float, int]:
    """
    Measure average elapsed nanoseconds for parameter-attribute modes.

    Args:
        shared: Dependency object passed into benchmark functions.
        mode: Either ``"direct"`` or ``"alias"``.
        iterations: Loop iterations per run.
        access_count: Number of dependency accesses per iteration.
        repeats: Number of repeated timed runs to average.

    Returns:
        Tuple[float, int]: (average_total_ns, final_checksum_result).
    """
    elapsed_runs: List[int] = []
    final_result = 0
    for _ in range(repeats):
        if mode == "direct":
            elapsed_ns, result = _measure_ns(
                _run_param_direct,
                shared=shared,
                iterations=iterations,
                access_count=access_count,
            )
        elif mode == "alias":
            elapsed_ns, result = _measure_ns(
                _run_param_alias,
                shared=shared,
                iterations=iterations,
                access_count=access_count,
            )
        else:
            raise ValueError("mode must be either 'direct' or 'alias'.")
        elapsed_runs.append(elapsed_ns)
        final_result = result
    return sum(elapsed_runs) / float(repeats), final_result


def _average_chain_self_mode_ns(
        *,
        owner: _OwnerWithChain,
        mode: str,
        iterations: int,
        access_count: int,
        depth: int,
        repeats: int,
) -> Tuple[float, int]:
    """
    Measure average elapsed nanoseconds for chained self-attribute modes.

    Args:
        owner: Benchmark owner object.
        mode: Either ``"direct"`` or ``"alias"``.
        iterations: Loop iterations per run.
        access_count: Number of dependency accesses per iteration.
        depth: Chain depth to resolve (2, 3, or 4).
        repeats: Number of repeated timed runs to average.

    Returns:
        Tuple[float, int]: (average_total_ns, final_checksum_result).
    """
    elapsed_runs: List[int] = []
    final_result = 0
    for _ in range(repeats):
        if mode == "direct":
            elapsed_ns, result = _measure_ns(
                owner.run_direct_chain,
                iterations=iterations,
                access_count=access_count,
                depth=depth,
            )
        elif mode == "alias":
            elapsed_ns, result = _measure_ns(
                owner.run_alias_chain,
                iterations=iterations,
                access_count=access_count,
                depth=depth,
            )
        else:
            raise ValueError("mode must be either 'direct' or 'alias'.")
        elapsed_runs.append(elapsed_ns)
        final_result = result
    return sum(elapsed_runs) / float(repeats), final_result


def _average_chain_param_mode_ns(
        *,
        chain_root: _ChainRoot,
        mode: str,
        iterations: int,
        access_count: int,
        depth: int,
        repeats: int,
) -> Tuple[float, int]:
    """
    Measure average elapsed nanoseconds for chained parameter-attribute modes.

    Args:
        chain_root: Root object passed into benchmark functions.
        mode: Either ``"direct"`` or ``"alias"``.
        iterations: Loop iterations per run.
        access_count: Number of dependency accesses per iteration.
        depth: Chain depth to resolve (2, 3, or 4).
        repeats: Number of repeated timed runs to average.

    Returns:
        Tuple[float, int]: (average_total_ns, final_checksum_result).
    """
    elapsed_runs: List[int] = []
    final_result = 0
    for _ in range(repeats):
        if mode == "direct":
            elapsed_ns, result = _measure_ns(
                _run_param_chain_direct,
                chain_root=chain_root,
                iterations=iterations,
                access_count=access_count,
                depth=depth,
            )
        elif mode == "alias":
            elapsed_ns, result = _measure_ns(
                _run_param_chain_alias,
                chain_root=chain_root,
                iterations=iterations,
                access_count=access_count,
                depth=depth,
            )
        else:
            raise ValueError("mode must be either 'direct' or 'alias'.")
        elapsed_runs.append(elapsed_ns)
        final_result = result
    return sum(elapsed_runs) / float(repeats), final_result


def _expected_checksum(*, iterations: int, access_count: int) -> int:
    """
    Return expected checksum for correctness validation.

    Args:
        iterations: Loop iterations to execute.
        access_count: Number of dependency fields used per iteration.

    Returns:
        int: Expected deterministic checksum value.
    """
    if access_count == 1:
        return iterations * 1
    if access_count == 2:
        return iterations * (1 + 2)
    if access_count == 3:
        return iterations * (1 + 2 + 3)
    if access_count == 4:
        return iterations * (1 + 2 + 3 + 4)
    raise ValueError("access_count must be between 1 and 4.")


def test_local_alias_vs_direct_attribute_access_perf() -> None:
    """
    Compare local aliasing versus direct ``self`` attribute access.

    Contract:
        - Uses exactly 1,000,000 iterations per scenario.
        - Measures access-count scenarios 1, 2, 3, and 4.
        - Prints average total time and average ns/iteration for each mode.
        - Validates checksums for both modes in every scenario.
    """
    iterations = 1_000_000
    repeats = 5
    owner = _Owner(_SharedDependencies())

    print(
        "[alias-vs-direct] iterations={0}, repeats={1}".format(
            iterations,
            repeats,
        )
    )
    print(
        "[alias-vs-direct] columns: accesses | direct_avg_total_ns | "
        "direct_avg_ns_per_iter | alias_avg_total_ns | alias_avg_ns_per_iter | "
        "alias_over_direct_ratio"
    )

    rows_emitted = 0
    for access_count in (1, 2, 3, 4):
        direct_avg_ns, direct_result = _average_mode_ns(
            owner=owner,
            mode="direct",
            iterations=iterations,
            access_count=access_count,
            repeats=repeats,
        )
        alias_avg_ns, alias_result = _average_mode_ns(
            owner=owner,
            mode="alias",
            iterations=iterations,
            access_count=access_count,
            repeats=repeats,
        )
        expected = _expected_checksum(
            iterations=iterations,
            access_count=access_count,
        )
        assert direct_result == expected
        assert alias_result == expected

        direct_avg_per_iter = direct_avg_ns / float(iterations)
        alias_avg_per_iter = alias_avg_ns / float(iterations)
        ratio = alias_avg_ns / direct_avg_ns
        print(
            "[alias-vs-direct] accesses={0} | direct_total_ns={1:.0f} | "
            "direct_ns_per_iter={2:.6f} | alias_total_ns={3:.0f} | "
            "alias_ns_per_iter={4:.6f} | ratio={5:.6f}".format(
                access_count,
                direct_avg_ns,
                direct_avg_per_iter,
                alias_avg_ns,
                alias_avg_per_iter,
                ratio,
            )
        )
        rows_emitted += 1

    assert rows_emitted == 4


def test_local_alias_vs_direct_parameter_attr_access_perf() -> None:
    """
    Compare local aliasing versus direct parameter-attribute access.

    Contract:
        - Uses exactly 1,000,000 iterations per scenario.
        - Measures access-count scenarios 1, 2, 3, and 4.
        - Prints average total time and average ns/iteration for each mode.
        - Validates checksums for both modes in every scenario.
    """
    iterations = 1_000_000
    repeats = 5
    shared = _SharedDependencies()

    print(
        "[param-alias-vs-direct] iterations={0}, repeats={1}".format(
            iterations,
            repeats,
        )
    )
    print(
        "[param-alias-vs-direct] columns: accesses | direct_avg_total_ns | "
        "direct_avg_ns_per_iter | alias_avg_total_ns | alias_avg_ns_per_iter | "
        "alias_over_direct_ratio"
    )

    rows_emitted = 0
    for access_count in (1, 2, 3, 4):
        direct_avg_ns, direct_result = _average_param_mode_ns(
            shared=shared,
            mode="direct",
            iterations=iterations,
            access_count=access_count,
            repeats=repeats,
        )
        alias_avg_ns, alias_result = _average_param_mode_ns(
            shared=shared,
            mode="alias",
            iterations=iterations,
            access_count=access_count,
            repeats=repeats,
        )
        expected = _expected_checksum(
            iterations=iterations,
            access_count=access_count,
        )
        assert direct_result == expected
        assert alias_result == expected

        direct_avg_per_iter = direct_avg_ns / float(iterations)
        alias_avg_per_iter = alias_avg_ns / float(iterations)
        ratio = alias_avg_ns / direct_avg_ns
        print(
            "[param-alias-vs-direct] accesses={0} | direct_total_ns={1:.0f} | "
            "direct_ns_per_iter={2:.6f} | alias_total_ns={3:.0f} | "
            "alias_ns_per_iter={4:.6f} | ratio={5:.6f}".format(
                access_count,
                direct_avg_ns,
                direct_avg_per_iter,
                alias_avg_ns,
                alias_avg_per_iter,
                ratio,
            )
        )
        rows_emitted += 1

    assert rows_emitted == 4


def test_local_alias_vs_direct_self_chained_attr_access_perf() -> None:
    """
    Compare direct versus aliased chained self-attribute access (depth 2..4).

    Contract:
        - Uses exactly 1,000,000 iterations per scenario.
        - Measures chain depth 2, 3, and 4.
        - Measures access-count scenarios 1, 2, 3, and 4.
        - Prints averaged timing rows for each (depth, access_count) pair.
        - Validates checksums for both modes in every scenario.
    """
    iterations = 1_000_000
    repeats = 3
    owner = _OwnerWithChain(_ChainRoot())

    print(
        "[self-chain-alias-vs-direct] iterations={0}, repeats={1}".format(
            iterations,
            repeats,
        )
    )
    print(
        "[self-chain-alias-vs-direct] columns: depth | accesses | "
        "direct_avg_total_ns | direct_avg_ns_per_iter | alias_avg_total_ns | "
        "alias_avg_ns_per_iter | alias_over_direct_ratio"
    )

    rows_emitted = 0
    for depth in (2, 3, 4):
        for access_count in (1, 2, 3, 4):
            direct_avg_ns, direct_result = _average_chain_self_mode_ns(
                owner=owner,
                mode="direct",
                iterations=iterations,
                access_count=access_count,
                depth=depth,
                repeats=repeats,
            )
            alias_avg_ns, alias_result = _average_chain_self_mode_ns(
                owner=owner,
                mode="alias",
                iterations=iterations,
                access_count=access_count,
                depth=depth,
                repeats=repeats,
            )
            expected = _expected_checksum(
                iterations=iterations,
                access_count=access_count,
            )
            assert direct_result == expected
            assert alias_result == expected

            direct_avg_per_iter = direct_avg_ns / float(iterations)
            alias_avg_per_iter = alias_avg_ns / float(iterations)
            ratio = alias_avg_ns / direct_avg_ns
            print(
                "[self-chain-alias-vs-direct] depth={0} | accesses={1} | "
                "direct_total_ns={2:.0f} | direct_ns_per_iter={3:.6f} | "
                "alias_total_ns={4:.0f} | alias_ns_per_iter={5:.6f} | "
                "ratio={6:.6f}".format(
                    depth,
                    access_count,
                    direct_avg_ns,
                    direct_avg_per_iter,
                    alias_avg_ns,
                    alias_avg_per_iter,
                    ratio,
                )
            )
            rows_emitted += 1

    assert rows_emitted == 12


def test_local_alias_vs_direct_parameter_chained_attr_access_perf() -> None:
    """
    Compare direct versus aliased chained parameter-attribute access (depth 2..4).

    Contract:
        - Uses exactly 1,000,000 iterations per scenario.
        - Measures chain depth 2, 3, and 4.
        - Measures access-count scenarios 1, 2, 3, and 4.
        - Prints averaged timing rows for each (depth, access_count) pair.
        - Validates checksums for both modes in every scenario.
    """
    iterations = 1_000_000
    repeats = 3
    chain_root = _ChainRoot()

    print(
        "[param-chain-alias-vs-direct] iterations={0}, repeats={1}".format(
            iterations,
            repeats,
        )
    )
    print(
        "[param-chain-alias-vs-direct] columns: depth | accesses | "
        "direct_avg_total_ns | direct_avg_ns_per_iter | alias_avg_total_ns | "
        "alias_avg_ns_per_iter | alias_over_direct_ratio"
    )

    rows_emitted = 0
    for depth in (2, 3, 4):
        for access_count in (1, 2, 3, 4):
            direct_avg_ns, direct_result = _average_chain_param_mode_ns(
                chain_root=chain_root,
                mode="direct",
                iterations=iterations,
                access_count=access_count,
                depth=depth,
                repeats=repeats,
            )
            alias_avg_ns, alias_result = _average_chain_param_mode_ns(
                chain_root=chain_root,
                mode="alias",
                iterations=iterations,
                access_count=access_count,
                depth=depth,
                repeats=repeats,
            )
            expected = _expected_checksum(
                iterations=iterations,
                access_count=access_count,
            )
            assert direct_result == expected
            assert alias_result == expected

            direct_avg_per_iter = direct_avg_ns / float(iterations)
            alias_avg_per_iter = alias_avg_ns / float(iterations)
            ratio = alias_avg_ns / direct_avg_ns
            print(
                "[param-chain-alias-vs-direct] depth={0} | accesses={1} | "
                "direct_total_ns={2:.0f} | direct_ns_per_iter={3:.6f} | "
                "alias_total_ns={4:.0f} | alias_ns_per_iter={5:.6f} | "
                "ratio={6:.6f}".format(
                    depth,
                    access_count,
                    direct_avg_ns,
                    direct_avg_per_iter,
                    alias_avg_ns,
                    alias_avg_per_iter,
                    ratio,
                )
            )
            rows_emitted += 1

    assert rows_emitted == 12


def test_local_alias_vs_direct_realworld_singleton_call_shape_perf() -> None:
    """
    Compare direct versus alias access for a singleton-hit call shape.

    Contract:
        - Models one real-world resolve call per iteration.
        - Preloads cache so timed calls run pure singleton-hit path.
        - Includes branch checks plus one cache read.
        - Uses 1,000,000 timed calls to stabilize per-call overhead.
    """
    iterations = 1_000_000
    warmup = 50_000
    repeats = 5
    direct_owner = _SingletonCallShapeBench(
        preload_cache=True,
        hooks_enabled=False,
        validation_required=False,
    )
    alias_owner = _SingletonCallShapeBench(
        preload_cache=True,
        hooks_enabled=False,
        validation_required=False,
    )

    direct_avg_ns, direct_checksum = _average_invoke_loop_ns(
        fn=direct_owner.resolve_direct_once,
        warmup=warmup,
        iterations=iterations,
        repeats=repeats,
    )
    alias_avg_ns, alias_checksum = _average_invoke_loop_ns(
        fn=alias_owner.resolve_alias_once,
        warmup=warmup,
        iterations=iterations,
        repeats=repeats,
    )

    assert direct_owner._runtime.counter == 0
    assert alias_owner._runtime.counter == 0
    assert direct_checksum == alias_checksum

    direct_avg_per_iter = direct_avg_ns / float(iterations)
    alias_avg_per_iter = alias_avg_ns / float(iterations)
    ratio = alias_avg_ns / direct_avg_ns
    print(
        "[realworld-singleton-hit] iterations={0}, warmup={1}, repeats={2} | "
        "direct_total_ns={3:.0f} | direct_ns_per_iter={4:.6f} | "
        "alias_total_ns={5:.0f} | alias_ns_per_iter={6:.6f} | ratio={7:.6f}".format(
            iterations,
            warmup,
            repeats,
            direct_avg_ns,
            direct_avg_per_iter,
            alias_avg_ns,
            alias_avg_per_iter,
            ratio,
        )
    )


def test_local_alias_vs_direct_realworld_row_build_call_shape_perf() -> None:
    """
    Compare direct versus alias access for runtime-like row build calls.

    Contract:
        - Models one row-build call per iteration over fixed socket refs.
        - Focuses on repeated chained field extraction per call.
        - Uses 250,000 timed calls with warmup for stable measurements.
    """
    iterations = 250_000
    warmup = 25_000
    repeats = 5
    direct_bench = _SocketShapeBench(ref_count=8)
    alias_bench = _SocketShapeBench(ref_count=8)

    direct_avg_ns, direct_checksum = _average_invoke_loop_ns(
        fn=direct_bench.build_rows_direct_once,
        warmup=warmup,
        iterations=iterations,
        repeats=repeats,
    )
    alias_avg_ns, alias_checksum = _average_invoke_loop_ns(
        fn=alias_bench.build_rows_alias_once,
        warmup=warmup,
        iterations=iterations,
        repeats=repeats,
    )

    assert direct_checksum == alias_checksum

    direct_avg_per_iter = direct_avg_ns / float(iterations)
    alias_avg_per_iter = alias_avg_ns / float(iterations)
    ratio = alias_avg_ns / direct_avg_ns
    print(
        "[realworld-row-build] iterations={0}, warmup={1}, repeats={2} | "
        "direct_total_ns={3:.0f} | direct_ns_per_iter={4:.6f} | "
        "alias_total_ns={5:.0f} | alias_ns_per_iter={6:.6f} | ratio={7:.6f}".format(
            iterations,
            warmup,
            repeats,
            direct_avg_ns,
            direct_avg_per_iter,
            alias_avg_ns,
            alias_avg_per_iter,
            ratio,
        )
    )


def test_pointer_call_only_self_flat_alias_vs_direct_perf() -> None:
    """
    Compare self-flat copy-unit overhead.

    Contract:
        - Timed work per invocation is: index -> copy -> return.
        - Uses fixed warmup and repeat counts.
    """
    iterations = 1_000_000
    warmup = 50_000
    pair_repeats = 8
    bench = _PointerMethodCallBench()
    print(
        "[pointer-self-flat] iterations={0}, warmup={1}, pair_repeats={2}".format(
            iterations,
            warmup,
            pair_repeats,
        )
    )
    print(
        "[pointer-self-flat] columns: unit | direct_avg_total_ns | "
        "direct_avg_ns_per_iter | alias_avg_total_ns | alias_avg_ns_per_iter | "
        "alias_over_direct_ratio | median_pair_delta_ns_per_iter | "
        "aa_noise_floor_ns_per_iter"
    )
    assert bench.call_self_flat_direct_copy_once() == 1
    assert bench.call_self_flat_alias_copy_once() == 1

    direct_avg_ns, alias_avg_ns, median_pair_delta_ns_per_iter = (
        _paired_order_call_only_avg_ns(
            direct_fn=bench.call_self_flat_direct_copy_once,
            direct_args=(),
            alias_fn=bench.call_self_flat_alias_copy_once,
            alias_args=(),
            warmup=warmup,
            iterations=iterations,
            pair_repeats=pair_repeats,
        )
    )
    aa_noise_floor_ns_per_iter = _aa_noise_floor_ns_per_iter(
        fn=bench.call_self_flat_direct_copy_once,
        args=(),
        warmup=warmup,
        iterations=iterations,
        pair_repeats=pair_repeats,
    )
    direct_avg_per_iter = direct_avg_ns / float(iterations)
    alias_avg_per_iter = alias_avg_ns / float(iterations)
    ratio = alias_avg_ns / direct_avg_ns
    print(
        "[pointer-self-flat] unit=copy_once | direct_total_ns={0:.0f} | "
        "direct_ns_per_iter={1:.6f} | alias_total_ns={2:.0f} | "
        "alias_ns_per_iter={3:.6f} | ratio={4:.6f} | "
        "median_pair_delta_ns_per_iter={5:.6f} | aa_noise_floor_ns_per_iter={6:.6f}".format(
            direct_avg_ns,
            direct_avg_per_iter,
            alias_avg_ns,
            alias_avg_per_iter,
            ratio,
            median_pair_delta_ns_per_iter,
            aa_noise_floor_ns_per_iter,
        )
    )


def test_pointer_call_only_param_flat_alias_vs_direct_perf() -> None:
    """
    Compare param-flat copy-unit overhead.

    Contract:
        - Timed work per invocation is: index -> copy -> return.
        - Uses fixed warmup and repeat counts.
    """
    iterations = 1_000_000
    warmup = 50_000
    pair_repeats = 8
    shared = _SharedDependencies()
    print(
        "[pointer-param-flat] iterations={0}, warmup={1}, pair_repeats={2}".format(
            iterations,
            warmup,
            pair_repeats,
        )
    )
    print(
        "[pointer-param-flat] columns: unit | direct_avg_total_ns | "
        "direct_avg_ns_per_iter | alias_avg_total_ns | alias_avg_ns_per_iter | "
        "alias_over_direct_ratio | median_pair_delta_ns_per_iter | "
        "aa_noise_floor_ns_per_iter"
    )
    assert _call_param_flat_direct_copy_once(shared) == 1
    assert _call_param_flat_alias_copy_once(shared) == 1

    direct_avg_ns, alias_avg_ns, median_pair_delta_ns_per_iter = (
        _paired_order_call_only_avg_ns(
            direct_fn=_call_param_flat_direct_copy_once,
            direct_args=(shared,),
            alias_fn=_call_param_flat_alias_copy_once,
            alias_args=(shared,),
            warmup=warmup,
            iterations=iterations,
            pair_repeats=pair_repeats,
        )
    )
    aa_noise_floor_ns_per_iter = _aa_noise_floor_ns_per_iter(
        fn=_call_param_flat_direct_copy_once,
        args=(shared,),
        warmup=warmup,
        iterations=iterations,
        pair_repeats=pair_repeats,
    )
    direct_avg_per_iter = direct_avg_ns / float(iterations)
    alias_avg_per_iter = alias_avg_ns / float(iterations)
    ratio = alias_avg_ns / direct_avg_ns
    print(
        "[pointer-param-flat] unit=copy_once | direct_total_ns={0:.0f} | "
        "direct_ns_per_iter={1:.6f} | alias_total_ns={2:.0f} | "
        "alias_ns_per_iter={3:.6f} | ratio={4:.6f} | "
        "median_pair_delta_ns_per_iter={5:.6f} | aa_noise_floor_ns_per_iter={6:.6f}".format(
            direct_avg_ns,
            direct_avg_per_iter,
            alias_avg_ns,
            alias_avg_per_iter,
            ratio,
            median_pair_delta_ns_per_iter,
            aa_noise_floor_ns_per_iter,
        )
    )


def test_pointer_call_only_self_chain_alias_vs_direct_perf() -> None:
    """
    Compare self-chain copy-unit overhead across depths.

    Contract:
        - Timed work per invocation is: index -> copy -> return.
        - Uses depth matrix 2..4.
        - Uses fixed warmup and repeat counts.
    """
    iterations = 1_000_000
    warmup = 50_000
    pair_repeats = 8
    bench = _PointerMethodCallBench()
    print(
        "[pointer-self-chain] iterations={0}, warmup={1}, pair_repeats={2}".format(
            iterations,
            warmup,
            pair_repeats,
        )
    )
    print(
        "[pointer-self-chain] columns: depth | direct_avg_total_ns | "
        "direct_avg_ns_per_iter | alias_avg_total_ns | alias_avg_ns_per_iter | "
        "alias_over_direct_ratio | median_pair_delta_ns_per_iter | "
        "aa_noise_floor_ns_per_iter"
    )
    cases: Tuple[
        Tuple[str, Callable[[], int], Callable[[], int]],
        ...,
    ] = (
        (
            "2",
            bench.call_self_chain_depth2_direct_copy_once,
            bench.call_self_chain_depth2_alias_copy_once,
        ),
        (
            "3",
            bench.call_self_chain_depth3_direct_copy_once,
            bench.call_self_chain_depth3_alias_copy_once,
        ),
        (
            "4",
            bench.call_self_chain_depth4_direct_copy_once,
            bench.call_self_chain_depth4_alias_copy_once,
        ),
    )
    rows_emitted = 0
    for depth, direct_fn, alias_fn in cases:
        assert direct_fn() == 1
        assert alias_fn() == 1
        direct_avg_ns, alias_avg_ns, median_pair_delta_ns_per_iter = (
            _paired_order_call_only_avg_ns(
                direct_fn=direct_fn,
                direct_args=(),
                alias_fn=alias_fn,
                alias_args=(),
                warmup=warmup,
                iterations=iterations,
                pair_repeats=pair_repeats,
            )
        )
        aa_noise_floor_ns_per_iter = _aa_noise_floor_ns_per_iter(
            fn=direct_fn,
            args=(),
            warmup=warmup,
            iterations=iterations,
            pair_repeats=pair_repeats,
        )
        direct_avg_per_iter = direct_avg_ns / float(iterations)
        alias_avg_per_iter = alias_avg_ns / float(iterations)
        ratio = alias_avg_ns / direct_avg_ns
        print(
            "[pointer-self-chain] depth={0} | direct_total_ns={1:.0f} | "
            "direct_ns_per_iter={2:.6f} | alias_total_ns={3:.0f} | "
            "alias_ns_per_iter={4:.6f} | ratio={5:.6f} | "
            "median_pair_delta_ns_per_iter={6:.6f} | aa_noise_floor_ns_per_iter={7:.6f}".format(
                depth,
                direct_avg_ns,
                direct_avg_per_iter,
                alias_avg_ns,
                alias_avg_per_iter,
                ratio,
                median_pair_delta_ns_per_iter,
                aa_noise_floor_ns_per_iter,
            )
        )
        rows_emitted += 1
    assert rows_emitted == 3


def test_pointer_call_only_param_chain_alias_vs_direct_perf() -> None:
    """
    Compare param-chain copy-unit overhead across depths.

    Contract:
        - Timed work per invocation is: index -> copy -> return.
        - Uses depth matrix 2..4.
        - Uses fixed warmup and repeat counts.
    """
    iterations = 1_000_000
    warmup = 50_000
    pair_repeats = 8
    chain_root = _ChainRoot()
    print(
        "[pointer-param-chain] iterations={0}, warmup={1}, pair_repeats={2}".format(
            iterations,
            warmup,
            pair_repeats,
        )
    )
    print(
        "[pointer-param-chain] columns: depth | direct_avg_total_ns | "
        "direct_avg_ns_per_iter | alias_avg_total_ns | alias_avg_ns_per_iter | "
        "alias_over_direct_ratio | median_pair_delta_ns_per_iter | "
        "aa_noise_floor_ns_per_iter"
    )
    cases: Tuple[
        Tuple[str, Callable[[_ChainRoot], int], Callable[[_ChainRoot], int]],
        ...,
    ] = (
        ("2", _call_param_chain_direct_copy_once, _call_param_chain_alias_copy_once),
        (
            "3",
            _call_param_chain_depth3_direct_copy_once,
            _call_param_chain_depth3_alias_copy_once,
        ),
        (
            "4",
            _call_param_chain_depth4_direct_copy_once,
            _call_param_chain_depth4_alias_copy_once,
        ),
    )
    rows_emitted = 0
    for depth, direct_fn, alias_fn in cases:
        assert direct_fn(chain_root) == 1
        assert alias_fn(chain_root) == 1
        direct_avg_ns, alias_avg_ns, median_pair_delta_ns_per_iter = (
            _paired_order_call_only_avg_ns(
                direct_fn=direct_fn,
                direct_args=(chain_root,),
                alias_fn=alias_fn,
                alias_args=(chain_root,),
                warmup=warmup,
                iterations=iterations,
                pair_repeats=pair_repeats,
            )
        )
        aa_noise_floor_ns_per_iter = _aa_noise_floor_ns_per_iter(
            fn=direct_fn,
            args=(chain_root,),
            warmup=warmup,
            iterations=iterations,
            pair_repeats=pair_repeats,
        )
        direct_avg_per_iter = direct_avg_ns / float(iterations)
        alias_avg_per_iter = alias_avg_ns / float(iterations)
        ratio = alias_avg_ns / direct_avg_ns
        print(
            "[pointer-param-chain] depth={0} | direct_total_ns={1:.0f} | "
            "direct_ns_per_iter={2:.6f} | alias_total_ns={3:.0f} | "
            "alias_ns_per_iter={4:.6f} | ratio={5:.6f} | "
            "median_pair_delta_ns_per_iter={6:.6f} | aa_noise_floor_ns_per_iter={7:.6f}".format(
                depth,
                direct_avg_ns,
                direct_avg_per_iter,
                alias_avg_ns,
                alias_avg_per_iter,
                ratio,
                median_pair_delta_ns_per_iter,
                aa_noise_floor_ns_per_iter,
            )
        )
        rows_emitted += 1
    assert rows_emitted == 3
