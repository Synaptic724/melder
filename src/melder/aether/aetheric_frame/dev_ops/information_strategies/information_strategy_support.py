import time
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Tuple

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
        DevopsInformationRegistry,
    )


class InformationFreshnessInspector:
    """
    Shared freshness math for DevOps information strategies.

    Purpose:
        Turn the registry's last-reported fact baselines into one uniform
        freshness view so every information strategy answers the same two
        questions the same way: "when was each touched region last reported?"
        and "is anything stale enough that the caller should re-derive?".

    Why this exists:
        The control plane's economy is "last report + committed deltas =
        current truth". A strategy run is only warranted when a region has no
        baseline (cold start) or the baseline is older than the caller's
        tolerance. Centralizing that check keeps the staleness vocabulary
        identical across the catalog instead of letting each strategy invent
        its own.

    Contract:
        - Stateless; all helpers are static.
        - Reads fact records through the registry's public API only.
        - Returns detached plain payloads (dicts/tuples of scalars).

    Threading:
        Stateless; all helpers are static and read fact records through the
        registry's public API.

    Registration:
        MELDER KERNEL - guarded. Shared support for the information family, not
        itself a registered strategy.

    Subsystem Context:
        The common freshness layer every information strategy delegates to, and
        the consumer of `DevopsFactRecord` baselines.

    System Context:
        The economy this enforces is "LAST REPORT PLUS COMMITTED DELTAS EQUALS
        CURRENT TRUTH", which means a strategy run is warranted in exactly two
        cases: a region has no baseline at all (cold start), or its baseline is
        older than the caller's stated tolerance. Everything else can be served
        from what the transaction plane already committed.
        Centralizing that arithmetic is not merely tidy - it keeps the staleness
        VOCABULARY identical across the catalog. If each strategy invented its
        own notion of stale, two views of the same frame could disagree about
        whether the data behind them was current, and a caller comparing them
        would have no way to reconcile the difference.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Shared freshness math for DevOps information strategies. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )

    @staticmethod
    def normalize_region(candidate: str) -> str:
        """
        Normalize one region or scope key into fact-record region form.

        Fact records are stored under "kind:<id>" regions (for example
        "conduit:abc" / "spellbook:xyz") while admission scope keys carry a
        "scope:" prefix ("scope:conduit:abc"). Strategies accept either and
        this helper folds them onto the stored form.

        Args:
            candidate:
                Region key or admission scope key.

        Returns:
            str: The region key without any leading "scope:" prefix.

        Raises:
            TypeError: If `candidate` is not a string.
            ValueError: If `candidate` is empty after stripping.
        """
        if not isinstance(candidate, str):
            raise TypeError("region must be a string.")
        normalized = candidate.strip()
        if normalized.startswith("scope:"):
            normalized = normalized[len("scope:"):]
        if not normalized:
            raise ValueError("region must not be empty.")
        return normalized

    @staticmethod
    def build_freshness_view(
            *,
            devops_information_registry: "DevopsInformationRegistry",
            regions: Iterable[str],
            max_age_in_seconds: Optional[float] = None,
    ) -> Dict[str, object]:
        """
        Build the uniform freshness block for one strategy result.

        Args:
            devops_information_registry:
                Live registry whose fact baselines are inspected.
            regions:
                Region or scope keys the strategy touched. Duplicates are
                folded; each key is normalized via `normalize_region`.
            max_age_in_seconds:
                Optional staleness tolerance. When supplied, the view also
                reports which regions have no baseline newer than the
                tolerance and an overall `fresh` verdict.

        Returns:
            Dict[str, object]: Detached freshness view:
                - "regions": region -> {"baseline_present", "newest_age_in_seconds",
                  "fact_records": ({"fact_family", "generation", "last_reporter",
                  "age_in_seconds"}, ...)}
                - when `max_age_in_seconds` is supplied: "max_age_in_seconds",
                  "stale_regions" (regions with no baseline or only baselines
                  older than the tolerance), and "fresh" (no stale regions).

        Raises:
            TypeError: If `max_age_in_seconds` is not numeric when supplied.
            ValueError: If `max_age_in_seconds` is not positive when supplied.
        """
        if max_age_in_seconds is not None:
            if (
                not isinstance(max_age_in_seconds, (int, float))
                or isinstance(max_age_in_seconds, bool)
            ):
                raise TypeError("max_age_in_seconds must be a float or int.")
            if max_age_in_seconds <= 0:
                raise ValueError("max_age_in_seconds must be greater than 0.")
        now = time.time()
        normalized_regions = sorted(
            {
                InformationFreshnessInspector.normalize_region(region)
                for region in regions
            }
        )
        region_views: Dict[str, Dict[str, object]] = {}
        stale_regions: List[str] = []
        for region in normalized_regions:
            records = devops_information_registry.list_fact_records(
                region=region,
            )
            record_views: Tuple[Dict[str, object], ...] = tuple(
                {
                    "fact_family": record.fact_family,
                    "generation": record.generation,
                    "last_reporter": record.last_reporter,
                    "age_in_seconds": max(0.0, now - record.last_reported_at),
                }
                for record in records
            )
            ages = tuple(view["age_in_seconds"] for view in record_views)
            newest_age = min(ages) if ages else None
            region_views[region] = {
                "baseline_present": bool(record_views),
                "newest_age_in_seconds": newest_age,
                "fact_records": record_views,
            }
            if max_age_in_seconds is not None:
                if newest_age is None or newest_age > max_age_in_seconds:
                    stale_regions.append(region)
        view: Dict[str, object] = {"regions": region_views}
        if max_age_in_seconds is not None:
            view["max_age_in_seconds"] = float(max_age_in_seconds)
            view["stale_regions"] = tuple(stale_regions)
            view["fresh"] = not stale_regions
        return view

    @staticmethod
    def read_optional_max_age(metadata: Dict[str, object]) -> Optional[float]:
        """
        Read the caller's optional staleness tolerance from metadata.

        Args:
            metadata:
                Caller-supplied strategy metadata.

        Returns:
            Optional[float]: The `max_age_in_seconds` value when present and
            numeric, otherwise None.

        Raises:
            TypeError: If the value is present but not numeric.
            ValueError: If the value is present but not positive.
        """
        raw = metadata.get("max_age_in_seconds")
        if raw is None:
            return None
        if not isinstance(raw, (int, float)) or isinstance(raw, bool):
            raise TypeError("max_age_in_seconds must be a float or int.")
        if raw <= 0:
            raise ValueError("max_age_in_seconds must be greater than 0.")
        return float(raw)
