import re
from collections import defaultdict
from dataclasses import dataclass

_WHITESPACE = re.compile(r"\s+")
_IN_LIST = re.compile(r"IN \((?:%s,?\s*)+\)")


def normalize(sql):
    """Reduce a query to its shape, so the same query with different params groups together."""
    sql = _WHITESPACE.sub(" ", sql).strip()
    return _IN_LIST.sub("IN (...)", sql)


@dataclass
class RepeatedQuery:
    sql: str
    count: int
    total_ms: float
    origin: str


@dataclass
class Report:
    queries: list
    slow: list
    repeated: list

    @property
    def total_ms(self):
        return sum(q.duration_ms for q in self.queries)

    @property
    def has_problems(self):
        return bool(self.slow or self.repeated)


def analyse(queries, slow_ms, n_plus_one_threshold):
    slow = [q for q in queries if q.duration_ms >= slow_ms]

    groups = defaultdict(list)
    for q in queries:
        groups[normalize(q.sql)].append(q)

    repeated = [
        RepeatedQuery(sql, len(qs), sum(q.duration_ms for q in qs), qs[0].origin)
        for sql, qs in groups.items()
        if len(qs) >= n_plus_one_threshold
    ]
    repeated.sort(key=lambda r: r.count, reverse=True)

    return Report(queries, slow, repeated)
