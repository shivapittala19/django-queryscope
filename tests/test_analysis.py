from queryscope.analysis import analyse, normalize
from queryscope.collector import Query


def query(sql, ms=1.0):
    return Query(sql, ms, "shop/views.py:1 in view")


def test_normalize_collapses_whitespace_and_in_lists():
    sql = "SELECT *\n  FROM t WHERE id IN (%s, %s, %s)"
    assert normalize(sql) == "SELECT * FROM t WHERE id IN (...)"


def test_slow_queries_respect_threshold():
    report = analyse([query("A", 50), query("B", 150)], slow_ms=100, n_plus_one_threshold=5)
    assert [q.sql for q in report.slow] == ["B"]


def test_repeats_below_threshold_are_ignored():
    report = analyse([query("A")] * 4, slow_ms=100, n_plus_one_threshold=5)
    assert report.repeated == []
    assert not report.has_problems


def test_repeats_group_by_shape_not_params():
    queries = [query("SELECT * FROM t WHERE id IN (%s)"), query("SELECT * FROM t WHERE id IN (%s, %s)")] * 3
    report = analyse(queries, slow_ms=100, n_plus_one_threshold=5)
    [repeated] = report.repeated
    assert repeated.count == 6
