"""
Blast-radius view over the custody manifests (S3 impact engine).

The record already knows every spell's module world - which modules it
carries, which modules import which, what every physical module's source
hashed to at bind time. The ImpactEngine indexes that recorded truth and
answers the questions the manifests were built for: which spells does a
module reach, what has drifted on disk since the world sealed, and what
does that drift touch. Read-only by law: the engine consumes detached
payloads from the record's describe seam and never mutates anything.

Lane: EPIC-2026-07-11-crystallizer-v3-horizon-iteration, story S3.
"""

import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set

from melder.utilities.general_base.cleanable import Cleanable


class ImpactEngine(Cleanable):
    """
    Index custody manifests and answer blast-radius questions.

    Purpose:
        One detached view over the whole custody surface: reverse module
        edges (who imports whom, who carries what) built once at
        construction, then pure-read verbs for radius and drift.

    Contract:
        - Input is the record's `describe_spell_crystals()` map (payloads
          only; the engine never sees twin objects).
        - All answers are detached dicts; unknown inputs answer honestly
          (empty radius + an "unknown_*" marker, never a raise - the
          question "what does X touch?" has the answer "nothing recorded"
          for unknown X).
        - Drift checking reads DISK ONLY (read_text/utf-8, the CRLF-safe
          custody read that produced the sealed fingerprints); the live
          runtime is never inspected.

    Threading:
        Construction builds all indexes under no lock (single-threaded
        construction contract); reads afterwards are immutable-state
        lookups and may be shared.

    Lifecycle / Cleanup:
        cleanup() deletes the carried indexes (del posture); idempotent.
    """

    __slots__ = Cleanable.__slots__ + [
        "_custody_by_spell",
        "_spells_by_module",
        "_importers_by_module",
        "_fingerprints_by_module",
        "_paths_by_module",
    ]

    def __init__(
            self,
            custody_payloads: Dict[str, Dict[str, object]],
    ) -> None:
        """
        Build the reverse indexes over one detached custody map.

        Contract:
            Copies each spell's top-level payload map, then derives reverse
            module and importer indexes plus fingerprint/path lookups. When
            multiple crystals describe the same physical module, the first
            fingerprint and path encountered become the comparison baseline.
            Construction performs no disk I/O; disk is read only by the drift
            verb.

        Args:
            custody_payloads:
                spell_id -> crystal describe() payload (+ the seam's
                additive "custody_state"), as returned by
                `PersistenceSystem.describe_spell_crystals()`.

        Returns:
            None.

        Raises:
            TypeError: If `custody_payloads` is not a dict.
        """
        super().__init__()
        if not isinstance(custody_payloads, dict):
            raise TypeError("custody_payloads must be a dict of payloads.")
        self._custody_by_spell: Dict[str, Dict[str, object]] = {
            str(spell_id): dict(payload)
            for spell_id, payload in custody_payloads.items()
        }
        # module -> spells whose recorded world carries it.
        self._spells_by_module: Dict[str, Set[str]] = {}
        # module -> modules that DIRECTLY import it (reverse edges over
        # the union of every crystal's module_to_direct_dependencies).
        self._importers_by_module: Dict[str, Set[str]] = {}
        # module -> bind-time sha256 / recorded path (first writer wins;
        # SHAs are content-derived so agreeing crystals carry the same).
        self._fingerprints_by_module: Dict[str, str] = {}
        self._paths_by_module: Dict[str, str] = {}
        for spell_id, payload in self._custody_by_spell.items():
            for module_name in list(payload.get("module_targets", [])):
                self._spells_by_module.setdefault(
                    str(module_name), set()
                ).add(spell_id)
            dependency_map = dict(
                payload.get("module_to_direct_dependencies", {})
            )
            for importer, imported_list in dependency_map.items():
                for imported in list(imported_list):
                    self._importers_by_module.setdefault(
                        str(imported), set()
                    ).add(str(importer))
            for module_name, sha in dict(
                    payload.get("physical_module_fingerprints", {})
            ).items():
                self._fingerprints_by_module.setdefault(
                    str(module_name), str(sha)
                )
            for module_name, module_path in dict(
                    payload.get("module_to_path", {})
            ).items():
                if module_path is not None:
                    self._paths_by_module.setdefault(
                        str(module_name), str(module_path)
                    )

    def cleanup(self) -> None:
        """
        Idempotently release the carried indexes.

        Contract:
            Terminal for this engine. Only detached custody payloads and
            derived sets/maps are released; no crystal, module, or record is
            owned or cleaned here.

        Returns:
            None.

        Threading:
            Must not race with a read verb.

        Lifecycle / Cleanup:
            The crystallizer facade builds an engine per impact request and
            cleans it in `finally` after producing a detached answer.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._custody_by_spell
        del self._spells_by_module
        del self._importers_by_module
        del self._fingerprints_by_module
        del self._paths_by_module

    def spells_touching_module(self, module_name: str) -> List[str]:
        """
        Return the spells whose recorded world carries one module.

        Contract:
            This is direct custody membership, not transitive impact. Use
            `blast_radius_of_module()` to include importing modules and the
            spells that carry them.

        Args:
            module_name:
                Canonical module name.

        Returns:
            List[str]: Sorted spell SHAs; empty for unknown modules.

        Raises:
            RuntimeError: If the engine has been cleaned.
        """
        self.check_cleaned()
        return sorted(self._spells_by_module.get(str(module_name), set()))

    def blast_radius_of_module(
            self,
            module_name: str,
    ) -> Dict[str, object]:
        """
        Return the transitive impact of changing one module.

        Purpose:
            The core question: a change to `module_name` invalidates every
            module that (transitively) imports it, and every spell whose
            recorded world carries any module in that closure.

        Contract:
            - Closure walks the RECORDED reverse import edges only.
            - Unknown modules answer honestly: empty radius +
              "unknown_module": True (nothing recorded depends on it).

        Args:
            module_name:
                Canonical module name at the blast center.

        Returns:
            Dict[str, object]:
                {"module": name, "unknown_module": bool,
                 "affected_modules": sorted names (center included when
                 known), "affected_spells": sorted SHAs,
                 "affected_spellbooks": sorted book ids,
                 "custody_states": {spell_id: state}}.

        Raises:
            RuntimeError: If the engine has been cleaned.
        """
        self.check_cleaned()
        center = str(module_name)
        known = (
            center in self._spells_by_module
            or center in self._importers_by_module
        )
        affected_modules: Set[str] = set()
        if known:
            pending = [center]
            while pending:
                current = pending.pop()
                if current in affected_modules:
                    continue
                affected_modules.add(current)
                pending.extend(
                    self._importers_by_module.get(current, set())
                )
        affected_spells: Set[str] = set()
        for affected in affected_modules:
            affected_spells |= self._spells_by_module.get(affected, set())
        custody_states: Dict[str, str] = {}
        spellbooks: Set[str] = set()
        for spell_id in affected_spells:
            payload = self._custody_by_spell.get(spell_id, {})
            custody_states[spell_id] = str(
                payload.get("custody_state", "active")
            )
            book_id = payload.get("spellbook_id")
            if book_id is not None:
                spellbooks.add(str(book_id))
        return {
            "module": center,
            "unknown_module": not known,
            "affected_modules": sorted(affected_modules),
            "affected_spells": sorted(affected_spells),
            "affected_spellbooks": sorted(spellbooks),
            "custody_states": custody_states,
        }

    def blast_radius_of_spell(self, spell_id: str) -> Dict[str, object]:
        """
        Return the impact of changing one spell (its root module world).

        Contract:
            - A spell change IS its root module changing; the radius is
              `blast_radius_of_module(root_module_name)` plus the spell's
              own identity row.
            - Unknown SHAs answer honestly ("unknown_spell": True).

        Args:
            spell_id:
                The spell's SHA256 custody identity (the system word is
                spell_id; vocabulary conformance 2026-07-11).

        Returns:
            Dict[str, object]:
                {"spell": sha, "unknown_spell": bool, "root_module":
                 name | None} + the module-radius keys when known.

        Raises:
            RuntimeError: If the engine has been cleaned.
        """
        self.check_cleaned()
        payload = self._custody_by_spell.get(str(spell_id))
        if payload is None:
            return {
                "spell": str(spell_id),
                "unknown_spell": True,
                "root_module": None,
            }
        root_module = str(payload.get("root_module_name"))
        radius = self.blast_radius_of_module(root_module)
        radius["spell"] = str(spell_id)
        radius["unknown_spell"] = False
        radius["root_module"] = root_module
        return radius

    def describe_source_drift(self) -> Dict[str, object]:
        """
        Compare every sealed fingerprint against the live disk.

        Purpose:
            The "what will my uncommitted edits break" view: each module
            the record fingerprinted at bind time re-hashes from disk
            (read_text/utf-8 - the same CRLF-safe read that sealed the
            fingerprint) and classifies as unchanged | drifted | absent |
            unreadable; every non-unchanged module carries its blast
            radius.

        Returns:
            Dict[str, object]:
                {"statuses": {module: status}, "radii": {module:
                 blast_radius payload} for every non-unchanged module,
                 "counts": {status: n}}.

        Raises:
            RuntimeError: If the engine has been cleaned.
        """
        self.check_cleaned()
        statuses: Dict[str, str] = {}
        radii: Dict[str, Dict[str, object]] = {}
        counts: Dict[str, int] = {
            "unchanged": 0, "drifted": 0, "absent": 0, "unreadable": 0,
        }
        for module_name, sealed_sha in (
                self._fingerprints_by_module.items()
        ):
            recorded_path = self._paths_by_module.get(module_name)
            status = "absent"
            if recorded_path is not None:
                live_path = Path(recorded_path)
                if live_path.exists():
                    try:
                        disk_sha = hashlib.sha256(
                            live_path.read_text(
                                encoding="utf-8"
                            ).encode("utf-8")
                        ).hexdigest()
                        status = (
                            "unchanged"
                            if disk_sha == sealed_sha
                            else "drifted"
                        )
                    except Exception:
                        status = "unreadable"
            statuses[module_name] = status
            counts[status] += 1
            if status != "unchanged":
                radii[module_name] = self.blast_radius_of_module(
                    module_name
                )
        return {"statuses": statuses, "radii": radii, "counts": counts}

    def describe(self) -> Dict[str, object]:
        """
        Return the engine's full detached report.

        Contract:
            This is not a metadata-only snapshot: it invokes
            `describe_source_drift()` and therefore reads every recorded
            physical path from disk at call time.

        Returns:
            Dict[str, object]:
                {"custody_count", "module_count", "drift":
                 describe_source_drift() payload}.

        Raises:
            RuntimeError: If the engine has been cleaned.
        """
        self.check_cleaned()
        return {
            "custody_count": len(self._custody_by_spell),
            "module_count": len(self._spells_by_module),
            "drift": self.describe_source_drift(),
        }
