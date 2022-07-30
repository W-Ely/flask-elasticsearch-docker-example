from structlog import configure, get_logger
from structlog.processors import format_exc_info, KeyValueRenderer, TimeStamper
from structlog.contextvars import (
    bind_contextvars,
    merge_contextvars,
    unbind_contextvars,
)
from structlog.stdlib import add_log_level


configure(
    processors=[
        add_log_level,
        TimeStamper(fmt="iso"),
        merge_contextvars,
        format_exc_info,
        KeyValueRenderer(sort_keys=True),
    ]
)

LOGGER = get_logger("geo-search")


def set_logging_context(**kwargs):
    bind_contextvars(**kwargs)


def clear_logging_context(*args):
    unbind_contextvars(*args)
