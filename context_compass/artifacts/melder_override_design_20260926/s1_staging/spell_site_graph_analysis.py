from typing import Dict, List, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable

SiteInstanceKey = Tuple[str, Optional[int]]
SiteTarget = Tuple[int, str]


class SpellSiteParam:
    """
    One constructor parameter of one construction site.

    Purpose:
        Describe a single constructor parameter of a physical site together with
        the source that supplies its value when no override applies. Every
        parameter of the constructor is present, including plain parameters with
        defaults, because every parameter is an override target today.

    Contract:
        - Immutable by convention: fields are written once in `__init__` and are
          value-typed (str, int, bool, None, tuples of int).
        - `dependency_sites` holds site indexes into the owning
          `SpellSiteGraphAnalysis.sites`; more than one entry means a collection
          parameter, in injection order. It is empty for every non-dependency
          source.
        - `source_kind` is one of "dependency", "contract", "unresolved_input",
          "override_required" or "plain".

    Registration:
        MELDER KERNEL - internal compiler value row; never user-instantiated.

    Subsystem Context:
        Row type of the Phase-9 site-graph section (`SpellSiteGraphAnalysis`).

    System Context:
        Phase 9 (artifact processor) of the conjure pipeline; consumed by override
        key resolution and, from design step S2, by the shared lowering.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. One constructor parameter of a site: name, position, kind, socket
        kind, collection/optional flags, source kind and dependency site indexes.
    """

    __slots__ = [
        "name",
        "position",
        "parameter_kind",
        "socket_kind_value",
        "is_collection",
        "is_optional",
        "source_kind",
        "contract_key",
        "dependency_sites",
    ]

    def __init__(
            self,
            *,
            name: str,
            position: int,
            parameter_kind: Optional[str],
            socket_kind_value: int,
            is_collection: bool,
            is_optional: bool,
            source_kind: str,
            contract_key: Optional[str],
            dependency_sites: Tuple[int, ...],
    ) -> None:
        """
        Build one parameter row.

        Args:
            name:
                Constructor parameter name.
            position:
                0-based position in the constructor signature, or -1 when the
                Phase-3 topology did not describe the parameter.
            parameter_kind:
                `inspect.Parameter` kind name (for example "POSITIONAL_OR_KEYWORD"),
                or None when unknown.
            socket_kind_value:
                `SocketKind` value of the Phase-3 socket.
            is_collection:
                True for a collection DI socket (the value is a list).
            is_optional:
                True when the parameter has a default.
            source_kind:
                Where the default operand comes from (see class contract).
            contract_key:
                Contract payload key when a contract payload names this parameter.
            dependency_sites:
                Site indexes that supply this parameter; empty unless
                `source_kind` is "dependency".

        Returns:
            None.
        """
        self.name = name
        self.position = position
        self.parameter_kind = parameter_kind
        self.socket_kind_value = socket_kind_value
        self.is_collection = is_collection
        self.is_optional = is_optional
        self.source_kind = source_kind
        self.contract_key = contract_key
        self.dependency_sites = dependency_sites

    def as_row(self) -> Tuple[object, ...]:
        """
        Return this parameter as one plain value tuple.

        Purpose:
            Give tests and later manifest export one deterministic value form.

        Returns:
            Tuple[object, ...]:
                (name, position, parameter_kind, socket_kind_value, is_collection,
                is_optional, source_kind, contract_key, dependency_sites).
        """
        return (
            self.name,
            self.position,
            self.parameter_kind,
            self.socket_kind_value,
            self.is_collection,
            self.is_optional,
            self.source_kind,
            self.contract_key,
            self.dependency_sites,
        )


class SpellSite:
    """
    One physical construction site of a root's graph.

    Purpose:
        Stand for one object the root's construction may build: one per Phase-9
        instance key. A shared existence is one site however many paths reach it;
        a `many` spell is one site per occurrence path.

    Contract:
        - Immutable by convention; value-typed fields only.
        - `index` equals the site's position in `SpellSiteGraphAnalysis.sites`
          (parents first; the root is index 0).
        - `shared` is True exactly when the instance key carries no path.
        - `params` lists every constructor parameter in position order.

    Registration:
        MELDER KERNEL - internal compiler value row; never user-instantiated.

    Subsystem Context:
        Row type of the Phase-9 site-graph section (`SpellSiteGraphAnalysis`).

    System Context:
        Phase 9 (artifact processor) of the conjure pipeline.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. One construction site: index, instance key, selected spell id,
        shared flag and its parameter rows.
    """

    __slots__ = [
        "index",
        "instance_key",
        "spell_id",
        "shared",
        "params",
    ]

    def __init__(
            self,
            *,
            index: int,
            instance_key: SiteInstanceKey,
            spell_id: str,
            shared: bool,
            params: Tuple[SpellSiteParam, ...],
    ) -> None:
        """
        Build one site row.

        Args:
            index:
                Position of this site in the owning section's `sites`.
            instance_key:
                Phase-9 instance key `(spell_id, path_id)`, or `(spell_id, None)`
                for a shared existence.
            spell_id:
                Selected spell id this site constructs.
            shared:
                True for a shared existence (instance key without a path).
            params:
                Parameter rows in position order.

        Returns:
            None.
        """
        self.index = index
        self.instance_key = instance_key
        self.spell_id = spell_id
        self.shared = shared
        self.params = params

    def as_row(self) -> Tuple[object, ...]:
        """
        Return this site as one plain value tuple.

        Returns:
            Tuple[object, ...]:
                (index, instance_key, spell_id, shared, parameter rows).
        """
        return (
            self.index,
            self.instance_key,
            self.spell_id,
            self.shared,
            tuple(param.as_row() for param in self.params),
        )


