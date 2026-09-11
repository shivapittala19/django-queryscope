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


# On Python < 3.12 a comprehension runs in a frame of its own, so the innermost
# frame is named "<listcomp>" rather than the function you wrote.
_COMPREHENSIONS = frozenset({"<listcomp>", "<dictcomp>", "<setcomp>", "<genexpr>", "<lambda>"})


def find_origin():
    """Return the line of application code that triggered the query."""
    frames = [
        f
        for f in traceback.extract_stack()
        if not f.filename.startswith(_SKIP_DIRS) and "site-packages" not in f.filename
    ]
    if not frames:
        return "unknown"

    where = frames[-1]  # innermost application frame: the real file and line
    name = where.name
    for frame in reversed(frames):  # name it after the enclosing function
        if frame.name not in _COMPREHENSIONS:
            name = frame.name
            break
    return f"{os.path.relpath(where.filename)}:{where.lineno} in {name}"
