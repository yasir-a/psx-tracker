from __future__ import annotations

from typing import Any
from flask import Flask, jsonify, Response
from werkzeug.exceptions import HTTPException


class AppError(Exception):
    """Base application exception for domain and API errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class ValidationError(AppError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required", details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401,
            details=details,
        )


class ForbiddenError(AppError):
    def __init__(self, message: str = "Access denied", details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
            details=details,
        )


def register_error_handlers(app: Flask) -> None:
    """Register uniform JSON error handlers on the Flask application."""

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError) -> tuple[Response, int]:
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException) -> tuple[Response, int]:
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            429: "TOO_MANY_REQUESTS",
            500: "INTERNAL_SERVER_ERROR",
        }
        error_code = code_map.get(error.code or 500, "HTTP_ERROR")
        response_body = {
            "error": {
                "code": error_code,
                "message": error.description or "An HTTP error occurred",
                "details": {},
            }
        }
        return jsonify(response_body), error.code or 500

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error: Exception) -> tuple[Response, int]:
        app.logger.exception("Unhandled exception occurred: %s", str(error))
        response_body = {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred on the server",
                "details": {},
            }
        }
        return jsonify(response_body), 500