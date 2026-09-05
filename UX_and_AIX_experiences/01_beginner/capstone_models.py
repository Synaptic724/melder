"""Ordinary application objects for the beginner capstone; this module does not import Melder."""


class AppConfig:
    """Carry the application's name as ordinary configuration data."""

    def __init__(self, app_name: str = "orders-service") -> None:
        """Store the application's default or supplied name; own no external resources."""
        self.app_name = app_name


class DbPool:
    """Demonstrate a shared resource with a small in-memory order store.

    No database connection is opened. The conduit owns this pool's lifetime.
    Closing deletes the store; closed/query_count remain readable for the
    example's shutdown checks. This single-threaded example does not promise
    concurrent access to the application-owned store.
    """

    def __init__(self) -> None:
        """Create the owned order store and initialize observable lifecycle/query state."""
        self._orders = {101: "coffee", 102: "tea", 103: "cocoa"}
        self.closed = False
        self.query_count = 0

    def close(self) -> None:
        """Release the store once; repeated closes preserve the recorded shutdown state."""
        if self.closed:
            return
        del self._orders
        self.closed = True

    def fetch_order(self, order_id: int) -> str:
        """Return one order and count the query; reject closed pools or unknown order IDs.

        Raises:
            RuntimeError: The pool has already closed.
            KeyError: The order ID does not exist in this demonstration store.
        """
        if self.closed:
            raise RuntimeError("The order pool is closed; run requests before application shutdown.")
        order = self._orders[order_id]
        self.query_count += 1
        return order


class RequestHandler:
    """Handle one request using borrowed configuration and a borrowed shared pool.

    Constructor annotations name real runtime classes so Melder can inspect
    them for dependency injection. The handler does not own or close the pool.
    """

    def __init__(self, config: AppConfig, pool: DbPool) -> None:
        """Borrow the injected dependencies and start this handler's independent request count."""
        self._config = config
        self._pool = pool
        self.requests_handled = 0

    def handle(self, order_id: int) -> str:
        """Fetch an order and return its application-facing message.

        A successful request increments this handler's count. Pool lookup or
        closed-state errors propagate to the caller without counting a request.
        """
        order = self._pool.fetch_order(order_id)
        self.requests_handled += 1
        return f"{self._config.app_name}: order {order_id} = {order}"
