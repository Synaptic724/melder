from enum import auto, Enum

class IncidentSeverity(Enum):
    """
    Severity classification for incidents recorded by `IncidentManager`.

    Contract:
    - Values are ordered conceptually from lowest urgency to highest urgency.
    - The enum is descriptive only; higher-level tooling decides what policy or
      escalation behavior each level should trigger.

    Levels:
    - `info`: Informational event; no immediate action expected.
    - `warning`: Unexpected but not immediately blocking condition.
    - `error`: Actionable failure that should be investigated.
    - `critical`: Severe condition requiring immediate attention.

    Threading:
        Immutable enum members; safe to read from any thread.

    Registration:
        MELDER KERNEL - guarded, readable by value. Incident vocabulary.

    Subsystem Context:
        The urgency axis of an `Incident`, paired with `IncidentStatus` (the
        lifecycle axis). Severity describes the CONDITION; status describes the
        human or agent response to it.

    System Context:
        Being "descriptive only" is the deliberate boundary and it matches
        `IncidentManager`'s refusal to make policy. The enum orders urgency but
        binds no behaviour - what a `critical` triggers is decided by tooling,
        not by the runtime that recorded it.
        That separation is what lets recording stay free. If severity carried
        automatic escalation, writing an incident would become a runtime action
        with consequences, and components would rationally under-report to
        avoid triggering something. An inert vocabulary can be used honestly.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Severity classification for incidents recorded by `IncidentManager`.
        Melder kernel machinery: read it to understand the runtime, do not drive it directly.
    """
    info = auto()
    warning = auto()
    error = auto()
    critical = auto()
