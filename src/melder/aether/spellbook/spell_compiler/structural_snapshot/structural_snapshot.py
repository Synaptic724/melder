import hashlib
import time
import types
import typing
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional, Sequence, Set, Tuple, Union, get_args, get_origin

from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_3 import CompilerPhase3
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
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

    The structural snapshot: value rows for the results of compiler phases 3
    and 4, one payload per owned spell, written into the conduit cache bundle
    beside the executor payloads at the end of conjure (capture) and replayed
    at the start of the next conjure when every owned spell still matches
    (hydrate).

    Purpose:
        A conjure that can prove its phase 3-4 results are still valid
        replays them instead of running the structural phases: `classify`
        decides per spell, and `hydrate_full_hit` performs the durable writes
        phases 3-4 would have made. Everything the seam writes is a value: strings,
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
        - Classification (`classify`): a spell HITS when its stored payload is
          well-formed (`payload_well_formed`), carries the live key, the live
          world stamp and `replayable: True`; anything else is a MISS.
          `structural_path` is `disabled` (no cache utility), `full_hit`
          (every owned spell hits), `partial` (some hit) or `miss`.
        - Replay (`hydrate_full_hit`, full hit only): per owned spell, in
          sorted id order, the durable writes of phase 3 through the same
          registry helpers phase 3 calls - `update_dependencies`,
          `register_local_topology` with descriptors rebuilt from the socket
          rows, `Spell._add_build_details`, Nexus publication when enabled -
          then the phase-4 verdict (`clear_dirty` and `set_validity` with the
          recorded validity and `contract_unvalidated` flag). No phase
          artifact is created: the cold conjure resets them before its end,
          and no reader past phase 4 needs them. A registry helper raising
          propagates as it would from phase 3.

    Threading / Concurrency:
        - Stateless. Runs on the conjure thread after the phases and the
          conduit wiring, under no lock of its own; the cache utility
          serializes its own store mutations.

    Lifecycle / Cleanup:
        - Slot-only static helper class: nothing to construct or clean.

    Registration:
        MELDER KERNEL - internal; never bound.

    Subsystem Context:
        The `structural_snapshot` package beside the compiler phases: both
        halves of the structural snapshot (capture at conjure end, classify
        and hydrate before the structural run).

    System Context:
        Capture is called once per conjure from the creation system's
        activation tail, after the executor payloads are staged and before
        the single conjure-end emit of the `.melc` bundle; classify and
        hydrate are called from `_prepare_spellbook_for_conjure` before the
        structural scheduler run (which they replace on a full hit).

    AGENT_ACCESS: internal
    AGENT_PURPOSE:
        access: internal. Builds per-spell structural payloads (phase 3-4 rows, key,
        world stamp, replayability), stores them in the conduit cache at conjure end, and
        classifies/replays them before the next conjure's structural run.
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
    def payload_well_formed(payload: Any, spell_id: str) -> bool:
        """
        Check the value shape of one decoded structural payload.

        Contract:
            - Format `PAYLOAD_FORMAT`, the key's spell id equal to `spell_id`,
              a string world stamp, a bool `replayable`, `phase3.dependency_ids`
              a list of str, `phase3.sockets` a list of 10-tuples whose socket
              kind names a `SocketKind` member and whose id fields are tuples
              of str, and `phase4.validity` one of the replayable validities
              (`valid`, `gated`) with a bool `contract_unvalidated`.
            - Never raises: any shape violation is False.

        Args:
            payload:
                Decoded payload (any object).
            spell_id:
                Spell id the payload must belong to.

        Returns:
            bool:
                True when every row can be replayed.
        """
        if not isinstance(payload, dict):
            return False
        key = payload.get("key")
        if not isinstance(key, dict):
            return False
        if key.get("format") != StructuralSnapshot.PAYLOAD_FORMAT or key.get("spell_id") != spell_id:
            return False
        if not isinstance(key.get("annotation_refs"), list):
            return False
        if not isinstance(payload.get("world_stamp"), str):
            return False
        if not isinstance(payload.get("replayable"), bool):
            return False
        phase3 = payload.get("phase3")
        phase4 = payload.get("phase4")
        if not isinstance(phase3, dict) or not isinstance(phase4, dict):
            return False
        dependency_ids = phase3.get("dependency_ids")
        if not isinstance(dependency_ids, list) or not all(isinstance(item, str) for item in dependency_ids):
            return False
        sockets = phase3.get("sockets")
        if not isinstance(sockets, list):
            return False
        for row in sockets:
            if not StructuralSnapshot._socket_row_well_formed(row):
                return False
        if phase4.get("validity") not in ("valid", "gated"):
            return False
        if not isinstance(phase4.get("contract_unvalidated"), bool):
            return False
        return True

    @staticmethod
    def _socket_row_well_formed(row: Any) -> bool:
        """
        Check one socket row against the `SpellSocketDescriptor` field shapes.

        Args:
            row:
                Candidate row (any object).

        Returns:
            bool:
                True when the row rebuilds into a descriptor.
        """
        if not isinstance(row, tuple) or len(row) != 10:
            return False
        (
            param_name, position, socket_kind_name, is_collection, is_optional,
            target_spell_ids, dependency_key, contract_key, referenced_spell_ids, parameter_kind,
        ) = row
        if not isinstance(param_name, str) or not isinstance(position, int):
            return False
        if not isinstance(socket_kind_name, str) or socket_kind_name not in SocketKind.__members__:
            return False
        if not isinstance(is_collection, bool) or not isinstance(is_optional, bool):
            return False
        for ids in (target_spell_ids, referenced_spell_ids):
            if not isinstance(ids, tuple) or not all(isinstance(item, str) for item in ids):
                return False
        for pair in (dependency_key, contract_key):
            if pair is None:
                continue
            if not isinstance(pair, tuple) or len(pair) != 2 or not all(isinstance(item, str) for item in pair):
                return False
        if parameter_kind is not None and not isinstance(parameter_kind, str):
            return False
        return True

    @staticmethod
    def rebuild_topology(spell_id: str, socket_rows: Sequence[Tuple[Any, ...]]) -> SpellLocalTopology:
        """
        Rebuild the local topology phase 3 registered from its socket rows.

        Contract:
            - The inverse of the `build_payload` projection: one
              `SpellSocketDescriptor` per row, field by field, with the socket
              kind resolved by name and the id fields as tuples.
            - Rows must have passed `payload_well_formed`.

        Args:
            spell_id:
                Spell the topology belongs to.
            socket_rows:
                Socket rows of the payload.

        Returns:
            SpellLocalTopology:
                Fresh topology owned by the caller (the registry, after
                `register_local_topology`).
        """
        descriptors: List[SpellSocketDescriptor] = []
        for row in socket_rows:
            (
                param_name, position, socket_kind_name, is_collection, is_optional,
                target_spell_ids, dependency_key, contract_key, referenced_spell_ids, parameter_kind,
            ) = row
            descriptors.append(
                SpellSocketDescriptor(
                    spell_id=spell_id,
                    param_name=param_name,
                    position=position,
                    socket_kind=SocketKind[socket_kind_name],
                    is_collection=is_collection,
                    is_optional=is_optional,
                    target_spell_ids=tuple(target_spell_ids),
                    dependency_key=None if dependency_key is None else (dependency_key[0], dependency_key[1]),
                    contract_key=None if contract_key is None else (contract_key[0], contract_key[1]),
                    referenced_spell_ids=tuple(referenced_spell_ids),
                    parameter_kind=parameter_kind,
                )
            )
        return SpellLocalTopology(spell_id=spell_id, sockets=descriptors)

    @staticmethod
    def classify(
            spellbook: "Spellbook",
            caching_system: Optional["CachingSystem"],
    ) -> Dict[str, Any]:
        """
        Classify every owned spell against the structural tier of the bundle.

        Contract:
            - `disabled` when no cache utility exists (nothing is read).
            - A spell hits when `caching_system.get_structural_payload` returns
              a payload that is well-formed for its id, whose key equals the
              live `structural_key`, whose world stamp equals the live
              `world_stamp` and whose `replayable` is True; every other spell
              (including one without a live key) misses.
            - `full_hit` requires at least one owned spell and no miss;
              `partial` some hits and some misses; `miss` no hits.
            - Reads only; nothing is written or removed here (capture at
              conjure end refreshes the tier).

        Args:
            spellbook:
                Conjuring Book.
            caching_system:
                The Book's conduit cache utility, or None when caching is off.

        Returns:
            Dict[str, Any]:
                ``{"structural_path", "world_stamp", "hits": {spell_id:
                payload}, "misses": set[spell_id]}``.
        """
        hits: Dict[str, Dict[str, Any]] = {}
        misses: Set[str] = set()
        if caching_system is None:
            return {"structural_path": "disabled", "world_stamp": "", "hits": hits, "misses": misses}
        stamp = StructuralSnapshot.world_stamp(spellbook)
        for spell in spellbook._spells.values():
            spell_id = spell.spell_id
            payload = caching_system.get_structural_payload(spell_id)
            if payload is None or not StructuralSnapshot.payload_well_formed(payload, spell_id):
                misses.add(spell_id)
                continue
            if payload["world_stamp"] != stamp or payload["replayable"] is not True:
                misses.add(spell_id)
                continue
            key = StructuralSnapshot.structural_key(spell)
            if key is None or payload["key"] != key or spell.spell_index is None:
                misses.add(spell_id)
                continue
            hits[spell_id] = payload
        if not hits:
            structural_path = "miss"
        elif misses:
            structural_path = "partial"
        else:
            structural_path = "full_hit"
        return {"structural_path": structural_path, "world_stamp": stamp, "hits": hits, "misses": misses}

    @staticmethod
    def hydrate_full_hit(
            spellbook: "Spellbook",
            hits: Dict[str, Dict[str, Any]],
    ) -> None:
        """
        Replay the phase 3-4 durable writes for every owned spell from its payload.

        Contract:
            - Requires a full hit: `hits` holds a payload for every owned
              spell (a missing id raises `KeyError` before any write).
            - Per spell, in sorted id order: `update_dependencies(index,
              dependency_ids)`, `register_local_topology(index,
              rebuild_topology(...))`, `spell._add_build_details(dependencies)`
              (de-duplicated ids, as phase 3 stores them), Nexus publication
              when `spellbook._nexus_publish_enabled`; then the verdict:
              `state.clear_dirty(now)` and `set_validity(valid,
              validation_passed, flags_to_remove=[contract_unvalidated])` or
              `set_validity(gated, contract_unvalidated,
              flags_to_add=[contract_unvalidated])` - the calls phase 4 makes.
            - A spell whose lineage state is missing raises RuntimeError (it
              exists from bind; its absence is a contract violation, not a
              cache condition).
            - No artifact is touched; no scheduler runs.

        Args:
            spellbook:
                Conjuring Book.
            hits:
                Payloads keyed by spell id, from `classify`.

        Returns:
            None.

        Raises:
            KeyError:
                When an owned spell has no payload in `hits`.
            RuntimeError:
                When an owned spell has no lineage state.
        """
        spell_system_states = spellbook._spell_system_states
        owned: Dict[str, "Spell"] = {}
        for spell in spellbook._spells.values():
            owned[spell.spell_id] = spell
        for spell_id in sorted(owned):
            if spell_id not in hits:
                raise KeyError(f"No structural payload for owned spell_id={spell_id}.")
        now = time.time()
        for spell_id in sorted(owned):
            spell = owned[spell_id]
            payload = hits[spell_id]
            spell_index = spell.spell_index
            if spell_index is None:
                raise RuntimeError(f"Spell {spell_id} has no SpellIndex at hydrate.")
            dependency_ids: List[str] = list(payload["phase3"]["dependency_ids"])
            spell_system_states.update_dependencies(spell_index, dependency_ids)
            spell_system_states.register_local_topology(
                spell_index,
                StructuralSnapshot.rebuild_topology(spell_id, payload["phase3"]["sockets"]),
            )
            spell._add_build_details(dependencies=list(dict.fromkeys(dependency_ids)))
            if spellbook._nexus_publish_enabled:
                spellbook._publish_spell_record_to_nexus(spell)
            state = spell_system_states.get_by_index_id(spell_index.id)
            if state is None:
                raise RuntimeError(f"Spell {spell_id} has no lineage state at hydrate.")
            state.clear_dirty(now)
            if payload["phase4"]["validity"] == "gated":
                state.set_validity(
                    SpellValidity.gated,
                    change_reason=SpellStateChangeReason.contract_unvalidated,
                    flags_to_add=[SpellState.contract_unvalidated],
                )
            else:
                state.set_validity(
                    SpellValidity.valid,
                    change_reason=SpellStateChangeReason.validation_passed,
                    flags_to_remove=[SpellState.contract_unvalidated],
                )

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
