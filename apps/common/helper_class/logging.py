# apps/common/logging.py

import logging


class ExtraFormatter(logging.Formatter):
    """
    Extends the default formatter to append extra={} fields to each log line.

    Output:
        INFO 2026-05-24 12:00:00 [services:42] Business user created. | user_id=42  username=john  action_by=user:1
    """

    _BUILTIN_KEYS = frozenset(
        {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
            "taskName",
        }
    )

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)

        extra_fields = {k: v for k, v in record.__dict__.items() if k not in self._BUILTIN_KEYS}

        if not extra_fields:
            return base

        extra_str = " | " + "  ".join(f"{k}={v}" for k, v in extra_fields.items())
        return base + extra_str
