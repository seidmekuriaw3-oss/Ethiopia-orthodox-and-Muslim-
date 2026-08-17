import os
from app import app, _start_background_services

# Gunicorn imports this WSGI module rather than calling app.main().
_start_background_services()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
