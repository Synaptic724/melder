from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Set, Tuple

from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_site_graph_analysis import (
    SiteInstanceKey,
    SpellSite,
    SpellSiteGraphAnalysis,
    SpellSiteParam,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy import (
    SpellArtifactProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_injection_analysis import (
        SpellInjectionAnalysis,
        SpellInjectionInstanceSpec,
        SpellInjectionParamSource,
    )
    from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
        SpellCodegenModel,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )
    from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
        SpellLocalTopology,
        SpellSocketDescriptor,
    )


class SpellSiteGraphProcessorStrategy(SpellArtifactProcessorStrategy):
    """
    Fit the site-graph section of `SpellCodegenModel`.

    Purpose:
        Build the physical construction graph of the root spell - one site per
        Phase-9 instance key, every constructor parameter with its default
        operand source, and logical root path counts - so override keys can be
        resolved by walking named edges instead of enumerating logical paths.

    Contract:
        - Requires `instance_shape` and `injection_shape` (runs after
          `spell_injection_processor`).
        - Reads each site's Phase-3 local topology through the spellbook's
          `SpellSystemStates`, the same source the injection processor reads.
          A site without a topology (for example an existing-creation spell)
          takes its parameter rows from its injection sources instead.
        - Writes only `model.site_graph_shape` and cleans a superseded section.
        - Changes no other section, executor or emitted source.

    Raises:
        RuntimeError:
            When a required section is missing or a reachable instance key has
            no injection spec.

    Registration:
        MELDER KERNEL - a built-in processor strategy; not bound as a spell.

    Subsystem Context:
        One of the `artifact_processor/strategies` family. Not in the default
        processor chain since 2026-09-26: `SitePlanOverrideRuntime` calls
        `build_site_graph` at the first override meld; `process` remains for
        callers that fit the section on a model.

    System Context:
        Phase 9 (artifact processor) of the conjure pipeline; design step S1 of
        the override site-plan lowering.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-9 strategy producing `site_graph_shape`: sites per instance
        key, full parameter tables from Phase-3 topology, name index and path counts.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable processor strategy id.
        """
        return "spell_site_graph_processor"

    def process(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            model: SpellCodegenModel,
    ) -> None:
        """
        Fit the site-graph model section.

        Contract:
            - Requires `model.instance_shape` and `model.injection_shape`.
            - Publishes `model.site_graph_shape` and cleans the previous section
              when it is a different object.

        Raises:
            RuntimeError:
                When `instance_shape` or `injection_shape` is missing, or when a
                reachable instance key has no injection spec.

        Returns:
            None.
        """
        _ = artifact
        instance_shape = model.instance_shape
        if instance_shape is None:
            raise RuntimeError(
                "SpellSiteGraphProcessorStrategy requires instance_shape first."
            )
        injection_shape = model.injection_shape
        if injection_shape is None:
            raise RuntimeError(
                "SpellSiteGraphProcessorStrategy requires injection_shape first."
            )
        spell_system_states = spell._spellbook._spell_system_states
        site_graph_shape = self.build_site_graph(
            root_instance_key=tuple(instance_shape.root_instance_key),
            injection_shape=injection_shape,
            topology_for=spell_system_states.get_local_topology_by_id,
        )
        previous_site_graph_shape = model.site_graph_shape
        model.site_graph_shape = site_graph_shape
        self._cleanup_previous(previous_site_graph_shape, site_graph_shape)

    @staticmethod
    def _cleanup_previous(
            previous: Optional[SpellSiteGraphAnalysis],
            current: SpellSiteGraphAnalysis,
    ) -> None:
        """
        Best-effort cleanup for one superseded site-graph section.
        """
        if previous is None or previous is current:
            return
        try:
            previous.cleanup()
        except Exception:
            pass

    @classmethod
    def build_site_graph(
            cls,
            *,
            root_instance_key: SiteInstanceKey,
            injection_shape: SpellInjectionAnalysis,
            topology_for: Callable[[str], Optional[SpellLocalTopology]],
    ) -> SpellSiteGraphAnalysis:
        """
        Build the site-graph section from injection sources and topologies.

        Contract:
            - Sites are the instance keys reachable from the root through
              dependency sources, ordered parents first (reversed DFS post-order).
            - Path counts are accumulated parents first: the root counts 1 and
              each dependency edge adds its parent's count to the child.

        Args:
            root_instance_key:
                Instance key of the root spell.
            injection_shape:
                Fitted Phase-9 injection section.
            topology_for:
                Lookup from spell id to its Phase-3 local topology (or None).

        Raises:
            RuntimeError:
                When a reachable instance key has no injection spec.

        Returns:
            SpellSiteGraphAnalysis:
                The fitted section.
        """
        specs = injection_shape.instance_specs_by_instance_key
        order = cls._parents_first_order(root_instance_key, specs)
        index_by_key: Dict[SiteInstanceKey, int] = {
            key: index for index, key in enumerate(order)
        }
        sites: List[SpellSite] = []
        for index, key in enumerate(order):
            spec = specs[key]
            sites.append(
                SpellSite(
                    index=index,
                    instance_key=key,
                    spell_id=key[0],
                    shared=key[1] is None,
                    params=cls._site_params(
                        spec=spec,
                        topology=topology_for(key[0]),
                        index_by_key=index_by_key,
                    ),
                )
            )
        path_counts = [0] * len(sites)
        path_counts[0] = 1
        for site in sites:
            for param in site.params:
                for dependency in param.dependency_sites:
                    path_counts[dependency] += path_counts[site.index]
        return SpellSiteGraphAnalysis(sites=tuple(sites), path_counts=tuple(path_counts))

    @staticmethod
    def _dependency_keys(
            spec: SpellInjectionInstanceSpec,
    ) -> List[SiteInstanceKey]:
        """
        Return the dependency instance keys of one spec in parameter order.
        """
        keys: List[SiteInstanceKey] = []
        for source in spec.param_sources.values():
            if source.kind != "dependency" or not source.dependency_keys:
                continue
            for dependency_key in source.dependency_keys:
                keys.append(tuple(dependency_key))
        return keys

    @classmethod
    def _parents_first_order(
            cls,
            root_instance_key: SiteInstanceKey,
            specs: Dict[SiteInstanceKey, SpellInjectionInstanceSpec],
    ) -> List[SiteInstanceKey]:
        """
        Return reachable instance keys parents first (iterative DFS, no recursion).

        Raises:
            RuntimeError:
                When a reachable instance key has no injection spec.
        """
        post_order: List[SiteInstanceKey] = []
        visited: Set[SiteInstanceKey] = {root_instance_key}
        if root_instance_key not in specs:
            raise RuntimeError(
                f"Site graph build is missing the injection spec for root {root_instance_key!r}."
            )
        stack: List[Tuple[SiteInstanceKey, List[SiteInstanceKey], int]] = [
            (root_instance_key, cls._dependency_keys(specs[root_instance_key]), 0)
        ]
        while stack:
            key, children, next_child = stack[-1]
            if next_child < len(children):
                stack[-1] = (key, children, next_child + 1)
                child = children[next_child]
                if child in visited:
                    continue
                spec = specs.get(child)
                if spec is None:
                    raise RuntimeError(
                        f"Site graph build is missing the injection spec for {child!r}."
                    )
                visited.add(child)
                stack.append((child, cls._dependency_keys(spec), 0))
                continue
            stack.pop()
            post_order.append(key)
        post_order.reverse()
        return post_order

    @classmethod
    def _site_params(
            cls,
            *,
            spec: SpellInjectionInstanceSpec,
            topology: Optional[SpellLocalTopology],
            index_by_key: Dict[SiteInstanceKey, int],
    ) -> Tuple[SpellSiteParam, ...]:
        """
        Build the parameter rows of one site in position order.

        Contract:
            - Topology sockets give every constructor parameter with its
              position, kind, socket kind and flags.
            - Injection sources give the default operand source; a socket with
              no source is "plain".
            - A source whose parameter has no topology socket is appended with
              the source's own position and kind (or -1 / None).
        """
        sources = spec.param_sources
        params: List[SpellSiteParam] = []
        seen: Set[str] = set()
        if topology is not None:
            sockets = sorted(topology.sockets, key=lambda socket: socket.position)
            for socket in sockets:
                if socket.param_name in seen:
                    continue
                seen.add(socket.param_name)
                params.append(
                    cls._param_from_socket(socket, sources.get(socket.param_name), index_by_key)
                )
        for name, source in sources.items():
            if name in seen:
                continue
            seen.add(name)
            params.append(cls._param_from_source(name, source, index_by_key))
        return tuple(params)

    @staticmethod
    def _dependency_sites(
            source: Optional[SpellInjectionParamSource],
            index_by_key: Dict[SiteInstanceKey, int],
    ) -> Tuple[int, ...]:
        """
        Map a dependency source's instance keys to site indexes.
        """
        if source is None or source.kind != "dependency" or not source.dependency_keys:
            return ()
        return tuple(index_by_key[tuple(key)] for key in source.dependency_keys)

    @classmethod
    def _param_from_socket(
            cls,
            socket: SpellSocketDescriptor,
            source: Optional[SpellInjectionParamSource],
            index_by_key: Dict[SiteInstanceKey, int],
    ) -> SpellSiteParam:
        """
        Build one parameter row from a topology socket and its injection source.
        """
        return SpellSiteParam(
            name=socket.param_name,
            position=socket.position,
            parameter_kind=socket.parameter_kind,
            socket_kind_value=socket.socket_kind.value,
            is_collection=socket.is_collection,
            is_optional=socket.is_optional,
            source_kind="plain" if source is None else source.kind,
            contract_key=None if source is None else source.contract_key,
            dependency_sites=cls._dependency_sites(source, index_by_key),
        )

    @classmethod
    def _param_from_source(
            cls,
            name: str,
            source: SpellInjectionParamSource,
            index_by_key: Dict[SiteInstanceKey, int],
    ) -> SpellSiteParam:
        """
        Build one parameter row from an injection source that has no topology socket.
        """
        if source.kind == "unresolved_input":
            socket_kind = SocketKind.UNRESOLVED_INPUT
        elif source.kind == "override_required":
            socket_kind = SocketKind.OVERRIDE_REQUIRED
        elif source.kind == "contract":
            socket_kind = SocketKind.SPELL_CONTRACT
        else:
            socket_kind = SocketKind.NORMAL
        return SpellSiteParam(
            name=name,
            position=-1 if source.position is None else source.position,
            parameter_kind=source.parameter_kind,
            socket_kind_value=socket_kind.value,
            is_collection=source.is_collection,
            is_optional=False,
            source_kind=source.kind,
            contract_key=source.contract_key,
            dependency_sites=cls._dependency_sites(source, index_by_key),
        )
