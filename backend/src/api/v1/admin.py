from __future__ import annotations

from uuid import UUID
from flask import Blueprint, g, jsonify, request, Response

from src.api.decorators import admin_required, jwt_required
from src.api.errors import ValidationError
from src.application.services.admin_service import AdminService
from src.infrastructure.db.session import get_db_session

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _get_admin_service() -> AdminService:
    return AdminService(get_db_session())


@admin_bp.route("/users", methods=["GET"])
@jwt_required
@admin_required
def list_users() -> tuple[Response, int]:
    """List registered users with pagination and search."""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    search = request.args.get("search")

    service = _get_admin_service()
    result = service.list_users(page=page, per_page=per_page, search=search)
    return jsonify(result), 200


@admin_bp.route("/users/<uuid:user_id>", methods=["GET"])
@jwt_required
@admin_required
def get_user(user_id: UUID) -> tuple[Response, int]:
    """Retrieve detailed user metadata."""
    service = _get_admin_service()
    details = service.get_user_details(user_id)
    return jsonify(details), 200


@admin_bp.route("/users/<uuid:user_id>/reset-password", methods=["POST"])
@jwt_required
@admin_required
def reset_password(user_id: UUID) -> tuple[Response, int]:
    """Reset a user's password."""
    data = request.get_json(silent=True) or {}
    new_password = data.get("new_password")
    if not new_password:
        raise ValidationError("Missing new_password field")

    service = _get_admin_service()
    service.reset_password(
        admin_id=g.current_user_id,
        target_user_id=user_id,
        new_password=new_password,
    )
    return jsonify({"message": "Password reset successfully. User sessions have been invalidated."}), 200


@admin_bp.route("/users/<uuid:user_id>", methods=["DELETE"])
@jwt_required
@admin_required
def delete_user(user_id: UUID) -> tuple[Response, int]:
    """Hard-delete user and all associated records."""
    service = _get_admin_service()
    service.delete_user(
        admin_id=g.current_user_id,
        target_user_id=user_id,
    )
    return jsonify({"message": "User and all associated data permanently deleted."}), 200