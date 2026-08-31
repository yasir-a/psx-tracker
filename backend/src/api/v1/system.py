from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from flask import Blueprint, Response, jsonify

from src.api.decorators import jwt_required
from src.config import get_settings

system_bp = Blueprint("system", __name__, url_prefix="/system")

# Dedicated backup directory
BACKUP_DIR = Path(r"C:\psx-tracker-backup")


@system_bp.route("/backup-db", methods=["POST"])
@jwt_required
def backup_database() -> tuple[Response, int]:
    """Take a full PostgreSQL database dump and store it in C:\\psx-tracker-backup."""
    settings = get_settings()
    
    # Ensure backup directory exists
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"psx_portfolio_backup_{timestamp}.sql"
    output_file = BACKUP_DIR / backup_filename

    # Parse database URL
    parsed = urlparse(settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://"))
    user = parsed.username or "psx_user"
    password = parsed.password or "Dai7aWu7ae"
    host = parsed.hostname or "localhost"
    port = str(parsed.port or 5432)
    dbname = parsed.path.lstrip("/") or "psx_portfolio"

    pg_dump_candidates = [
        r"C:\PostgreSQL\16\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
        "pg_dump",
    ]

    pg_dump_cmd = "pg_dump"
    for candidate in pg_dump_candidates:
        if os.path.exists(candidate):
            pg_dump_cmd = candidate
            break

    cmd = [
        pg_dump_cmd,
        "-U",
        user,
        "-h",
        host,
        "-p",
        port,
        "-d",
        dbname,
        "-F",
        "p",
        "-f",
        str(output_file),
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = password

    try:
        res = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if res.returncode != 0:
            error_msg = res.stderr.strip() or f"pg_dump exited with return code {res.returncode}"
            return jsonify({
                "error": {
                    "code": "BACKUP_FAILED",
                    "message": error_msg,
                }
            }), 500

        return jsonify({
            "message": f"Database backup saved successfully to C:\\psx-tracker-backup\\{backup_filename}",
            "file_path": str(output_file),
        }), 200
    except Exception as e:
        return jsonify({
            "error": {
                "code": "BACKUP_FAILED",
                "message": f"Failed to execute database backup: {str(e)}",
            }
        }), 500