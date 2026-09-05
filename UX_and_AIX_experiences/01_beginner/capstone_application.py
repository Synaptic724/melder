"""Consume the running graph using concrete types without runtime model imports."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import melder as md
    from capstone_models import AppConfig, DbPool, RequestHandler


def run_application(conduit: md.Conduit) -> list[str]:
    """Resolve and use application objects; borrow the conduit without owning its cleanup.

    TYPE_CHECKING supplies editor/checker types. The strings passed to meld are
    the runtime addresses registered by the bootstrap. Return the three request
    messages, with assertions that demonstrate shared and fresh lifetimes.
    """
    config: AppConfig = conduit.meld(spell="AppConfig")
    pool: DbPool = conduit.meld(spell="DbPool")
    assert config is conduit.meld(spell="AppConfig")
    assert pool is conduit.meld(spell="DbPool")

    handlers: list[RequestHandler] = []
    messages: list[str] = []
    for order_id in (101, 102, 103):
        handler: RequestHandler = conduit.meld(spell="RequestHandler")
        assert handler.requests_handled == 0
        messages.append(handler.handle(order_id))
        assert handler.requests_handled == 1
        handlers.append(handler)

    assert handlers[0] is not handlers[1] and handlers[1] is not handlers[2]
    assert handlers[0] is not handlers[2]
    assert pool.query_count == 3
    return messages
