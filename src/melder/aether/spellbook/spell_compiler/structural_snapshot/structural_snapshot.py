import hashlib
import types
import typing
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional, Tuple, Union, get_args, get_origin

from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_3 import CompilerPhase3
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements import (
        SpellRequirements,
    )
    from melder.utilities.caching_system.caching_system import CachingSystem


class StructuralSnapshot:
    """
    Internal

    Capture side of the structural snapshot: value rows for the results of
    compiler phases 3 and 4, one payload per owned spell, written into the
    conduit cache bundle beside the executor payloads at the end of conjure.

    Purpose:
        A conjure that can prove its phase 3-4 results are still valid should
        be able to replay them instead of running the structural phases. This
        seam produces the rows that a later hydrate replays; nothing in the
        runtime reads them yet. Everything it writes is a value: strings,
        ints, bools, None and tuples/lists of those - never an index ULID, an
        object or the repr of an object - so the payloads are marshal-safe and
        identical across processes for the same world.

    Contract:
        - Reads DURABLE state only. The per-spell phase artifacts are reset
          before conjure end, so the rows come from `Spell.dependencies`, the
          registered `SpellLocalTopology`, the lineage `SpellSystemState`
          (validity and the `contract_unvalidated` flag) and the bind-time
          profile requirements (annotation type references for the key).
        - Payload schema (`PAYLOAD_FORMAT` 1):
          ``{"key": {"format", "spell_id", "annotation_refs"},
             "world_stamp": str, "replayable": bool,
             "phase3": {"dependency_ids": [...], "sockets": [...]},
             "phase4": {"validity": str, "contract_unvalidated": bool}}``
          where a socket row is the `SpellSocketDescriptor` fields in order
          ``(param_name, position, socket_kind_name, is_collection,
          is_optional, target_spell_ids, dependency_key, contract_key,
          referenced_spell_ids, parameter_kind)``.
        - The ordered local frame is NOT stored: it is the sorted distinct
          dependency ids (without the spell itself) followed by the spell id,
          the same law phase 3 applies.
        - The world stamp is a SHA-256 over the inputs phases 3-4 read from
          the world: the sorted pool ids, the frame posture and the sorted
          borrowed (contracted) spell ids. A payload is only meaningful for
          the world it was captured in.
        - Replayability is a POOL property: phase 3 disables its candidate
          index, and so falls back to `==` scans, when any bound object or
          spellframe in the pool overrides `__eq__`; such matching cannot be
          reproduced from names, so every payload of that book carries
          `replayable: False`. The rule is `CompilerPhase3._eq_safe_object`,
          applied here to the same objects.
        - A spell without bind-time profile requirements has no key and gets
          no payload (it will be a structural miss).
        - Capture is best-effort per spell: a payload that cannot be built is
          logged and skipped; nothing raises into conjure.

    Threading / Concurrency:
        - Stateless. Runs on the conjure thread after the phases and the
          conduit wiring, under no lock of its own; the cache utility
          serializes its own store mutations.

    Lifecycle / Cleanup:
        - Slot-only static helper class: nothing to construct or clean.

    Registration:
        MELDER KERNEL - internal; never bound.

    Subsystem Context:
        The `structural_snapshot` package beside the compiler phases: the
        capture half of the structural snapshot (the hydrate half is the
        next task of the same lane).

    System Context:
        Called once per conjure from the creation system's activation tail,
        after the executor payloads are staged and before the single
        conjure-end emit of the `.melc` bundle.

    AGENT_ACCESS: internal
    AGENT_PURPOSE:
        access: internal. Builds per-spell structural payloads (phase 3-4 rows, key,
        world stamp, replayability) and stores them in the conduit cache at conjure end.
    """

    __slots__ = ()

    PAYLOAD_FORMAT: ClassVar[int] = 1

    @staticmethod
    def type_refs(value: Any) -> List[Tuple[str, str]]:
        """
        Render one annotation-like value as address-free reference rows.

        Contract:
            - `None` -> ``("none", "None")``; a string -> ``("str", text)``; a
              `typing.ForwardRef` -> ``("forward_ref", text)``; a class ->
              ``(module, qualname)``; an `Optional`/`Union` -> the refs of its
              non-None members (one row each); any other typing construct ->
              ``("typing", repr)`` (typing reprs carry no addresses); any
              other object -> ``("object", "<module>.<qualname>")`` of its type.
            - Deterministic across processes for the same source.

        Args:
            value:
                Annotation, spellframe or bound object to reference.

        Returns:
            List[Tuple[str, str]]:
                One or more reference rows, in member order for unions.
        """
        if value is None:
            return [("none", "None")]
        if isinstance(value, str):
            return [("str", value)]
        if isinstance(value, typing.ForwardRef):
            return [("forward_ref", value.__forward_arg__)]
        if isinstance(value, type):
            return [(value.__module__, value.__qualname__)]
        origin = get_origin(value)
        if origin in (Union, types.UnionType):
            rows: List[Tuple[str, str]] = []
            for member in get_args(value):
                if member is type(None):
                    continue
                rows.extend(StructuralSnapshot.type_refs(member))
            return rows
        if origin is not None:
            return [("typing", repr(value))]
        return [("object", f"{type(value).__module__}.{type(value).__qualname__}")]

    @staticmethod
    def annotation_refs(requirements: "SpellRequirements") -> List[Tuple[str, str]]:
        """
        Collect the sorted, de-duplicated type references phase 3 matches on.

        Contract:
            - SINGLE_BY_ANNOTATION parameters contribute their annotation;
              COLLECTION_BY_ANNOTATION parameters their element annotation
              (the annotation itself when no element is recorded);
              SPELLMAP_DEFAULT parameters the map's `spell`, `spellframe` and
              a ``("binding_name", name)`` row; PLAIN and SpellContract
              parameters contribute nothing (contract keys are already
              strings inside the socket rows).
            - Sorted and unique, so two processes render the same rows.

        Args:
            requirements:
                Bind-time phase-1 requirements of the spell.

        Returns:
            List[Tuple[str, str]]:
                Sorted reference rows.
        """
        rows: set[Tuple[str, str]] = set()
        for parameter in requirements.parameters:
            di_shape = parameter.di_shape
            if di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION:
                rows.update(StructuralSnapshot.type_refs(parameter.annotation))
            elif di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION:
                element = parameter.collection_element_annotation
                if element is None:
                    element = parameter.annotation
                rows.update(StructuralSnapshot.type_refs(element))
            elif di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
                spellmap = parameter.spellmap_default
                if spellmap is None:
                    continue
                if spellmap.spell is not None:
                    rows.update(StructuralSnapshot.type_refs(spellmap.spell))
                if spellmap.spellframe is not None:
                    rows.update(StructuralSnapshot.type_refs(spellmap.spellframe))
                rows.add(("binding_name", spellmap.binding_name or ""))
        return sorted(rows)

    @staticmethod
    def bind_time_requirements(spell: "Spell") -> Optional["SpellRequirements"]:
        """
        Return the spell's live bind-time requirements, or None.

        Contract:
            - The same borrow rule as phase 1: the profile chain must exist,
              the requirements must not be cleaned, and their spell id must
              match this spell (a rebind mints a fresh Spell and profile).
            - Borrow only; ownership stays with the profile.

        Args:
            spell:
                Spell whose profile requirements are wanted.

        Returns:
            Optional[SpellRequirements]:
                Live requirements, or None when unavailable.
        """
        profile = spell.profile
        if profile is None:
            return None
        resolution_profile = profile.resolution_profile
        if resolution_profile is None:
            return None
        requirements = resolution_profile.requirements
        if requirements is None or requirements.cleaned:
            return None
        if requirements.spell_id != spell.spell_id:
            return None
        return requirements

    @staticmethod
    def structural_key(spell: "Spell") -> Optional[Dict[str, Any]]:
        """
        Build the per-spell key of a structural payload.

        Contract:
            - ``{"format": PAYLOAD_FORMAT, "spell_id": spell.spell_id,
              "annotation_refs": [...]}``; the spell id already covers the
              spell's own signature, names, existence and resolvability, and
              the annotation refs add the (module, qualname) of every type the
              spell's sockets match on, so a type that moves module while
              keeping its rendered name changes the key.
            - None when the spell has no live bind-time requirements.

        Args:
            spell:
                Spell to key.

        Returns:
            Optional[Dict[str, Any]]:
                Value-only key, or None.
        """
        requirements = StructuralSnapshot.bind_time_requirements(spell)
        if requirements is None:
            return None
        return {
            "format": StructuralSnapshot.PAYLOAD_FORMAT,
            "spell_id": spell.spell_id,
            "annotation_refs": StructuralSnapshot.annotation_refs(requirements),
        }

    @staticmethod
    def world_stamp(spellbook: "Spellbook") -> str:
        """
        Digest the world inputs phases 3-4 read for this Book.

        Contract:
            - SHA-256 hex over three lines: the sorted ids of
              `spellbook._spell_id_pool`, the frame posture name
              (`system_state`, empty when no frame configuration is bound)
              and the sorted ids of the borrowed spells in
              `spellbook._contracted_spells`.
            - No runtime identity (frame name, conduit id, ULIDs) enters the
              stamp.

        Args:
            spellbook:
                Book whose world is stamped.

        Returns:
            str:
                Hex digest.
        """
        pool_ids = sorted(spellbook._spell_id_pool.keys())
        frame_configuration = spellbook._aetheric_frame_configuration
        posture = "" if frame_configuration is None else frame_configuration.system_state.name
        borrowed_ids: set[str] = set()
        for by_index in spellbook._contracted_spells.values():
            for borrowed in by_index.values():
                borrowed_ids.add(borrowed.spell_id)
        text = "\n".join((
            "pool:" + ",".join(pool_ids),
            "posture:" + posture,
            "borrowed:" + ",".join(sorted(borrowed_ids)),
        ))
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def pool_replayable(spellbook: "Spellbook") -> bool:
        """
        Decide whether phase 3's matching for this pool can be replayed from names.

        Contract:
            - True when every pool spell's bound object and spellframe are
              eq-safe under `CompilerPhase3._eq_safe_object` (the rule that
              keeps phase 3's candidate index enabled); False as soon as one
              is not, because phase 3 then matched with `==` scans a name
              cannot reproduce.

        Args:
            spellbook:
                Book whose pool is checked.

        Returns:
            bool:
                Pool-wide replayability verdict.
        """
        for spell in spellbook._spell_id_pool.values():
            if not CompilerPhase3._eq_safe_object(spell.spell):
                return False
            if not CompilerPhase3._eq_safe_object(spell.spellframe):
                return False
        return True

    @staticmethod
    def build_payload(
            spell: "Spell",
            spell_system_states: "SpellSystemStates",
            *,
            world_stamp: str,
            replayable: bool,
    ) -> Optional[Dict[str, Any]]:
        """
        Build one spell's structural payload from durable state.

        Contract:
            - Requires the key (bind-time requirements), a bound SpellIndex,
              the lineage state and the registered local topology; returns
              None when any is missing (the spell is then a structural miss).
            - `phase3.dependency_ids` is `Spell.dependencies` as phase 3 left
              it (resolution order, de-duplicated, a recorded self-dependency
              included); `phase3.sockets` are the topology descriptor rows.
            - `phase4.validity` is the lineage validity name and
              `phase4.contract_unvalidated` the flag's presence.
            - Values only; two builds over the same state are equal.

        Args:
            spell:
                Owned spell to snapshot.
            spell_system_states:
                Frame registry holding the lineage state and topology.
            world_stamp:
                Digest from `world_stamp` for this conjure.
            replayable:
                Verdict from `pool_replayable` for this conjure.

        Returns:
            Optional[Dict[str, Any]]:
                Marshal-safe payload, or None.
        """
        key = StructuralSnapshot.structural_key(spell)
        if key is None:
            return None
        spell_index = spell.spell_index
        if spell_index is None:
            return None
        state = spell_system_states.get_by_index_id(spell_index.id)
        if state is None:
            return None
        topology = spell_system_states.get_local_topology(spell_index)
        if topology is None:
            return None
        sockets: List[Tuple[Any, ...]] = []
        for descriptor in topology.sockets:
            sockets.append((
                descriptor.param_name,
                descriptor.position,
                descriptor.socket_kind.name,
                descriptor.is_collection,
                descriptor.is_optional,
                tuple(descriptor.target_spell_ids),
                None if descriptor.dependency_key is None else tuple(descriptor.dependency_key),
                None if descriptor.contract_key is None else tuple(descriptor.contract_key),
                tuple(descriptor.referenced_spell_ids),
                descriptor.parameter_kind,
            ))
        return {
            "key": key,
            "world_stamp": world_stamp,
            "replayable": replayable,
            "phase3": {
                "dependency_ids": list(spell.dependencies),
                "sockets": sockets,
            },
            "phase4": {
                "validity": state.validity.name,
                "contract_unvalidated": SpellState.contract_unvalidated in state.flags,
            },
        }

    @staticmethod
    def capture_at_conjure_end(
            spellbook: "Spellbook",
            caching_system: "CachingSystem",
    ) -> bool:
        """
        Store a structural payload for every owned spell and drop dead ids.

        Contract:
            - One stamp and one replayability verdict per call, shared by
              every payload of this conjure.
            - Owned spells (`spellbook._spells`) in sorted id order; a spell
              with caching disabled, or without a buildable payload, has its
              stale payload removed instead.
            - Ids in the store that are no longer owned are removed.
            - Returns True when the store's bytes changed for any spell, so
              the caller can flag the conjure-end emit; an unchanged world
              rewrites nothing.
            - Best-effort per spell: a build failure is logged through the
              Book's logger and that spell is skipped (its payload removed).

        Args:
            spellbook:
                Conjuring Book.
            caching_system:
                The Book's conduit cache utility.

        Returns:
            bool:
                True when any structural payload was added, replaced or removed.
        """
        changed = False
        stamp = StructuralSnapshot.world_stamp(spellbook)
        replayable = StructuralSnapshot.pool_replayable(spellbook)
        spell_system_states = spellbook._spell_system_states
        live: Dict[str, "Spell"] = {}
        for spell in spellbook._spells.values():
            live[spell.spell_id] = spell
        for spell_id in sorted(live):
            spell = live[spell_id]
            payload: Optional[Dict[str, Any]] = None
            if spell._caching_enabled:
                try:
                    payload = StructuralSnapshot.build_payload(
                        spell,
                        spell_system_states,
                        world_stamp=stamp,
                        replayable=replayable,
                    )
                except Exception as exc:
                    # Best-effort capture (documented): a payload that cannot be
                    # built must never break conjure; the spell simply misses.
                    if spellbook._logger is not None:
                        spellbook._logger.error(
                            f"Failed to capture the structural payload for spell_id={spell_id}: {exc}",
                            "capture_at_conjure_end",
                            exc_info=True,
                        )
                    payload = None
            if payload is None:
                if caching_system.remove_structural_payload(spell_id):
                    changed = True
                continue
            if caching_system.upsert_structural_payload(spell_id, payload):
                changed = True
        for cached_id in tuple(caching_system.cached_structural_spell_ids):
            if cached_id not in live and caching_system.remove_structural_payload(cached_id):
                changed = True
        return changed
