import logging
from typing import Optional


class std_logger_factory:
    """
    Stdlib logger factory that takes the target object and returns a logger.
    Name format: "<frame>.<ClassName>[<IDENT>]" (frame optional).
    IDENT prefers obj._id, then obj.id, else falls back to memory id().
    """

    def __init__(self, frame: Optional[str] = None):
        self._frame = frame

    def __call__(self, obj) -> logging.Logger:
        # identity: prefer _id, then id, else memory id
        try:
            ident = str(obj._id)  # type: ignore[attr-defined]
        except AttributeError:
            try:
                ident = str(obj.id)  # type: ignore[attr-defined]
            except AttributeError:
                ident = hex(id(obj))

        cls = obj.__class__.__name__
        if self._frame:
            return logging.getLogger(f"{self._frame}.{cls}[{ident}]")
        return logging.getLogger(f"{cls}[{ident}]")
