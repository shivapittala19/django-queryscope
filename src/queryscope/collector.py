import os
import sysconfig
import time
import traceback
from dataclasses import dataclass

import django

# Frames from these locations are skipped when finding which line of *your*
# code triggered a query.
_SKIP_DIRS = (
    os.path.dirname(__file__),
    os.path.dirname(django.__file__),
    sysconfig.get_paths()["stdlib"],
)


@dataclass
class Query:
    sql: str
    duration_ms: float
    origin: str  # e.g. "shop/views.py:42 in order_list"


class QueryCollector:
    """Records every query while installed with connection.execute_wrapper()."""

    def __init__(self):
        self.queries = []

    def __call__(self, execute, sql, params, many, context):
        start = time.perf_counter()
        try:
            return execute(sql, params, many, context)
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            self.queries.append(Query(sql, duration_ms, find_origin()))


def find_origin():
    """Return the innermost stack frame that belongs to application code."""
    for frame in reversed(traceback.extract_stack()):
        if frame.filename.startswith(_SKIP_DIRS) or "site-packages" in frame.filename:
            continue
        return f"{os.path.relpath(frame.filename)}:{frame.lineno} in {frame.name}"
    return "unknown"
