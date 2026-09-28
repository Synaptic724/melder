"""
melc cache ledger: what each cached creation plan does per creation, and what a codegen style could remove.

WHY THIS EXISTS
    Proof before design. A creation cache (`__melder_cache__/__conjure_cache__/<frame>/<conduit>.melc`) holds one
    marshal bundle per conduit; each spell payload carries the family manifest, and for the generalized and
    many_only families the `no_overrides.steps_rows` the normal plan is re-emitted from at hydration. Those rows
    say what the emitted body does on every creation of that root: which sites are shared reads (singletons,
    existing objects), which are inline constructor calls (transients), which transients register for disposal,
    how wide and deep the tree is. This tool tallies that per root and prices it with measured VM costs, so a real
    application's cache answers "where is there anything to trim, and how much" without a runtime probe.

WHAT IT DOES NOT KNOW
    How often each root is melded. A singleton root (`unique*`) runs its plan once per scope; its warm melds are
    door hits and never enter the body, so the body's cost matters only cold. A `many` root runs the body on every
    meld. The ledger prints both and marks which one applies.

PRICES (VM, CPython 3.14t with the GIL disabled, directional; calibrated on the commandops-shaped live runs of
    2026-09-27 - override any of them through the environment variable named)
    MELC_NS_DOOR           entry by name plus the route door of a warm meld          150
    MELC_NS_SHARED         one shared-site read (store attribute + dict.get + test)   23
    MELC_NS_CAPTURE        the same site as a guarded constant                        7
    MELC_NS_CTOR           floor of one inline constructor call (user code excluded)  60
    MELC_NS_REGISTER       one many registration with disposal, in situ              600
    MELC_NS_REGISTER_TRIM  the same after the trim (per-key methods, one append)      63
    MELC_NS_PLAN           the plan frame itself                                      25

RUN
    python tests/experimentation/melc_cache_ledger.py <cache root, or a directory holding __conjure_cache__>
"""

import marshal
import os
import pathlib
import sys
from typing import Any, Dict, List, Tuple


class Prices:
    """Per-component nanosecond prices, overridable through the environment (see the module docstring)."""

    __slots__ = ("door", "shared", "capture", "ctor", "register", "register_trim", "plan")

    def __init__(self) -> None:
        self.door: float = float(os.environ.get("MELC_NS_DOOR", "150"))
        self.shared: float = float(os.environ.get("MELC_NS_SHARED", "23"))
        self.capture: float = float(os.environ.get("MELC_NS_CAPTURE", "7"))
        self.ctor: float = float(os.environ.get("MELC_NS_CTOR", "60"))
        self.register: float = float(os.environ.get("MELC_NS_REGISTER", "600"))
        self.register_trim: float = float(os.environ.get("MELC_NS_REGISTER_TRIM", "63"))
        self.plan: float = float(os.environ.get("MELC_NS_PLAN", "25"))


class RootLedger:
    """One cached root plan, tallied from its step rows."""

    __slots__ = (
        "conduit", "spell_id", "family", "route", "existence", "steps", "width", "depth",
        "shared_constructed", "shared_existing", "many_steps", "many_with_disposal", "generic_steps",
    )

    def __init__(self, conduit: str, spell_id: str, family: str, manifest: Dict[str, Any]) -> None:
        self.conduit = conduit
        self.spell_id = spell_id
        self.family = family
        self.route: str = str(manifest.get("route_key"))
        self.existence: str = "?"
        self.steps: int = 0
        self.width: int = 0
        self.depth: int = 0
        self.shared_constructed: int = 0
        self.shared_existing: int = 0
        self.many_steps: int = 0
        self.many_with_disposal: int = 0
        self.generic_steps: int = 0
        lane = manifest.get("no_overrides")
        if not isinstance(lane, dict):
            return
        rows: Tuple[Dict[str, Any], ...] = tuple(lane.get("steps_rows", ()))
        root_key = tuple(lane.get("root_instance_key", ()))
        self.steps = len(rows)
        by_key: Dict[Tuple[Any, ...], Dict[str, Any]] = {tuple(r["instance_key"]): r for r in rows}
        root = by_key.get(root_key)
        if root is not None:
            self.existence = str(root["existence"])
            self.width = len(root["dependency_resolution_order"])
            self.depth = self._depth(root, by_key, 0)
        for row in rows:
            if row["shared_instance"]:
                if row["spell_is_existing_creation"]:
                    self.shared_existing += 1
                else:
                    self.shared_constructed += 1
            else:
                self.many_steps += 1
                if row["spell_has_disposal_methods"]:
                    self.many_with_disposal += 1
            if row["has_contract_payload"] or row["uses_positional_override"] or row["collection_param_names"]:
                self.generic_steps += 1

    @staticmethod
    def _depth(row: Dict[str, Any], by_key: Dict[Tuple[Any, ...], Dict[str, Any]], seen: int) -> int:
        """Longest provider chain below `row` (bounded so a malformed cycle cannot recurse forever)."""
        if seen > 64:
            return seen
        best = 0
        for _param, targets in row["dependency_resolution_order"]:
            for target in targets:
                child = by_key.get(tuple(target))
                if child is not None:
                    best = max(best, 1 + RootLedger._depth(child, by_key, seen + 1))
        return best

    @property
    def shared_sites(self) -> int:
        """Shared-site reads the body performs on a creation that misses nothing."""
        return self.shared_constructed + self.shared_existing

    def warm_body_ns(self, p: Prices) -> float:
        """Estimated cost of one full run of the body with every shared site already stored."""
        return (
            p.plan
            + self.shared_sites * p.shared
            + self.many_steps * p.ctor
            + self.many_with_disposal * p.register
        )

    def lever_capture_ns(self, p: Prices) -> float:
        """Saving if every shared site became a guarded constant (the singleton-capture style)."""
        return self.shared_sites * (p.shared - p.capture)

    def lever_register_ns(self, p: Prices) -> float:
        """Saving if every many registration took the trimmed shape."""
        return self.many_with_disposal * (p.register - p.register_trim)


