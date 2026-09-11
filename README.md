# django-queryscope

Find slow queries and N+1 patterns in Django — per request, pointing at the exact line of your code that caused them.

```
WARNING  queryscope: GET /n-plus-one/ - 11 queries, 0.2 ms in DB
  N+1: 10x at tests/app/views.py:8 in n_plus_one (0.2 ms total)
       SELECT "app_author"."id", "app_author"."name" FROM "app_author" WHERE "app_author"."id" = %s LIMIT 21
```

## Why

N+1 queries are invisible with 10 rows in development. With 10 million rows in production, the same view makes thousands of round trips and takes minutes. `django-queryscope` catches the pattern while the data is still small, and tells you where it comes from.

## Install

```bash
pip install django-queryscope
```

Add the middleware (near the top, so it sees queries from the rest of the stack):

```python
MIDDLEWARE = [
    "queryscope.middleware.QueryScopeMiddleware",
    # ...
]
```

That's it. Any request with a slow query or an N+1 pattern is logged to the `queryscope` logger at `WARNING`.

## Settings

```python
QUERYSCOPE = {
    "ENABLED": True,             # turn it off per environment
    "SLOW_QUERY_MS": 100,        # a single query at or above this is "slow"
    "N_PLUS_ONE_THRESHOLD": 5,   # the same query shape this many times in one request is N+1
}
```

The full analysis is also attached to the request as `request.queryscope`, so you can inspect it in tests:

```python
response = client.get("/orders/")
assert not response.wsgi_request.queryscope.repeated
```

## How it works

1. **Capture.** The middleware installs a [`connection.execute_wrapper`](https://docs.djangoproject.com/en/stable/topics/db/instrumentation/) on every database connection for the duration of the request, timing each query and recording the first stack frame that belongs to your code.
2. **Normalise.** Each query is reduced to its shape — whitespace collapsed, `IN (%s, %s, …)` lists folded — so the same query with different parameters groups together.
3. **Analyse.** Queries over `SLOW_QUERY_MS` are flagged as slow; any shape repeated `N_PLUS_ONE_THRESHOLD` or more times is flagged as N+1.

## Development

```bash
python -m venv .venv
.venv/bin/pip install -e ".[test]"
.venv/bin/pytest
```

Tested on Django 4.2, 5.2 and 6.1.

## Roadmap

- [ ] `EXPLAIN` slow queries and suggest missing indexes (MySQL, PostgreSQL)
- [ ] pytest helpers — `assert_no_n_plus_one()` to fail CI when a regression lands
- [ ] Detect exact duplicates (same SQL *and* same params)
- [ ] Support Celery tasks and management commands, not just requests
- [ ] Async views
- [ ] Benchmark and document the middleware's own overhead

## License

MIT
