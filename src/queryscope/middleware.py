import logging
from contextlib import ExitStack

from django.db import connections

from . import conf
from .analysis import analyse
from .collector import QueryCollector
from .report import format_report

logger = logging.getLogger("queryscope")


class QueryScopeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not conf.get("ENABLED"):
            return self.get_response(request)

        collector = QueryCollector()
        with ExitStack() as stack:
            for connection in connections.all():
                stack.enter_context(connection.execute_wrapper(collector))
            response = self.get_response(request)

        report = analyse(
            collector.queries,
            slow_ms=conf.get("SLOW_QUERY_MS"),
            n_plus_one_threshold=conf.get("N_PLUS_ONE_THRESHOLD"),
        )
        request.queryscope = report
        if report.has_problems:
            logger.warning(format_report(request, report))
        return response
