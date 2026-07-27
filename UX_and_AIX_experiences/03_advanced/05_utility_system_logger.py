"""
TIER: advanced (05)
GOAL: Logging through the AetherUtilitySystem - the process-wide
      provider host every runtime object resolves its logger from.
      THE BOOT LAW: melder boots SILENT. Aether starts with a null
      SafeLogger and stays quiet until YOU attach something - no
      surprise stdout, no library spam. Two public doors:
        aether.attach_logger(logger)  - attach one real logger (stdlib
                                        Logger or channel-style), or
                                        None to detach back to silence
        aether.enable_logging(logger) - attach explicitly, or with no
                                        argument try the configured
                                        automatic channel-logger policy
      Runtime objects (books, conduits, the frames themselves) resolve
      their loggers through the utility system's provider path.
SURFACE EXERCISED: md.Aether().attach_logger, enable_logging,
                   the boots-silent law
"""
import logging

import melder as md


class CollectingHandler(logging.Handler):
    """A tiny handler that keeps every record it sees."""

    def __init__(self) -> None:
        super().__init__()
        self.records = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def main() -> None:
    aether = md.Aether()

    # Build a real stdlib logger with a capturing handler...
    handler = CollectingHandler()
    logger = logging.getLogger("melder-advanced-05")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    # ...and attach it through the public post-boot seam.
    aether.attach_logger(logger)
    print("logger attached; the world is no longer silent")

    # Detaching is the same door with None - back to the null wrapper.
    aether.attach_logger(None)
    print("detached; melder is silent again (the boot default)")

    # enable_logging(explicit) is attach; enable_logging() with no
    # argument asks the configured channel policy instead.
    aether.enable_logging(logger)
    print("enable_logging(explicit) attached the same logger")
    aether.attach_logger(None)


if __name__ == "__main__":
    main()
