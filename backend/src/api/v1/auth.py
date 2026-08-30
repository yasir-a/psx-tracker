from __future__ import annotations

from typing import Any
from flask import Blueprint, g, jsonify, request, Response

from src.api.decorators import jwt_required, rate_limit
from src.api.errors import ValidationError
from src.application.services.auth_service import AuthService
from src.infrastructure.db.repositories.pg_portfolio_repository import PgPortfolioRepository
from src.infrastructure.db.repositories.pg_user_repository import PgUserRepository
from src.infrastructure.db.session import get_db_session

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

def _get_auth_service() -> AuthService:
    session = get_db_session()
    return AuthService(session)

@auth_bp.route("/register", methods=["POST"])
@rate_limit(max_requests=10, window_seconds=60)
def register() -> tuple[Response, int]:
    """Register a new user account."""
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")

    if not email or not password or not full_name:
        raise ValidationError("Missing required fields: email, password, full_name")

    service = _get_auth_service()
    user, access_token, refresh_token = service.register(email, password, full_name)
    session = get_db_session()
    session.commit()

    payload = {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "created_at": user.created_at.isoformat(),
        },
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        },
    }
    return jsonify(payload), 201


@auth_bp.route("/login", methods=["POST"])
@rate_limit(max_requests=10, window_seconds=60)
def login() -> tuple[Response, int]:
    """Log in existing user and issue tokens."""
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise ValidationError("Missing email or password")

    service = _get_auth_service()
    user, access_token, refresh_token = service.login(email, password)

    payload = {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "created_at": user.created_at.isoformat(),
        },
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        },
    }
    return jsonify(payload), 200


@auth_bp.route("/refresh", methods=["POST"])
def refresh() -> tuple[Response, int]:
    """Exchange a valid refresh token for a fresh access token."""
    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        raise ValidationError("Missing refresh_token")

    service = _get_auth_service()
    new_access_token = service.refresh_access_token(refresh_token)

    return jsonify({"access_token": new_access_token, "token_type": "Bearer"}), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required
def logout() -> tuple[Response, int]:
    """Revoke the current access token."""
    service = _get_auth_service()
    if getattr(g, "token_jti", None) and getattr(g, "token_exp", None):
        service.logout(g.token_jti, g.token_exp)
    return jsonify({"message": "Successfully logged out"}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required
def get_me() -> tuple[Response, int]:
    """Retrieve authenticated user profile."""
    session = get_db_session()
    user_repo = PgUserRepository(session)
    user = user_repo.get_by_id(g.current_user_id)

    if not user:
        raise ValidationError("User not found")

    payload = {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
        }
    }
    return jsonify(payload), 200