def load_bundles(root: pathlib.Path) -> List[Tuple[pathlib.Path, Dict[str, Any]]]:
    """Decode every `.melc` bundle under a conjure cache root; unreadable files are reported, not fatal."""
    conjure = root / "__conjure_cache__" if (root / "__conjure_cache__").is_dir() else root
    bundles: List[Tuple[pathlib.Path, Dict[str, Any]]] = []
    for path in sorted(conjure.glob("*/*.melc")):
        try:
            bundles.append((path, marshal.loads(path.read_bytes())))
        except (ValueError, EOFError, TypeError) as exc:
            print(f"UNREADABLE {path}: {type(exc).__name__}: {exc}")
    return bundles


def ledgers_for(bundle: Dict[str, Any]) -> Tuple[List[RootLedger], int, int]:
    """Return one bundle's root ledgers, its solo count and its count of payloads with no readable manifest."""
    conduit = f"{bundle.get('frame_name')}/{bundle.get('conduit_name')}"
    out: List[RootLedger] = []
    solos = 0
    unreadable = 0
    for spell_id, payload in bundle.get("spell_payloads", {}).items():
        try:
            inner = marshal.loads(payload) if isinstance(payload, (bytes, bytearray)) else payload
        except (ValueError, EOFError, TypeError):
            unreadable += 1
            continue
        if not isinstance(inner, dict) or "manifest" not in inner:
            unreadable += 1
            continue
        family = str(inner.get("family_id"))
        if family == "solo_codegen_creation":
            solos += 1
            continue
        out.append(RootLedger(conduit, str(spell_id), family, inner["manifest"]))
    return out, solos, unreadable


def main(argv: List[str]) -> int:
    """Print the ledger for one cache root."""
    if len(argv) != 2:
        print(__doc__)
        return 2
    root = pathlib.Path(argv[1])
    prices = Prices()
    bundles = load_bundles(root)
    print(f"# melc cache ledger: {root}\n")
    print(f"bundles: {len(bundles)}; prices (ns): door {prices.door:.0f}, shared read {prices.shared:.0f} -> capture "
          f"{prices.capture:.0f}, constructor floor {prices.ctor:.0f}, registration {prices.register:.0f} -> trimmed "
          f"{prices.register_trim:.0f}, plan {prices.plan:.0f}\n")
    print("| conduit | root | existence | steps | width | depth | shared (built+existing) | many (with disposal) | "
          "generic | body ns | capture lever | registration lever | warm meld ns |")
    print("| --- | --- | --- | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |")
    totals: Dict[str, int] = {
        "roots": 0, "many_roots": 0, "singleton_roots": 0, "solo": 0, "disposal_many_roots": 0, "unreadable": 0,
    }
    for _path, bundle in bundles:
        ledgers, solos, unreadable = ledgers_for(bundle)
        totals["solo"] += solos
        totals["unreadable"] += unreadable
        for ledger in ledgers:
            totals["roots"] += 1
            transient_root = ledger.existence == "many"
            if transient_root:
                totals["many_roots"] += 1
                if ledger.many_with_disposal:
                    totals["disposal_many_roots"] += 1
            else:
                totals["singleton_roots"] += 1
            body = ledger.warm_body_ns(prices)
            warm = prices.door + body if transient_root else prices.door
            note = "" if transient_root else " (body once per scope; warm melds are door hits)"
            print(f"| {ledger.conduit} | {ledger.spell_id[:10]} | {ledger.existence} | {ledger.steps} | {ledger.width} | "
                  f"{ledger.depth} | {ledger.shared_sites} ({ledger.shared_constructed}+{ledger.shared_existing}) | "
                  f"{ledger.many_steps} ({ledger.many_with_disposal}) | {ledger.generic_steps} | {body:.0f} | "
                  f"{ledger.lever_capture_ns(prices):.0f} | {ledger.lever_register_ns(prices):.0f} | {warm:.0f}{note} |")
    print(f"\nroots: {totals['roots']} generalized/many_only (+{totals['solo']} solo, {totals['unreadable']} payloads "
          f"without a readable manifest); transient (`many`) roots: {totals['many_roots']}, of which "
          f"{totals['disposal_many_roots']} register for disposal on every creation; singleton roots: "
          f"{totals['singleton_roots']} (their bodies run once per scope).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
