from __future__ import annotations

from src.app import create_app
from src.config import get_settings

settings = get_settings()
app = create_app(settings)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=settings.DEBUG)