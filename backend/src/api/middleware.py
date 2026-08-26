from __future__ import annotations

import time
import uuid
from flask import Flask, g, request, Response


def register_middleware(app: Flask) -> None:
    """Register request tracing and lifecycle middleware."""

    @app.before_request
    def before_request() -> None:
        # Generate or capture existing request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        g.request_id = request_id
        g.start_time = time.perf_counter()

    @app.after_request
    def after_request(response: Response) -> Response:
        # Attach request ID to response header
        if hasattr(g, "request_id"):
            response.headers["X-Request-ID"] = g.request_id

        # Log request latency in debug/info
        if hasattr(g, "start_time"):
            duration_ms = (time.perf_counter() - g.start_time) * 1000
            app.logger.info(
                "%s %s %s %.2fms [req_id=%s]",
                request.method,
                request.path,
                response.status_code,
                duration_ms,
                getattr(g, "request_id", "-"),
            )
        return response