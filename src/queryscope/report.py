def _short(sql, limit=200):
    return sql if len(sql) <= limit else sql[:limit] + " ..."


def format_report(request, report):
    lines = [
        f"{request.method} {request.path} - {len(report.queries)} queries, "
        f"{report.total_ms:.1f} ms in DB"
    ]
    for r in report.repeated:
        lines.append(f"  N+1: {r.count}x at {r.origin} ({r.total_ms:.1f} ms total)")
        lines.append(f"       {_short(r.sql)}")
    for q in report.slow:
        lines.append(f"  Slow: {q.duration_ms:.1f} ms at {q.origin}")
        lines.append(f"       {_short(q.sql)}")
    return "\n".join(lines)
