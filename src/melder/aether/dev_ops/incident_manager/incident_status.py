from enum import auto, Enum
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class IncidentStatus(Enum):
    """
    Lifecycle status for an `Incident`.

    Contract:
    - Status values describe where the incident sits in the operational review
      lifecycle, not the underlying runtime condition itself.
    - Status transitions are driven by `Incident` methods such as
      `acknowledge()`, `resolve()`, and `suppress()`.

    States:
    - `open`: Newly created and not yet triaged.
    - `acknowledged`: Seen/triaged but not yet resolved.
    - `resolved`: The incident has been marked as addressed.
    - `suppressed`: The incident is intentionally muted or accepted.
    """
    __melder_internal__ = _mrg.sentinel
    open = auto()
    acknowledged = auto()
    resolved = auto()
    suppressed = auto()