class SpellSiteGraphAnalysis(Cleanable):
    """
    Processor-owned site-graph section of `SpellCodegenModel`.

    Purpose:
        Hold the physical construction graph of one root without enumerating
        logical paths: one site per instance key, every constructor parameter
        with its default operand source, a parameter-name index and the number of
        logical root paths reaching each site. Override key resolution walks this
        section instead of the per-path targeting section.

    Contract:
        - `sites` is ordered parents first; the root is `sites[0]` and
          `root_site_index` is 0. Every dependency index points at a later site.
        - `path_counts[i]` is the number of logical root paths to site i (the
          root counts 1; a collection edge contributes once per member edge). It
          reproduces the socket count today's UNIQUE targeting checks.
        - `param_index[name]` lists every (site index, name) pair in site order.
        - `site_index_by_instance_key` maps instance keys to site indexes.
        - Construction validates index consistency and raises ValueError on a
          malformed section.

    Lifecycle / Cleanup:
        Owned by `SpellCodegenModel`; `cleanup()` is idempotent, clears the
        owned dicts and deletes every field.

    Registration:
        MELDER KERNEL - built by `SpellSiteGraphProcessorStrategy`; never
        user-instantiated.

    Subsystem Context:
        A processor-owned section beside `injection_shape` and
        `override_targeting_shape` in `SpellCodegenModel`.

    System Context:
        Phase 9 (artifact processor) of the conjure pipeline. Design step S1 of
        the override site-plan lowering: nothing at run time reads it yet.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Physical site graph of one root: sites parents-first, parameter
        rows, name index and logical path counts. Input to override key resolution.
    """

    __slots__ = Cleanable.__slots__ + [
        "sites",
        "root_site_index",
        "path_counts",
        "site_index_by_instance_key",
        "param_index",
        "site_count",
        "shared_site_count",
        "_params_by_target",
    ]

    def __init__(
            self,
            *,
            sites: Tuple[SpellSite, ...],
            path_counts: Tuple[int, ...],
    ) -> None:
        """
        Build one site-graph section and its lookup indexes.

        Args:
            sites:
                Site rows ordered parents first, root first.
            path_counts:
                Logical root path count per site, aligned with `sites`.

        Raises:
            ValueError:
                If `sites` is empty, a site index does not match its position,
                `path_counts` is misaligned, or a dependency index does not point
                at a later site.

        Returns:
            None.
        """
        super().__init__()
        if not sites:
            raise ValueError("SpellSiteGraphAnalysis requires at least the root site.")
        if len(path_counts) != len(sites):
            raise ValueError("path_counts must align with sites.")
        site_index_by_instance_key: Dict[SiteInstanceKey, int] = {}
        params_by_target: Dict[SiteTarget, SpellSiteParam] = {}
        index_lists: Dict[str, List[SiteTarget]] = {}
        shared_site_count = 0
        for position, site in enumerate(sites):
            if site.index != position:
                raise ValueError(
                    f"Site index {site.index} does not match its position {position}."
                )
            site_index_by_instance_key[site.instance_key] = position
            if site.shared:
                shared_site_count += 1
            for param in site.params:
                for dependency in param.dependency_sites:
                    if dependency <= position or dependency >= len(sites):
                        raise ValueError(
                            f"Site {position} parameter '{param.name}' points at "
                            f"site {dependency}; dependencies must be later sites."
                        )
                params_by_target[(position, param.name)] = param
                index_lists.setdefault(param.name, []).append((position, param.name))
        self.sites: Tuple[SpellSite, ...] = sites
        self.root_site_index: int = 0
        self.path_counts: Tuple[int, ...] = path_counts
        self.site_index_by_instance_key: Dict[SiteInstanceKey, int] = (
            site_index_by_instance_key
        )
        self.param_index: Dict[str, Tuple[SiteTarget, ...]] = {
            name: tuple(targets) for name, targets in index_lists.items()
        }
        self.site_count: int = len(sites)
        self.shared_site_count: int = shared_site_count
        self._params_by_target: Dict[SiteTarget, SpellSiteParam] = params_by_target

    def cleanup(self) -> None:
        """
        Deterministically release section-owned lookup state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self.site_index_by_instance_key.clear()
        self.param_index.clear()
        self._params_by_target.clear()
        del self.sites
        del self.root_site_index
        del self.path_counts
        del self.site_index_by_instance_key
        del self.param_index
        del self.site_count
        del self.shared_site_count
        del self._params_by_target

    def param(self, site_index: int, name: str) -> Optional[SpellSiteParam]:
        """
        Return one parameter row of one site, or None when the site has no such
        parameter.

        Args:
            site_index:
                Index into `sites`.
            name:
                Constructor parameter name.

        Returns:
            Optional[SpellSiteParam]:
                The parameter row, or None.
        """
        return self._params_by_target.get((site_index, name))
