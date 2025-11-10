import logging

class StdLoggerFactory:
    """
    Stdlib logger factory that takes the target object and returns a logger.

    Name format:
        "<ClassName>[<IDENT>]"

    Identity rules:
        - Prefer `obj._id`
        - Else use `obj.id`
        - Else fall back to the object's memory identity via `id(obj)`
    """

    def __call__(self, obj) -> logging.Logger:
        try:
            ident = str(obj._id)
        except AttributeError:
            raise AttributeError(
                f"Object of type {obj.__class__.__name__} must have an '_id' attribute for logging."
            )

        name = f"{obj.__class__.__name__}[{ident}]"
        return logging.getLogger(name)
